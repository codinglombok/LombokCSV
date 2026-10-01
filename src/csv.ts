/**
 * LombokCSV - CSV parser, type detector, HTML table generator and aggregator.
 * Zero runtime dependencies. Normative behaviour: docs/SPEC_LombokCSV_v<version>.md
 */

export type DataType = 'string' | 'number' | 'date' | 'boolean'

export interface CSVOptions {
  /** Field separator, exactly one UTF-16 code unit (default `,`). */
  delimiter?: string
  /** Quote character, exactly one UTF-16 code unit (default `"`). */
  quote?: string
  /**
   * @deprecated Ignored. RFC 4180 escapes a quote by doubling it; kept only for
   * source compatibility with 1.0.0.
   */
  escape?: string
  /** First record is the header row (default `true`). */
  hasHeader?: boolean
  /** Remove spaces and tabs around unquoted field content (default `true`). */
  trim?: boolean
}

export interface CSVData {
  headers?: string[]
  rows: string[][]
  types: DataType[]
}

export interface AggregationOptions {
  /** Column index or header name. */
  groupBy: number | string
  /** Columns to sum. */
  sum?: (number | string)[]
  count?: boolean
  /** Columns to average. */
  avg?: (number | string)[]
}

export interface AggregationResult {
  [key: string]: string | number | null
}

export interface HTMLOptions {
  className?: string
  id?: string
}

export type CSVErrorCode = 'INVALID_OPTION' | 'UNKNOWN_COLUMN'

/** Error with a stable, language-neutral `code` (SPEC §5). */
export class CSVError extends Error {
  readonly code: CSVErrorCode
  constructor(code: CSVErrorCode, message: string) {
    super(message)
    this.name = 'CSVError'
    this.code = code
  }
}

/** Number of leading rows inspected by type detection (SPEC §3). */
export const TYPE_SAMPLE_ROWS = 10

const NUMBER_RE = /^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/
const DATE_RES = [
  /^\d{4}-\d{2}-\d{2}$/,
  /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$/,
  /^\d{1,2}\/\d{1,2}\/\d{4}$/,
  /^\d{1,2}-\d{1,2}-\d{4}$/,
]
const BOOLEAN_RE = /^(true|false|yes|no|1|0)$/i

export function isNumber(val: string): boolean {
  return NUMBER_RE.test(val)
}

export function isDate(val: string): boolean {
  return DATE_RES.some(re => re.test(val))
}

export function isBoolean(val: string): boolean {
  return BOOLEAN_RE.test(val)
}

function isBlank(c: string): boolean {
  return c === ' ' || c === '\t'
}

/** Strips SPACE, TAB, CR and LF from both ends (SPEC §3.1). */
function strip(val: string): string {
  return val.replace(/^[ \t\r\n]+|[ \t\r\n]+$/g, '')
}

function singleChar(name: string, value: string): string {
  if (value.length !== 1 || value === '\n' || value === '\r') {
    throw new CSVError('INVALID_OPTION', `${name} must be a single character other than CR/LF`)
  }
  return value
}

/**
 * CSV parser - RFC 4180 records with configurable delimiter and quote.
 */
export class CSVParser {
  private data: string
  private delimiter: string
  private quote: string
  private trim: boolean

  constructor(data: string, options: CSVOptions = {}) {
    this.data = data.charCodeAt(0) === 0xfeff ? data.slice(1) : data
    this.delimiter = singleChar('delimiter', options.delimiter ?? ',')
    this.quote = singleChar('quote', options.quote ?? '"')
    if (this.delimiter === this.quote) {
      throw new CSVError('INVALID_OPTION', 'delimiter and quote must differ')
    }
    this.trim = options.trim ?? true
  }

  parse(hasHeader: boolean = true): CSVData {
    const rows = this.parseRows()
    if (rows.length === 0) {
      return { rows: [], types: [] }
    }
    const headers = hasHeader ? rows.shift() : undefined
    return { headers, rows, types: detectTypes(rows) }
  }

  /** Splits the input into records (SPEC §2). */
  parseRows(): string[][] {
    const { data, delimiter, quote, trim } = this
    const rows: string[][] = []
    let row: string[] = []
    let field = ''
    let quoted = false
    let rowQuoted = false
    // 0 = field start, 1 = unquoted, 2 = inside quotes, 3 = after closing quote
    let state = 0

    const endField = () => {
      row.push(trim && !quoted ? field.replace(/[ \t]+$/, '') : field)
      rowQuoted ||= quoted
      field = ''
      quoted = false
      state = 0
    }
    const endRecord = () => {
      endField()
      // A line holding a single empty unquoted field is blank and skipped.
      if (row.length > 1 || row[0] !== '' || rowQuoted) rows.push(row)
      row = []
      rowQuoted = false
    }

    let i = 0
    const n = data.length
    while (i < n) {
      const c = data[i]
      if (state === 2) {
        if (c === quote) {
          if (data[i + 1] === quote) {
            field += quote
            i += 2
            continue
          }
          state = 3
        } else {
          field += c
        }
        i++
        continue
      }
      if (c === delimiter) {
        endField()
      } else if (c === '\n' || c === '\r') {
        endRecord()
        if (c === '\r' && data[i + 1] === '\n') i++
      } else if (state === 0) {
        if (c === quote) {
          quoted = true
          state = 2
        } else if (!(trim && isBlank(c))) {
          field += c
          state = 1
        }
      } else if (state === 3) {
        // Lenient: text after a closing quote is appended literally.
        if (!(trim && isBlank(c))) field += c
      } else {
        field += c
      }
      i++
    }
    if (state !== 0 || row.length > 0) endRecord()
    return rows
  }
}

/** Detects one type per column from the first TYPE_SAMPLE_ROWS rows (SPEC §3). */
export function detectTypes(rows: string[][]): DataType[] {
  let numCols = 0
  for (const r of rows) if (r.length > numCols) numCols = r.length
  const types: DataType[] = []
  const sample = rows.slice(0, TYPE_SAMPLE_ROWS)
  for (let col = 0; col < numCols; col++) {
    let any = false
    let num = true
    let date = true
    let bool = true
    for (const row of sample) {
      const val = strip(row[col] ?? '')
      if (val === '') continue
      any = true
      if (num && !isNumber(val)) num = false
      if (date && !isDate(val)) date = false
      if (bool && !isBoolean(val)) bool = false
    }
    types.push(!any ? 'string' : num ? 'number' : date ? 'date' : bool ? 'boolean' : 'string')
  }
  return types
}

/** Escapes text for HTML element content and double-quoted attribute values. */
export function escapeHTML(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/**
 * HTML generator - semantic table markup (SPEC §4).
 */
export class HTMLGenerator {
  private data: CSVData

  constructor(data: CSVData) {
    this.data = data
  }

  generate(options?: HTMLOptions): string {
    const classAttr = options?.className ? ` class="${escapeHTML(options.className)}"` : ''
    const idAttr = options?.id ? ` id="${escapeHTML(options.id)}"` : ''

    let html = `<table${classAttr}${idAttr}>\n`
    if (this.data.headers && this.data.headers.length > 0) {
      html += '<thead>\n<tr>\n'
      for (const header of this.data.headers) {
        html += `<th>${escapeHTML(header)}</th>\n`
      }
      html += '</tr>\n</thead>\n'
    }
    html += '<tbody>\n'
    for (const row of this.data.rows) {
      html += '<tr>\n'
      for (let i = 0; i < row.length; i++) {
        const align = this.data.types[i] === 'number' ? ' style="text-align: right"' : ''
        html += `<td${align}>${escapeHTML(row[i] ?? '')}</td>\n`
      }
      html += '</tr>\n'
    }
    html += '</tbody>\n</table>'
    return html
  }
}

/**
 * Aggregator - GROUP BY with SUM / COUNT / AVG (SPEC §5).
 */
export class CSVAggregator {
  private data: CSVData

  constructor(data: CSVData) {
    this.data = data
  }

  private width(): number {
    let w = this.data.headers?.length ?? 0
    for (const r of this.data.rows) if (r.length > w) w = r.length
    return w
  }

  private resolve(col: number | string): number {
    if (typeof col === 'string') {
      const idx = this.data.headers ? this.data.headers.indexOf(col) : -1
      if (idx < 0) throw new CSVError('UNKNOWN_COLUMN', `unknown column: ${col}`)
      return idx
    }
    if (!Number.isInteger(col) || col < 0 || col >= this.width()) {
      throw new CSVError('UNKNOWN_COLUMN', `column index out of range: ${col}`)
    }
    return col
  }

  private name(idx: number): string {
    return this.data.headers?.[idx] ?? `col_${idx}`
  }

  aggregate(options: AggregationOptions): AggregationResult[] {
    const g = this.resolve(options.groupBy)
    const sums = (options.sum ?? []).map(c => this.resolve(c))
    const avgs = (options.avg ?? []).map(c => this.resolve(c))
    const groupName = this.name(g)

    interface Acc { key: string; count: number; sum: number[]; avgSum: number[]; avgN: number[] }
    const groups = new Map<string, Acc>()

    for (const row of this.data.rows) {
      const key = row[g] ?? ''
      let acc = groups.get(key)
      if (!acc) {
        acc = { key, count: 0, sum: sums.map(() => 0), avgSum: avgs.map(() => 0), avgN: avgs.map(() => 0) }
        groups.set(key, acc)
      }
      acc.count++
      sums.forEach((c, k) => {
        const v = strip(row[c] ?? '')
        if (isNumber(v)) acc!.sum[k] += Number(v)
      })
      avgs.forEach((c, k) => {
        const v = strip(row[c] ?? '')
        if (isNumber(v)) {
          acc!.avgSum[k] += Number(v)
          acc!.avgN[k]++
        }
      })
    }

    const out: AggregationResult[] = []
    for (const acc of groups.values()) {
      const r: AggregationResult = { [groupName]: acc.key }
      sums.forEach((c, k) => { r[`${this.name(c)}_sum`] = acc.sum[k] })
      avgs.forEach((c, k) => { r[`${this.name(c)}_avg`] = acc.avgN[k] === 0 ? null : acc.avgSum[k] / acc.avgN[k] })
      if (options.count) r['count'] = acc.count
      out.push(r)
    }
    return out
  }
}

/**
 * CSV - main API combining parser, generator and aggregator.
 */
export class CSV {
  private csvData: CSVData

  constructor(data: string, options: CSVOptions = {}) {
    const parser = new CSVParser(data, options)
    this.csvData = parser.parse(options.hasHeader ?? true)
  }

  toHTML(options?: HTMLOptions): string {
    return new HTMLGenerator(this.csvData).generate(options)
  }

  aggregate(options: AggregationOptions): AggregationResult[] {
    return new CSVAggregator(this.csvData).aggregate(options)
  }

  getHeaders(): string[] | undefined {
    return this.csvData.headers
  }

  getRows(): string[][] {
    return this.csvData.rows
  }

  getTypes(): DataType[] {
    return this.csvData.types
  }

  /**
   * Rows as objects keyed by header (SPEC §6). Missing cells become `""`, extra
   * cells are dropped, and for duplicate header names the last column wins.
   * Without a header row the raw rows are returned.
   */
  toJSON(): Record<string, string>[] | string[][] {
    const headers = this.csvData.headers
    if (!headers) return this.csvData.rows
    return this.csvData.rows.map(row => {
      const obj: Record<string, string> = {}
      for (let i = 0; i < headers.length; i++) obj[headers[i]] = row[i] ?? ''
      return obj
    })
  }
}
