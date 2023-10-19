from typing import Tuple

def is_in_board(position: Tuple[int, int]) -> bool:
    r, c = position
    return 0 <= r <= 8 and 0 <= c <= 8

def parse_string_to_pos(notation: str) -> Tuple[int, int, bool]:
    row = 9 - int(notation[1])
    col = (ord(notation[0]) - 97)

    is_promoted = True if len(notation) == 3 else False
    return row, col, is_promoted

def parse_pos_to_string(src: Tuple[int, int], dst: Tuple[int, int], is_promoted: bool = False) -> str:
    src_r, src_c = src
    dst_r, dst_c = dst

    str_src_c, str_src_r = (chr(src_c + 97)), str(9 - src_r)
    str_dst_c, str_dst_r = (chr(dst_c + 97)), str(9 - dst_r)

    notation = str_src_c + str_src_r + str_dst_c + str_dst_r

    return notation + '+' if is_promoted else notation

def parse_drop_to_string(piece_name: str, dst: Tuple[int, int]) -> str:
    dst_r, dst_c = dst
    
    str_dst_c, str_dst_r = (chr(dst_c + 97)), str(9 - dst_r)
    
    notation = piece_name + '*' + str_dst_c + str_dst_r

    return notation