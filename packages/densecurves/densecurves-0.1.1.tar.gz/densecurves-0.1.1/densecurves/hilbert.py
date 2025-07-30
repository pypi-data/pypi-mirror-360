"""Map a flat dimension with points of rank N, according to the Hilbert curve."""

import functools

import densecurves.linear

# BINARY #######################################################################

def encode_binary(number: int, width: int) -> str:
    return format(number, 'b').zfill(width)[:width] # truncated at width

# SHAPING ######################################################################

def transpose_axes(number: int, order: int, rank: int) -> list:
    __bits = encode_binary(number, width=rank * order)
    return [int(__bits[__i::rank], 2) for __i in range(rank)]

def flatten_axes(coords: list, order: int, rank: int) -> int:
    __coords = [encode_binary(__c, width=order) for __c in coords]
    return int(''.join([__y[__i] for __i in range(order) for __y in __coords]), 2)

# GRAY CODES ###################################################################

def encode_gray(number: int) -> int:
    return number ^ (number >> 1)

def decode_gray(number: int) -> int:
    return functools.reduce(
        lambda __a, __b: __a ^ __b,
        [number >> __i for __i in range(len(format(number, 'b')))])

# ENTANGLE #####################################################################

def _entangle(coords: list, order: int, rank: int, step: int=1) -> list:
    __coords = list(coords)
    # undo the extra rotations
    for __j in range(1, order)[::-step]:
        # q is a single bit mask and (q - 1) is a string of ones
        __q = 2 ** __j
        for __i in range(0, rank)[::step]:
            # invert the least significant bits
            if __coords[__i] & __q:
                __coords[0] ^= __q - 1
            # exchange the least significant bits
            else:
                __t = (__coords[0] ^ __coords[__i]) & (__q - 1)
                __coords[0] ^= __t
                __coords[__i] ^= __t
    # list of rank coordinates
    return __coords

def entangle(coords: list, order: int, rank: int) -> list:
    return _entangle(coords=coords, order=order, rank=rank, step=1)

def untangle(coords: list, order: int, rank: int) -> list:
    return _entangle(coords=coords, order=order, rank=rank, step=-1)

# 1D => 2D #####################################################################

def _point(position: int, order: int, rank: int) -> list:
    # gray encoding H ^ (H/2)
    __gray = encode_gray(position)
    # approximate the curve
    __coords = transpose_axes(__gray, order=order, rank=rank)
    # Undo excess work
    return untangle(__coords, order=order, rank=rank)

def point(position: int, order: int, rank: int, group: int=0) -> list:
    # side of the fine blocks
    __block = 1 << group
    # split the index into blocks
    __coarse, __fine = divmod(position, __block ** rank)
    # coarse coordinates, following the Hilbert curve
    __coarse = _point(__coarse, order=order, rank=rank)
    # fine coordinates, inside each block
    __fine = densecurves.linear.point(__fine, base=__block, rank=rank)
    # combine both coordinates systems
    return [__c * __block + __f for __c, __f in zip(__coarse, __fine)]

# 2D => 1D #####################################################################

def _index(coords: list, order: int, rank: int) -> int:
    # entangle the positions back
    __coords = entangle(coords, order=order, rank=rank)
    # flatten the coordinate
    __position = flatten_axes(__coords, order=order, rank=rank)
    # decode the gray encodings
    return decode_gray(__position)

def index(coords: list, order: int, rank: int, group: int=0) -> int:
    # side of the fine blocks
    __block = 1 << group
    # split the coordinates
    __coarse, __fine = list(zip(*[divmod(__c, __block) for __c in coords]))
    # coarse index, on the curve
    __coarse = _index(__coarse, order=order, rank=rank)
    # fine index, inside the block
    __fine = densecurves.linear.index(__fine, base=__block, rank=rank)
    # combine the indexes
    return __fine + __coarse * (__block ** rank)
