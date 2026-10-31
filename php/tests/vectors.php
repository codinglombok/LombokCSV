<?php

declare(strict_types=1);

// Runs every case of the shared vector file. Comparison follows SPEC section
// 0.5: strings byte-exact, numbers by IEEE 754 binary64 equality (integral
// doubles equal integers), booleans and null by identity, arrays element-wise
// in order, objects by key sequence.

require_once __DIR__ . '/bootstrap.php';

use CodingLombok\LombokCSV\Csv;
use CodingLombok\LombokCSV\CsvError;
use CodingLombok\LombokCSV\CsvParser;

$doc = json_decode((string) file_get_contents(__DIR__ . '/../../vectors/lombokcsv-vectors-v1.json'), true, 512, JSON_THROW_ON_ERROR);

/** @param mixed $got @param mixed $want */
function expect_eq(mixed $got, mixed $want, string $path = '$'): void
{
    if (is_bool($want) || is_bool($got)) {
        check(is_bool($got) && is_bool($want) && $got === $want, "$path: " . json_encode($got) . ' != ' . json_encode($want));

        return;
    }
    if ($want === null || $got === null) {
        check($got === null && $want === null, "$path: " . json_encode($got) . ' != ' . json_encode($want));

        return;
    }
    if (is_int($want) || is_float($want)) {
        check((is_int($got) || is_float($got)) && (float) $got === (float) $want, "$path: " . json_encode($got) . ' != ' . json_encode($want));

        return;
    }
    if (is_string($want)) {
        check(is_string($got) && $got === $want, "$path: " . var_export($got, true) . ' != ' . var_export($want, true));

        return;
    }
    if (is_array($want)) {
        if (array_is_list($want)) {
            check(is_array($got) && array_is_list($got) && count($got) === count($want), "$path: list length mismatch");
            foreach ($want as $i => $w) {
                expect_eq($got[$i], $w, "{$path}[{$i}]");
            }

            return;
        }
        check(
            is_array($got) && !array_is_list($got) && array_keys($got) === array_keys($want),
            "$path: key order " . json_encode(array_keys($got ?: [])) . ' != ' . json_encode(array_keys($want))
        );
        foreach ($want as $k => $w) {
            expect_eq($got[$k] ?? null, $w, "{$path}.{$k}");
        }

        return;
    }
    check(false, "$path: unsupported type " . get_debug_type($want));
}

/** @param array{fn: string, input: string, options?: array, html?: array, agg?: array} $c */
function vector_run(array $c): mixed
{
    $options = $c['options'] ?? [];
    return match ($c['fn']) {
        'parseRows' => (new CsvParser($c['input'], $options))->parseRows(),
        'parse' => (static function () use ($c, $options): array {
            $r = (new CsvParser($c['input'], $options))->parse($options['hasHeader'] ?? true);

            return ['headers' => $r['headers'], 'rows' => $r['rows'], 'types' => $r['types']];
        })(),
        'toHTML' => (new Csv($c['input'], $options))->toHTML($c['html'] ?? []),
        'toJSON' => (new Csv($c['input'], $options))->toJSON(),
        'aggregate' => (new Csv($c['input'], $options))->aggregate($c['agg']),
        default => throw new RuntimeException("unknown fn {$c['fn']}"),
    };
}

$cases = $doc['cases'];
check(count($cases) >= 100, 'at least 100 cases');
foreach ($cases as $c) {
    $id = $c['id'];
    if ($c['fn'] === 'error') {
        try {
            vector_run(['fn' => $c['call']] + $c);
            check(false, "$id: no exception");
        } catch (CsvError $e) {
            check($e->errorCode === $c['expected']['code'], "$id: got {$e->errorCode}, want {$c['expected']['code']}");
            check($e->getMessage() === $c['expected']['message'], "$id: message '{$e->getMessage()}' != '{$c['expected']['message']}'");
        }
        continue;
    }
    try {
        $got = vector_run($c);
    } catch (CsvError $e) {
        check(false, "$id: unexpected CsvError {$e->errorCode}");
        continue;
    }
    expect_eq($got, $c['expected'], '$');
}

finish('vectors');
