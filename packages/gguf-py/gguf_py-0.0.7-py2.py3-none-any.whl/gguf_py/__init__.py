# !/usr/bin/env python3

__version__ = '0.0.7'

def __init__():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    subparsers.add_parser('a', help='[a] assembler')
    subparsers.add_parser('b', help='[b] brush: remove tensor')
    subparsers.add_parser('c', help='[c] checker')
    subparsers.add_parser('d', help='[d] decomposer')
    subparsers.add_parser('e', help='[e] extractor')
    subparsers.add_parser('f', help='[f] fixer: rename tensor')
    subparsers.add_parser('g', help='[g] group: component extractor')
    args = parser.parse_args()
    if args.subcommand == 'a':
        from gguf_connector import f
    if args.subcommand == 'b':
        from pig_gguf import b
    if args.subcommand == 'c':
        from gguf_connector import r2
    if args.subcommand == 'd':
        from pig_gguf import d
    if args.subcommand == 'e':
        from pig_gguf import e
    if args.subcommand == 'f':
        from pig_gguf import f
    if args.subcommand == 'g':
        from gguf_connector import e3