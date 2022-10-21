import argparse
import copy
import os
import re
import sys
import textwrap
import warnings
from collections import defaultdict

import click
import packaging.specifiers
import packaging.version
import prettytable
import yaml
from jinja2 import BaseLoader
from jinja2 import Environment
from packaging.version import _cmpkey
from packaging.version import Version

from ._version import version

_MinInf = Version("0")
_MinInf._key = _cmpkey(
    epoch=-sys.maxsize, release=(-sys.maxsize,), pre=None, post=None, dev=None, local=None
)

_PlusInf = Version("999999999999")
_PlusInf._key = _cmpkey(
    epoch=+sys.maxsize, release=(+sys.maxsize,), pre=None, post=None, dev=None, local=None
)


class VersionRange:
    """
    Specify the most restrictive version range.

    *   Modification of properties only leads to a change if the new value is more restrictive.
        For example::

            >>> vr = VersionRange(less="2.0")
            >>> vr.less_equal = "1.0"
            >>> print(vr)
            "<=1.0"

        while::

            >>> vr = VersionRange(less="2.0")
            >>> vr.less_equal = "3.0"
            >>> print(vr)
            "<2.0"

    *   Merging two ranges to the most restrictive is done using ``+``::

            >>> a = VersionRange(less="2.0")
            >>> b = VersionRange(greater="1.0")
            >>> print(a + b)
            ">1.0, <2.0"
    """

    def __init__(
        self,
        equal: str = None,
        less: str = None,
        less_equal: str = None,
        greater: str = None,
        greater_equal: str = None,
    ):

        self._eq = _PlusInf
        self._lt = _PlusInf
        self._le = _PlusInf
        self._gt = _MinInf
        self._ge = _MinInf

        self.eq = None
        self.lt = None
        self.le = None
        self.gt = None
        self.ge = None

        self.less = less
        self.less_equal = less_equal
        self.greater = greater
        self.greater_equal = greater_equal

        if equal:
            self.equal = equal

    @property
    def equal(self):
        return self.eq

    @property
    def less(self):
        return self.lt

    @property
    def less_equal(self):
        return self.lt

    @property
    def greater(self):
        return self.gt

    @property
    def greater_equal(self):
        return self.gt

    @equal.setter
    def equal(self, value: str):

        if not value:
            self.eq = None
            self._eq = _PlusInf
            return

        self.set_equal(value, packaging.version.parse(value))

    @less.setter
    def less(self, value: str):

        if not value:
            self.lt = None
            self._lt = _PlusInf
            return

        self.set_less(value, packaging.version.parse(value))

    @less_equal.setter
    def less_equal(self, value: str):

        if not value:
            self.le = None
            self._le = _PlusInf
            return

        self.set_less_equal(value, packaging.version.parse(value))

    @greater.setter
    def greater(self, value: str):

        if not value:
            self.gt = None
            self._gt = _MinInf
            return

        self.set_greater(value, packaging.version.parse(value))

    @greater_equal.setter
    def greater_equal(self, value: str):

        if not value:
            self.ge = None
            self._ge = _MinInf
            return

        self.set_greater_equal(value, packaging.version.parse(value))

    def set_equal(self, value: str, parsed: Version, force: bool = True):

        if self.eq:
            if parsed != self._eq:
                raise ValueError("Can't set equal to two different values")
            if not force:
                if len(self.eq) > len(value):
                    return

        self.eq = value
        self._eq = parsed

        if self._eq >= self._lt:
            raise ValueError(f"Version clash: ={value}")

        if self._eq > self._le:
            raise ValueError(f"Version clash: ={value}")

        if self._eq <= self._gt:
            raise ValueError(f"Version clash: ={value}")

        if self._eq < self._ge:
            raise ValueError(f"Version clash: ={value}")

        self.less = None
        self.less_equal = None
        self.greater = None
        self.greater_equal = None

    def set_less(self, value: str, parsed: Version, force: bool = True):

        if self.eq:
            if parsed > self._eq:
                return
            else:
                raise ValueError(f"Version clash: <{value}")

        if self.lt and self._lt == parsed and not force:
            if len(self.lt) > len(value):
                return
            else:
                self.lt = value
                self._lt = parsed
                return

        if parsed >= self._lt:
            return

        if parsed <= self._le:
            self.lt = value
            self._lt = parsed
            self.less_equal = None

        if parsed <= self._gt:
            raise ValueError(f"Version clash: <{value}")

        if parsed <= self._ge:
            raise ValueError(f"Version clash: <={value}")

    def set_less_equal(self, value: str, parsed: Version, force: bool = True):

        if self.eq:
            if parsed >= self._eq:
                return
            else:
                raise ValueError(f"Version clash: <={value}")

        if self.le and self._le == parsed and not force:
            if len(self.le) > len(value):
                return
            else:
                self.le = value
                self._le = parsed
                return

        if parsed > self._le:
            return

        if parsed < self._lt:
            self.le = value
            self._le = parsed
            self.less = None

        if parsed <= self._gt:
            raise ValueError(f"Version clash: <{value}")

        if parsed < self._ge:
            raise ValueError(f"Version clash: <={value}")

        if self._le == self._ge:
            self.set_equal(value, parsed)

    def set_greater(self, value: str, parsed: Version, force: bool = True):

        if self.eq:
            if parsed < self._eq:
                return
            else:
                raise ValueError(f"Version clash: <{value}")

        if self.gt and self._gt == parsed and not force:
            if len(self.gt) > len(value):
                return
            else:
                self.gt = value
                self._gt = parsed
                return

        if parsed <= self._gt:
            return

        if parsed >= self._ge:
            self.gt = value
            self._gt = parsed
            self.greater_equal = None

        if parsed >= self._lt:
            raise ValueError(f"Version clash: >{value}")

        if parsed >= self._le:
            raise ValueError(f"Version clash: >={value}")

    def set_greater_equal(self, value: str, parsed: Version, force: bool = True):

        if self.eq:
            if parsed <= self._eq:
                return
            else:
                raise ValueError(f"Version clash: <={value}")

        if self.ge and self._ge == parsed and not force:
            if len(self.ge) > len(value):
                return
            else:
                self.ge = value
                self._ge = parsed
                return

        if parsed <= self._ge:
            return

        if parsed > self._gt:
            self.ge = value
            self._ge = parsed
            self.greater = None

        if parsed >= self._lt:
            raise ValueError(f"Version clash: >{value}")

        if parsed > self._le:
            raise ValueError(f"Version clash: >={value}")

        if self._le == self._ge:
            self.set_equal(value, parsed)

    def set(self, cmp: str, value: str = None):

        if cmp == "=":
            self.equal = value
        elif cmp == "<":
            self.less = value
        elif cmp == "<=":
            self.less_equal = value
        elif cmp == ">":
            self.greater = value
        elif cmp == ">=":
            self.greater_equal = value
        elif cmp == "==":
            self.equal = value
        else:
            raise ValueError(f"Unknown comparator: {cmp}")

    def __eq__(self, other) -> bool:
        return all(
            [
                self.eq == other.eq,
                self.lt == other.lt,
                self.le == other.le,
                self.gt == other.gt,
                self.ge == other.ge,
            ]
        )

    def same(self, other) -> bool:
        """
        Return True if the two VersionSpecs point to the same range,
        ignoring the string representation.
        """
        return all(
            [
                self._eq == other._eq,
                self._lt == other._lt,
                self._le == other._le,
                self._gt == other._gt,
                self._ge == other._ge,
            ]
        )

    def isempty(self) -> bool:
        return not any([self.eq, self.lt, self.le, self.gt, self.ge])

    def __str__(self) -> str:
        ret = []
        if self.eq:
            ret.append("==" + self.eq)
        if self.gt:
            ret.append(">" + self.gt)
        if self.ge:
            ret.append(">=" + self.ge)
        if self.lt:
            ret.append("<" + self.lt)
        if self.le:
            ret.append("<=" + self.le)
        return ", ".join(ret)

    def __repr__(self) -> str:
        return str(self)

    def __iadd__(self, other):
        return _mymerge(self, other)

    def __add__(self, other):
        return _mymerge(self, other)

    def __concat__(self, other):
        return _mymerge(self, other)

    def __contains__(self, other):

        if self == other:
            return True

        if self.eq:
            if other.eq:
                return self.eq == other.eq
            return False

        if other.eq:
            if other._eq >= self._lt:
                return False
            if other._eq > self._le:
                return False
            if other._eq <= self._gt:
                return False
            if other._eq < self._ge:
                return False
            return True

        if other._lt > self._le and other.lt:
            return False
        if other._le >= self._lt and other.le:
            return False
        if other._ge <= self._gt and other.ge:
            return False
        if other._gt < self._ge and other.gt:
            return False

        if (self.ge or self.gt) and (self.lt or self.le):
            if not (other.ge or other.gt) and (other.lt or other.le):
                return False

        lt = other._lt
        le = other._le
        gt = other._gt
        ge = other._ge

        if not other.lt:
            lt = _MinInf
        if not other.le:
            le = _MinInf
        if not other.gt:
            gt = _PlusInf
        if not other.ge:
            ge = _PlusInf

        if gt < self._gt:
            return False
        if ge < self._ge:
            return False
        if lt > self._lt:
            return False
        if le > self._le:
            return False

        if any([self.lt, self.le, self.gt, self.ge]):
            if not any([other.lt, other.le, other.gt, other.ge]):
                return False

        return True


def _mymerge(a: VersionRange, b: VersionRange) -> VersionRange:

    if a.isempty():
        return b

    if b.isempty():
        return a

    if a._lt < b._lt and a._le < b._le and a._gt > b._gt and a._ge > b._ge:
        return a

    elif b._lt < a._lt and b._le < a._le and b._gt > a._gt and b._ge > a._ge:
        return b

    if a.eq and b.eq:
        if a._eq == b._eq:
            return a
        else:
            raise ValueError(f"Version clash: ={a.eq} and ={b.eq}")

    ret = copy.deepcopy(a)

    if b.lt:
        ret.set_less(b.lt, b._lt, False)
    if b.le:
        ret.set_less_equal(b.le, b._le, False)
    if b.gt:
        ret.set_greater(b.gt, b._gt, False)
    if b.ge:
        ret.set_greater_equal(b.ge, b._ge, False)
    if b.eq:
        ret.set_equal(b.eq, b._eq, False)

    return ret


def _interpret(dependency: str) -> dict:
    """
    Interpret a version string.

    :param dependency: Dependency specifier.
    :return: Dictionary with keys 'name', 'range', and optionally 'wildcard', 'build'.
    """

    if dependency is None:
        return {}

    dep = dependency

    if "#" in dep:
        dep, comment = dep.split("#", 1)
        warnings.warn(f"Comment '{comment}' ignored.", Warning)

    # foo ==1.0

    if re.match(r"^([^=^<^>^\s]*)(\s*)(==)(.*)$", dep):

        _, name, _, eq, version, _ = re.split(r"^([^=^<^>^\s]*)(\s*)(==)(.*)$", dep)

        if "=" in version:
            raise ValueError(f"Invalid build specifier '{dep}'.")

        return {
            "name": name,
            "wildcard": eq + version,
            "range": VersionRange(equal=version),
        }

    # foo =1.0=abc

    if re.match(r"^([^=^<^>^\s]*)(\s*)([=]+)([^=^<^>^\s]*)(\s*)([=]+)(.*)$", dep):

        _, name, _, eq, version, _, eq2, build, _ = re.split(
            r"^([^=^<^>^\s]*)(\s*)([=]+)([^=^<^>^\s]*)(\s*)([=]+)(.*)$", dep
        )

        if eq != "=":
            raise ValueError(f"Invalid version specification '{dep}'.")

        if eq2 != "=":
            raise ValueError(f"Invalid build specifier '{dep}'.")

        return {"name": name, "build": build, "range": VersionRange(equal=version)}

    # foo =1.0.*

    if re.match(r"^([^=^\s]*)(\s*)([=]+)([^\*]*)(\*)$", dep):

        _, name, _, eq, basename, wildcard, _ = re.split(
            r"^([^=^\s]*)(\s*)([=]*)([^\*]*)(\*)$", dep
        )

        if eq != "=":
            raise ValueError(f"Invalid wildcard dependency '{dep}'.")

        if len(basename.split(".")) == 0:
            lower = basename
            upper = f"{int(lower) + 1}"
        else:
            lower = basename.rstrip(".")
            if len(lower.split(".")) == 1:
                upper = f"{int(lower) + 1}"
                if basename[-1] == ".":
                    upper += ".0"
            else:
                base, minor = lower.rsplit(".", 1)
                upper = f"{base}.{int(minor) + 1}.0"

        if len(lower) == 0:
            lower = "0"
        else:
            lower = f"{lower}.0"

        return {
            "name": name,
            "wildcard": eq + basename + wildcard,
            "range": VersionRange(greater_equal=lower, less=upper),
        }

    # foo =1.0

    if re.match(r"^([^=^<^>^\s]*)(\s*)([=]+)([^=^<^>^\s]*)$", dep):

        _, name, _, eq, basename, _ = re.split(r"^([^=^\s]*)(\s*)([=]+)(.*)$", dep)

        if eq != "=":
            raise ValueError(f"Invalid version specification '{dep}'.")

        if len(basename.split(".")) == 0:
            lower = basename
            upper = f"{int(lower) + 1}"
        else:
            lower = basename.rstrip(".")
            if len(lower.split(".")) == 1:
                upper = f"{int(lower) + 1}"
                if basename[-1] == ".":
                    upper += ".0"
            else:
                base, minor = lower.rsplit(".", 1)
                upper = f"{base}.{int(minor) + 1}.0"

        if len(lower) == 0:
            lower = "0"
        else:
            lower = f"{lower}.0"

        return {
            "name": name,
            "wildcard": eq + basename,
            "range": VersionRange(greater_equal=lower, less=upper),
        }

    # foo *

    if re.match(r"^([^\*^\s]*)(\s*)(\*)$", dep):
        _, name, _, wildcard, _ = re.split(r"^([^\*^\s]*)(\s*)(\*)$", dep)
        return {"name": name, "wildcard": wildcard, "range": VersionRange()}

    # foo
    # foo =1.0
    # foo >1.0
    # foo >=1.0
    # foo <1.0
    # foo <=1.0
    # foo >1.0, <2.0
    # foo >=1.0, <2.0
    # foo >1.0, <=2.0
    # foo >=1.0, <=2.0

    _, name, _, eq, ver, _ = re.split(r"^([^>^<^=^\s]*)(\s*)([<>=]*)(.*)$", dep)
    eq2 = None
    ver2 = None
    sp = re.split(r"^([^,]*)(,)(\s*)([<>=]*)(.*)$", ver)
    if len(sp) > 1:
        _, ver, _, _, eq2, ver2, _ = sp

    ret = {"name": name, "range": VersionRange()}

    if eq == "=" and eq2:
        raise ValueError(f"Cannot have two equalities in '{dep}'")
    if eq in [">=", ">"] and eq2 in [">=", ">"]:
        raise ValueError(f"Illegal bound in '{dep}'")

    for e, v in [(eq, ver), (eq2, ver2)]:
        if not e:
            if v:
                raise ValueError(f"Missing equality in '{dep}'")
            continue
        ret["range"].set(e, v)

    return ret


def _merge_property(a, b):
    if a is None:
        return b
    if b is None:
        return a
    assert a == b
    return a


class PackageSpecifier:
    """
    Interpret a package specifier, e.g.::

        foo
        foo *
        foo =1.*
        for >1.0
        for <2.0
        for >=1.0
        for <=1.0
        foo >=1.0, <2.0

    To combine multiple specifiers in the most restrictive one::

        >>> print(PackageSpecifier("foo") + PackageSpecifier("foo >1.0, <2.0"))
        "foo >1.0, <2.0"

        >>> print(PackageSpecifier("foo =1.*") + PackageSpecifier("foo >1.0, <2.0"))
        "foo >1.0, <2.0"

        >>> print(PackageSpecifier("foo =1.*") + PackageSpecifier("foo"))
        "foo *"
    """

    def __init__(self, interpret: str = None):

        self.name = None
        self.wildcard = None
        self.build = None
        self.range = VersionRange()

        if interpret is None:
            return
        elif type(interpret) == PackageSpecifier:
            self.name = interpret.name
            self.wildcard = interpret.wildcard
            self.build = interpret.build
            self.range = copy.deepcopy(interpret.range)
        else:
            data = _interpret(interpret)
            self.name = data.pop("name", None)
            self.wildcard = data.pop("wildcard", None)
            self.build = data.pop("build", None)
            self.range = data.pop("range", None)

    @property
    def version(self) -> str:
        """
        The version specification, e.g. ``=1.0``, ``=1.0.*``, ``>=1.0``, ``>=1.0, <2.0``.
        """
        if self.wildcard:
            return self.wildcard
        return str(self.range)

    @version.setter
    def version(self, value: str):
        self.data = _interpret(self.name + " " + value)

    def __eq__(self, other) -> bool:

        if type(other) == str:
            other = PackageSpecifier(other)

        return all(
            [
                self.name == other.name,
                self.wildcard == other.wildcard,
                self.build == other.build,
                self.range == other.range,
            ]
        )

    def __str__(self):
        if self.wildcard:
            return f"{self.name} {self.wildcard}"

        if self.build:
            return f"{self.name}={self.range.eq}={self.build}"

        if self.range.isempty():
            return self.name

        return f"{self.name} {self.range}".replace("==", "=")

    def __repr__(self) -> str:
        return str(self)

    def merge(self, other):
        if self.name is None:
            return other

        if self.name != other.name:
            raise ValueError(f"Cannot combine '{self.name}' with '{other.name}'")

        r = self.range + other.range

        if r == self.range and r == other.range:
            self.wildcard = _merge_property(self.wildcard, other.wildcard)
            self.build = _merge_property(self.build, other.build)
            return self

        if r.same(self.range) and r.same(other.range):
            self.wildcard = _merge_property(self.wildcard, other.wildcard)
            self.build = _merge_property(self.build, other.build)
            self.range = r
            return self

        if r == self.range:
            return self

        if r == other.range:
            return other

        self.wildcard = None
        self.build = None
        self.range = r
        return self

    def __iadd__(self, other):
        return self.merge(other)

    def __add__(self, other):
        return self.merge(other)

    def __concat__(self, other):
        return self.merge(other)

    def __contains__(self, other):

        if type(other) == str:
            other = PackageSpecifier(other)

        if self == other:
            return True

        if other.name != self.name:
            return False

        return other.range in self.range


def remove(dependencies: list[str], *args: list[str]) -> list[str]:
    """
    Remove dependencies.

    :param dependencies: List of dependencies.
    :param args: List of dependencies to remove (version specification is ignored).
    :return: List of dependencies.
    """

    ret = []
    rm = [PackageSpecifier(i).name for i in args]

    for dep in dependencies:
        if PackageSpecifier(dep).name not in rm:
            ret.append(dep)

    return ret


def unique(*args) -> list[PackageSpecifier]:
    """
    Return a list of 'unique' dependencies. If multiple dependencies with the same name are given,
    the most restrictive version specification is returned.

    :param args: Dependencies to merge.
    :return: List of unique dependencies (convert to strings: ``list(map(str, unique(*args)))``)
    """

    deps = defaultdict(PackageSpecifier)

    for dep in args:
        dep = PackageSpecifier(dep)
        deps[dep.name] += dep

    return [deps[key] for key in sorted(deps)]


def restrict(source, other: list[str] = None) -> list[PackageSpecifier]:
    """
    Restrict all dependencies in ``source`` to the most restrictive version specification in
    ``source`` and ``other``. All dependencies that are in ``other`` but not in ``source`` are
    ignored. In instead you want to integrate them, use :py:func:`unique`::

        merged = unique(*source, *other)

    :param source: List of dependencies.
    :param other: List of other dependencies.
    :return: List of dependencies.
    """

    restriction = defaultdict(PackageSpecifier)

    for dep in unique(*other):
        restriction[dep.name] += dep

    ret = [PackageSpecifier(i) for i in source]

    for i, dep in enumerate(ret):
        if dep.name in restriction:
            ret[i] += restriction[dep.name]

    return ret


def contains(requirements: list[PackageSpecifier], installed: list[PackageSpecifier]) -> bool:
    """
    Check if all dependencies in ``requirements`` are satisfied by ``installed``.

    :param requirements: List of requirements.
    :param installed: List of 'installed' dependencies.
    :return: True if all requirements are satisfied, False otherwise.
    """

    installed = {i.name: i for i in map(PackageSpecifier, installed)}

    for req in map(PackageSpecifier, requirements):
        if req.name not in installed:
            return False
        if installed[req.name] not in req:
            return False

    return True


def print_diff(
    a: list[PackageSpecifier], b: list[PackageSpecifier], silent: bool = False
) -> prettytable.PrettyTable:
    """
    Print differences between ``a`` and ``b``.

    :param a: List of dependencies.
    :param b: List of dependencies.
    :param silent: Do not print the table.
    :return: PrettyTable object.
    """

    a = {i.name: i for i in map(PackageSpecifier, a)}
    b = {i.name: i for i in map(PackageSpecifier, b)}
    out = prettytable.PrettyTable()
    out.field_names = ["a", "diff", "b"]
    out.align["a"] = "l"
    out.align["diff"] = "c"
    out.align["b"] = "l"
    out.header = False

    for key in a:
        if key not in b:
            out.add_row([str(a[key]), "->", ""])
            continue
        if a[key] not in b[key]:
            out.add_row([str(a[key]), "!=", str(b[key])])
            continue

    for key in b:
        if key not in a:
            out.add_row(["", "<-", str(b[key])])

    if not silent:
        print(out.get_string())

    return out


def condaforge_dependencies(
    text: str,
    name: str = None,
    flatten: bool = True,
    selectors: list[str] = [],
    target_platform: str = "myplatform",
) -> list[str]:
    """
    Get the dependencies from a conda-forge feedstock.

    :param name: Name of the recipe to select (use to select one of multi-outputs).
    :param flatten: Flatten the dependencies, otherwise keep as ``"host"``, ``"run"``, ``"build"``.
    :param selectors: List of selectors to keep (all non-selected selectors are removed).
    :param target_platform: Target platform to use to substitute ``{{ target_platform }}``.
    """

    data = text.replace("{{ compiler('c') }}", "c-compiler")
    data = data.replace("{{ compiler('cxx') }}", "cxx-compiler")
    data = data.replace('{{ compiler("c") }}', "c-compiler")
    data = data.replace('{{ compiler("cxx") }}', "cxx-compiler")
    rtemplate = Environment(loader=BaseLoader).from_string(data)
    data = rtemplate.render(target_platform=target_platform)

    data = data.split("\n")

    rm_selectors = [
        "x86",
        "x86_64",
        "linux",
        "linux32",
        "linux64",
        "armv6l",
        "armv7l",
        "aarch64",
        "ppc64le",
        "osx",
        "arm64",
        "unix",
        "win",
        "win32",
        "win64",
        "py",
        "py3k",
        "py2k",
        "py27",
        "py34",
        "py35",
        "py36",
        "np",
        "build_platform",
        "build_platform != target_platform",
    ]

    for selector in selectors:
        rm_selectors.remove(selector)

    for selector in rm_selectors:
        data = [i for i in data if not re.match(rf"(.*)(# \[{selector}\])(.*)", i)]

    data = yaml.load("\n".join(data), Loader=yaml.FullLoader)

    ret = {key: [] for key in ["host", "run", "build"]}

    if "outputs" in data:
        for sub in data["outputs"]:
            if not name or sub["name"] == name:
                for key in ["host", "run", "build"]:
                    if key in sub["requirements"]:
                        ret[key] = sub["requirements"][key]
    else:
        for key in ret:
            if key in data["requirements"]:
                ret[key] = data["requirements"][key]

    if flatten:
        out = []
        for key in ret:
            out += ret[key]
        return unique(*out)

    for key in ret:
        ret[key] = [PackageSpecifier(i) for i in ret[key]]

    return ret


def parse_file(*args: list[str]) -> dict:
    """
    Parse one or more files and return the raw result.

    :param args: List of filenames to parse.
    :return: Raw result: ``{"name": [...], "channels": [...], "dependencies": [...]}``
    """

    env = {"name": [], "channels": [], "dependencies": []}

    for filename in args:

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        with open(filename) as file:

            data = yaml.load(file.read(), Loader=yaml.FullLoader)

            for key, value in data.items():
                if key not in env:
                    raise ValueError(f"Unknown key '{key}' in '{filename}'.")
                if type(value) == str:
                    env[key].append(value)
                elif type(value) == list:
                    env[key] += value

    for key in ["channels", "name"]:
        if "channels" in env:
            env["channels"] = list(set(env["channels"]))

    if len(env["name"]) > 1:
        raise ValueError("Multiple 'name' keys.")
    if len(env["name"]) == 1:
        env["name"] = env["name"][0]
    else:
        del env["name"]

    if len(env["channels"]) == 0:
        del env["channels"]

    env["dependencies"] = [PackageSpecifier(i) for i in env["dependencies"]]

    return env


def _iterate_nested_dict(mydict: dict):
    for key, value in mydict.items():
        yield key, value
        if isinstance(value, dict):
            yield from _iterate_nested_dict(value)


def apply_selector(text: str) -> str:
    """
    Apply platform selector::

        sel(linux): ...
        sel(osx): ...
        sel(win): ...

    based on current platform.

    :param text: Package specifier with optional selector.
    :return: Package specifier. Returns ``None`` is excluded by selector.
    """

    if re.match(r"(\s*)(sel\(\w*\)\:)(.*)", text):
        _, _, _, plat, _, package, _ = re.split(r"(\s*)(sel\()(\w*)(\)\:\s*)(.*)", text)
        if (sys.platform == "linux" or sys.platform == "linux2") and plat == "linux":
            return package
        elif sys.platform == "darwin" and plat == "osx":
            return package
        elif sys.platform == "win32" and plat == "win":
            return package
        else:
            return None

    return text


def filter_selectors(deps: list[str]) -> list[str]:
    """
    Filter selectors from dependencies.

    :param deps: List of dependencies (text).
    :return: List of dependencies (text) without selectors, and dependencies excluded by selectors.
    """
    return [apply_selector(i) for i in deps if apply_selector(i)]


def parse_github_action(text: str) -> dict:
    """
    Parse a GitHub action.
    Currently very basic. Looks for the first occurrence of ``mamba-org/provision-with-micromamba``.

    :param filename: Filename to parse.
    :return: Raw result: ``{"name": [...], "channels": [...], "dependencies": [...]}``
    """

    if "mamba-org/provision-with-micromamba" in text:
        data = text.split("mamba-org/provision-with-micromamba")[1].split("with:")[1]
        data = data.split("\n")
        if len(data[0].strip()) == 0:
            data = data[1:]
        indent = len(re.split(r"(\s*)(.*)", data[0])[1])
        select = []
        for line in data:
            if len(re.split(r"(\s*)(.*)", line)[1]) < indent:
                break
            if re.match(r"(\s*)(-\s)(.*)", line):
                break
            select += [line]
        data = yaml.load("\n".join(select), Loader=yaml.FullLoader)

        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].split("\n")

        if "environment-file" in data:
            env = parse_file(*data["environment-file"])
        else:
            env = {"dependencies": []}
        if "environment-name" in data:
            env["name"] = data["environment-name"]

        if "extra-specs" in data:
            for deps in data["extra-specs"]:
                deps = apply_selector(deps)
                if deps:
                    env["dependencies"].append(deps)

        return env

    return {}


def _conda_envfile_parse_parser():
    """
    Return parser for :py:func:`conda_envfile_parse`.
    """

    desc = """
    Parse YAML environment files, formatted::

        name: ...
        channels:
        - ...
        - ...
        dependencies:
        - ...
        - ...
    """

    class MyFmt(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.MetavarTypeHelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(formatter_class=MyFmt, description=textwrap.dedent(desc))
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("files", type=str, nargs="*", help="Input files.")
    return parser


def conda_envfile_parse(args: list[str]):
    """
    Command-line tool, see ``--help``.

    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_parse_parser()
    args = parser.parse_args(args)

    for filename in args.files:
        env = parse_file(filename)
        env["dependencies"] = list(map(str, unique(*env["dependencies"])))
        with open(filename, "w") as file:
            yaml.dump(env, file)


def _conda_envfile_parse_cli():
    conda_envfile_parse(sys.argv[1:])


def _conda_envfile_merge_parser():
    """
    Return parser for :py:func:`conda_envfile_merge`.
    """

    desc = """
    Merge YAML environment files, formatted::

        name: ...
        channels:
        - ...
        - ...
        dependencies:
        - ...
        - ...
    """

    class MyFmt(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.MetavarTypeHelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(formatter_class=MyFmt, description=textwrap.dedent(desc))
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite output file.")
    parser.add_argument("-o", "--output", type=str, help="Write to output file.")
    parser.add_argument("-a", "--append", type=str, action="append", default=[], help="Append deps")
    parser.add_argument("-r", "--remove", type=str, action="append", default=[], help="Remove deps")
    parser.add_argument("--no-name", action="store_true", help="Remove name from output.")
    parser.add_argument(
        "--github-action",
        type=str,
        action="append",
        default=[],
        help="Interpret file as GitHub action",
    )
    parser.add_argument("files", type=str, nargs="*", help="Input file(s).")
    return parser


def conda_envfile_merge(args: list[str]):
    """
    Command-line tool, see ``--help``.

    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_merge_parser()
    args = parser.parse_args(args)
    env = parse_file(*args.files)

    if args.github_action:
        for filename in args.github_action:
            with open(filename) as file:
                extra = parse_github_action(file.read())
                for key in extra:
                    if key not in env:
                        env[key] = extra[key]
                    else:
                        env[key] += extra[key]

    env["dependencies"] = unique(*(env["dependencies"] + filter_selectors(args.append)))

    if args.remove:
        env["dependencies"] = remove(env["dependencies"], *filter_selectors(args.remove))

    env["dependencies"] = list(map(str, env["dependencies"]))

    for key in env:
        if key == "dependencies":
            continue
        if type(env[key]) == list:
            env[key] = list(set(env[key]))

    if args.no_name:
        env.pop("name", None)

    if not args.output:
        print(yaml.dump(env, default_flow_style=False, default_style="").strip())
        return 0

    dirname = os.path.dirname(args.output)

    if not args.force:
        if os.path.isfile(args.output):
            if not click.confirm(f'Overwrite "{args.output:s}"?'):
                raise OSError("Cancelled")
        elif not os.path.isdir(dirname) and len(dirname) > 0:
            if not click.confirm(f'Create "{os.path.dirname(args.output):s}"?'):
                raise OSError("Cancelled")

    if not os.path.isdir(dirname) and len(dirname) > 0:
        os.makedirs(os.path.dirname(args.output))

    with open(args.output, "w") as file:
        yaml.dump(env, file)


def _conda_envfile_merge_cli():
    conda_envfile_merge(sys.argv[1:])


def _conda_envfile_restrict_parser():
    """
    Return parser for :py:func:`conda_envfile_restrict`.
    """

    desc = """
    Restrict version of packages based on another YAML file. Example::

        conda_envfile_restrict source.yml env.yml ... > source_restricted.yml

    To check conda-forge feedstocks, use::

        conda_envfile_restrict --conda-forge meta.yml env.yml

    In this case, this function only checks and outputs a ``1`` return code if the feedstock
    is not restrictive enough. It does not print a formatted output of ``source``.
    """

    class MyFmt(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.MetavarTypeHelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(formatter_class=MyFmt, description=textwrap.dedent(desc))
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite output file.")
    parser.add_argument("-o", "--output", type=str, help="Write to output file.")
    parser.add_argument(
        "--conda-forge",
        type=str,
        action="append",
        help="Interpret the next file (``source`` or ``comparison``) as conda-forge feedstock.",
    )
    parser.add_argument("-a", "--append", type=str, action="append", default=[], help="Append deps")
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("source", type=str, nargs="?", help="Input file.")
    parser.add_argument("comparison", type=str, nargs="*", help="Comparison file(s).")
    return parser


def conda_envfile_restrict(args: list[str]):
    """
    Command-line tool, see ``--help``.

    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_restrict_parser()
    args = parser.parse_args(args)

    if len(args.conda_forge) > 0:
        other = []
        with open(args.conda_forge[0]) as file:
            source = unique(*condaforge_dependencies(file.read()))
        if args.source:
            other += parse_file(args.source)["dependencies"]
        for filename in args.comparison:
            other += parse_file(filename)["dependencies"]
        for filename in args.conda_forge[1:]:
            with open(filename) as file:
                other += condaforge_dependencies(file.read())
        ret = restrict(source, unique(*(other + filter_selectors(args.append))))
        if ret != source:
            print("Difference found")
            print("\n".join([i for i in ret if i not in source]))
            return 1
        else:
            return 0

    env = parse_file(args.source)

    other = []
    for filename in args.comparison:
        other += parse_file(filename)["dependencies"]

    env["dependencies"] = restrict(source, unique(*(other + filter_selectors(args.append))))
    env["dependencies"] = list(map(str, *env["dependencies"]))

    if not args.output:
        print(yaml.dump(env, default_flow_style=False, default_style="").strip())
        return 0

    dirname = os.path.dirname(args.output)

    if not args.force:
        if os.path.isfile(args.output):
            if not click.confirm(f'Overwrite "{args.output:s}"?'):
                raise OSError("Cancelled")
        elif not os.path.isdir(dirname) and len(dirname) > 0:
            if not click.confirm(f'Create "{os.path.dirname(args.output):s}"?'):
                raise OSError("Cancelled")

    if not os.path.isdir(dirname) and len(dirname) > 0:
        os.makedirs(os.path.dirname(args.output))

    with open(args.output, "w") as file:
        yaml.dump(env, file)


def _conda_envfile_restrict_cli():
    conda_envfile_restrict(sys.argv[1:])


def _conda_envfile_diff_parser():
    """
    Return parser for :py:func:`conda_envfile_diff`.
    """

    desc = """
    Print diff of two files.
    """

    class MyFmt(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.MetavarTypeHelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(formatter_class=MyFmt, description=textwrap.dedent(desc))
    parser.add_argument(
        "--conda-forge",
        type=str,
        action="append",
        default=[],
        help="Interpret the next file (``a`` or ``b``) as conda-forge feedstock.",
    )
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("files", type=str, nargs="*", help="Input files.")
    return parser


def conda_envfile_diff(args: list[str]):
    """
    Command-line tool, see ``--help``.

    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_diff_parser()
    args = parser.parse_args(args)

    diff = []
    for filename in args.files:
        diff += [parse_file(filename)["dependencies"]]
        print(diff)

    for filename in args.conda_forge:
        with open(filename) as file:
            diff += [unique(*condaforge_dependencies(file.read()))]

    if len(diff) != 2:
        raise ValueError("Need exactly two files")

    print_diff(*diff)


def _conda_envfile_diff_cli():
    conda_envfile_diff(sys.argv[1:])
