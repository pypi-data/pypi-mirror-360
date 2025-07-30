# 1D => ND #####################################################################

def point(position: int, base: int, rank: int) -> list:
    return [divmod(position, base ** __r)[0] % base for __r in range(rank)]

# ND => 1D #####################################################################

def index(coords: list, base: int, rank: int) -> int:
    return sum(
        __c * __b
        for __c, __b in zip(
            coords,
            [base ** __r for __r in range(rank)]))
