import { describe, it, expect } from 'vitest'
import { CSV, CSVParser } from '../src/csv'

describe('LombokCSV - CSV Parsing', () => {
  it('parses simple CSV', () => {
    const csv = new CSV('a,b,c\n1,2,3')
    expect(csv.getRows()).toHaveLength(1)
    expect(csv.getRows()[0]).toEqual(['1', '2', '3'])
  })

  it('parses with headers', () => {
    const csv = new CSV('Name,Age,City\nJohn,30,NYC')
    expect(csv.getHeaders()).toEqual(['Name', 'Age', 'City'])
    expect(csv.getRows()).toHaveLength(1)
  })

  it('handles quoted fields', () => {
    const csv = new CSV('"Name","Age"\n"John Smith",30')
    expect(csv.getHeaders()).toEqual(['Name', 'Age'])
    expect(csv.getRows()[0][0]).toBe('John Smith')
  })

  it('handles commas inside quotes', () => {
    const csv = new CSV('Name,Address\n"Smith, John","123 Main, Apt 4"')
    expect(csv.getRows()[0][0]).toContain('Smith')
    expect(csv.getRows()[0][1]).toContain('123 Main')
  })

  it('handles newlines inside quotes', () => {
    const csv = new CSV('Name,Description\n"John","Line 1\nLine 2"')
    expect(csv.getRows()).toHaveLength(1)
  })

  it('parses multiple rows', () => {
    const csv = new CSV('A,B\n1,2\n3,4\n5,6')
    expect(csv.getRows()).toHaveLength(3)
  })
})

describe('LombokCSV - Type Detection', () => {
  it('detects numbers', () => {
    const csv = new CSV('Name,Score\nJohn,95\nJane,88')
    const types = csv.getTypes()
    expect(types[0]).toBe('string')
    expect(types[1]).toBe('number')
  })

  it('detects dates', () => {
    const csv = new CSV('Event,Date\nConference,2026-07-24')
    const types = csv.getTypes()
    expect(types[1]).toBe('date')
  })

  it('detects booleans', () => {
    const csv = new CSV('Item,Active\nWidget,true')
    const types = csv.getTypes()
    expect(types[1]).toBe('boolean')
  })

  it('defaults to string', () => {
    const csv = new CSV('Name\nJohn')
    expect(csv.getTypes()[0]).toBe('string')
  })

  it('handles mixed types', () => {
    const csv = new CSV('Name,Value,Date,Active\nTest,123,2026-01-01,true')
    const types = csv.getTypes()
    expect(types[0]).toBe('string')
    expect(types[1]).toBe('number')
    expect(types[2]).toBe('date')
  })
})

describe('LombokCSV - HTML Generation', () => {
  it('generates HTML table', () => {
    const csv = new CSV('Name,Age\nJohn,30')
    const html = csv.toHTML()
    expect(html).toContain('<table>')
    expect(html).toContain('<thead>')
    expect(html).toContain('<th>Name</th>')
    expect(html).toContain('<tbody>')
    expect(html).toContain('<td>John</td>')
    expect(html).toContain('</table>')
  })

  it('right-aligns numeric columns', () => {
    const csv = new CSV('Name,Score\nJohn,95')
    const html = csv.toHTML()
    expect(html).toContain('text-align: right')
  })

  it('escapes HTML in content', () => {
    const csv = new CSV('Name\n<script>alert("xss")</script>')
    const html = csv.toHTML()
    expect(html).not.toContain('<script>')
    expect(html).toContain('&lt;script&gt;')
  })

  it('adds custom class and id', () => {
    const csv = new CSV('A\n1')
    const html = csv.toHTML({ className: 'data-table', id: 'table1' })
    expect(html).toContain('class="data-table"')
    expect(html).toContain('id="table1"')
  })
})

describe('LombokCSV - Aggregation', () => {
  const data = 'Department,Employee,Salary\nIT,John,50000\nIT,Jane,55000\nSales,Bob,40000\nSales,Alice,45000'

  it('groups by column', () => {
    const csv = new CSV(data)
    const result = csv.aggregate({
      groupBy: 0,
      count: true
    })

    expect(result).toHaveLength(2)
    const it = result.find((r: any) => r.Department === 'IT')
    expect(it?.count).toBe(2)
  })

  it('sums numeric columns', () => {
    const csv = new CSV(data)
    const result = csv.aggregate({
      groupBy: 'Department',
      sum: ['Salary']
    })

    const it = result.find((r: any) => r.Department === 'IT')
    expect(it?.Salary_sum).toBe(105000)

    const sales = result.find((r: any) => r.Department === 'Sales')
    expect(sales?.Salary_sum).toBe(85000)
  })

  it('counts rows per group', () => {
    const csv = new CSV(data)
    const result = csv.aggregate({
      groupBy: 'Department',
      count: true
    })

    expect(result).toHaveLength(2)
    const it = result.find((r: any) => r.Department === 'IT')
    expect(it?.count).toBe(2)
  })
})

describe('LombokCSV - JSON Export', () => {
  it('converts to JSON objects', () => {
    const csv = new CSV('Name,Age\nJohn,30\nJane,25')
    const json = csv.toJSON()

    expect(json).toHaveLength(2)
    expect(json[0]).toEqual({ Name: 'John', Age: '30' })
    expect(json[1]).toEqual({ Name: 'Jane', Age: '25' })
  })

  it('handles missing headers', () => {
    const csv = new CSV('1,2\n3,4', { hasHeader: false })
    expect(csv.getRows()).toHaveLength(2)
  })
})

describe('LombokCSV - Edge Cases', () => {
  it('handles empty CSV', () => {
    const csv = new CSV('')
    expect(csv.getRows()).toHaveLength(0)
  })

  it('handles single column', () => {
    const csv = new CSV('Name\nJohn')
    expect(csv.getRows()[0]).toHaveLength(1)
  })

  it('handles blank cells', () => {
    const csv = new CSV('A,B,C\n1,,3')
    expect(csv.getRows()[0]).toEqual(['1', '', '3'])
  })

  it('handles trailing commas', () => {
    const csv = new CSV('A,B,C\n1,2,')
    expect(csv.getRows()[0]).toHaveLength(3)
  })

  it('handles Windows line endings', () => {
    const csv = new CSV('A,B\r\n1,2\r\n3,4')
    expect(csv.getRows()).toHaveLength(2)
  })
})

describe('LombokCSV - Parser Options', () => {
  it('respects custom delimiter', () => {
    const csv = new CSV('A;B;C\n1;2;3', { delimiter: ';' })
    expect(csv.getRows()[0]).toHaveLength(3)
  })

  it('handles without header option', () => {
    const csv = new CSV('1,2,3', { hasHeader: false })
    expect(csv.getRows()).toHaveLength(1)
    expect(csv.getHeaders()).toBeUndefined()
  })
})

describe('LombokCSV - Large Data', () => {
  it('handles large CSV', () => {
    const rows = Array(1000)
      .fill(null)
      .map((_, i) => `${i},value_${i}`)
      .join('\n')

    const csv = new CSV(`ID,Value\n${rows}`)
    expect(csv.getRows()).toHaveLength(1000)
  })

  it('performs aggregation on large data', () => {
    const rows = Array(100)
      .fill(null)
      .map((_, i) => `Group_${i % 10},Value_${i % 10}`)
      .join('\n')

    const csv = new CSV(`Group,Value\n${rows}`)
    const result = csv.aggregate({ groupBy: 0, count: true })

    expect(result).toHaveLength(10)
  })
})
