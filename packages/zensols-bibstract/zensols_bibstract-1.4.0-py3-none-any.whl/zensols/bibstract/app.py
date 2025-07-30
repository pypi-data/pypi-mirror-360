"""This utility extracts Bib(La)Tex references (a.k.a *markers*) from a
(La)TeX project.

"""
__author__ = 'Paul Landes'

from typing import Dict, Set
from dataclasses import dataclass, field
import logging
from pathlib import Path
from zensols.config import ConfigFactory
from . import Extractor, ConverterLibrary, PackageFinder

logger = logging.getLogger(__name__)


@dataclass
class Application(object):
    """This utility extracts Bib(La)Tex references from a (La)Tex.

    """
    config_factory: ConfigFactory = field()
    """The configuration factory used to create this instance."""

    converter_library: ConverterLibrary = field()
    """The converter library used to print what's available."""

    log_name: str = field()
    """The name of the package logger."""

    def _get_extractor(self, texpath: str) -> Extractor:
        return self.config_factory.new_instance(
            'bib_extractor', texpaths=texpath)

    def _get_package_finder(self, texpath: str, package_regex: str,
                            library_dir: str, inverse: bool = False) -> \
            PackageFinder:
        return self.config_factory.new_instance(
            'bib_package_finder',
            texpaths=texpath,
            package_regex=package_regex,
            library_dirs=library_dir,
            inverse=inverse)

    def converters(self):
        """List converters and their information."""
        self.converter_library.write()

    def print_bibtex_ids(self):
        """Print BibTex citation keys."""
        extractor = self._get_extractor()
        extractor.print_bibtex_ids()

    def print_texfile_refs(self, texpath: Path):
        """Print citation references.

        :param texpath: either a file or directory to recursively scan for
                        files with LaTex citation references

        """
        extractor = self.get_extractor(texpath)
        extractor.print_texfile_refs()

    def print_extracted_ids(self, texpath: Path):
        """Print BibTex export citation keys.

        :param texpath: either a file or directory to recursively scan for
                        files with LaTex citation references

        """
        extractor = self.get_extractor(texpath)
        extractor.print_extracted_ids()

    def print_entry(self, citation_key: str):
        """Print a single BibTex entry as it would be given in the output.

        :param citation_key: the citation key of entry to print out

        """
        extractor = self._get_extractor()
        entry: Dict[str, Dict[str, str]] = extractor.get_entry(citation_key)
        extractor.write_entry(entry)

    def export(self, texpath: str, output: Path = None):
        """Export the derived BibTex file.

        :param texpath: a path separated (':' on Linux) list of files or
                         directories to export

        :param output: the output path name, or standard out if not given

        """
        extractor = self._get_extractor(texpath)
        if output is None:
            extractor.extract()
        else:
            with open(output, 'w') as f:
                extractor.extract(writer=f)

    def package(self, texpath: str, libpath: str = None,
                package_regex: str = None, no_extension: bool = False,
                inverse: bool = False):
        """Return a list of all packages.

        :param texpath: a path separated (':' on Linux) list of files or
                        directories to export

        :param libpath: a path separated (':' on Linux) list of files or
                        directories of libraries to not include in results

        :param package_regex: the regular expression used to filter packages

        :param no_extension: do not add the .sty extension

        """
        pkg_finder: PackageFinder = self._get_package_finder(
            texpath, package_regex, library_dir=libpath, inverse=inverse)
        pkgs: Set[str] = pkg_finder.get_packages()
        pkgs = sorted(pkgs)
        if not no_extension:
            pkgs = tuple(map(lambda s: f'{s}.sty', pkgs))
        print('\n'.join(pkgs))
