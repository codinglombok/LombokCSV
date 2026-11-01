<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

/** HTML generator - semantic table markup (SPEC section 4). */
final class HtmlGenerator
{
    /** @param array{headers: string[]|null, rows: list<list<string>>, types: list<string>} $data */
    public function __construct(private readonly array $data)
    {
    }

    /** @param array{className?: string, id?: string} $options */
    public function generate(array $options = []): string
    {
        $classAttr = !empty($options['className']) ? ' class="' . escape_html($options['className']) . '"' : '';
        $idAttr = !empty($options['id']) ? ' id="' . escape_html($options['id']) . '"' : '';

        $html = "<table{$classAttr}{$idAttr}>\n";
        $headers = $this->data['headers'];
        if ($headers !== null && $headers !== []) {
            $html .= "<thead>\n<tr>\n";
            foreach ($headers as $header) {
                $html .= '<th>' . escape_html($header) . "</th>\n";
            }
            $html .= "</tr>\n</thead>\n";
        }
        $html .= "<tbody>\n";
        foreach ($this->data['rows'] as $row) {
            $html .= "<tr>\n";
            foreach ($row as $i => $cell) {
                $align = ($this->data['types'][$i] ?? '') === 'number' ? ' style="text-align: right"' : '';
                $html .= '<td' . $align . '>' . escape_html($cell) . "</td>\n";
            }
            $html .= "</tr>\n";
        }
        $html .= "</tbody>\n</table>";

        return $html;
    }
}
