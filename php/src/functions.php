<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

// Shared helpers of the PHP port (SPEC sections 0.3 and 3.1). The port
// operates on UTF-8 byte strings; PCRE with the /u flag gives code-point
// semantics without any extension dependency.

const TYPE_SAMPLE_ROWS = 10;

const NUMBER_RE = '/^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/';
const DATE_RES = [
    '/^\d{4}-\d{2}-\d{2}$/',
    '/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$/',
    '/^\d{1,2}\/\d{1,2}\/\d{4}$/',
    '/^\d{1,2}-\d{1,2}-\d{4}$/',
];
const BOOLEAN_RE = '/^(true|false|yes|no|1|0)$/i';

/** Reports whether $value matches the SPEC number pattern (section 3.1). */
function is_number(string $value): bool
{
    return preg_match(NUMBER_RE, $value) === 1;
}

/** Reports whether $value matches one of the SPEC date patterns (section 3.1). */
function is_date(string $value): bool
{
    foreach (DATE_RES as $re) {
        if (preg_match($re, $value) === 1) {
            return true;
        }
    }

    return false;
}

/** Reports whether $value matches the SPEC boolean pattern (section 3.1). */
function is_boolean(string $value): bool
{
    return preg_match(BOOLEAN_RE, $value) === 1;
}

/** Strips SPACE, TAB, CR and LF from both ends (SPEC section 0.3). */
function strip_cell(string $value): string
{
    return trim($value, " \t\r\n");
}

/** Splits a valid UTF-8 string into single-code-point strings. */
function split_chars(string $value): array
{
    if ($value === '') {
        return [];
    }
    $count = preg_match_all('/./us', $value, $matches);
    if ($count === false) {
        // Invalid UTF-8 is outside the contract (SPEC section 0.1); fall back
        // to bytes so the parser still runs in linear time without throwing.
        return str_split($value);
    }

    return $matches[0];
}

/** Detects one type per column from the first TYPE_SAMPLE_ROWS rows (SPEC section 3). */
function detect_types(array $rows): array
{
    $numCols = 0;
    foreach ($rows as $row) {
        $numCols = max($numCols, count($row));
    }
    $types = [];
    $sample = array_slice($rows, 0, TYPE_SAMPLE_ROWS);
    for ($col = 0; $col < $numCols; $col++) {
        $any = false;
        $num = $date = $bool = true;
        foreach ($sample as $row) {
            $val = strip_cell($row[$col] ?? '');
            if ($val === '') {
                continue;
            }
            $any = true;
            if ($num && !is_number($val)) {
                $num = false;
            }
            if ($date && !is_date($val)) {
                $date = false;
            }
            if ($bool && !is_boolean($val)) {
                $bool = false;
            }
        }
        $types[] = !$any ? 'string' : ($num ? 'number' : ($date ? 'date' : ($bool ? 'boolean' : 'string')));
    }

    return $types;
}

/** Escapes text for HTML element content and double-quoted attribute values. */
function escape_html(string $text): string
{
    return str_replace(
        ['&', '<', '>', '"', "'"],
        ['&amp;', '&lt;', '&gt;', '&quot;', '&#39;'],
        $text
    );
}
