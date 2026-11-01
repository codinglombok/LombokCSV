<?php

declare(strict_types=1);

namespace CodingLombok\LombokCSV;

/** Error with a stable, language-neutral code (SPEC section 7). */
final class CsvError extends \Exception
{
    /** The canonical error code: INVALID_OPTION or UNKNOWN_COLUMN. */
    public readonly string $errorCode;

    public function __construct(string $code, string $message)
    {
        parent::__construct($message);
        $this->errorCode = $code;
    }
}
