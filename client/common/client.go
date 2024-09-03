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

		// Request the bets to the bet reader
		c.channels.RequestChannel <- true
		bets := <-c.channels.BetsChannel
		err := <-c.channels.ErrorChannel
		if err == nil && bets == nil {
			break // No more bets to read
		}
		if err != nil {
			log.Errorf("action: request_bets | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// Send the bet to the server
		msg := c.serializer.SerializeBetChunk(bets)
		err = c.protocol.Send(c.conn, msg, MultipleBet)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			break
		}
		msgType, _, err := c.protocol.Receive(c.conn)

		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			continue
		}

		if msgType[0] != BetACK {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v",
				c.config.ID,
				"Invalid message type",
			)
			continue
		}

		log.Infof("action: apuesta_enviada | result: success | cantidad: %v",
			len(bets),
		)

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
