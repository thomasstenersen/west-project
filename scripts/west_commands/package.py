#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path
import yaml

from west.configuration import config
from west.commands import WestCommand


PACKAGE_DESCRIPTION = ""


class Package(WestCommand):
    def __init__(self):
        super(Package, self).__init__('package', 'compile an application', PACKAGE_DESCRIPTION, accepts_unknown_args=True)
        self.source_dir = None
        self.build_dir = None
        self.package_config_path = None
        self.package_config = None

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
            usage="Package"
        )

        parser.add_argument('-c', '--config')
        parser.add_argument('-d', '--build-dir')
        parser.add_argument('-o', '--output-file', required=True)
        return parser

    def do_run(self, args, remainder):
        self.args = args

        self.source_dir = self._get_project_root_directory()
        self.build_dir = Path(args.build_dir) if args.build_dir  else self.source_dir / 'build'
        self.package_config_path = Path(args.config) if args.config else self.source_dir / 'package-config.yml'
        self.output_file = Path(args.output_file)

        self._path_exists_or_die(self.output_file.parent)
        self._path_exists_or_die(self.package_config_path)
        self._path_exists_or_die(self.build_dir)
        self.inf(f'Using configuration {self.package_config_path} in {self.build_dir}')

        self._load_package_config()

        paths_to_zip = {path.relative_to(os.getcwd()) for pattern in self._package_config['package-config']['input-patterns'] for path in self.build_dir.rglob(pattern)}

        self._create_package(paths_to_zip)

    def _create_package(self, paths_to_zip):
        stdout = subprocess.run(['zip', self.output_file] + list(paths_to_zip),
                                encoding=sys.getdefaultencoding(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                check=True).stdout.strip()

    def _load_package_config(self):
        with open(self.package_config_path, 'r') as config_fd:
            self._package_config = yaml.load(config_fd, Loader=yaml.SafeLoader)

        self.inf(f'{self._package_config}')

    def _get_project_root_directory(self) -> Path:
        return Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                   encoding=sys.getdefaultencoding(),
                                   stdout=subprocess.PIPE,
                                   check=True).stdout.strip())

    def _path_exists_or_die(self, path: Path):
        if not path.exists():
            self.die(f'Path {path} does not exist')
