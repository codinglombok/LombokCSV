package lombokcsv_test

import (
	"errors"
	"strings"
	"testing"

	lombokcsv "github.com/codinglombok/lombokcsv/go"
)

func TestParsesSimpleCSV(t *testing.T) {
	csv, err := lombokcsv.NewCSV("a,b,c\n1,2,3", nil)
	if err != nil {
		t.Fatal(err)
	}
	rows := csv.GetRows()
	if len(rows) != 1 || rows[0][0] != "1" || rows[0][1] != "2" || rows[0][2] != "3" {
		t.Fatalf("got %v", rows)
	}
}

func TestParsesWithHeaders(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("Name,Age,City\nJohn,30,NYC", nil)
	headers := csv.GetHeaders()
	if len(headers) != 3 || headers[0] != "Name" {
		t.Fatalf("got %v", headers)
	}
}

func TestQuotedFields(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("\"Name\",\"Age\"\n\"John Smith\",30", nil)
	if csv.GetRows()[0][0] != "John Smith" {
		t.Fatalf("got %v", csv.GetRows())
	}
}

func TestCommasInsideQuotes(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("Name,Address\n\"Smith, John\",\"123 Main, Apt 4\"", nil)
	row := csv.GetRows()[0]
	if row[0] != "Smith, John" || row[1] != "123 Main, Apt 4" {
		t.Fatalf("got %v", row)
	}
}

func TestNewlinesInsideQuotes(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("Name,Description\n\"John\",\"Line 1\nLine 2\"", nil)
	if len(csv.GetRows()) != 1 {
		t.Fatalf("got %d rows", len(csv.GetRows()))
	}
}

func TestTypeDetection(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("Name,Value,Date,Active\nTest,123,2026-01-01,true", nil)
	types := csv.GetTypes()
	want := []lombokcsv.DataType{lombokcsv.TypeString, lombokcsv.TypeNumber, lombokcsv.TypeDate, lombokcsv.TypeBoolean}
	if len(types) != len(want) {
		t.Fatalf("got %v", types)
	}
	for i := range want {
		if types[i] != want[i] {
			t.Fatalf("got %v, want %v", types, want)
		}
	}
}

func TestHTMLGeneration(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("Name,Age\nJohn,30", nil)
	html := csv.ToHTML(nil)
	want := "<table>\n<thead>\n<tr>\n<th>Name</th>\n<th>Age</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>John</td>\n<td style=\"text-align: right\">30</td>\n</tr>\n</tbody>\n</table>"
	if html != want {
		t.Fatalf("got:\n%s", html)
	}
}

func TestHTMLEscaping(t *testing.T) {
	csv, _ := lombokcsv.NewCSV("A\n<script>alert(\"x\")</script>", nil)
	html := csv.ToHTML(nil)
	if strings.Contains(html, "<script>") || !strings.Contains(html, "&lt;script&gt;") {
		t.Fatalf("not escaped: %s", html)
	}
	evil := mustCSV(t, "A\nx").ToHTML(&lombokcsv.HTMLOptions{ClassName: "\" onclick=\"alert(1)"})
	if strings.Contains(evil, "onclick=\"alert(1)\"") {
		t.Fatalf("attribute injection: %s", evil)
	}
}

func TestAggregation(t *testing.T) {
	csv := mustCSV(t, "Department,Salary\nIT,50000\nIT,55000\nSales,40000")
	rows, err := csv.Aggregate(lombokcsv.AggregationOptions{GroupBy: "Department", Sum: []any{"Salary"}, Count: true})
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 2 {
		t.Fatalf("got %d groups", len(rows))
	}
	it, _ := rows[0].Get("Salary_sum")
	if it.(float64) != 105000 {
		t.Fatalf("IT sum %v", it)
	}
	if k := rows[0].Keys(); k[0] != "Department" || k[1] != "Salary_sum" || k[2] != "count" {
		t.Fatalf("key order %v", k)
	}
}

func TestAggregationInsertionOrder(t *testing.T) {
	csv := mustCSV(t, "g,v\nb,1\na,2\nb,3")
	rows, _ := csv.Aggregate(lombokcsv.AggregationOptions{GroupBy: "g", Sum: []any{"v"}})
	if rows[0].Keys()[0] != "g" || rows[0].Keys()[1] != "v_sum" {
		t.Fatalf("keys %v", rows[0].Keys())
	}
	v, _ := rows[0].Get("g")
	if v.(string) != "b" {
		t.Fatalf("first group %v (want insertion order b)", v)
	}
}

func TestUnknownColumnError(t *testing.T) {
	csv := mustCSV(t, "a,b\n1,2")
	_, err := csv.Aggregate(lombokcsv.AggregationOptions{GroupBy: "Missing", Count: true})
	var ce *lombokcsv.CSVError
	if !errors.As(err, &ce) || ce.Code != lombokcsv.CodeUnknownColumn {
		t.Fatalf("got %v", err)
	}
	if ce.Error() != "[UNKNOWN_COLUMN] unknown column: Missing" {
		t.Fatalf("message %q", ce.Error())
	}
}

func TestIndexOutOfRangeError(t *testing.T) {
	csv := mustCSV(t, "a,b\n1,2")
	_, err := csv.Aggregate(lombokcsv.AggregationOptions{GroupBy: 3})
	var ce *lombokcsv.CSVError
	if !errors.As(err, &ce) || ce.Msg != "[UNKNOWN_COLUMN] column index out of range: 3" {
		t.Fatalf("got %v", err)
	}
	if _, err := csv.Aggregate(lombokcsv.AggregationOptions{GroupBy: 1.5}); err == nil {
		t.Fatal("expected error for 1.5")
	} else if ce := err.(*lombokcsv.CSVError); ce.Msg != "[UNKNOWN_COLUMN] column index out of range: 1.5" {
		t.Fatalf("message %q", ce.Msg)
	}
}

func TestInvalidOptionErrors(t *testing.T) {
	if _, err := lombokcsv.NewCSV("a,b", &lombokcsv.CSVOptions{Delimiter: strPtrS("")}); err == nil {
		t.Fatal("expected error for empty delimiter")
	} else if ce := err.(*lombokcsv.CSVError); ce.Msg != "[INVALID_OPTION] delimiter must be a single character other than CR/LF" {
		t.Fatalf("message %q", ce.Msg)
	}
	if _, err := lombokcsv.NewCSV("a,b", &lombokcsv.CSVOptions{Delimiter: strPtrS("\"")}); err == nil {
		t.Fatal("expected error for equal delimiter/quote")
	} else if ce := err.(*lombokcsv.CSVError); ce.Msg != "[INVALID_OPTION] delimiter and quote must differ" {
		t.Fatalf("message %q", ce.Msg)
	}
}

func TestToJSON(t *testing.T) {
	csv := mustCSV(t, "Name,Age\nJohn,30\nJane,25")
	rows := csv.ToJSON().([]*lombokcsv.Obj)
	first, _ := rows[0].Get("Name")
	if first.(string) != "John" {
		t.Fatalf("got %v", first)
	}
	if k := rows[0].Keys(); k[0] != "Name" || k[1] != "Age" {
		t.Fatalf("key order %v", k)
	}
}

func TestToJSONWithoutHeader(t *testing.T) {
	noHeader := false
	csv, err := lombokcsv.NewCSV("1,2\n3,4", &lombokcsv.CSVOptions{HasHeader: &noHeader})
	if err != nil {
		t.Fatal(err)
	}
	rows, ok := csv.ToJSON().([][]string)
	if !ok || len(rows) != 2 || rows[0][0] != "1" {
		t.Fatalf("got %#v", csv.ToJSON())
	}
}

func TestEmptyCSV(t *testing.T) {
	csv := mustCSV(t, "")
	if len(csv.GetRows()) != 0 || csv.GetHeaders() != nil {
		t.Fatalf("got %v %v", csv.GetRows(), csv.GetHeaders())
	}
}

func TestCRLFAndBOM(t *testing.T) {
	csv := mustCSV(t, "\uFEFFA,B\r\n1,2\r\n")
	if csv.GetHeaders()[0] != "A" || len(csv.GetRows()) != 1 {
		t.Fatalf("got %v %v", csv.GetHeaders(), csv.GetRows())
	}
}

func TestObjOrderedSet(t *testing.T) {
	o := lombokcsv.NewObj()
	o.Set("b", 1)
	o.Set("a", 2)
	o.Set("b", 3) // overwrite keeps position
	if k := o.Keys(); k[0] != "b" || k[1] != "a" {
		t.Fatalf("keys %v", k)
	}
	v, _ := o.Get("b")
	if v.(int) != 3 {
		t.Fatalf("value %v", v)
	}
}

func mustCSV(t *testing.T, data string) *lombokcsv.CSV {
	t.Helper()
	csv, err := lombokcsv.NewCSV(data, nil)
	if err != nil {
		t.Fatal(err)
	}
	return csv
}
