#!/usr/bin/env python3
#
#    update_data.py
#
# Script to fix errors in Quranic source data files
#
# check charset:
#   $ qran --source tanzil-uthmani | awk '{print $2}' | grep -o . | sort -u
#
# chexk output:
#   $ cat mushaf_uthmani-updated.json | jq -r '.blocks | flatten[]' | grep -o . | sort -u
#
# Copyright (c) 2025 Alicia González Martínez
#
# usage:
#   $ python3 update_data.py mushaf_uthmani.json mushaf_uthmani-updated.json
#     --latin_graph "/ـ//"
#
#########################################################################################


import re
import sys
import json
from typing import Pattern
from argparse import ArgumentParser, FileType, ArgumentTypeError



def _parse_sub(value: str) -> tuple[Pattern, str]:
    """ parse arg with a pattern and replacement modification

    Args:
        arg: argument to parse

    Return:
        regex and replacement.

    Raise:
        ValueError: if value is ill-formed.

    """
    try:
        if value[0] == value[-1] == "/":
            value = value[1:-1]
            pat, repl = value.split("/")
            return re.compile(pat), repl
        raise ArgumentTypeError
    except ValueError:
        raise ArgumentTypeError


def main():
    parser = ArgumentParser(
    	description="Script to fix errors in Quranic source data files"
    )
    parser.add_argument(
        "infile",
        type=FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="Quran data file"
    )
    parser.add_argument(
        "outfile",
        type=FileType("w"),
        nargs="?",
        default=sys.stdout,
        help="modified file"
    )
    parser.add_argument(
        "--latin_graph",
        type=_parse_sub,
        help="modify field with regex, format: /pattern/replacement/"
    )
    args = parser.parse_args()

    data = json.load(args.infile)

    latin_graph_regex, latin_graph_repl = args.latin_graph

    for iblock in range(len(data["blocks"])):
        arabic_graph, latin_graph, arabic_arch, latin_arch = data["blocks"][iblock]
        data["blocks"][iblock][1] = latin_graph_regex.sub(latin_graph_repl, latin_graph)

    # for isura in range(len(data["indexes"])):
    #     sura = data["indexes"][isura]
    #     for ivers in range(len(data["indexes"][isura])):
    #         vers = data["indexes"][isura][ivers]
    #         for iword in range(len(data["indexes"][isura][ivers])):
    #             word = data["indexes"][isura][ivers][iword]
    #             for iblock in range(len(data["indexes"][isura][ivers][iword])):
    #                 block = data["indexes"][isura][ivers][iword][iblock]

    json.dump(data, args.outfile)


if __name__ == "__main__":
    main()

