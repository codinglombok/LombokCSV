/**
 * LombokCSV - CSV Parser, Type Detector, HTML Generator
 * Zero dependencies, production-grade
 */

export type DataType = 'string' | 'number' | 'date' | 'boolean'

export interface CSVOptions {
  delimiter?: string
  quote?: string
  escape?: string
  hasHeader?: boolean
}

export interface CSVData {
  headers?: string[]
  rows: any[][]
  types: DataType[]
}

export interface AggregationOptions {
  groupBy: number | string         // Column index or name
  sum?: (number | string)[]         // Columns to sum
  count?: boolean
  avg?: (number | string)[]         // Columns to average
}

export interface AggregationResult {
  [key: string]: any
}

/**
 * CSV Parser - handles quoting, escaping, delimiters
 */
export class CSVParser {
  private data: string
  private delimiter: string
  private quote: string
  private escape: string

  constructor(data: string, options: CSVOptions = {}) {
    this.data = data
    this.delimiter = options.delimiter || ','
    this.quote = options.quote || '"'
    this.escape = options.escape || '"'
  }

  parse(hasHeader: boolean = true): CSVData {
    const rows = this.parseRows()

    if (rows.length === 0) {
      return { rows: [], types: [] }
    }

    const headers = hasHeader ? rows.shift() : undefined
    const types = this.detectTypes(rows)

    return {
      headers,
      rows,
      types
    }
  }

  private parseRows(): string[][] {
    const rows: string[][] = []
    let currentRow: string[] = []
    let currentField = ''
    let inQuotes = false
    let i = 0

    while (i < this.data.length) {
      const char = this.data[i]
      const nextChar = this.data[i + 1]

      // Handle quotes
      if (char === this.quote) {
        if (inQuotes && nextChar === this.quote) {
          // Escaped quote
          currentField += this.quote
          i += 2
        } else {
          // Toggle quote state
          inQuotes = !inQuotes
          i++
        }
      }
      // Handle delimiter
      else if (char === this.delimiter && !inQuotes) {
        currentRow.push(currentField.trim())
        currentField = ''
        i++
      }
      // Handle newline
      else if ((char === '\n' || char === '\r') && !inQuotes) {
        if (currentField || currentRow.length > 0) {
          currentRow.push(currentField.trim())
          if (currentRow.length > 0) {
            rows.push(currentRow)
          }
          currentRow = []
          currentField = ''
        }
        if (char === '\r' && nextChar === '\n') {
          i += 2
        } else {
          i++
        }
      }
      // Regular character
      else {
        currentField += char
        i++
      }
    }

    // Add last field and row
    if (currentField || currentRow.length > 0) {
      currentRow.push(currentField.trim())
      if (currentRow.length > 0) {
        rows.push(currentRow)
      }
    }

    return rows
  }

  private detectTypes(rows: string[][]): DataType[] {
    if (rows.length === 0) return []

    const numCols = Math.max(...rows.map(r => r.length))
    const types: DataType[] = Array(numCols).fill('string')

    // Sample first 10 rows for type detection
    const sample = rows.slice(0, Math.min(10, rows.length))

    for (let col = 0; col < numCols; col++) {
      let isNumber = true
      let isDate = true
      let isBoolean = true

      for (const row of sample) {
        const val = row[col]?.trim() || ''

        if (!val) continue

        if (isNumber && !this.isNumber(val)) isNumber = false
        if (isDate && !this.isDate(val)) isDate = false
        if (isBoolean && !this.isBoolean(val)) isBoolean = false
      }

      if (isNumber) types[col] = 'number'
      else if (isDate) types[col] = 'date'
      else if (isBoolean) types[col] = 'boolean'
    }

    return types
  }

  private isNumber(val: string): boolean {
    return /^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(val)
  }

  private isDate(val: string): boolean {
    return /^\d{4}-\d{2}-\d{2}|^\d{1,2}\/\d{1,2}\/\d{4}|^\d{1,2}-\d{1,2}-\d{4}/.test(val)
  }

  private isBoolean(val: string): boolean {
    return /^(true|false|yes|no|1|0)$/i.test(val)
  }
}

/**
 * HTML Generator - creates semantic HTML tables from CSV data
 */
export class HTMLGenerator {
  private data: CSVData

  constructor(data: CSVData) {
    this.data = data
  }

  generate(options?: { className?: string; id?: string }): string {
    const classAttr = options?.className ? ` class="${options.className}"` : ''
    const idAttr = options?.id ? ` id="${options.id}"` : ''

    let html = `<table${classAttr}${idAttr}>\n`

    // Headers
    if (this.data.headers) {
      html += '<thead>\n<tr>\n'
      for (const header of this.data.headers) {
        html += `<th>${this.escape(header)}</th>\n`
      }
      html += '</tr>\n</thead>\n'
    }

    // Body
    html += '<tbody>\n'
    for (const row of this.data.rows) {
      html += '<tr>\n'
      for (let i = 0; i < row.length; i++) {
        const type = this.data.types[i]
        const align = type === 'number' ? ' style="text-align: right"' : ''
        html += `<td${align}>${this.escape(String(row[i] || ''))}</td>\n`
      }
      html += '</tr>\n'
    }
    html += '</tbody>\n</table>'

    return html
  }

  private escape(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }
}

/**
 * CSV Aggregator - grouping, summing, counting
 */
export class CSVAggregator {
  private data: CSVData

  constructor(data: CSVData) {
    this.data = data
  }

  aggregate(options: AggregationOptions): AggregationResult[] {
    const groupByCol = typeof options.groupBy === 'string'
      ? this.data.headers?.indexOf(options.groupBy) || 0
      : options.groupBy

    const groups = new Map<string, AggregationResult>()

    for (const row of this.data.rows) {
      const key = String(row[groupByCol])
      if (!groups.has(key)) {
        groups.set(key, { [this.data.headers?.[groupByCol] || groupByCol]: key })
      }

      const group = groups.get(key)!

      // Sum columns
      if (options.sum) {
        for (const sumCol of options.sum) {
          const colIndex = typeof sumCol === 'string'
            ? this.data.headers?.indexOf(sumCol) || 0
            : sumCol
          const colName = this.data.headers?.[colIndex] || `col_${colIndex}`
          const value = parseFloat(String(row[colIndex])) || 0
          group[`${colName}_sum`] = (group[`${colName}_sum`] || 0) + value
        }
      }

      // Average columns
      if (options.avg) {
        for (const avgCol of options.avg) {
          const colIndex = typeof avgCol === 'string'
            ? this.data.headers?.indexOf(avgCol) || 0
            : avgCol
          const colName = this.data.headers?.[colIndex] || `col_${colIndex}`
          const value = parseFloat(String(row[colIndex])) || 0
          const countKey = `${colName}_count`
          const avgKey = `${colName}_avg`
          group[countKey] = (group[countKey] || 0) + 1
          group[avgKey] = ((group[avgKey] || 0) * ((group[countKey] as number) - 1) + value) / (group[countKey] as number)
        }
      }

      // Count
      if (options.count) {
        group['count'] = (group['count'] || 0) + 1
      }
    }

    return Array.from(groups.values())
  }
}

/**
 * CSV Class - main API combining parser, generator, aggregator
 */
export class CSV {
  private csvData: CSVData
  private options: CSVOptions

  constructor(data: string, options: CSVOptions = {}) {
    this.options = { hasHeader: true, ...options }
    const parser = new CSVParser(data, options)
    this.csvData = parser.parse(this.options.hasHeader)
  }

  toHTML(options?: { className?: string; id?: string }): string {
    const generator = new HTMLGenerator(this.csvData)
    return generator.generate(options)
  }

  aggregate(options: AggregationOptions): AggregationResult[] {
    const aggregator = new CSVAggregator(this.csvData)
    return aggregator.aggregate(options)
  }

  getHeaders(): string[] | undefined {
    return this.csvData.headers
  }

  getRows(): any[][] {
    return this.csvData.rows
  }

  getTypes(): DataType[] {
    return this.csvData.types
  }

  toJSON(): any[] {
    if (!this.csvData.headers) {
      return this.csvData.rows
    }

    return this.csvData.rows.map(row => {
      const obj: any = {}
      for (let i = 0; i < this.csvData.headers!.length; i++) {
        obj[this.csvData.headers![i]] = row[i]
      }
      return obj
    })
  }
}


