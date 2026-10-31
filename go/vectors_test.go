package lombokcsv_test

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	lombokcsv "github.com/codinglombok/lombokcsv/go"
)

// ---- ordered JSON decoding (SPEC section 0.5: key order is normative) ----

type jobj struct {
	keys []string
	vals map[string]any
}

func (o *jobj) keysEqual(other []string) bool {
	if len(o.keys) != len(other) {
		return false
	}
	for i, k := range o.keys {
		if k != other[i] {
			return false
		}
	}
	return true
}

func decodeOrdered(t *testing.T, path string) any {
	t.Helper()
	f, err := os.Open(path)
	if err != nil {
		t.Fatalf("open %s: %v", path, err)
	}
	defer f.Close()
	dec := json.NewDecoder(f)
	dec.UseNumber()
	v, err := decodeValue(dec)
	if err != nil {
		t.Fatalf("decode %s: %v", path, err)
	}
	return v
}

func decodeValue(dec *json.Decoder) (any, error) {
	tok, err := dec.Token()
	if err != nil {
		return nil, err
	}
	switch t := tok.(type) {
	case json.Delim:
		switch t {
		case '{':
			obj := &jobj{vals: map[string]any{}}
			for dec.More() {
				kt, err := dec.Token()
				if err != nil {
					return nil, err
				}
				key := kt.(string)
				v, err := decodeValue(dec)
				if err != nil {
					return nil, err
				}
				obj.keys = append(obj.keys, key)
				obj.vals[key] = v
			}
			_, err := dec.Token() // closing '}'
			return obj, err
		case '[':
			arr := []any{}
			for dec.More() {
				v, err := decodeValue(dec)
				if err != nil {
					return nil, err
				}
				arr = append(arr, v)
			}
			_, err := dec.Token() // closing ']'
			return arr, err
		}
		return nil, fmt.Errorf("unexpected delim %v", t)
	case json.Number:
		f, err := t.Float64()
		return f, err
	default:
		return tok, nil // string, bool, nil
	}
}

// assertEqual compares got and want with the SPEC section 0.5 semantics.
func assertEqual(t *testing.T, got, want any, path string) {
	t.Helper()
	switch w := want.(type) {
	case *jobj:
		g, ok := got.(*jobj)
		if !ok {
			t.Fatalf("%s: got %T, want object", path, got)
		}
		if !g.keysEqual(w.keys) {
			t.Fatalf("%s: key order %v != %v", path, g.keys, w.keys)
		}
		for _, k := range w.keys {
			assertEqual(t, g.vals[k], w.vals[k], path+"."+k)
		}
	case []any:
		g, ok := got.([]any)
		if !ok {
			t.Fatalf("%s: got %T, want array", path, got)
		}
		if len(g) != len(w) {
			t.Fatalf("%s: length %d != %d", path, len(g), len(w))
		}
		for i := range w {
			assertEqual(t, g[i], w[i], fmt.Sprintf("%s[%d]", path, i))
		}
	case float64:
		g, ok := got.(float64)
		if !ok || g != w {
			t.Fatalf("%s: got %#v, want %v", path, got, w)
		}
	case string:
		g, ok := got.(string)
		if !ok || g != w {
			t.Fatalf("%s: got %#v, want %#v", path, got, w)
		}
	case bool:
		g, ok := got.(bool)
		if !ok || g != w {
			t.Fatalf("%s: got %#v, want %v", path, got, w)
		}
	case nil:
		if got != nil {
			t.Fatalf("%s: got %#v, want null", path, got)
		}
	default:
		t.Fatalf("%s: unexpected want type %T", path, want)
	}
}

// ---- value conversion from the Go API to the comparison tree ----

func toTree(v any) any {
	switch x := v.(type) {
	case nil:
		return nil
	case *lombokcsv.Obj:
		o := &jobj{vals: map[string]any{}}
		for _, k := range x.Keys() {
			val, _ := x.Get(k)
			o.keys = append(o.keys, k)
			o.vals[k] = toTree(val)
		}
		return o
	case []string:
		if x == nil {
			return nil // absent headers are null; empty rows stay arrays
		}
		arr := make([]any, 0, len(x))
		for _, s := range x {
			arr = append(arr, s)
		}
		return arr
	case [][]string:
		arr := make([]any, 0, len(x))
		for _, row := range x {
			arr = append(arr, toTree(row))
		}
		return arr
	case []lombokcsv.DataType:
		arr := make([]any, 0, len(x))
		for _, s := range x {
			arr = append(arr, string(s))
		}
		return arr
	case []*lombokcsv.Obj:
		arr := make([]any, 0, len(x))
		for _, o := range x {
			arr = append(arr, toTree(o))
		}
		return arr
	case int:
		return float64(x)
	case float64:
		return x
	default:
		return v // string, bool pass through
	}
}

func strPtr(b bool) *bool { return &b }

func strPtrS(s string) *string { return &s }

func buildOptions(t *testing.T, raw any) *lombokcsv.CSVOptions {
	t.Helper()
	if raw == nil {
		return nil
	}
	o, ok := raw.(*jobj)
	if !ok {
		t.Fatalf("options: want object, got %T", raw)
	}
	opts := &lombokcsv.CSVOptions{}
	if v, ok := o.vals["delimiter"]; ok {
		opts.Delimiter = strPtrS(v.(string))
	}
	if v, ok := o.vals["quote"]; ok {
		opts.Quote = strPtrS(v.(string))
	}
	if v, ok := o.vals["hasHeader"]; ok {
		opts.HasHeader = strPtr(v.(bool))
	}
	if v, ok := o.vals["trim"]; ok {
		opts.Trim = strPtr(v.(bool))
	}
	return opts
}

func runCase(t *testing.T, c *jobj) any {
	t.Helper()
	fn, _ := c.vals["fn"].(string)
	input, _ := c.vals["input"].(string)
	opts := buildOptions(t, c.vals["options"])

	switch fn {
	case "parseRows":
		p, err := lombokcsv.NewCSVParser(input, opts)
		if err != nil {
			t.Fatalf("NewCSVParser: %v", err)
		}
		return toTree(p.ParseRows())
	case "parse":
		p, err := lombokcsv.NewCSVParser(input, opts)
		if err != nil {
			t.Fatalf("NewCSVParser: %v", err)
		}
		hasHeader := true
		if o, ok := c.vals["options"].(*jobj); ok {
			if v, ok := o.vals["hasHeader"]; ok {
				hasHeader = v.(bool)
			}
		}
		r := p.Parse(hasHeader)
		o := lombokcsv.NewObj()
		o.Set("headers", toTree(r.Headers))
		o.Set("rows", toTree(r.Rows))
		o.Set("types", toTree(r.Types))
		return toTree(o)
	case "toHTML":
		csv, err := lombokcsv.NewCSV(input, opts)
		if err != nil {
			t.Fatalf("NewCSV: %v", err)
		}
		var hopts *lombokcsv.HTMLOptions
		if h, ok := c.vals["html"].(*jobj); ok {
			hopts = &lombokcsv.HTMLOptions{}
			if v, ok := h.vals["className"]; ok {
				hopts.ClassName = v.(string)
			}
			if v, ok := h.vals["id"]; ok {
				hopts.ID = v.(string)
			}
		}
		return csv.ToHTML(hopts)
	case "toJSON":
		csv, err := lombokcsv.NewCSV(input, opts)
		if err != nil {
			t.Fatalf("NewCSV: %v", err)
		}
		return toTree(csv.ToJSON())
	case "aggregate":
		csv, err := lombokcsv.NewCSV(input, opts)
		if err != nil {
			t.Fatalf("NewCSV: %v", err)
		}
		raw, ok := c.vals["agg"].(*jobj)
		if !ok {
			t.Fatalf("aggregate: missing agg object")
		}
		agg := lombokcsv.AggregationOptions{}
		agg.GroupBy = numify(raw.vals["groupBy"])
		if v, ok := raw.vals["sum"]; ok {
			agg.Sum = toAnySlice(v)
		}
		if v, ok := raw.vals["avg"]; ok {
			agg.Avg = toAnySlice(v)
		}
		if v, ok := raw.vals["count"]; ok {
			agg.Count = v.(bool)
		}
		rows, err := csv.Aggregate(agg)
		if err != nil {
			t.Fatalf("Aggregate: %v", err)
		}
		return toTree(rows)
	default:
		t.Fatalf("unknown fn %s", fn)
		return nil
	}
}

func numify(v any) any {
	switch x := v.(type) {
	case json.Number:
		f, _ := x.Float64()
		return f
	default:
		return v
	}
}

func toAnySlice(v any) []any {
	arr, ok := v.([]any)
	if !ok {
		return []any{numify(v)}
	}
	out := make([]any, 0, len(arr))
	for _, item := range arr {
		out = append(out, numify(item))
	}
	return out
}

// TestVectors executes every case of the shared vector file (GP-11).
func TestVectors(t *testing.T) {
	path := filepath.Join("..", "vectors", "lombokcsv-vectors-v1.json")
	doc := decodeOrdered(t, path)
	root := doc.(*jobj)
	rawCases, ok := root.vals["cases"].([]any)
	if !ok {
		t.Fatalf("vectors file has no cases array")
	}
	if len(rawCases) < 100 {
		t.Fatalf("only %d cases (<100, GP-11)", len(rawCases))
	}
	for _, rc := range rawCases {
		c := rc.(*jobj)
		id, _ := c.vals["id"].(string)
		fn, _ := c.vals["fn"].(string)
		t.Run(id, func(t *testing.T) {
			if fn == "error" {
				runErrorCase(t, c)
				return
			}
			got := runCase(t, c)
			want := c.vals["expected"]
			assertEqual(t, got, want, "$")
		})
	}
}

func runErrorCase(t *testing.T, c *jobj) {
	t.Helper()
	input, _ := c.vals["input"].(string)
	opts := buildOptions(t, c.vals["options"])
	call, _ := c.vals["call"].(string)
	var err error
	switch call {
	case "parseRows":
		_, err = lombokcsv.NewCSVParser(input, opts)
	case "aggregate":
		var csv *lombokcsv.CSV
		csv, err = lombokcsv.NewCSV(input, opts)
		if err == nil {
			raw, ok := c.vals["agg"].(*jobj)
			if !ok {
				t.Fatalf("error case without agg object")
			}
			agg := lombokcsv.AggregationOptions{}
			agg.GroupBy = numify(raw.vals["groupBy"])
			if v, ok := raw.vals["sum"]; ok {
				agg.Sum = toAnySlice(v)
			}
			if v, ok := raw.vals["avg"]; ok {
				agg.Avg = toAnySlice(v)
			}
			if v, ok := raw.vals["count"]; ok {
				agg.Count = v.(bool)
			}
			_, err = csv.Aggregate(agg)
		}
	default:
		t.Fatalf("unknown error call %s", call)
	}
	if err == nil {
		t.Fatalf("expected an error, got none")
	}
	ce, ok := err.(*lombokcsv.CSVError)
	if !ok {
		t.Fatalf("expected *lombokcsv.CSVError, got %T", err)
	}
	expected := c.vals["expected"].(*jobj)
	code, _ := expected.vals["code"].(string)
	msg, _ := expected.vals["message"].(string)
	if string(ce.Code) != code {
		t.Fatalf("code %s != %s", ce.Code, code)
	}
	if ce.Msg != msg {
		t.Fatalf("message %#v != %#v", ce.Msg, msg)
	}
}
