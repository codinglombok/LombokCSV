/**
 * Vector runner (GP-11): executes every case in vectors/lombokcsv-vectors-v1.json
 * against the TypeScript reference. Results are compared as canonical JSON, so key
 * order inside objects is part of the contract.
 */
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { CSV, CSVError, CSVParser, type CSVOptions } from '../src/index'

interface Case {
  id: string
  fn: string
  input: string
  options?: CSVOptions
  html?: { className?: string; id?: string }
  agg?: any
  call?: string
  expected: any
}

const file = new URL('../vectors/lombokcsv-vectors-v1.json', import.meta.url)
const doc = JSON.parse(readFileSync(file, 'utf-8')) as { cases: Case[] }

function run(fn: string, c: Case): unknown {
  const opts = c.options ?? {}
  switch (fn) {
    case 'parseRows':
      return new CSVParser(c.input, opts).parseRows()
    case 'parse': {
      const r = new CSVParser(c.input, opts).parse(opts.hasHeader ?? true)
      return { headers: r.headers ?? null, rows: r.rows, types: r.types }
    }
    case 'toHTML':
      return new CSV(c.input, opts).toHTML(c.html)
    case 'toJSON':
      return new CSV(c.input, opts).toJSON()
    case 'aggregate':
      return new CSV(c.input, opts).aggregate(c.agg)
    default:
      throw new Error(`unknown fn ${fn}`)
  }
}

describe('lombokcsv vectors v1', () => {
  it('has at least 100 cases', () => {
    expect(doc.cases.length).toBeGreaterThanOrEqual(100)
  })

  for (const c of doc.cases) {
    it(c.id, () => {
      if (c.fn === 'error') {
        let caught: unknown
        try {
          run(c.call!, c)
        } catch (e) {
          caught = e
        }
        expect(caught).toBeInstanceOf(CSVError)
        expect((caught as CSVError).code).toBe(c.expected.code)
        return
      }
      expect(JSON.stringify(run(c.fn, c))).toBe(JSON.stringify(c.expected))
    })
  }
})
