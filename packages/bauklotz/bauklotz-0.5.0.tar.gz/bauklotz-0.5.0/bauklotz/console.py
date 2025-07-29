from argparse import ArgumentParser, BooleanOptionalAction
from functools import partial
from pathlib import Path

from bauklotz.business.pipe import Pipe
from bauklotz.business.pipe.graph import GraphPipe
from bauklotz.configuration.catalog.builtin import BuiltinCatalog
from bauklotz.configuration.dsl.parser import MortarParser
from bauklotz.configuration.dsl.tokenizer import MortarTokenizer
from bauklotz.reporting.item.python.project import PythonProjectLocation
from bauklotz.reporting.logging import DEFAULT_LOGGER


def main():
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("config", type=Path, help='Bauklotz configuration file')
    parser.add_argument("project", type=Path, help='Project to process')
    parser.add_argument("channel", nargs='+', help='Input channels to use', action='extend')
    parser.add_argument("--extension", action='append', help='Contrib modules to consider', default=[])
    parser.add_argument("-config-relative-paths", action=BooleanOptionalAction, default=True)
    args = parser.parse_args()
    print(args)
    with open(args.config, encoding='utf-8') as src:
        mortar_script = src.read()
    relative_path: Path = args.config.parent if args.config_relative_paths else Path()
    create_pipe = partial(GraphPipe, DEFAULT_LOGGER)
    pipe: Pipe = MortarParser(MortarTokenizer(mortar_script).tokenize(), BuiltinCatalog(args.extension), create_pipe, relative_path).parse()
    pipe.visualize('pipe')
    item: PythonProjectLocation = PythonProjectLocation(args.project)
    for channel in args.channel:
        pipe.inject(item, channel)
    pipe.close()



