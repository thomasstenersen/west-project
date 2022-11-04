#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path

from west.configuration import config
from west.commands import WestCommand


TEST_DESCRIPTION = ""


class Test(WestCommand):
    def __init__(self):
        super(Test, self).__init__('test', 'run tests', TEST_DESCRIPTION, accepts_unknown_args=True)
        self.source_dir = None
        self.test_dir = None

        # Next release of West wil deprecate the `self.dbg|inf|err..` attribute
        if not hasattr(self, 'dbg'):
            from west import log
            self.dbg = log.dbg
            self.inf = log.inf
            self.err = log.err
            self.die = log.die

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(
            self.name,
            help=self.help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=self.description,
            usage=""
        )

        parser.add_argument('-d', '--build-dir')

        return parser

    def do_run(self, args, remainder):
        self.args = args

        self.dbg(f'running tests')

        self.source_dir = self._get_project_root_directory()
        self.build_dir = Path(args.build_dir) if args.build_dir  else self.source_dir / 'build'

        self.inf(f'running tests..')

        stdout = self._meson_test(self.build_dir)
        self.inf(stdout)

    def _meson_test(self, build_dir: Path):
        args = ['meson', 'test', '-v', '-C', self.build_dir]
        self.inf(f'Running {args}')
        return subprocess.run(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding=sys.getdefaultencoding(),
                              check=False).stdout.strip()

    def _get_project_root_directory(self) -> Path:
        return Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                   encoding=sys.getdefaultencoding(),
                                   stdout=subprocess.PIPE,
                                   check=True).stdout.strip())

    def _path_exists_or_die(self, path: Path):
        if not path.exists():
            self.die(f'Path {path} does not exist')
