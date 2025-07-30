#!/usr/bin/env python3
#
#    qran
#
# standalone entry point for qran
#                         
#    __ _ _ __ __ _ _ __  
#   / _` | '__/ _` | '_ \ 
#  | (_| | | | (_| | | | |
#   \__, |_|  \__,_|_| |_|
#      |_|                
# 
#
# Copyright (c) 2025 Alicia González Martínez
#
####################################################################################

import sys
import textwrap
import orjson as json
from argparse import ArgumentParser, FileType, RawTextHelpFormatter

from qran import __version__
from .util import parse_quran_range
from .models import Source
from .mushaf import get_text


def main():

    parser = ArgumentParser(
        description="Quran structured text API.\n\n" \
        "Unless indicated in parameters, each output token is given in four shapes:\n"\
        "  (1) Arabic graphemic representation\n" \
        "  (2) Latin graphemic representation\n" \
        "  (3) Arabic archgraphemic representation\n" \
        "  (4) Latin graphemic representation\n\n" \
        "Example of usage:\n" \
        "  $ qran 1:7:9:2-2:1:2 --blocks",
        formatter_class=RawTextHelpFormatter,
        epilog="Ya Kabikaj, protect this code from bugs!"
    )
    parser.add_argument(
        "index",
        type=parse_quran_range,
        nargs="?",
        default="1-",
        help=textwrap.dedent(""" \
            Quranic index range to retrieve [DEFAULT WHOLE TEXT]. 
             A complete range must have the following format:
                ini_sura:ini_verse:ini_word:ini_block-end_sura:end_verse:end_word:end_block
             Both beginning and end indexes are inclusive. All indexes are optional.
        """))
    parser.add_argument(
        "--source", "-s",
        choices=[s.value for s in Source],
        default=Source.TANZIL_SIMPLE.value,
        help="Quran encoding"
    )
    parser.add_argument(
        "--blocks",
        action="store_true",
        help="retrieve text as letterblocks instead of words"
    )
    script = parser.add_mutually_exclusive_group()
    script.add_argument(
        "--no_lat",
        action="store_true",
        help="omit Latin traslineration in output"
    )
    script.add_argument(
        "--no_ara",
        action="store_true",
        help="omit Arabic script in output"
    )
    layer = parser.add_mutually_exclusive_group()
    layer.add_argument(
        "--no_arch",
        action="store_true",
        help="omit archigraphemic representations in output"
    )
    layer.add_argument(
        "--no_graph",
        action="store_true",
        help="omit graphemic representations in output"
    )
    parser.add_argument(
        "--sep",
        default="\t",
        help="field separator for text output [DEFAULT \\t]"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print output in json instead of plain text"
    )
    parser.add_argument(
        "--out",
        type=FileType("w"),
        help="write output in file instead of stdin"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="prints the program version number and exits successfully"
    )
    args = parser.parse_args()

    try:
        tokens = get_text(
            ini_index=args.index[0],
            end_index=args.index[1],
            source=Source.from_str(args.source),
            args={
                "blocks": args.blocks,
                "no_lat": args.no_lat,
                "no_ara": args.no_ara,
                "no_graph": args.no_graph,
                "no_arch": args.no_arch,
            }
        )

        out = args.out or sys.stdout

        if args.json:
            data = [{"tok": tok[:-1], "ind": tok[-1]} for tok in tokens]
            out.write(json.dumps(data).decode("utf-8"))

        else:
            for tok in tokens:
                print(args.sep.join(tok), file=out)
    
    except FileNotFoundError as err:
        print(err, file=sys.stderr)

    except (KeyboardInterrupt, BrokenPipeError, IOError):
        pass

    sys.stderr.close()


if __name__ == "__main__":
    main()
