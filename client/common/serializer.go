package common

import (
	"bytes"
	"strconv"
)

const (
	// Field separator, a 1f (hex) character in byte format
	FieldSeparator = byte(0x1f)
	// Record Separator, a 1e (hex) character in byte format
	RecordSeparator = byte(0x1e)
)

type BetSerializer struct{}

func NewBetSerializer() *BetSerializer { return &BetSerializer{} }

// SerializeBet serializes a bet into a byte array
func (s *BetSerializer) SerializeBet(bet *Bet) []byte {
	var barray []byte
	barray = append(barray, []byte(strconv.Itoa(bet.agencyID))...)
	barray = append(barray, FieldSeparator)
	barray = append(barray, []byte(bet.player.name)...)
	barray = append(barray, FieldSeparator)
	barray = append(barray, []byte(bet.player.lastname)...)
	barray = append(barray, FieldSeparator)
	barray = append(barray, []byte(bet.player.document)...)
	barray = append(barray, FieldSeparator)
	barray = append(barray, []byte(bet.player.birthdate)...)
	barray = append(barray, FieldSeparator)
	barray = append(barray, []byte(strconv.Itoa(bet.number))...)
	return barray
}

// SerializeBetChunk serializes a chunk of bets into a byte array
func (s *BetSerializer) SerializeBetChunk(bets []*Bet) []byte {
	var barray []byte
	for _, bet := range bets {
		barray = append(barray, s.SerializeBet(bet)...)
		barray = append(barray, RecordSeparator)
	}
	barray = barray[:len(barray)-1] // Remove last record separator
	return barray
}

// DeserializeBet deserializes a byte array into a bet
func (s *BetSerializer) DeserializeBet(barray []byte) (*Bet, error) {
	split := bytes.Split(barray, []byte{FieldSeparator})
	player := Player{
		name:      string(split[1]),
		lastname:  string(split[2]),
		document:  string(split[3]),
		birthdate: string(split[4]),
	}
	number, err := strconv.Atoi(string(split[5]))
	if err != nil {
		return nil, err
	}
	agencyID, err := strconv.Atoi(string(split[0]))
	if err != nil {
		return nil, err
	}
	return NewBet(player, number, agencyID), nil
}

// DeserializeBetChunk deserializes a byte array into a chunk of bets
func (s *BetSerializer) DeserializeBetChunk(barray []byte) ([]*Bet, error) {
	split := bytes.Split(barray, []byte{RecordSeparator})
	var bets []*Bet
	for _, betBytes := range split {
		bet, err := s.DeserializeBet(betBytes)
		if err != nil {
			return nil, err
		}
		bets = append(bets, bet)
	}
	return bets, nil
}

// ResultSerializer serializes a result into a byte array
type ResultSerializer struct{}

func NewResultSerializer() *ResultSerializer { return &ResultSerializer{} }

// DeserializeResult deserializes a byte array into a result
func (s *ResultSerializer) DeserializeDrawResult(barray []byte) (*DrawResult, error) {
	split := bytes.Split(barray, []byte{RecordSeparator})
	winners := []string{}
	for _, winner := range split {
		if len(winner) == 0 {
			continue
		}
		winners = append(winners, string(winner))
	}
	return DrawResultFromDocuments(winners), nil
}
