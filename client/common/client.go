package common

import (
	"net"
	"os"
	"strconv"
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

// Client Entity that encapsulates how
type Client struct {
	config     ClientConfig
	conn       net.Conn
	protocol   *BetProtocol
	serializer *BetSerializer
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:     config,
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
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		betNumber, parseErr := strconv.Atoi(os.Getenv("NUMERO"))
		if parseErr != nil {
			return
		}
		bet := NewBet(
			Player{
				name:      os.Getenv("NOMBRE"),
				lastname:  os.Getenv("APELLIDO"),
				document:  os.Getenv("DOCUMENTO"),
				birthdate: os.Getenv("NACIMIENTO"),
			},
			betNumber,
			c.config.NumericID,
		)

		// Send the bet to the server
		msg := c.serializer.Serialize(bet)
		err := c.protocol.Send(c.conn, msg, SingleBet)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		msgType, _, err := c.protocol.Receive(c.conn)

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		if msgType[0] != BetACK {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				"Invalid message type",
			)
			return
		}

		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			bet.player.document,
			bet.number,
		)

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
