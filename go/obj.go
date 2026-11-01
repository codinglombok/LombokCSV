package lombokcsv

import (
	"bytes"
	"encoding/json"
)

// Obj is an insertion-ordered string-keyed map used wherever the contract
// mandates a JSON object with a specific key order (SPEC sections 5.4 and 6).
// Setting an existing key overwrites the value but keeps the original position.
type Obj struct {
	keys []string
	vals map[string]any
}

// NewObj returns an empty ordered object.
func NewObj() *Obj { return &Obj{vals: map[string]any{}} }

// Set inserts or overwrites key. Overwriting keeps the original position.
func (o *Obj) Set(key string, value any) {
	if o.vals == nil {
		o.vals = map[string]any{}
	}
	if _, ok := o.vals[key]; !ok {
		o.keys = append(o.keys, key)
	}
	o.vals[key] = value
}

// Get returns the value stored under key.
func (o *Obj) Get(key string) (any, bool) {
	v, ok := o.vals[key]
	return v, ok
}

// Keys returns the keys in insertion order.
func (o *Obj) Keys() []string {
	return append([]string(nil), o.keys...)
}

// Len returns the number of keys.
func (o *Obj) Len() int { return len(o.keys) }

// MarshalJSON emits the object with its keys in insertion order.
func (o *Obj) MarshalJSON() ([]byte, error) {
	var b bytes.Buffer
	b.WriteByte('{')
	for i, k := range o.keys {
		if i > 0 {
			b.WriteByte(',')
		}
		kb, err := json.Marshal(k)
		if err != nil {
			return nil, err
		}
		b.Write(kb)
		b.WriteByte(':')
		vb, err := json.Marshal(o.vals[k])
		if err != nil {
			return nil, err
		}
		b.Write(vb)
	}
	b.WriteByte('}')
	return b.Bytes(), nil
}
