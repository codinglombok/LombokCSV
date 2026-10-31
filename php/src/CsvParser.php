<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

/** CSV parser - RFC 4180 records with configurable delimiter and quote (SPEC section 2). */
final class CsvParser
{
    private string $data;
    private string $delimiter;
    private string $quote;
    private bool $trim;

    /** @param array{delimiter?: string, quote?: string, hasHeader?: bool, trim?: bool, escape?: string} $options */
    public function __construct(string $data, array $options = [])
    {
        // SPEC section 2.1: a leading U+FEFF is removed; elsewhere it is data.
        $this->data = str_starts_with($data, "\xEF\xBB\xBF") ? substr($data, 3) : $data;
        $this->delimiter = self::singleUnit('delimiter', $options['delimiter'] ?? ',');
        $this->quote = self::singleUnit('quote', $options['quote'] ?? '"');
        if ($this->delimiter === $this->quote) {
            throw new CsvError('INVALID_OPTION', '[INVALID_OPTION] delimiter and quote must differ');
        }
        $this->trim = $options['trim'] ?? true;
    }

    private static function singleUnit(string $name, string $value): string
    {
        // SPEC section 0.4: exactly one UTF-16 code unit - a single code point
        // no greater than U+FFFF (1-3 UTF-8 bytes), and not CR/LF.
        if (preg_match('/^.$/u', $value) !== 1 || strlen($value) > 3 || $value === "\n" || $value === "\r") {
            throw new CsvError('INVALID_OPTION', "[INVALID_OPTION] {$name} must be a single character other than CR/LF");
        }

        return $value;
    }

    /** Splits the input into records (SPEC section 2). */
    public function parseRows(): array
    {
        $chars = split_chars($this->data);
        $delimiter = $this->delimiter;
        $quote = $this->quote;
        $trim = $this->trim;
        $rows = [];
        $row = [];
        $field = '';
        $quoted = false;
        $rowQuoted = false;
        // 0 = field start, 1 = unquoted, 2 = inside quotes, 3 = after closing quote
        $state = 0;

        $endField = function () use (&$rows, &$row, &$field, &$quoted, &$rowQuoted, &$state, $trim): void {
            if ($trim && !$quoted) {
                $field = rtrim($field, " \t");
            }
            $row[] = $field;
            $rowQuoted = $rowQuoted || $quoted;
            $field = '';
            $quoted = false;
            $state = 0;
        };
        $endRecord = function () use (&$rows, &$row, &$field, &$quoted, &$rowQuoted, &$state, $endField): void {
            $endField();
            // A line holding a single empty unquoted field is blank and skipped.
            if (count($row) > 1 || $row[0] !== '' || $rowQuoted) {
                $rows[] = $row;
            }
            $row = [];
            $rowQuoted = false;
        };

        $i = 0;
        $n = count($chars);
        while ($i < $n) {
            $c = $chars[$i];
            if ($state === 2) {
                if ($c === $quote) {
                    if ($i + 1 < $n && $chars[$i + 1] === $quote) {
                        $field .= $quote;
                        $i += 2;
                        continue;
                    }
                    $state = 3;
                } else {
                    $field .= $c;
                }
                $i++;
                continue;
            }
            if ($c === $delimiter) {
                $endField();
            } elseif ($c === "\n" || $c === "\r") {
                $endRecord();
                if ($c === "\r" && $i + 1 < $n && $chars[$i + 1] === "\n") {
                    $i++;
                }
            } elseif ($state === 0) {
                if ($c === $quote) {
                    $quoted = true;
                    $state = 2;
                } elseif (!($trim && ($c === ' ' || $c === "\t"))) {
                    $field .= $c;
                    $state = 1;
                }
            } elseif ($state === 3) {
                // Lenient: text after a closing quote is appended literally.
                if (!($trim && ($c === ' ' || $c === "\t"))) {
                    $field .= $c;
                }
            } else {
                $field .= $c;
            }
            $i++;
        }
        if ($state !== 0 || count($row) > 0) {
            $endRecord();
        }

        return $rows;
    }

    /**
     * Separates the header row (SPEC section 3).
     *
     * @return array{headers: string[]|null, rows: list<list<string>>, types: list<string>}
     */
    public function parse(bool $hasHeader = true): array
    {
        $rows = $this->parseRows();
        if ($rows === []) {
            return ['headers' => null, 'rows' => [], 'types' => []];
        }
        $headers = null;
        if ($hasHeader) {
            $headers = array_shift($rows);
        }

        return ['headers' => $headers, 'rows' => $rows, 'types' => detect_types($rows)];
    }
}
