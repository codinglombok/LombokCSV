<?php

declare(strict_types=1);

// Unit tests for the PHP port (mirrors the TypeScript unit suite).

require_once __DIR__ . '/bootstrap.php';

use CodingLombok\LombokCSV\Csv;
use CodingLombok\LombokCSV\CsvError;
use CodingLombok\LombokCSV\CsvParser;
use function CodingLombok\LombokCSV\detect_types;
use function CodingLombok\LombokCSV\escape_html;
use function CodingLombok\LombokCSV\is_boolean;
use function CodingLombok\LombokCSV\is_date;
use function CodingLombok\LombokCSV\is_number;

// --- helpers -----------------------------------------------------------------
check(is_number('12.5') && is_number('-1e10') && is_number('.5') && is_number('3.'), 'is_number patterns');
check(!is_number('+1') && !is_number('0x1F') && !is_number('NaN') && !is_number('12abc') && !is_number(''), 'is_number rejects');
check(is_date('2026-07-24') && is_date('2026-07-24T10:30') && is_date('24/07/2026') && is_date('7-4-2026'), 'is_date patterns');
check(!is_date('2026-07-24x') && !is_date('2026-7-24'), 'is_date anchored');
check(is_boolean('true') && is_boolean('FALSE') && is_boolean('Yes') && is_boolean('1') && is_boolean('0'), 'is_boolean patterns');
check(!is_boolean('y') && !is_boolean('2'), 'is_boolean rejects');
check(escape_html('<b>&"\'') === '&lt;b&gt;&amp;&quot;&#39;', 'escape_html order');
check(detect_types([['1'], ['abc']]) === ['string'], 'detect_types mixed column');

// --- parsing -----------------------------------------------------------------
$csv = new Csv('a,b,c
1,2,3');
check($csv->getRows() === [['1', '2', '3']], 'parses simple CSV');

$csv = new Csv('Name,Age,City
John,30,NYC');
check($csv->getHeaders() === ['Name', 'Age', 'City'] && count($csv->getRows()) === 1, 'parses with headers');

$csv = new Csv('"Name","Age"
"John Smith",30');
check($csv->getRows()[0][0] === 'John Smith', 'quoted fields');

$csv = new Csv('Name,Address
"Smith, John","123 Main, Apt 4"');
check($csv->getRows()[0] === ['Smith, John', '123 Main, Apt 4'], 'commas inside quotes');

$csv = new Csv("Name,Description\n\"John\",\"Line 1\nLine 2\"");
check(count($csv->getRows()) === 1, 'newlines inside quotes');

$csv = new Csv("A,B\r
1,2\r
3,4");
check(count($csv->getRows()) === 2, 'CRLF line endings');

$csv = new Csv("\xEF\xBB\xBFA,B
1,2");
check($csv->getHeaders() === ['A', 'B'], 'BOM removed');

$csv = new Csv('a,b

1,2');
check($csv->getRows() === [['1', '2']], 'blank lines skipped');

$parser = new CsvParser('"unterminated,x
y');
check($parser->parseRows() === [['unterminated,x
y']], 'unterminated quote is lenient');

$parser = new CsvParser('  a  ,  b  ', ['trim' => false]);
check($parser->parseRows() === [['  a  ', '  b  ']], 'trim=false keeps blanks');

$parser = new CsvParser('" a ",b');
check($parser->parseRows() === [[' a ', 'b']], 'quoted content is never trimmed');

$parser = new CsvParser("'a,b',c", ['quote' => "'"]);
check($parser->parseRows() === [['a,b', 'c']], 'custom quote');

$parser = new CsvParser('a;b;c
1;2;3', ['delimiter' => ';']);
check($parser->parseRows() === [['a', 'b', 'c'], ['1', '2', '3']], 'custom delimiter');

$csv = new Csv('');
check($csv->getRows() === [] && $csv->getHeaders() === null, 'empty CSV');

// --- types -------------------------------------------------------------------
$csv = new Csv('Name,Value,Date,Active
Test,123,2026-01-01,true');
check($csv->getTypes() === ['string', 'number', 'date', 'boolean'], 'type detection');

$csv = new Csv('b
true
FALSE
Yes
no');
check($csv->getTypes() === ['boolean'], 'boolean detection');

$csv = new Csv('m
1
abc');
check($csv->getTypes() === ['string'], 'mixed column falls back to string');

// --- HTML --------------------------------------------------------------------
$csv = new Csv('Name,Age
John,30');
$html = $csv->toHTML();
check(str_contains($html, '<table>') && str_contains($html, '<thead>') && str_contains($html, '<th>Name</th>')
    && str_contains($html, '<td style="text-align: right">30</td>') && str_ends_with($html, '</table>'), 'HTML table');

$csv = new Csv('Name
<script>alert("xss")</script>');
$html = $csv->toHTML();
check(!str_contains($html, '<script>') && str_contains($html, '&lt;script&gt;'), 'HTML escaping');

$csv = new Csv('A
1');
$html = $csv->toHTML(['className' => '" onclick="alert(1)']);
check(!str_contains($html, 'onclick="alert(1)"'), 'class attribute escaped');

$html = $csv->toHTML(['className' => 'data-table', 'id' => 't1']);
check(str_contains($html, 'class="data-table"') && str_contains($html, 'id="t1"'), 'class and id attributes');

$html = (new Csv(''))->toHTML();
check($html === "<table>\n<tbody>\n</tbody>\n</table>", 'empty HTML table');

// --- JSON --------------------------------------------------------------------
$csv = new Csv('Name,Age
John,30
Jane,25');
check($csv->toJSON() === [['Name' => 'John', 'Age' => '30'], ['Name' => 'Jane', 'Age' => '25']], 'JSON export');

$csv = new Csv('1,2
3,4', ['hasHeader' => false]);
check($csv->toJSON() === [['1', '2'], ['3', '4']], 'JSON without header');

$csv = new Csv('a,a
1,2');
check($csv->toJSON() === [['a' => '2']], 'duplicate headers: last wins');

$csv = new Csv('a,b
1');
check($csv->toJSON() === [['a' => '1', 'b' => '']], 'missing cells become empty strings');

// --- aggregation -------------------------------------------------------------
$data = 'Department,Employee,Salary
IT,John,50000
IT,Jane,55000
Sales,Bob,40000
Sales,Alice,45000';
$csv = new Csv($data);
$result = $csv->aggregate(['groupBy' => 'Department', 'sum' => ['Salary'], 'count' => true]);
check(count($result) === 2, 'two groups');
check($result[0]['Department'] === 'IT' && $result[0]['Salary_sum'] === 105000.0 && $result[0]['count'] === 2, 'IT group');
check($result[1]['Salary_sum'] === 85000.0, 'Sales group');
check(array_keys($result[0]) === ['Department', 'Salary_sum', 'count'], 'key order');

$csv = new Csv('g,v
x,1
x,abc
x,
x,2');
$result = $csv->aggregate(['groupBy' => 'g', 'sum' => ['v'], 'avg' => ['v'], 'count' => true]);
check($result === [['g' => 'x', 'v_sum' => 3.0, 'v_avg' => 1.5, 'count' => 4]], 'sum/avg ignore non-numeric');

$csv = new Csv('g,v
x,abc');
$result = $csv->aggregate(['groupBy' => 'g', 'sum' => ['v'], 'avg' => ['v']]);
check($result === [['g' => 'x', 'v_sum' => 0.0, 'v_avg' => null]], 'avg null without numbers');

$csv = new Csv('a,1
b,2
a,3', ['hasHeader' => false]);
$result = $csv->aggregate(['groupBy' => 0, 'sum' => [1]]);
check($result === [['col_0' => 'a', 'col_1_sum' => 4.0], ['col_0' => 'b', 'col_1_sum' => 2.0]], 'col_ names without header');

$csv = new Csv('g,v
A,1
a,2');
$result = $csv->aggregate(['groupBy' => 'g', 'count' => true]);
check(count($result) === 2, 'group keys are case-sensitive');

// --- errors ------------------------------------------------------------------
try {
    new Csv('a,b', ['delimiter' => '']);
    check(false, 'empty delimiter: no exception');
} catch (CsvError $e) {
    check($e->errorCode === 'INVALID_OPTION', 'empty delimiter code');
    check($e->getMessage() === '[INVALID_OPTION] delimiter must be a single character other than CR/LF', 'empty delimiter message');
}

try {
    new Csv('a,b', ['delimiter' => '"']);
    check(false, 'delimiter equals quote: no exception');
} catch (CsvError $e) {
    check($e->errorCode === 'INVALID_OPTION', 'delimiter equals quote code');
    check($e->getMessage() === '[INVALID_OPTION] delimiter and quote must differ', 'delimiter equals quote message');
}

$csv = new Csv('a,b
1,2');
try {
    $csv->aggregate(['groupBy' => 'Missing', 'count' => true]);
    check(false, 'unknown column: no exception');
} catch (CsvError $e) {
    check($e->errorCode === 'UNKNOWN_COLUMN', 'unknown column code');
    check($e->getMessage() === '[UNKNOWN_COLUMN] unknown column: Missing', 'unknown column message');
}

try {
    $csv->aggregate(['groupBy' => 3]);
    check(false, 'index out of range: no exception');
} catch (CsvError $e) {
    check($e->errorCode === 'UNKNOWN_COLUMN', 'index out of range code');
    check($e->getMessage() === '[UNKNOWN_COLUMN] column index out of range: 3', 'index out of range message');
}

try {
    $csv->aggregate(['groupBy' => 1.5]);
    check(false, 'fractional index: no exception');
} catch (CsvError $e) {
    check($e->getMessage() === '[UNKNOWN_COLUMN] column index out of range: 1.5', 'fractional index message');
}

finish('api');
