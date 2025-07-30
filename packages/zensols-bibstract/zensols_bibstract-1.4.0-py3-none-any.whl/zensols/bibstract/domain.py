"""Domain and utility classes.

"""
__author__ = 'Paul Landes'

from typing import Set, Dict, List, Tuple, Sequence, Union, Iterable
from dataclasses import dataclass, field
import os
import logging
import sys
import itertools as it
from pathlib import Path
from io import TextIOBase
import re
from zensols.persist import persisted
from zensols.config import Writable, ConfigFactory
from zensols.introspect import ClassImporter, ClassInspector, Class
from zensols.cli import ApplicationError

logger = logging.getLogger(__name__)


class BibstractError(ApplicationError):
    """Application level error."""
    pass


@dataclass
class TexPathIterator(object):
    """Base class that finds LaTeX files (``.tex``, ``.sty``, etc).

    """
    TEX_FILE_REGEX = re.compile(r'.+\.(?:tex|sty|cls)$')

    texpaths: Union[str, Path, Sequence[Path]] = field()
    """Either a file or directory to recursively scan for files with LaTex citation
    references.

    """
    def __post_init__(self):
        self.texpaths = self._to_path_seq(self.texpaths)

    def _to_path_seq(self, path_thing: Union[str, Path, Sequence[Path]]) -> \
            Sequence[Path]:
        """Create a path sequence from a string, path or sequence of paths."""
        if path_thing is None:
            path_thing = ()
        if isinstance(path_thing, Path):
            path_thing = (path_thing,)
        elif isinstance(path_thing, str):
            path_thing = tuple(map(Path, path_thing.split(os.pathsep)))
        return path_thing

    def _iterate_path(self, par: Path) -> Iterable[Path]:
        """Recursively find LaTeX files."""
        childs: Iterable[Path]
        if par.is_file():
            childs = (par,)
        elif par.is_dir():
            childs = it.chain.from_iterable(
                map(self._iterate_path, par.iterdir()))
        else:
            childs = ()
            logger.warning(f'unknown file type: {par}--skipping')
        return childs

    def _get_tex_paths(self, paths: Sequence[Path] = None) -> Iterable[Path]:
        """Recursively find LaTeX files in all directories/files in ``paths``.

        """
        paths = self.texpaths if paths is None else paths
        files = it.chain.from_iterable(map(self._iterate_path, paths))
        return filter(self._is_tex_file, files)

    def _is_tex_file(self, path: Path) -> bool:
        """Return whether or not path is a file that might contain citation references.

        """
        return path.is_file() and \
            self.TEX_FILE_REGEX.match(path.name) is not None


@dataclass
class RegexFileParser(object):
    """Finds all instances of the citation references in a file.

    """
    REF_REGEX = re.compile(r'\\cite\{(.+?)\}|\{([a-zA-Z0-9,-]+?)\}')
    """The default regular expression used to find citation references in sty and
    tex files (i.e. ``\\cite`` commands).

    """
    MULTI_REF_REGEX = re.compile(r'[^,\s]+')
    """The regular expression used to find comma separated lists of citations
    commands (i.e. ``\\cite``).

    """
    pattern: re.Pattern = field(default=REF_REGEX)
    """The regular expression pattern used to find the references."""

    collector: Set[str] = field(default_factory=set)
    """The set to add found references."""

    def find(self, fileobj: TextIOBase):
        def map_match(t: Union[str, Tuple[str, str]]) -> Iterable[str]:
            if not isinstance(t, str):
                t = t[0] if len(t[0]) > 0 else t[1]
            return filter(lambda s: not s.startswith('\\'),
                          re.findall(self.MULTI_REF_REGEX, t))

        for line in fileobj.readlines():
            refs: List[Tuple[str, str]] = self.pattern.findall(line)
            refs = it.chain.from_iterable(map(map_match, refs))
            self.collector.update(refs)


@dataclass
class Converter(object):
    """A base class to convert fields of a BibTex entry (which is of type ``dict``)
    to another field.

    Subclasses should override :meth:`_convert`.

    """
    ENTRY_TYPE = 'ENTRYTYPE'

    name: str = field()
    """The name of the converter."""

    def convert(self, entry: Dict[str, str]) -> Dict[str, str]:
        """Convert and return a new entry.

        :param entry: the source data to transform

        :return: a new instance of a ``dict`` with the transformed data
        """
        entry = dict(entry)
        self._convert(entry)
        return entry

    def _convert(self, entry: Dict[str, str]):
        """The templated method subclasses should extend.  The default base class
        implementation is to return what's given as an identity mapping.

        """
        return entry

    def __str__(self) -> str:
        return f'converter: {self.name}'


@dataclass
class DestructiveConverter(Converter):
    """A converter that can optionally remove or modify entries.

    """
    destructive: bool = field(default=False)
    """If true, remove the original field if converting from one key to another in
    the Bibtex entry.

    """


@dataclass
class ConverterLibrary(Writable):
    config_factory: ConfigFactory = field()
    """The configuration factory used to create the converters."""

    converter_class_names: List[str] = field()
    """The list of converter class names currently available."""

    converter_names: List[str] = field(default=None)
    """A list of converter names used to convert to BibTex entries."""

    def __post_init__(self):
        self.converter_names = list(filter(
            lambda x: x != 'identity', self.converter_names))
        self._unregistered = {}

    def _create_converter(self, name: str) -> Converter:
        conv = self.config_factory(f'{name}_converter')
        conv.name = name
        return conv

    @property
    @persisted('_converters')
    def converters(self) -> Tuple[Converter]:
        return tuple(map(self._create_converter, self.converter_names))

    @property
    @persisted('_by_name')
    def converters_by_name(self) -> Dict[str, Converter]:
        convs = self.converters
        return {c.name: c for c in convs}

    def __getitem__(self, key: str):
        conv = self.converters_by_name.get(key)
        if conv is None:
            conv = self._unregistered.get(key)
            if conv is None:
                conv = self._create_converter(key)
                self._unregistered[key] = conv
        if conv is None:
            raise BibstractError(f'No such converter: {key}')
        return conv

    def write(self, depth: int = 0, writer: TextIOBase = sys.stdout,
              markdown_depth: int = 1):
        for cname in self.converter_class_names:
            cls = ClassImporter(cname).get_class()
            inspector = ClassInspector(cls)
            mcls: Class = inspector.get_class()
            header = '#' * markdown_depth
            self._write_line(f'{header} Converter {cls.NAME}', depth, writer)
            writer.write('\n')
            self._write_line(mcls.doc.text, depth, writer)
            writer.write('\n\n')
