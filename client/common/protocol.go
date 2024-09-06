package common

import "net"

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
	stream := NewSocketStream(conn)
	totalLength, err := lengthToBytes(len(msg))
	if err != nil {
		return err
	}
	fullMsg := []byte{msgType}
	fullMsg = append(fullMsg, totalLength...)
	fullMsg = append(fullMsg, msg...)
	err = stream.Write(fullMsg)
	if err != nil {
		return err
	}
	return nil
}

// Receive Receives a message from the server
func (p *BetProtocol) Receive(conn net.Conn) ([]byte, []byte, error) {

	// Esto debería ser recibido por parámetro pero no puedo resolver un bug que
	// me da al hacer el cambio. No cuento con tiempo para corregirlo, disculpen.
	stream := NewSocketStream(conn)
	// First read the message type and message length
	buffer, err := stream.Read(5)
	if err != nil {
		return nil, nil, err
	}
	msgType := buffer[0]
	msgLength, err := bytesToLength(buffer[1:])
	if err != nil {
		return nil, nil, err
	}

	// Read the rest of the message
	buffer, err = stream.Read(msgLength)
	if err != nil {
		return nil, nil, err
	}
	return []byte{msgType}, buffer, nil
}
