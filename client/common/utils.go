package common

import (
	"bytes"
	"encoding/binary"
)

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// Length to byte array
func lengthToBytes(l int) ([]byte, error) {
	var lenght int32 = int32(l)
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, lenght)
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

// Bytes to length
func bytesToLength(barray []byte) (int, error) {
	buf := bytes.NewBuffer(barray)
	var l int32
	err := binary.Read(buf, binary.BigEndian, &l)
	if err != nil {
		return 0, err
	}
	return int(l), nil
}
