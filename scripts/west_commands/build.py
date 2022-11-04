#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path

from west.configuration import config
from west.commands import WestCommand


BUILD_DESCRIPTION = ""


class Build(WestCommand):
    def __init__(self):
        super(Build, self).__init__('build', 'compile an application', BUILD_DESCRIPTION, accepts_unknown_args=True)
        self.source_dir = None
        self.build_dir = None

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
            usage="Build stuff"
        )

        parser.add_argument('-s', '--source-dir')
        parser.add_argument('-d', '--build-dir')

        return parser

    def do_run(self, args, remainder):
        self.args = args

        self.dbg(f'Running build {args} -- {remainder}')

        self.source_dir = Path(args.source_dir) if args.source_dir else self._get_project_root_directory()
        self.build_dir = Path(args.build_dir)   if args.build_dir  else self.source_dir / 'build'

        # Make sure source directory exists and contain a meson.build file
        self._path_exists_or_die(self.source_dir / 'meson.build')

        self.inf(f'Setting up build..')
        self.inf(f'Source: {self.source_dir}')
        self.inf(f'Build: {self.build_dir}')

        if not self.build_dir.exists():
            stdout = self._meson_setup(self.build_dir)
            self.inf(stdout)

        stdout = self._meson_compile(self.build_dir)
        self.inf(stdout)

    def _meson_compile(self, build_dir: Path):
        return subprocess.run(['meson', 'compile', '-C', self.build_dir],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding=sys.getdefaultencoding(),
                              check=False).stdout.strip()

    def _meson_setup(self, build_dir: Path):
        args = ['meson', 'setup', build_dir]
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
