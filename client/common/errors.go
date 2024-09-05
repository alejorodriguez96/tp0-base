package common

import "errors"

// ErrInvalidBet Error returned when a bet is invalid
var ErrInvalidBet = errors.New("invalid bet")

// ErrInvalidMessage Error returned when a message is invalid
var ErrInvalidMessage = errors.New("invalid message")

// ErrUnexpectedResponse Error returned when an unexpected response is received
var ErrUnexpectedResponse = errors.New("unexpected response")
