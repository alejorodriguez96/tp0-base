package common

import (
	"net"
)

// BaseStream interface that defines the methods that a stream should implement
type BaseStream interface {
	// Write Writes a byte array to the stream. Returns an error if could not write
	// full message. This does not perform short writes
	Write([]byte) error
	// Read Reads a byte array from the stream. Returns an error if could not read
	// full message. This does not perform short reads
	Read(int) ([]byte, error)
}

// SocketStream implementation of the BaseStream interface that uses a socket
type SocketStream struct {
	conn net.Conn
}

// NewSocketStream Initializes a new socket stream
func NewSocketStream(conn net.Conn) *SocketStream {
	return &SocketStream{conn: conn}
}

// Write Writes a byte array to the stream. Returns an error if could not write
// full message. This does not perform short writes
func (s *SocketStream) Write(msg []byte) error {
	remainingBytes := len(msg)
	for remainingBytes > 0 {
		n, err := s.conn.Write(msg)
		if err != nil {
			return err
		}
		remainingBytes -= n
	}
	return nil
}

// Read Reads a byte array from the stream. Returns an error if could not read
// full message. This does not perform short reads
func (s *SocketStream) Read(length int) ([]byte, error) {
	var buffer []byte
	remainingBytes := length
	for remainingBytes > 0 {
		tmp := make([]byte, min(1024, remainingBytes))
		n, err := s.conn.Read(tmp)
		if err != nil {
			return nil, err
		}
		buffer = append(buffer, tmp...)
		remainingBytes -= n
	}
	return buffer, nil
}
