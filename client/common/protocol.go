package common

import (
	"io"
	"net"
)

// Message types
const (
	SingleBet = iota
	MultipleBet
)

// BetProtocol entity that encapsulates the communication protocol with the server
type BetProtocol struct {
	serializer *BetSerializer
}

// NewProtocol Initializes a new protocol
func NewBetProtocol() *BetProtocol {
	return &BetProtocol{
		serializer: NewBetSerializer(),
	}
}

// SendBet Sends a bet to the server
func (p *BetProtocol) SendBet(conn net.Conn, bet *Bet) error {
	serializedBet := p.serializer.Serialize(bet)
	totalLength, err := lengthToBytes(len(serializedBet))
	if err != nil {
		return err
	}
	msg := []byte{SingleBet}
	msg = append(msg, totalLength...)
	msg = append(msg, serializedBet...)
	remainingBytes := len(serializedBet) + 5
	for remainingBytes > 0 {
		n, err := conn.Write(msg)
		if err != nil {
			return err
		}
		remainingBytes -= n
	}
	return nil
}

// ReceiveBet Receives a bet from the server
func (p *BetProtocol) ReceiveBet(conn net.Conn) (*Bet, error) {
	var buffer []byte
	// First read the message type and message length
	tmp := make([]byte, 5)
	_, err := conn.Read(tmp)
	if err != nil {
		return nil, err
	}
	buffer = append(buffer, tmp...)
	//_msgType := buffer[0]
	msgLength, err := bytesToLength(buffer[1:])
	if err != nil {
		return nil, err
	}

	// Read the rest of the message
	remaningBytes := msgLength
	buffer = buffer[:0]
	for remaningBytes > 0 {
		bytesToRead := max(1024, remaningBytes)
		tmp := make([]byte, bytesToRead)
		r, err := conn.Read(tmp)
		if err == io.EOF && remaningBytes > 0 {
			return nil, ErrInvalidMessage
		}
		if err != nil {
			return nil, err
		}
		buffer = append(buffer, tmp[:r]...)
		remaningBytes -= r
	}
	// TODO: Deserialize according to the message type
	return p.serializer.Deserialize(buffer)
}
