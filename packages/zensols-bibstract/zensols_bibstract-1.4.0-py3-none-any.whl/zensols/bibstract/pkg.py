"""Find packages used in the tex path.

"""
__author__ = 'Paul Landes'

from typing import Set, Union, Iterable, Sequence
from dataclasses import dataclass, field
import logging
import re
from pathlib import Path
from . import TexPathIterator, RegexFileParser

logger = logging.getLogger(__name__)


@dataclass
class PackageFinder(TexPathIterator):
    """Find packages used in the tex path.

    """
    package_regex: Union[str, re.Pattern] = field(default=re.compile(r'.*'))
    """The regular expression used to filter what to return."""

    library_dirs: Union[str, Path, Sequence[Path]] = field(default=None)
    """The list of library paths.  Each path is not traversed to find packages.

    """
    inverse: bool = field(default=False)
    """Whether to invert the packages with all those packages found in
    :obj:`library_dirs`.

    """
    def __post_init__(self):
        super().__post_init__()
        self.library_dirs = set(self._to_path_seq(self.library_dirs))
        if isinstance(self.package_regex, str):
            self.package_regex = re.compile(self.package_regex)

    def _get_tex_paths(self) -> Iterable[Path]:
        paths = super()._get_tex_paths()
        paths = filter(lambda p: p.parent not in self.library_dirs, paths)
        return paths

    def _get_use_packages(self) -> Set[str]:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'finding packages in {self.texpaths}')
        pattern: re.Pattern = re.compile(r'\\usepackage{([a-zA-Z0-9,-]+?)\}')
        parser = RegexFileParser(pattern=pattern)
        path: Path
        for path in self._get_tex_paths():
            with open(path) as f:
                parser.find(f)
        return parser.collector

    def get_packages(self) -> Set[str]:
        pks: Set[str] = self._get_use_packages()
        if self.package_regex is not None:
            pks = set(filter(
                lambda s: self.package_regex.match(s) is not None, pks))
        if self.inverse:
            lps = super()._get_tex_paths(self.library_dirs)
            lps = set(map(lambda p: p.stem, lps))
            pks = lps - pks
        return pks
