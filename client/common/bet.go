package common

type Player struct {
	name      string
	lastname  string
	document  string
	birthdate string
}

// Bet entity represents a bet placed by a player
type Bet struct {
	player Player
	number int
}

// NewBet Initializes a new bet
func NewBet(player Player, number int) *Bet {
	bet := &Bet{
		player: player,
		number: number,
	}
	return bet
}
