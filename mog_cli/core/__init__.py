### constants

# turns
BLACK = '+'
WHITE = '-'
TURNS = [BLACK, WHITE]
FLIP_TURN = {BLACK: WHITE, WHITE: BLACK}

# pieces
KING = 'OU'
PAWN = 'FU'
LANCE = 'KY'
KNIGHT = 'KE'
SILVER = 'GI'
GOLD = 'KI'
BISHOP = 'KA'
ROOK = 'HI'
PPAWN = 'TO'
PLANCE = 'NY'
PKNIGHT = 'NK'
PSILVER = 'NG'
PBISHOP = 'UM'
PROOK = 'RY'
PIECE_TYPES = [
    KING, PAWN, LANCE, KNIGHT, SILVER, GOLD, BISHOP, ROOK,
    PPAWN, PLANCE, PKNIGHT, PSILVER, PBISHOP, PROOK
]
HAND_PIECE_TYPES = [PAWN, LANCE, KNIGHT, SILVER, GOLD, BISHOP, ROOK]

_PROMO = {PAWN: PPAWN, LANCE: PLANCE, KNIGHT: PKNIGHT, SILVER: PSILVER, BISHOP: PBISHOP, ROOK: PROOK}
_PROMO_INV = {v: k for k, v in _PROMO.items()}
UPPER_PIECE_TYPE = lambda p: _PROMO.get(p, p)
LOWER_PIECE_TYPE = lambda p: _PROMO_INV.get(p, p)

# positions
POS_HAND = '00'

from core.move import Move
from core.state import State
from core.game import Game
