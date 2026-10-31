// Package lombokcsv implements the LombokCSV contract: RFC 4180 CSV parsing,
// column type detection, safe HTML table generation, JSON export and GROUP BY
// aggregation. Zero dependencies. Normative behaviour:
// docs/SPEC_LombokCSV_v<version>.md.
//
// The Go port consumes the same shared vector file as every other port
// (vectors/lombokcsv-vectors-v1.json) and must produce byte-identical results.
package lombokcsv

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

// TypeSampleRows is the number of leading rows inspected by type detection (SPEC section 3).
const TypeSampleRows = 10

// DataType is one column type as defined by SPEC section 3.
type DataType string

// Column types.
const (
	TypeString  DataType = "string"
	TypeNumber  DataType = "number"
	TypeDate    DataType = "date"
	TypeBoolean DataType = "boolean"
)

// CSVErrorCode is a stable, language-neutral error code (SPEC section 7).
type CSVErrorCode string

// Error codes.
const (
	CodeInvalidOption CSVErrorCode = "INVALID_OPTION"
	CodeUnknownColumn CSVErrorCode = "UNKNOWN_COLUMN"
)

// CSVError is the error type of this package. The message always starts with
// the canonical "[CODE] " prefix and is byte-identical across ports.
type CSVError struct {
	Code CSVErrorCode
	Msg  string
}

// Error implements the error interface.
func (e *CSVError) Error() string { return e.Msg }

func newCSVError(code CSVErrorCode, msg string) *CSVError {
	return &CSVError{Code: code, Msg: msg}
}

var (
	numberRe = regexp.MustCompile(`^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$`)
	dateRes  = []*regexp.Regexp{
		regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`),
		regexp.MustCompile(`^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$`),
		regexp.MustCompile(`^\d{1,2}/\d{1,2}/\d{4}$`),
		regexp.MustCompile(`^\d{1,2}-\d{1,2}-\d{4}$`),
	}
	booleanRe   = regexp.MustCompile(`(?i)^(true|false|yes|no|1|0)$`)
	trailingBla = regexp.MustCompile(`[ \t]+$`)
)

// IsNumber reports whether v matches the SPEC number pattern (section 3.1).
func IsNumber(v string) bool { return numberRe.MatchString(v) }

// IsDate reports whether v matches one of the SPEC date patterns (section 3.1).
func IsDate(v string) bool {
	for _, re := range dateRes {
		if re.MatchString(v) {
			return true
		}
	}
	return false
}

// IsBoolean reports whether v matches the SPEC boolean pattern (section 3.1).
func IsBoolean(v string) bool { return booleanRe.MatchString(v) }

// strip removes SPACE, TAB, CR and LF from both ends (SPEC section 0.3).
func strip(v string) string {
	return strings.Trim(v, " \t\r\n")
}

// formatIndexNumber renders a binary64 value the way ECMAScript does for the
// values that can reach an error message (shortest round-trip decimal).
func formatIndexNumber(f float64) string {
	if f == float64(int64(f)) && f >= -9.007199254740992e15 && f <= 9.007199254740992e15 {
		return strconv.FormatInt(int64(f), 10)
	}
	return strconv.FormatFloat(f, 'g', -1, 64)
}

// errInvalidOption builds the canonical INVALID_OPTION error for delimiter/quote.
func errInvalidOption(name string) *CSVError {
	return newCSVError(CodeInvalidOption, "[INVALID_OPTION] "+name+" must be a single character other than CR/LF")
}

// singleUnit validates that value is exactly one UTF-16 code unit: a single
// rune no greater than U+FFFF and not CR/LF (SPEC section 0.4).
func singleUnit(value string) (rune, bool) {
	r := []rune(value)
	if len(r) != 1 || r[0] > 0xFFFF || r[0] == '\n' || r[0] == '\r' {
		return 0, false
	}
	return r[0], true
}

// CSVOptions holds the parser options (SPEC section 1). A nil *CSVOptions or a
// nil pointer field means "use the default". An explicit empty string for
// Delimiter or Quote is invalid (SPEC section 1) and yields INVALID_OPTION.
type CSVOptions struct {
	Delimiter *string // default ","
	Quote     *string // default "\""
	HasHeader *bool   // default true
	Trim      *bool   // default true
	Escape    string  // deprecated, ignored
}

func (o *CSVOptions) hasHeader() bool {
	return o == nil || o.HasHeader == nil || *o.HasHeader
}

func (o *CSVOptions) trim() bool {
	return o == nil || o.Trim == nil || *o.Trim
}

// CSVData is the parsed document: optional headers, rows and per-column types.
type CSVData struct {
	Headers []string   // nil when absent
	Rows    [][]string // never includes the header row
	Types   []DataType
}

// CSVParser splits RFC 4180 records and detects header/type information.
type CSVParser struct {
	data      string
	delimiter string
	quote     string
	trim      bool
}

// NewCSVParser validates the options (SPEC section 1) and returns a parser.
// It returns a *CSVError with code INVALID_OPTION for invalid options.
func NewCSVParser(data string, options *CSVOptions) (*CSVParser, error) {
	delim := ","
	if options != nil && options.Delimiter != nil {
		delim = *options.Delimiter
	}
	quot := "\""
	if options != nil && options.Quote != nil {
		quot = *options.Quote
	}
	if _, ok := singleUnit(delim); !ok {
		return nil, errInvalidOption("delimiter")
	}
	if _, ok := singleUnit(quot); !ok {
		return nil, errInvalidOption("quote")
	}
	if delim == quot {
		return nil, newCSVError(CodeInvalidOption, "[INVALID_OPTION] delimiter and quote must differ")
	}
	// SPEC section 2.1: a leading U+FEFF is removed; elsewhere it is data.
	data = strings.TrimPrefix(data, "\uFEFF")
	trim := options == nil || options.trim()
	return &CSVParser{data: data, delimiter: delim, quote: quot, trim: trim}, nil
}

// Parse splits the header row (when hasHeader is true) and detects the column
// types of the remaining rows (SPEC section 3).
func (p *CSVParser) Parse(hasHeader bool) CSVData {
	rows := p.ParseRows()
	if len(rows) == 0 {
		return CSVData{}
	}
	var headers []string
	if hasHeader {
		headers = rows[0]
		rows = rows[1:]
	}
	return CSVData{Headers: headers, Rows: rows, Types: DetectTypes(rows)}
}

// ParseRows splits the input into records (SPEC section 2).
func (p *CSVParser) ParseRows() [][]string {
	data, delimiter, quote, trim := p.data, p.delimiter, p.quote, p.trim
	delimRune, _ := singleUnit(delimiter)
	quoteRune, _ := singleUnit(quote)
	rows := [][]string{}
	row := []string{}
	var field strings.Builder
	quoted := false
	rowQuoted := false
	// 0 = field start, 1 = unquoted, 2 = inside quotes, 3 = after closing quote
	state := 0

	endField := func() {
		f := field.String()
		if trim && !quoted {
			f = trailingBla.ReplaceAllString(f, "")
		}
		row = append(row, f)
		rowQuoted = rowQuoted || quoted
		field.Reset()
		quoted = false
		state = 0
	}
	endRecord := func() {
		endField()
		// A line holding a single empty unquoted field is blank and skipped.
		if len(row) > 1 || row[0] != "" || rowQuoted {
			rows = append(rows, row)
		}
		row = []string{}
		rowQuoted = false
	}

	runes := []rune(data)
	i := 0
	n := len(runes)
	for i < n {
		c := runes[i]
		if state == 2 {
			if c == quoteRune {
				if i+1 < n && runes[i+1] == quoteRune {
					field.WriteRune(quoteRune)
					i += 2
					continue
				}
				state = 3
			} else {
				field.WriteRune(c)
			}
			i++
			continue
		}
		switch {
		case c == delimRune:
			endField()
		case c == '\n' || c == '\r':
			endRecord()
			if c == '\r' && i+1 < n && runes[i+1] == '\n' {
				i++
			}
		case state == 0:
			if c == quoteRune {
				quoted = true
				state = 2
			} else if !(trim && (c == ' ' || c == '\t')) {
				field.WriteRune(c)
				state = 1
			}
		case state == 3:
			// Lenient: text after a closing quote is appended literally.
			if !(trim && (c == ' ' || c == '\t')) {
				field.WriteRune(c)
			}
		default:
			field.WriteRune(c)
		}
		i++
	}
	if state != 0 || len(row) > 0 {
		endRecord()
	}
	return rows
}

// DetectTypes assigns one type per column from the first TypeSampleRows rows (SPEC section 3).
func DetectTypes(rows [][]string) []DataType {
	numCols := 0
	for _, r := range rows {
		if len(r) > numCols {
			numCols = len(r)
		}
	}
	types := make([]DataType, 0, numCols)
	sample := rows
	if len(sample) > TypeSampleRows {
		sample = sample[:TypeSampleRows]
	}
	for col := 0; col < numCols; col++ {
		anyValue := false
		num, date, boolean := true, true, true
		for _, row := range sample {
			var v string
			if col < len(row) {
				v = row[col]
			}
			v = strip(v)
			if v == "" {
				continue
			}
			anyValue = true
			if num && !IsNumber(v) {
				num = false
			}
			if date && !IsDate(v) {
				date = false
			}
			if boolean && !IsBoolean(v) {
				boolean = false
			}
		}
		switch {
		case !anyValue:
			types = append(types, TypeString)
		case num:
			types = append(types, TypeNumber)
		case date:
			types = append(types, TypeDate)
		case boolean:
			types = append(types, TypeBoolean)
		default:
			types = append(types, TypeString)
		}
	}
	return types
}

// EscapeHTML escapes text for HTML element content and double-quoted attribute
// values (SPEC section 4).
func EscapeHTML(text string) string {
	return strings.NewReplacer(
		"&", "&amp;",
		"<", "&lt;",
		">", "&gt;",
		"\"", "&quot;",
		"'", "&#39;",
	).Replace(text)
}

// HTMLOptions customises the generated <table> element.
type HTMLOptions struct {
	ClassName string
	ID        string
}

// HTMLGenerator renders a CSVData as a semantic HTML table (SPEC section 4).
type HTMLGenerator struct {
	data CSVData
}

// NewHTMLGenerator returns a generator for data.
func NewHTMLGenerator(data CSVData) *HTMLGenerator { return &HTMLGenerator{data: data} }

// Generate renders the table.
func (g *HTMLGenerator) Generate(options *HTMLOptions) string {
	var b strings.Builder
	b.WriteString("<table")
	if options != nil && options.ClassName != "" {
		b.WriteString(` class="` + EscapeHTML(options.ClassName) + `"`)
	}
	if options != nil && options.ID != "" {
		b.WriteString(` id="` + EscapeHTML(options.ID) + `"`)
	}
	b.WriteString(">\n")
	if len(g.data.Headers) > 0 {
		b.WriteString("<thead>\n<tr>\n")
		for _, header := range g.data.Headers {
			b.WriteString("<th>" + EscapeHTML(header) + "</th>\n")
		}
		b.WriteString("</tr>\n</thead>\n")
	}
	b.WriteString("<tbody>\n")
	for _, row := range g.data.Rows {
		b.WriteString("<tr>\n")
		for i, cell := range row {
			align := ""
			if i < len(g.data.Types) && g.data.Types[i] == TypeNumber {
				align = ` style="text-align: right"`
			}
			b.WriteString("<td" + align + ">" + EscapeHTML(cell) + "</td>\n")
		}
		b.WriteString("</tr>\n")
	}
	b.WriteString("</tbody>\n</table>")
	return b.String()
}

// AggregationOptions describes a GROUP BY query (SPEC section 5). GroupBy and
// the Sum/Avg entries are either a string (header name) or an integer-valued
// number (column index).
type AggregationOptions struct {
	GroupBy any
	Sum     []any
	Avg     []any
	Count   bool
}

// CSVAggregator computes GROUP BY aggregations over a CSVData (SPEC section 5).
type CSVAggregator struct {
	data CSVData
}

// NewCSVAggregator returns an aggregator for data.
func NewCSVAggregator(data CSVData) *CSVAggregator { return &CSVAggregator{data: data} }

func (a *CSVAggregator) width() int {
	w := len(a.data.Headers)
	for _, r := range a.data.Rows {
		if len(r) > w {
			w = len(r)
		}
	}
	return w
}

func (a *CSVAggregator) resolve(col any) (int, error) {
	switch c := col.(type) {
	case string:
		idx := -1
		for i, h := range a.data.Headers {
			if h == c {
				idx = i
				break
			}
		}
		if idx < 0 {
			return 0, newCSVError(CodeUnknownColumn, fmt.Sprintf("[UNKNOWN_COLUMN] unknown column: %s", c))
		}
		return idx, nil
	case int:
		return a.resolveIndex(float64(c))
	case int64:
		return a.resolveIndex(float64(c))
	case float64:
		return a.resolveIndex(c)
	default:
		return 0, newCSVError(CodeUnknownColumn, fmt.Sprintf("[UNKNOWN_COLUMN] column index out of range: %v", col))
	}
}

func (a *CSVAggregator) resolveIndex(f float64) (int, error) {
	if f != float64(int64(f)) || f < 0 || f >= float64(a.width()) {
		return 0, newCSVError(CodeUnknownColumn, fmt.Sprintf("[UNKNOWN_COLUMN] column index out of range: %s", formatIndexNumber(f)))
	}
	return int(f), nil
}

func (a *CSVAggregator) name(idx int) string {
	if idx < len(a.data.Headers) {
		return a.data.Headers[idx]
	}
	return fmt.Sprintf("col_%d", idx)
}

// Aggregate runs the GROUP BY query. The result objects preserve the key order
// mandated by SPEC section 5.4 and the first-occurrence order of groups.
func (a *CSVAggregator) Aggregate(options AggregationOptions) ([]*Obj, error) {
	g, err := a.resolve(options.GroupBy)
	if err != nil {
		return nil, err
	}
	sums := make([]int, 0, len(options.Sum))
	for _, c := range options.Sum {
		idx, err := a.resolve(c)
		if err != nil {
			return nil, err
		}
		sums = append(sums, idx)
	}
	avgs := make([]int, 0, len(options.Avg))
	for _, c := range options.Avg {
		idx, err := a.resolve(c)
		if err != nil {
			return nil, err
		}
		avgs = append(avgs, idx)
	}
	groupName := a.name(g)

	type acc struct {
		key    string
		count  int
		sum    []float64
		avgSum []float64
		avgN   []int
	}
	groups := map[string]*acc{}
	var order []string // first-occurrence order of group keys

	for _, row := range a.data.Rows {
		key := ""
		if g < len(row) {
			key = row[g]
		}
		cur, ok := groups[key]
		if !ok {
			cur = &acc{
				key:    key,
				sum:    make([]float64, len(sums)),
				avgSum: make([]float64, len(avgs)),
				avgN:   make([]int, len(avgs)),
			}
			groups[key] = cur
			order = append(order, key)
		}
		cur.count++
		for k, c := range sums {
			var v string
			if c < len(row) {
				v = row[c]
			}
			v = strip(v)
			if IsNumber(v) {
				f, _ := strconv.ParseFloat(v, 64)
				cur.sum[k] += f
			}
		}
		for k, c := range avgs {
			var v string
			if c < len(row) {
				v = row[c]
			}
			v = strip(v)
			if IsNumber(v) {
				f, _ := strconv.ParseFloat(v, 64)
				cur.avgSum[k] += f
				cur.avgN[k]++
			}
		}
	}

	out := make([]*Obj, 0, len(order))
	for _, key := range order {
		cur := groups[key]
		r := NewObj()
		r.Set(groupName, cur.key)
		for k, c := range sums {
			r.Set(a.name(c)+"_sum", cur.sum[k])
		}
		for k, c := range avgs {
			if cur.avgN[k] == 0 {
				r.Set(a.name(c)+"_avg", nil)
			} else {
				r.Set(a.name(c)+"_avg", cur.avgSum[k]/float64(cur.avgN[k]))
			}
		}
		if options.Count {
			r.Set("count", cur.count)
		}
		out = append(out, r)
	}
	return out, nil
}

// CSV is the main API combining parser, generator and aggregator.
type CSV struct {
	data CSVData
}

// NewCSV parses data once with the given options (nil means defaults).
// It returns a *CSVError with code INVALID_OPTION for invalid options.
func NewCSV(data string, options *CSVOptions) (*CSV, error) {
	p, err := NewCSVParser(data, options)
	if err != nil {
		return nil, err
	}
	return &CSV{data: p.Parse(options.hasHeader())}, nil
}

// GetHeaders returns the header row, or nil when there is none.
func (c *CSV) GetHeaders() []string { return c.data.Headers }

// GetRows returns the data rows (without the header row).
func (c *CSV) GetRows() [][]string { return c.data.Rows }

// GetTypes returns the detected type of every column.
func (c *CSV) GetTypes() []DataType { return c.data.Types }

// ToHTML renders the parsed document as an HTML table.
func (c *CSV) ToHTML(options *HTMLOptions) string {
	return NewHTMLGenerator(c.data).Generate(options)
}

// Aggregate runs a GROUP BY query (SPEC section 5).
func (c *CSV) Aggregate(options AggregationOptions) ([]*Obj, error) {
	return NewCSVAggregator(c.data).Aggregate(options)
}

// ToJSON returns rows as objects keyed by header (SPEC section 6). Missing
// cells become "", extra cells are dropped, and for duplicate header names the
// last column wins. Without a header row the raw rows are returned.
func (c *CSV) ToJSON() any {
	if c.data.Headers == nil {
		return c.data.Rows
	}
	out := make([]*Obj, 0, len(c.data.Rows))
	for _, row := range c.data.Rows {
		o := NewObj()
		for i, h := range c.data.Headers {
			var v string
			if i < len(row) {
				v = row[i]
			}
			o.Set(h, v)
		}
		out = append(out, o)
	}
	return out
}
