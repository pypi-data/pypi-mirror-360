#!/usr/bin/env python3
#
#    util.py
#
# Copyright (c) 2025 Alicia González Martínez
#
################################################

from typing import TypedDict
from argparse import ArgumentTypeError

from .models import Index, Block


class TextArgs(TypedDict, total=False):
    blocks: bool
    no_lat: bool
    no_ara: bool
    no_graph: bool
    no_arch: bool


def _parse_index(index: str, default: int) -> Index:
    """ convert string containing an index into an Index object.

    Args:
        index: index to parse.
        default: default value if not included in index.

    Return:
        splited index.

    Raise:
        ValueError: if index is ill-formed.

    """
    try:
        indexes = iter(index.split(":"))
        sura, verse, word, block = (next(indexes, None) for _ in range(4))
        return Index(
            sura=int(sura) if sura else default,
            verse=int(verse) if verse else default,
            word=int(word) if word else default,
            block=int(block) if block else default
        )
    except ValueError:
        raise


def parse_quran_range(arg: str) -> tuple[Index, Index]:
    """ Parse index range contained in arg. Complete format:

        "sura,verse,word,block-sura,verse,word,block"

        All individual indexes are optional

    Args:
        arg: string containing the quranic index range or single index.

    Return:
        range of indexes.

    Raise:
        ArgumentTypeError: if arg does not follow the expected format.

    """
    if "-" in arg:
        ini, _, end = arg.partition("-")
    else:
        ini = end = arg

    try:
        return (
            _parse_index(index=ini if ini else "", default=1),
            _parse_index(index=end if end else "", default=-1)
        )

    except ValueError:
        raise ArgumentTypeError(
            "argument format must be sura:verse:word:block-sura:verse:word:block, eg. 2:3-2:10:2"
        )

def group_idx(block: Block) -> tuple[int, int, int]:
    """
    """
    idx = block.index
    return (idx.sura, idx.verse, idx.word)

