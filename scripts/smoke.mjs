/**
 * Smoke test against the built package (dist/), not the sources.
 * Run: npm run smoke   (builds first)
 *
 * The fixtures and expected strings are taken from the shared vector file
 * (vectors/lombokcsv-vectors-v1.json) so this proves the shipped artifact,
 * not just the sources.
 */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const pkg = require('../package.json');
const { CSV, CSVError } = await import(`../dist/index.js`);

// Fixture: Region,Product,Qty
const csv = new CSV('Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95');

assert.deepEqual(csv.getHeaders(), ['Region', 'Product', 'Qty']);
assert.deepEqual(csv.getTypes(), ['string', 'string', 'number']);
assert.equal(
  JSON.stringify(csv.toJSON()),
  JSON.stringify([
    { Region: 'West', Product: 'Rice', Qty: '120' },
    { Region: 'West', Product: 'Corn', Qty: '80' },
    { Region: 'East', Product: 'Rice', Qty: '95' },
  ]),
);

const agg = csv.aggregate({ groupBy: 'Region', sum: ['Qty'], avg: ['Qty'], count: true });
assert.deepEqual(agg, [
  { Region: 'West', Qty_sum: 200, Qty_avg: 100, count: 2 },
  { Region: 'East', Qty_sum: 95, Qty_avg: 95, count: 1 },
]);

const html = csv.toHTML({ className: 'report' });
assert.ok(html.startsWith('<table class="report">'));
assert.ok(html.includes('<th>Region</th>'));
assert.ok(html.includes('<td style="text-align: right">120</td>'));
assert.ok(html.endsWith('</table>'));

// Quoting edge: doubled quotes and commas inside quotes stay intact.
const quoted = new CSV('a,b\n"say ""hi""",x,y"');
assert.deepEqual(quoted.getRows(), [['say "hi"', 'x', 'y"']]);

// Errors are [CODE]-prefixed CSVError instances.
let caught;
try {
  new CSV('a,b', { delimiter: '' });
} catch (e) {
  caught = e;
}
assert.ok(caught instanceof CSVError);
assert.equal(caught.code, 'INVALID_OPTION');
assert.equal(caught.message, '[INVALID_OPTION] delimiter must be a single character other than CR/LF');

console.log(`lombokcsv smoke OK (v${pkg.version}, dist import)`);
