package common

import "errors"

// ErrInvalidBet Error returned when a bet is invalid
var ErrInvalidBet = errors.New("invalid bet")

// ErrInvalidMessage Error returned when a message is invalid
var ErrInvalidMessage = errors.New("invalid message")
