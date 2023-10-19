from typing import List, Optional
from .piece import ShogiPiece

class ShogiPlayer:
    def __init__(self, name, team: int, captured: Optional[List[str]] = None) -> None:
        self.name = name
        self.team = team
        self.captured = captured if captured else []

    def __repr__(self) -> str:
        return self.name

    # Pieces that the player has captured, printed every turn
    def capture(self, piece: ShogiPiece) -> None:
        self.captured.append(piece.name)

    # Piece that has been placed on to the board and removed from captured
    def drop(self, piece: ShogiPiece) -> None:
        self.captured.remove(piece)