package common

import (
	"net"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	NumericID     int
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// ClientChannels Channels used by the client
type ClientChannels struct {
	BetsChannel    chan []*Bet
	RequestChannel chan bool
	ErrorChannel   chan error
}

// Client Entity that encapsulates how
type Client struct {
	config     ClientConfig
	conn       net.Conn
	channels   ClientChannels
	protocol   *BetProtocol
	serializer *BetSerializer
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, channels ClientChannels) *Client {
	client := &Client{
		config:     config,
		channels:   channels,
		protocol:   NewBetProtocol(),
		serializer: NewBetSerializer(),
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// Close gracefully closes the client connection
func (c *Client) Close() {
	log.Debugf("Client gracefully quitting")
	c.conn.Close()
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	for {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		moreBets, err := c.sendChunk()
		if err != nil {
			log.Errorf("action: send_chunk | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		if !moreBets {
			break
		}

		// Wait a time between sending one message and the next one
		//time.Sleep(c.config.LoopPeriod)

	}
	err := c.sendEndMessage()
	if err != nil {
		return
	}

	for {
		c.createClientSocket()
		response, err := c.pollResults()
		if err != nil {
			log.Errorf("action: consulta_ganadores | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		if response == nil {
			time.Sleep(c.config.LoopPeriod)
			continue
		}
		resultSerializer := NewResultSerializer()
		result, err := resultSerializer.DeserializeDrawResult(response)
		if err != nil {
			log.Errorf("action: consulta_ganadores | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v",
			result.winnerCount(),
		)

		break
	}

}

// sendChunk Sends a chunk of bets to the server
//
// Returns true if there are more bets to read, false otherwise
func (c *Client) sendChunk() (bool, error) {
	// Request the bets to the bet reader
	c.channels.RequestChannel <- true
	bets := <-c.channels.BetsChannel
	err := <-c.channels.ErrorChannel
	if err == nil && bets == nil {
		return false, nil // No more bets to read
	}
	if err != nil {
		log.Errorf("action: request_bets | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return false, err
	}

	// Send the bet to the server
	msg := c.serializer.SerializeBetChunk(bets)
	err = c.protocol.Send(c.conn, msg, MultipleBet)
	if err != nil {
		log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return false, err
	}
	msgType, _, err := c.protocol.Receive(c.conn)

	if err != nil {
		log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return false, err
	}

	if msgType[0] != BetACK {
		log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v",
			c.config.ID,
			"Invalid message type",
		)
		return false, ErrUnexpectedResponse
	}

	log.Infof("action: apuesta_enviada | result: success | cantidad: %v",
		len(bets),
	)
	return true, nil
}

// sendEndMessage Sends an end message to the server
func (c *Client) sendEndMessage() error {
	retries := 0
	for {
		err := c.protocol.Send(c.conn, []byte{byte(c.config.NumericID)}, End)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			retries++
			if retries > 3 {
				log.Errorf("Server is not responding. Exiting")
				return err
			}
			continue
		}
		break
	}
	return nil
}

// pollResults Polls the server for results
func (c *Client) pollResults() ([]byte, error) {
	err := c.protocol.Send(c.conn, []byte{byte(c.config.NumericID)}, ResultRequest)
	if err != nil {
		return nil, err
	}

	msgType, msg, err := c.protocol.Receive(c.conn)
	if err != nil {
		return nil, err
	}

	if msgType[0] == DrawInProcess {
		return nil, nil
	}

	if msgType[0] != Result {
		return nil, ErrUnexpectedResponse
	}

	return msg, nil
}
