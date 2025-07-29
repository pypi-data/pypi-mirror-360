"""A tool for composing and synchronizing .gitignore from GitHub's template collection."""

__version__ = "0.1.0"

import argparse
import asyncio
import logging
import os
import re
import sys
from collections.abc import Generator, Sequence
from contextlib import ExitStack, contextmanager
from difflib import unified_diff
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TextIO

import patch_ng
from dotenv import load_dotenv

from ._logging import (
    LoggingType,
    StructLogAdapter,
    make_logging_handler,
)
from .consts import RAW_BASE_URL
from .net import get_template

_log = StructLogAdapter(logger=logging.getLogger(__name__))

MARKER_RE = re.compile(
    rf"# --- (?P<type>BEGIN|END) {re.escape(RAW_BASE_URL)}/"
    rf"(?P<sha>[0-9a-fA-F]{{40}})/(?P<template>.*[^/])\.gitignore ---$",
    flags=re.MULTILINE,
)


def patch_with_diff(
    target: Sequence[str], old: Sequence[str], new: Sequence[str]
) -> Sequence[str] | None:
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        diff_str = "".join(unified_diff(old, new, fromfile="old", tofile="new"))
        diff = patch_ng.fromstring(diff_str.encode())
        path = tmp_path / "old"
        with path.open("w") as f:
            f.writelines(target)
        if not diff.apply(root=tmp_path, fuzz=True):
            return None
        with path.open("r") as f:
            return f.readlines()


@contextmanager
def input_file(path: Path) -> Generator[TextIO, None, None]:
    # noinspection PyAbstractClass
    # (ExitStack is not an abstract class)
    with ExitStack() as stack:
        if str(path) == "-":
            _log.debug("reading from stdin")
            yield sys.stdin
        else:
            _log.debug("reading from file", path=path)
            yield stack.enter_context(path.open("r"))


@contextmanager
def output_file(path: Path | None) -> Generator[TextIO, None, None]:
    # noinspection PyAbstractClass
    # (ExitStack is not an abstract class)
    with ExitStack() as stack:
        if str(path) == "-":
            _log.debug("writing to stdout")
            yield sys.stdout
        else:
            _log.debug("writing to file", path=str(path))
            yield stack.enter_context(path.open("w"))


async def async_main(args: argparse.Namespace) -> int | None:
    templates: dict[str, str | None] = dict(args.templates)
    template: str | None = None
    sha: str | None = None
    input_lines: list[str] = []
    output_lines: list[str] = []
    local_lines: list[str] = []

    with input_file(args.file) as f:
        input_lines.extend(f)

    if not templates:
        _log.info("auto-detecting existing templates", path=str(args.file))
        for line in input_lines:
            if (m := MARKER_RE.match(line)) is not None:
                templates[m.group("template")] = None
    _log.info("starting", path=str(args.file), templates=list(templates.keys()))
    for line_num, line in enumerate(input_lines):
        if (m := MARKER_RE.match(line)) is None:
            if template is None or template not in templates:
                output_lines.append(line)
            else:
                local_lines.append(line)
            continue
        gd = m.groupdict()
        expected_type = "BEGIN" if template is None else "END"
        if gd["type"] != expected_type:
            # Mismatched/out-of-order template marker lines is a gross structure error:
            # risks losing/confusing template sections.  Bail out.
            _log.error("unexpected marker", type=gd["type"], expected=expected_type)
            return os.EX_DATAERR

        if template is None:
            template = gd["template"]
            sha = gd["sha"]
            if template in templates:
                _log.debug("started processing local template", template=template)
            else:
                _log.debug("skipping local template", template=template)
                output_lines.append(line)
        elif gd["template"] != template or gd["sha"] != sha:
            # Mismatched/out-of-order template marker lines is a gross structure error:
            # risks losing/confusing template sections.  Bail out.
            _log.error("unexpected END marker", template=gd["template"])
            return os.EX_DATAERR
        elif template in templates:
            as_of = templates[template]
            ((old_lines, old_sha), (new_lines, new_sha)) = await asyncio.gather(
                get_template(template, sha), get_template(template, as_of)
            )
            if as_of is not None and new_sha.lower() != as_of.lower():
                _log.info(
                    "latest hash in which template was modified",
                    template=template,
                    as_of=as_of,
                    sha=new_sha,
                )
            if old_sha != new_sha:
                # strategy A: apply old-new diff to local
                patched_a = patch_with_diff(local_lines, old_lines, new_lines)
                # strategy B: apply old-local diff to new
                patched_b = patch_with_diff(new_lines, old_lines, local_lines)
                if patched_a is not None:
                    local_lines[:] = patched_a
                    if patched_b is not None and patched_a != patched_b:
                        _log.warning(
                            "two strategies resulted in different output",
                            template=template,
                        )
                    _log.debug("using local + (new - old) strategy")
                elif patched_b is not None:
                    local_lines[:] = patched_b
                    _log.debug("using new + (local - old) strategy")
                else:
                    _log.error(
                        "cannot apply diff, local contents unchanged",
                        template=template,
                        old_sha=old_sha,
                        new_sha=new_sha,
                    )
            else:
                _log.info("no changes in remote template", template=template)
            output_lines.append(
                f"# --- BEGIN {RAW_BASE_URL}/{new_sha}/{template}.gitignore ---\n"
            )
            output_lines.extend(local_lines)
            output_lines.append(
                f"# --- END {RAW_BASE_URL}/{new_sha}/{template}.gitignore ---\n"
            )
            local_lines.clear()
            templates.pop(template)
            template = None
            sha = None
            _log.debug("finished processing local template", template=template)
        else:
            output_lines.append(line)
            template = None
            sha = None
    if template is not None:
        _log.error("missing END marker for template", template=template)
        return os.EX_DATAERR
    for template, as_of in templates.items():  # those not found in input
        _log.info("adding template", template=template)
        lines, sha = await get_template(template, as_of)
        output_lines.append(
            f"# --- BEGIN {RAW_BASE_URL}/{sha}/{template}.gitignore ---\n"
        )
        output_lines.extend(lines)
        output_lines.append(
            f"# --- END {RAW_BASE_URL}/{sha}/{template}.gitignore ---\n"
        )
    diff = "".join(
        unified_diff(
            input_lines,
            output_lines,
            fromfile=str(args.file),
            tofile=str(args.output or args.file),
        )
    )
    if not diff:
        _log.info("no changes")
    else:
        if not args.dry_run:
            with output_file(args.output or args.file) as f:
                f.writelines(output_lines)
        if args.diff:
            print(diff)
    return os.EX_OK


def _build_argparser():
    parser = argparse.ArgumentParser(description=__doc__)

    def parse_template_arg(arg: str) -> (str, str | None):
        if "@" in arg:
            name, sha = arg.split("@", 1)
        else:
            name, sha = arg, None
        return name, sha

    parser.add_argument(
        "--file",
        "-f",
        metavar="FILE",
        type=Path,
        default=Path(".gitignore"),
        help="""Read .gitignore input from FILE (default: .gitignore; - means stdin)""",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        type=Path,
        help="""Write merged .gitignore to FILE
                (default: same as input, except stdout if input is stdin;
                - means stdout)""",
    )
    parser.add_argument(
        "--diff",
        "-d",
        action="store_true",
        default=False,
        help="""Show diff to stdout; can be used with --dry-run/-n.""",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        default=False,
        help="""Dry-run (don't write output); can be used with --diff/-d.""",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="""Verbose output.""",
    )
    parser.add_argument(
        "--logging",
        type=LoggingType,
        default=LoggingType.CONSOLE,
        help=f"""Logging type, one of: {", ".join(e.value for e in LoggingType)}.""",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="""Debug output: set DEBUG level on the root logger.""",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
        help="""Print version and exit.""",
    )
    parser.add_argument(
        "templates",
        metavar="TEMPLATE[@HASH]",
        nargs="*",
        type=parse_template_arg,
        default=[],
        help="""GitHub template names (without .gitignore extension),
                optionally with commit hash.""",
    )
    return parser


def main() -> int | None:
    load_dotenv()
    parser = _build_argparser()
    args = parser.parse_args()
    _log.setLevel(logging.WARNING)
    handler = make_logging_handler(args.logging)
    _log.addHandler(handler)
    if args.verbose:
        _log.setLevel(logging.INFO)
    if args.debug:
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
    try:
        return asyncio.run(async_main(args))
    except Exception as e:
        _log.error(e, dict(exc_info=True))
        return os.EX_UNAVAILABLE if isinstance(e, RuntimeError) else os.EX_SOFTWARE
