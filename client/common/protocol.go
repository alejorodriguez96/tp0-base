package common

import (
	"io"
	"net"
)

// Message types
const (
	SingleBet     = byte(0x01)
	MultipleBet   = byte(0x02)
	Error         = byte(0x03)
	BetACK        = byte(0x04)
	End           = byte(0x05)
	ResultRequest = byte(0x06)
	Result        = byte(0x07)
	DrawInProcess = byte(0x08)
)

// BetProtocol entity that encapsulates the communication protocol with the server
type BetProtocol struct{}

// NewProtocol Initializes a new protocol
func NewBetProtocol() *BetProtocol {
	return &BetProtocol{}
}

// Send Sends a message to the server
func (p *BetProtocol) Send(conn net.Conn, msg []byte, msgType byte) error {
	totalLength, err := lengthToBytes(len(msg))
	if err != nil {
		return err
	}
	fullMsg := []byte{msgType}
	fullMsg = append(fullMsg, totalLength...)
	fullMsg = append(fullMsg, msg...)
	remainingBytes := len(msg) + 5
	for remainingBytes > 0 {
		n, err := conn.Write(fullMsg)
		if err != nil {
			return err
		}
		remainingBytes -= n
	}
	return nil
}

// Receive Receives a message from the server
func (p *BetProtocol) Receive(conn net.Conn) ([]byte, []byte, error) {
	var buffer []byte
	// First read the message type and message length
	tmp := make([]byte, 5)
	_, err := conn.Read(tmp)
	if err != nil {
		return nil, nil, err
	}
	buffer = append(buffer, tmp...)
	msgType := buffer[0]
	msgLength, err := bytesToLength(buffer[1:])
	if err != nil {
		return nil, nil, err
	}

	// Read the rest of the message
	remaningBytes := msgLength
	buffer = buffer[:0]
	for remaningBytes > 0 {
		bytesToRead := max(1024, remaningBytes)
		tmp := make([]byte, bytesToRead)
		r, err := conn.Read(tmp)
		if err == io.EOF && remaningBytes > 0 {
			return nil, nil, ErrInvalidMessage
		}
		if err != nil {
			return nil, nil, err
		}
		buffer = append(buffer, tmp[:r]...)
		remaningBytes -= r
	}
	return []byte{msgType}, buffer, nil
}
