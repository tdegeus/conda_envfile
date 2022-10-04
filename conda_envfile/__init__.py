import argparse
import os
import re
import sys
import warnings

import click
import packaging.version
import yaml

from ._version import version


def _parse(version):
    return packaging.version.parse(version)


def parse_file(*args: list[str]) -> dict:
    """
    Parse one or more files and return the raw result.

    :param args: List of filenames to parse.
    :return: Raw result.
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

    return env

def unique(*args) -> list[str]:
    """
    Return a list of unique dependencies.

    :param args: Dependencies to merge.
    :return: List of unique dependencies.
    """

    deps = {}

    for dep in args:

        dep = re.split("#", dep)

        if len(dep) > 1:
            dep, comment = dep
            warnings.warn(f"Comment '{comment}' ignored.", Warning)
        else:
            dep = dep[0]

        _, name, _, eq, ver, _ = re.split(r"^([^>^<^=^\s]*)(\s*)([<>=]*)(.*)$", dep)
        eq2 = None
        ver2 = None
        sp = re.split(r"^([^,]*)(,)(\s*)([<>=]*)(.*)$", ver)
        if len(sp) > 1:
            _, ver, _, _, eq2, ver2, _ = sp

        ret = {}

        if eq == "=" and eq2:
            raise ValueError(f"Cannot have two equalities in '{dep}'")
        if eq in [">=", ">"] and eq2 in [">=", ">"]:
            raise ValueError(f"Illegal bound in '{dep}'")

        for a, b in [(eq, ver), (eq2, ver2)]:
            if not a:
                if b:
                    raise ValueError(f"Missing equality in '{dep}'")
                continue
            if "*" in b:
                raise ValueError(f"WIP: wildcard not yet implemented '{dep}'")
            ret[a] = b

        if name not in deps:
            deps[name] = ret
        else:
            for key, value in ret.items():
                if key in deps[name]:
                    if _parse(value) > _parse(deps[name][key]):
                        deps[name][key] = value
                else:
                    deps[name][key] = value

    for key in deps:

        if ">=" in deps[key] and ">" in deps[key]:
            if _parse(deps[key][">="]) >= _parse(deps[key][">"]):
                del deps[key][">"]
            else:
                del deps[key][">="]

        if ">=" in deps[key] and ">" in deps[key]:
            if _parse(deps[key]["<="]) <= _parse(deps[key]["<"]):
                del deps[key]["<"]
            else:
                del deps[key]["<="]

        deps[key]["ret"] = (
            key + " " + ", ".join([f"{e}{v}" for e, v in deps[key].items()])
        ).strip(" ")

    return [deps[key]["ret"] for key in sorted(deps)]


def _conda_envfile_parse_parser():
    """
    Return parser for :py:func:`conda_envfile_parse`.
    """

    desc = "Parse YAML environnement files."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("files", type=str, nargs="*", help="Input files.")
    return parser


def conda_envfile_parse(args: list[str]):
    """
    Command-line tool to print datasets from a file, see ``--help``.
    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_parse_parser()
    args = parser.parse_args(args)

    for filename in args.files:
        env = parse_file(filename)
        env["dependencies"] = unique(*env["dependencies"])
        with open(filename, "w") as file:
            yaml.dump(env, file)

def _conda_envfile_parse_cli():
    conda_envfile_parse(sys.argv[1:])


def _conda_envfile_merge_parser():
    """
    Return parser for :py:func:`conda_envfile_merge`.
    """

    desc = "Merge YAML environnement files."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite output file.")
    parser.add_argument("-o", "--output", type=str, help="Write to output file.")
    parser.add_argument("-a", "--append", type=str, action="append", help="Append dependencies.")
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("files", type=str, nargs="*", help="Input files.")
    return parser


def conda_envfile_merge(args: list[str]):
    """
    Command-line tool to print datasets from a file, see ``--help``.
    :param args: Command-line arguments (should be all strings).
    """

    parser = _conda_envfile_merge_parser()
    args = parser.parse_args(args)
    env = parse_file(*args.files)
    env["dependencies"] = unique(*(env["dependencies"] + args.append))

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
