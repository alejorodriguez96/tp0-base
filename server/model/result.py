from model.bet import Bet
from common.utils import has_won

class DrawResult:
    """ A lottery draw result. """
    def __init__(self, winners: list[Bet]):
        """
        agency must be passed with integer format.
        winners must be a list of Bet objects.
        """
        self.winners = winners

    @staticmethod
    def from_bet_list(bets: list[Bet]):
        """
        Create a DrawResult object from a list of Bet objects.
        """
        winners = [bet for bet in bets if has_won(bet)]
        return DrawResult(winners)

    def get_winners_from_agency(self, agency: int) -> list[Bet]:
        """
        Get the winners from a specific agency.
        """
        return [bet for bet in self.winners if bet.agency == agency]
