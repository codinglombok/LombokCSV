<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

/** Aggregator - GROUP BY with SUM / COUNT / AVG (SPEC section 5). */
final class CsvAggregator
{
    /** @param array{headers: string[]|null, rows: list<list<string>>, types: list<string>} $data */
    public function __construct(private readonly array $data)
    {
    }

    private function width(): int
    {
        $w = $this->data['headers'] !== null ? count($this->data['headers']) : 0;
        foreach ($this->data['rows'] as $row) {
            $w = max($w, count($row));
        }

        return $w;
    }

    private function resolve(int|float|string $col): int
    {
        if (is_string($col)) {
            $idx = $this->data['headers'] === null ? false : array_search($col, $this->data['headers'], true);
            if ($idx === false) {
                throw new CsvError('UNKNOWN_COLUMN', "[UNKNOWN_COLUMN] unknown column: {$col}");
            }

            return (int) $idx;
        }
        if (is_float($col)) {
            if (floor($col) !== $col) {
                throw new CsvError('UNKNOWN_COLUMN', "[UNKNOWN_COLUMN] column index out of range: {$col}");
            }
            $col = (int) $col;
        }
        if ($col < 0 || $col >= $this->width()) {
            throw new CsvError('UNKNOWN_COLUMN', "[UNKNOWN_COLUMN] column index out of range: {$col}");
        }

        return $col;
    }

    private function name(int $idx): string
    {
        return $this->data['headers'][$idx] ?? "col_{$idx}";
    }

    /**
     * Runs the GROUP BY query. Result objects keep the key order mandated by
     * SPEC section 5.4 and the first-occurrence order of groups.
     *
     * @param array{groupBy: int|string, sum?: list<int|string>, avg?: list<int|string>, count?: bool} $options
     *
     * @return list<array<string, string|int|float|null>>
     */
    public function aggregate(array $options): array
    {
        $g = $this->resolve($options['groupBy']);
        $sums = [];
        foreach ($options['sum'] ?? [] as $c) {
            $sums[] = $this->resolve($c);
        }
        $avgs = [];
        foreach ($options['avg'] ?? [] as $c) {
            $avgs[] = $this->resolve($c);
        }
        $groupName = $this->name($g);

        /** @var array<string, array{key: string, count: int, sum: list<float>, avgSum: list<float>, avgN: list<int>}> $groups */
        $groups = [];

        foreach ($this->data['rows'] as $row) {
            $key = $row[$g] ?? '';
            if (!isset($groups[$key])) {
                $groups[$key] = [
                    'key' => $key,
                    'count' => 0,
                    'sum' => array_fill(0, count($sums), 0.0),
                    'avgSum' => array_fill(0, count($avgs), 0.0),
                    'avgN' => array_fill(0, count($avgs), 0),
                ];
            }
            $acc = $groups[$key];
            $acc['count']++;
            foreach ($sums as $k => $c) {
                $v = strip_cell($row[$c] ?? '');
                if (is_number($v)) {
                    $acc['sum'][$k] += (float) $v;
                }
            }
            foreach ($avgs as $k => $c) {
                $v = strip_cell($row[$c] ?? '');
                if (is_number($v)) {
                    $acc['avgSum'][$k] += (float) $v;
                    $acc['avgN'][$k]++;
                }
            }
            $groups[$key] = $acc;
        }

        $out = [];
        foreach ($groups as $acc) {
            $r = [$groupName => $acc['key']];
            foreach ($sums as $k => $c) {
                $r[$this->name($c) . '_sum'] = $acc['sum'][$k];
            }
            foreach ($avgs as $k => $c) {
                $r[$this->name($c) . '_avg'] = $acc['avgN'][$k] === 0 ? null : $acc['avgSum'][$k] / $acc['avgN'][$k];
            }
            if (isset($options['count']) && $options['count']) {
                $r['count'] = $acc['count'];
            }
            $out[] = $r;
        }

        return $out;
    }
}
