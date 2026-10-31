<?php

declare(strict_types=1);

// PSR-4 autoloader for src/ so the tests run without Composer.

spl_autoload_register(static function (string $class): void {
    if (str_starts_with($class, 'CodingLombok\\LombokCSV\\')) {
        $file = __DIR__ . '/../src/' . str_replace('\\', '/', substr($class, strlen('CodingLombok\\LombokCSV\\'))) . '.php';
        if (is_file($file)) {
            require $file;
        }
    }
});

require __DIR__ . '/../src/functions.php';

$GLOBALS['lombok_failures'] = [];
$GLOBALS['lombok_checks'] = 0;

function check(bool $ok, string $what): void
{
    $GLOBALS['lombok_checks']++;
    if (!$ok) {
        $GLOBALS['lombok_failures'][] = $what;
    }
}

/** @param callable(): void $fn */
function throwsCode(callable $fn, string $code, string $message, string $what): void
{
    try {
        $fn();
        check(false, "$what: no exception");
    } catch (\CodingLombok\LombokCSV\CsvError $e) {
        check($e->errorCode === $code, "$what: got {$e->errorCode}, want $code");
        check($e->getMessage() === $message, "$what: message '{$e->getMessage()}' != '$message'");
    }
}

function finish(string $name): void
{
    $f = $GLOBALS['lombok_failures'];
    if ($f !== []) {
        fwrite(STDERR, count($f) . " failures in $name:\n" . implode("\n", $f) . "\n");
        exit(1);
    }
    echo "$name: {$GLOBALS['lombok_checks']} checks passed\n";
}
