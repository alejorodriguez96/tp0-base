package common

type Player struct {
	name      string
	lastname  string
	document  string
	birthdate string
}

// Bet entity represents a bet placed by a player
type Bet struct {
	agencyID int
	player   Player
	number   int
}

// NewBet Initializes a new bet
func NewBet(player Player, number int, agency int) *Bet {
	bet := &Bet{
		agencyID: agency,
		player:   player,
		number:   number,
	}
	return bet
}
