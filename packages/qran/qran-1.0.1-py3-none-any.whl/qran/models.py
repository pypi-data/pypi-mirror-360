#!/usr/bin/env python3
#
#    models.py
#
# Copyright (c) 2025 Alicia González Martínez
#
################################################

from enum import Enum
from pydantic import BaseModel


class Source(Enum):
    """ Encoding of Quranic text
    """
    TANZIL_SIMPLE = "tanzil-simple"
    TANZIL_UTHMANI = "tanzil-uthmani"
    DECOTYPE = "decotype"

    @classmethod
    def from_str(cls, s: str) -> "Source":
        """Convert string to Source enum member"""
        try:
            return cls(s)
        except ValueError as e:
            raise ValueError(f"Invalid source: {s}. Must be one of {[e.value for e in cls]}") from e

    def get_file(self) -> str:
        """ Get the corresponding Quran file name based on the source
        """
        mapping = {
            Source.TANZIL_SIMPLE: "mushaf_simple.json",
            Source.TANZIL_UTHMANI: "mushaf_uthmani.json",
            Source.DECOTYPE: "mushaf_dt.json"
        }
        return mapping[self]


class Index(BaseModel):
    """ Quranic index.
    """
    sura: int
    verse: int
    word: int
    block: int | None

    @classmethod
    def from_tuple(cls, index: tuple[int, int, int, int]) -> "Index":
        """ Create an Index instance from a tuple.

        Args:
            index_tuple: Quran index.

        """
        if len(index) != 4:
            raise ValueError("Tuple must have exactly four elements")
        
        return cls(sura=index[0], verse=index[1], word=index[2], block=index[3])


    def to_zero_index(self) -> None:
        """ Convert all indexes to 0-index"""
        self.sura -= 1
        self.verse -= 1
        self.word -= 1
        if self.block is not None:
            self.block -= 1


class Block(BaseModel):
    """ Quranic block with corresponding index.
    """
    grapheme_ar: str
    grapheme_lt: str
    archigrapheme_ar: str
    archigrapheme_lt: str 
    index: Index
