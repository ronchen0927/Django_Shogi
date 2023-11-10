from typing import Tuple, List
from abc import ABCMeta, abstractmethod
from .utils import is_in_board, parse_pos_to_string

class ShogiPiece:
    __metaclass__ = ABCMeta

    _GGeneral_pattern = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0)]

    OUR_PROMOTION_ZONE = [0, 1, 2]
    OPPONENT_PROMOTION_ZONE = [6, 7, 8]

    def __init__(self, name: str, team: int, promoted: bool = False) -> None:
        self.name = name
        self.team = team          # 1: Our team, -1: Opponent team
        self.promoted = promoted


    def __repr__(self):
        return self.name


    @abstractmethod
    def get_valid_moves(self):
        pass
    

    # Pattern provided to this function dictates the directions in which the piece may move
    def pattern_check(self, pattern: List[Tuple[int, int]], position: Tuple[int, int], board) -> List[str]:
        src_r, src_c = position
        opponent_team = -self.team
        possible_moves = []

        for pr, pc in pattern:
            dst_r, dst_c = src_r + pr, src_c + pc

            if is_in_board((dst_r, dst_c)):
                if not board[dst_r][dst_c] or board[dst_r][dst_c].team == opponent_team:
                    move_notation = parse_pos_to_string((src_r, src_c), (dst_r, dst_c))
                    possible_moves.append(move_notation)

                    # 加上能升變的 move
                    if not board[src_r][src_c].promoted:
                        if (self.team == 1 and dst_r in self.OUR_PROMOTION_ZONE) or (self.team == -1 and dst_r in self.OPPONENT_PROMOTION_ZONE):
                            move_notation += '+'
                            possible_moves.append(move_notation)
        
        return possible_moves
    

    # Loop check diagonals or cardinal directions in the case of a rook or bishop that can move like this
    def loop_pattern_check(self, pattern: List[Tuple[int, int]], position: Tuple[int, int], board) -> List[str]:
        src_r, src_c = position
        opponent_team = -self.team
        possible_moves = []

        for pr, pc in pattern:
            dst_r, dst_c = src_r + pr, src_c + pc

            while is_in_board((dst_r, dst_c)):
                if not board[dst_r][dst_c] or board[dst_r][dst_c].team == opponent_team:
                    move_notation = parse_pos_to_string((src_r, src_c), (dst_r, dst_c))
                    possible_moves.append(move_notation)

                    # 加上能升變的 move
                    if not board[src_r][src_c].promoted:
                        if (self.team == 1 and dst_r in self.OUR_PROMOTION_ZONE) or (self.team == -1 and dst_r in self.OPPONENT_PROMOTION_ZONE):
                            move_notation += '+'
                            possible_moves.append(move_notation)
                else:
                    break

                dst_r += pr
                dst_c += pc
        
        return possible_moves


class King(ShogiPiece):
    '''
    King mask:
    [D, D, D],
    [D, S, D],
    [D, D, D]
    '''
    _king_pattern = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        moves = self.pattern_check(self._king_pattern, position, board)
        return moves


class Rook(ShogiPiece):
    '''
    Rook mask:
    [D, E, D],
    [E, S, E],
    [D, E, D]
    '''
    _rook_pattern = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    _king_pattern = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Including promoted pattern.

    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        moves = self.loop_pattern_check(self._rook_pattern, position, board)
        if self.promoted:
            moves.extend(self.pattern_check(self._king_pattern, position, board))
        return moves


class Bishop(ShogiPiece):
    '''
    Bishop mask:
    [D, E, D],
    [E, S, E],
    [D, E, D]
    '''
    _bishop_pattern = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    _king_pattern = [(-1, 0), (0, -1), (0, 1), (1, 0)]  # Including promoted pattern.

    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        moves = self.loop_pattern_check(self._bishop_pattern, position, board)
        if self.promoted:
            moves.extend(self.pattern_check(self._king_pattern, position, board))
        return moves


class GGeneral(ShogiPiece):
    '''
    GGeneral mask:
    [D, D, D],
    [D, S, D],
    [E, D, E]
    '''
    _GGeneral_pattern = ShogiPiece._GGeneral_pattern

    @property
    def _pattern(self):
        return self._GGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._GGeneral_pattern]

    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        moves = self.pattern_check(self._pattern, position, board)
        return moves


class SGeneral(ShogiPiece):
    '''
    SGeneral mask:
    [D, D, D],
    [E, S, E],
    [D, E, D]
    '''
    _SGeneral_pattern = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 1)]
    
    @property
    def _pattern(self):
        return self._SGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._SGeneral_pattern]
    
    @property
    def _pattern_promoted(self):
        return self._GGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._GGeneral_pattern]
    
    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        pattern = self._pattern_promoted if self.promoted else self._pattern
        moves = self.pattern_check(pattern, position, board)
        return moves


class Knight(ShogiPiece):
    '''
    Knight mask:
    [D, E, D],
    [E, E, E],
    [E, S, E]
    '''
    _Kinght_pattern = [(-2, -1), (-2, 1)]
    _GGeneral_pattern = ShogiPiece._GGeneral_pattern
    
    @property
    def _pattern(self):
        return self._Kinght_pattern if self.team == 1 else [(-r, c) for r, c in self._Kinght_pattern]
    
    @property
    def _pattern_promoted(self):
        return self._GGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._GGeneral_pattern]
    
    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        pattern = self._pattern_promoted if self.promoted else self._pattern
        moves = self.pattern_check(pattern, position, board)
        return moves


class Lance(ShogiPiece):
    '''
    Lance mask:
    [E, D, E],
    [E, S, E],
    [E, E, E]
    '''
    _Lance_pattern = [(-1, 0)]
    _GGeneral_pattern = ShogiPiece._GGeneral_pattern

    @property
    def _pattern(self):
        return self._Lance_pattern if self.team == 1 else [(-r, c) for r, c in self._Lance_pattern]
    
    @property
    def _pattern_promoted(self):
        return self._GGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._GGeneral_pattern]
    
    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        pattern = self._pattern_promoted if self.promoted else self._pattern
        moves = self.loop_pattern_check(pattern, position, board)
        return moves


class Pawn(ShogiPiece):
    '''
    Pawn mask:
    [E, D, E],
    [E, S, E],
    [E, E, E]
    '''
    _Pawn_pattern = [(-1, 0)]
    _GGeneral_pattern = ShogiPiece._GGeneral_pattern

    @property
    def _pattern(self):
        return self._Pawn_pattern if self.team == 1 else [(-r, c) for r, c in self._Pawn_pattern]
    
    @property
    def _pattern_promoted(self):
        return self._GGeneral_pattern if self.team == 1 else [(-r, c) for r, c in self._GGeneral_pattern]
    
    def get_valid_moves(self, position: Tuple[int, int], board: List[List[int]]) -> List[str]:
        pattern = self._pattern_promoted if self.promoted else self._pattern
        moves = self.pattern_check(pattern, position, board)
        return moves