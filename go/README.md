# LombokCSV — Go port

Go implementation of the [LombokCSV](../../README.md) contract: RFC 4180 CSV parsing, column type detection, safe HTML tables, JSON export and GROUP BY aggregation. Zero dependencies.

| Item | Value |
|---|---|
| Module | `github.com/codinglombok/lombokcsv/go` |
| Version | 1.1.0 (tag `go/v1.1.0`) |
| Contract | [SPEC](../../docs/SPEC_LombokCSV_v1.1.0.md) |
| Vectors | runs all 152 cases in [`vectors/lombokcsv-vectors-v1.json`](../../vectors/lombokcsv-vectors-v1.json) |
| Acceptance | every vector case passes with byte-identical results (GP-11) |
| Go | >= 1.22 |

## Installation

```bash
go get github.com/codinglombok/lombokcsv/go
```

The module is published through the Go module proxy when the `go/vX.Y.Z` tag is pushed; until then use a pseudo-version or `replace` the module with a local checkout.

## Quick start

```go
package main

import (
	"fmt"

	lombokcsv "github.com/codinglombok/lombokcsv/go"
)

func main() {
	csv, _ := lombokcsv.NewCSV("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95", nil)

	fmt.Println(csv.GetHeaders()) // [Region Product Qty]
	fmt.Println(csv.GetTypes())   // [string string number]
	fmt.Println(csv.ToJSON())     // ordered objects keyed by header
	fmt.Println(csv.ToHTML(nil))

	rows, _ := csv.Aggregate(lombokcsv.AggregationOptions{
		GroupBy: "Region",
		Sum:     []any{"Qty"},
		Avg:     []any{"Qty"},
		Count:   true,
	})
	for _, row := range rows {
		fmt.Println(row) // key order preserved: Region, Qty_sum, Qty_avg, count
	}
}
```

Notes on the Go API:

- `Delimiter` / `Quote` / `HasHeader` / `Trim` are pointer fields; `nil` means "use the default". An explicit empty string for `Delimiter` or `Quote` is invalid and yields `INVALID_OPTION` (SPEC section 1).
- `Obj` is an insertion-ordered JSON object; the contract mandates specific key order for aggregate results and JSON export, so Go cannot use plain maps there (SPEC sections 5.4 and 6).
- Errors are `*lombokcsv.CSVError` with a stable `Code` (`INVALID_OPTION`, `UNKNOWN_COLUMN`) and the canonical `[CODE] message` text; match on `Code`, not on the message.

## Development

```bash
gofmt -l .      # must print nothing
go vet ./...
go test -coverprofile=cover.out ./...
go tool cover -func=cover.out   # total must be >= 90%
```

Contributions are welcome; see [CONTRIBUTING.md](../../CONTRIBUTING.md).
