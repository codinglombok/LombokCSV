// Container smoke test: runs real parsing/HTML/JSON/aggregation against
// expectations pinned from the shared vectors (vectors/lombokcsv-vectors-v1.json).
import assert from 'node:assert/strict'
import { CSV, CSVError } from './dist/index.js'

const version = process.env.LOMBOKCSV_VERSION ?? 'dev'

const csv = new CSV('Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95')

assert.deepEqual(csv.getHeaders(), ['Region', 'Product', 'Qty'])
assert.deepEqual(csv.getTypes(), ['string', 'string', 'number'])
assert.deepEqual(csv.aggregate({ groupBy: 'Region', sum: ['Qty'], avg: ['Qty'], count: true }), [
  { Region: 'West', Qty_sum: 200, Qty_avg: 100, count: 2 },
  { Region: 'East', Qty_sum: 95, Qty_avg: 95, count: 1 },
])
assert.deepEqual(csv.toJSON(), [
  { Region: 'West', Product: 'Rice', Qty: '120' },
  { Region: 'West', Product: 'Corn', Qty: '80' },
  { Region: 'East', Product: 'Rice', Qty: '95' },
])
assert.ok(csv.toHTML().startsWith('<table>\n<thead>\n<tr>\n<th>Region</th>'))

let caught
try {
  new CSV('a,b', { delimiter: '' })
} catch (e) {
  caught = e
}
assert.ok(caught instanceof CSVError)
assert.equal(caught.code, 'INVALID_OPTION')
assert.equal(caught.message, '[INVALID_OPTION] delimiter must be a single character other than CR/LF')

console.log(`lombokcsv container smoke OK (v${version})`)
