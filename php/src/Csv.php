<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

/** Main API combining parser, generator and aggregator. */
final class Csv
{
    /** @var array{headers: string[]|null, rows: list<list<string>>, types: list<string>} */
    private array $data;

    /** @param array{delimiter?: string, quote?: string, hasHeader?: bool, trim?: bool, escape?: string} $options */
    public function __construct(string $data, array $options = [])
    {
        $parser = new CsvParser($data, $options);
        $this->data = $parser->parse($options['hasHeader'] ?? true);
    }

    /** @return string[]|null */
    public function getHeaders(): ?array
    {
        return $this->data['headers'];
    }

    /** @return list<list<string>> */
    public function getRows(): array
    {
        return $this->data['rows'];
    }

    /** @return list<string> */
    public function getTypes(): array
    {
        return $this->data['types'];
    }

    /** @param array{className?: string, id?: string} $options */
    public function toHTML(array $options = []): string
    {
        return (new HtmlGenerator($this->data))->generate($options);
    }

    /** @return list<list<string>>|list<array<string, string>> */
    public function toJSON(): array
    {
        $headers = $this->data['headers'];
        if ($headers === null) {
            return $this->data['rows'];
        }
        $out = [];
        foreach ($this->data['rows'] as $row) {
            $obj = [];
            foreach ($headers as $i => $header) {
                $obj[$header] = $row[$i] ?? '';
            }
            $out[] = $obj;
        }

        return $out;
    }

    /**
     * @param array{groupBy: int|string, sum?: list<int|string>, avg?: list<int|string>, count?: bool} $options
     *
     * @return list<array<string, string|int|float|null>>
     */
    public function aggregate(array $options): array
    {
        return (new CsvAggregator($this->data))->aggregate($options);
    }
}
