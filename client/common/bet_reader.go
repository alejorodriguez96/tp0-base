package common

import (
	"bufio"
	"os"
	"strconv"
	"strings"
)

// BetReader entity that encapsulates the reading of bets
type BetReader struct {
	// ID of the client
	ClientID int
	// Max number of bets to read
	NumberOfBets int
	// Channels to communicate with the client
	ClientChannels
	// File descriptor
	File *os.File
	// Scanner
	Scanner *bufio.Scanner
}

// NewBetReader Initializes a new bet reader
func NewBetReader(clientID int, numberOfBets int, betsFilePath string, clientChannels ClientChannels) (*BetReader, error) {
	file, err := os.Open(betsFilePath)
	if err != nil {
		return nil, err
	}
	scanner := bufio.NewScanner(file)
	return &BetReader{
		ClientID:       clientID,
		NumberOfBets:   numberOfBets,
		ClientChannels: clientChannels,
		File:           file,
		Scanner:        scanner,
	}, nil
}

// Start Starts the bet reader
func (br *BetReader) Start() {
	for {
		<-br.ClientChannels.RequestChannel
		bets, err := br.ReadBets()
		if err == nil && len(bets) == 0 {
			br.ClientChannels.BetsChannel <- nil
			br.ClientChannels.ErrorChannel <- nil
			continue
		}
		if err != nil {
			br.ClientChannels.BetsChannel <- nil
			br.ClientChannels.ErrorChannel <- err
			continue
		}
		br.ClientChannels.BetsChannel <- bets
		br.ErrorChannel <- nil
	}
}

// Close Closes the file descriptor
func (br *BetReader) Close() {
	log.Debugf("Closing bet reader")
	br.File.Close()
}

// ReadBets Reads the bets from the file
func (br *BetReader) ReadBets() ([]*Bet, error) {
	var bets []*Bet
	scanner := br.Scanner
	// for br.NumberOfBets > 0 {
	readLines := 0
	for readLines < br.NumberOfBets && scanner.Scan() {
		line := scanner.Text()
		bet, err := br.parseBet(line)
		if err != nil {
			return nil, err
		}
		bets = append(bets, bet)
		readLines++
	}
	return bets, nil
}

// parseBet Parses a bet from a string
func (br *BetReader) parseBet(line string) (*Bet, error) {
	// Split the line by commas
	parts := strings.Split(line, ",")
	if len(parts) != 5 {
		return nil, ErrInvalidBet
	}
	// Parse the player
	player := Player{
		name:      parts[0],
		lastname:  parts[1],
		document:  parts[2],
		birthdate: parts[3],
	}
	// Parse the number
	number, err := strconv.Atoi(parts[4])
	if err != nil {
		return nil, err
	}

	return NewBet(player, number, br.ClientID), nil
}
