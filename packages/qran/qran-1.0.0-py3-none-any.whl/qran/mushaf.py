#!/usr/bin/env python3
#
#    mushaf.py
#
# retrieve Quranic text
#
#  __  __           _            __ 
# |  \/  |_   _ ___| |__   __ _ / _|
# | |\/| | | | / __| '_ \ / _` | |_ 
# | |  | | |_| \__ \ | | | (_| |  _|
# |_|  |_|\__,_|___/_| |_|\__,_|_|  
#
# Copyright (c) 2025 Alicia González Martínez
#
################################################

import sys
import orjson as json
import importlib.resources as pkg_resources
from itertools import groupby
from typing import Generator

from .models import Source, Index, Block
from .util import TextArgs, group_idx


def _extract_seq(
    data: dict,
    ini_ind: Index,
    end_ind: Index
    ) -> Generator[Block, None, None]:
    """ Extracts the sequece of Quranic blocks indicated in index range ind.

    Args:
        data: Quran data
        ind: index range.

    Yield:
        Representations of Quranic token together with its index.

    """
    ini_sura = ini_ind.sura
    ini_verse = ini_ind.verse
    ini_word = ini_ind.word
    ini_block = ini_ind.block

    end_sura = end_ind.sura
    end_verse = end_ind.verse
    end_word = end_ind.word
    end_block = end_ind.block

    for isura in range(ini_sura, end_sura+1):
        for iverse in range(len(data["indexes"][isura])):
            if isura == ini_sura and iverse < ini_verse:
                continue
            if isura == end_sura and iverse > end_verse:
                return
            for iword in range(len(data["indexes"][isura][iverse])):
                if isura == ini_sura and iverse == ini_verse and iword < ini_word:
                    continue
                if isura == end_sura and iverse == end_verse and iword > end_word:
                    return
                for iblock in range(len(data["indexes"][isura][iverse][iword])):
                    if isura == ini_sura and iverse == ini_verse and \
                        iword == ini_word and iblock < ini_block:
                        continue
                    if isura == end_sura and iverse == end_verse and \
                        iword == end_word and iblock > end_block:
                        return

                    block_index = data["indexes"][isura][iverse][iword][iblock]

                    graph_ar, graph_lt, arch_ar, arch_lt = data["blocks"][block_index]
                    
                    yield Block(
                        grapheme_ar=graph_ar,
                        grapheme_lt=graph_lt,
                        archigrapheme_ar=arch_ar, 
                        archigrapheme_lt=arch_lt,
                        index=Index(
                            sura=isura+1,
                            verse=iverse+1,
                            word=iword+1,
                            block=iblock+1
                        )
                    )


def _correct_out_of_bounds(ind: Index, data: dict) -> None:
    """ Adjust all indexes in ind so that none of them is out of bounds.

    ind is still 1-based index

    Args:
       ind: index to correct.
       data: data containig whole Quran structure.


    """
    if ind.sura > len(data["indexes"]):
        print(
            f"Warning! sura {ind.sura} is out of bounds. "
            f"We set it to last sura, i.e. {len(data['indexes'])} ",
            file=sys.stderr
        )
        ind.sura = len(data["indexes"])

    if ind.verse > len(data["indexes"][ind.sura-1]):
        print(
            f"Warning! verse {ind.verse} is out of bounds. "
            f"We set it to last verse in sura, i.e. {len(data['indexes'][ind.sura-1])} ",
            file=sys.stderr
        )
        ind.verse = len(data["indexes"][ind.sura-1])
    
    if ind.word > len(data["indexes"][ind.sura-1][ind.verse-1]):
        print(
            f"Warning! word {ind.word} is out of bounds. "
            f"We set it to last word in verse, i.e. {len(data['indexes'][ind.sura-1][ind.verse-1])} ",
            file=sys.stderr
        )
        ind.word = len(data["indexes"][ind.sura-1][ind.verse-1])
    
    if ind.block > len(data["indexes"][ind.sura-1][ind.verse-1][ind.word-1]):
        print(
            f"Warning! block {ind.block} is out of bounds. "
            f"We set it to last block in word, i.e. {len(data['indexes'][ind.sura-1][ind.verse-1][ind.word-1])} ",
            file=sys.stderr
        )
        ind.block = len(data["indexes"][ind.sura-1][ind.verse-1][ind.word-1])


def get_text(
    ini_index: Index | tuple[int, int, int, int] = (1, 1, 1, 1),
    end_index: Index | tuple[int, int, int, int] = (-1, -1, -1, -1),
    source: Source | str = Source.TANZIL_SIMPLE,
    args: TextArgs = {}
    ) -> Generator[tuple[str, ...], None, None]:
    """ Get all tokens corresponding to the indicated Quranic index ranges.

    Unless indicated with args parameters, each token is given in four shapes:
    (1) Arabic graphemic representation
    (2) Latin graphemic representation
    (3) Arabic archgraphemic representation
    (4) Latin graphemic representation

    Args:
        index: initial and end indexes
        source: Quranic encoding to retrieve:
            (1) "tanzil-simple"
            (2) "tanzil-uthmani"
            (3) "decotype"
        args: parameters to configure desired output 
            {
                "blocks": bool,    # display tokens in blocks instead of words
                "no_lat": bool,    # do not show representations in Latin script
                "no_ara": bool,    # do not show representations in Arabic script
                "no_graph": bool,  # do not show graphemic representations 
                "no_arch": bool,   # do not show archigraphemic representations
            }
    Yield:
        Representations of Quranic token together with its index.

    """
    default_args: TextArgs = {
        "blocks": False,
        "no_lat": False,
        "no_ara": False,
        "no_graph": False,
        "no_arch": False
    }
    args = {**default_args, **args}

    if isinstance(source, str):
        source = Source.from_str(source)

    quran = source.get_file()

    quran_path = pkg_resources.files(__package__).joinpath(quran)
    
    if not quran_path.is_file():
        raise FileNotFoundError("Decotype Quran is private.")

    with quran_path.open("rb") as fp:
        data = json.loads(fp.read())

    if isinstance(ini_index, tuple):
        ini_index = Index.from_tuple(ini_index)

    if isinstance(end_index, tuple):
        end_index = Index.from_tuple(end_index)

    ini = ini_index
    end = end_index

    _correct_out_of_bounds(ini, data)
    _correct_out_of_bounds(end, data)

    # correct -1 end indexes
    if end.sura == -1:
        end.sura = len(data["indexes"])
    
    if end.verse == -1:
        end.verse = len(data["indexes"][end.sura-1])

    if end.word == -1:
        end.word = len(data["indexes"][end.sura-1][end.verse-1])

    if end.block == -1:
        end.block = len(data["indexes"][end.sura-1][end.verse-1][end.word-1])

    ini.to_zero_index()
    end.to_zero_index()

    sequence = _extract_seq(data, ini, end)

    if not args["blocks"]:
        
        seq = ((k, list(g)) for k, g in groupby(sequence, key=group_idx))
        
        sequence = (
            Block(
                grapheme_ar="".join(b.grapheme_ar for b in blocks_group),
                grapheme_lt="".join(b.grapheme_lt for b in blocks_group),
                archigrapheme_ar="".join(b.archigrapheme_ar for b in blocks_group),
                archigrapheme_lt="".join(b.archigrapheme_lt for b in blocks_group),
                index=Index(
                    sura=ind[0],
                    verse=ind[1],
                    word=ind[2],
                    block=None
                )
        ) for ind, blocks_group in seq)

    res: tuple[str, ...]

    for block in sequence:
    
        if args["no_lat"]:
            if args["no_graph"]:
                res = block.archigrapheme_ar,
            elif args["no_arch"]:
                res = block.grapheme_ar,
            else:
                res = block.grapheme_ar, block.archigrapheme_ar
        elif args["no_ara"]:
            if args["no_graph"]:
                res = block.archigrapheme_lt,
            elif args["no_arch"]:
                res = block.grapheme_lt,
            else:
                res = block.grapheme_lt, block.archigrapheme_lt
        else:
            if args["no_graph"]:
                res = block.archigrapheme_ar, block.archigrapheme_lt
            elif args["no_arch"]:
                res = block.grapheme_ar, block.grapheme_lt
            else:
                res = block.grapheme_ar, block.grapheme_lt, block.archigrapheme_ar, block.archigrapheme_lt

        ind = f"{block.index.sura}:{block.index.verse}:{block.index.word}"
        if block.index.block:
            ind = f"{ind}:{block.index.block}"

        res = res + (ind,)

        yield res
