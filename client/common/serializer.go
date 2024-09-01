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

// Serialize serializes a bet into a byte array
func (s *BetSerializer) Serialize(bet *Bet) []byte {
	var barray []byte
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

// Deserialize deserializes a byte array into a bet
func (s *BetSerializer) Deserialize(barray []byte) (*Bet, error) {
	split := bytes.Split(barray, []byte{FieldSeparator})
	player := Player{
		name:      string(split[0]),
		lastname:  string(split[1]),
		document:  string(split[2]),
		birthdate: string(split[3]),
	}
	number, err := strconv.Atoi(string(split[4]))
	if err != nil {
		return nil, err
	}
	return NewBet(player, number), nil
}
