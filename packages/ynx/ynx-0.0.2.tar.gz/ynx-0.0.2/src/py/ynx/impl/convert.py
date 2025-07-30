"""
YNX → Nix converter (pretty‑print + identifier rule)
===================================================

* Pretty‑prints with two‑space indentation.
* **Unquotes** scalars that look like Nix identifiers or attribute paths
  when they appear as the function or arguments inside a `call:` mapping.
* Strict/permissive modes, line‑numbered error messages.

Usage
-----
```bash
python ynx_to_nix.py [-m strict|permissive] file.ynx
```

Requires `PyYAML`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

# ---------------------------------------------------------------------------
# YAML loader that keeps line info
# ---------------------------------------------------------------------------


class MarkedDict(dict):
    __slots__ = ("mark",)


class MarkedList(list):
    __slots__ = ("mark",)


class MarkedLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node):
    mapping = MarkedDict()
    mapping.mark = node.start_mark
    loader.flatten_mapping(node)
    for k_node, v_node in node.value:
        mapping[loader.construct_object(k_node, True)] = loader.construct_object(
            v_node, True
        )
    return mapping


def _construct_sequence(loader, node):
    seq = MarkedList()
    seq.mark = node.start_mark
    for child in node.value:
        seq.append(loader.construct_object(child, True))
    return seq


MarkedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)
MarkedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Nix identifier / attr-path: segments cannot contain hyphen (-)
ID_REGEX = re.compile(r"[A-Za-z_][A-Za-z0-9_'-]*(?:\.[A-Za-z_][A-Za-z0-9_'-]*)*$")

IND = "  "  # two spaces per indent level


def _mark(node):
    return (
        f"line {getattr(node, 'mark', None).line + 1 if hasattr(node, 'mark') else '?'}"
    )


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _is_scalar(x: Any) -> bool:
    return isinstance(x, (str, int, float, bool)) or x is None


class YnxError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Pretty‑print helpers
# ---------------------------------------------------------------------------


def _render_list(items: List[Any], *, lvl: int, strict: bool) -> str:
    if all(_is_scalar(i) for i in items) and len(items) <= 4:
        body = " ".join(_render_scalar(i) for i in items)
        return f"[ {body} ]"

    def render_item(i):
        s = to_nix(i, strict=strict, lvl=lvl + 1)
        # wrap any non-scalar element in parentheses so it parses inside a list
        return s if _is_scalar(i) else f"({s})"

    inner = "\n".join(f"{IND * (lvl + 1)}{render_item(i)}" for i in items)
    return f"[\n{inner}\n{IND * lvl}]"


def _render_attrset(
    mapping: Dict[str, Any], *, rec: bool, lvl: int, strict: bool
) -> str:
    inner = "\n".join(
        f"{IND * (lvl + 1)}{k} = {to_nix(v, strict=strict, lvl=lvl + 1)};"
        for k, v in mapping.items()
    )
    opener = "rec {" if rec else "{"
    return f"{opener}\n{inner}\n{IND * lvl}}}"


def _render_scalar(val: Any) -> str:
    """Quote the scalar unless it's an identifier/attr‑path string."""
    if isinstance(val, str) and ID_REGEX.fullmatch(val):
        return val
    if val is None:
        return "null"
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return _quote(val)
    raise TypeError("non‑scalar passed to _render_scalar")


# ---------------------------------------------------------------------------
# Lead‑keyword table and handlers
# ---------------------------------------------------------------------------

LEADS: dict[str, Set[str]] = {
    "if": {"then", "else"},
    "let": {"in"},
    "with": {"in"},
    "assert": {"in"},
    "call": set(),
    "args": {"lambda"},
    "rec": set(),
    "attrset": set(),
}


def _h_if(n, lvl, strict):
    return (
        f"if {to_nix(n['if'], strict=strict, lvl=lvl)} then "
        f"{to_nix(n['then'], strict=strict, lvl=lvl)} else "
        f"{to_nix(n['else'], strict=strict, lvl=lvl)}"
    )


def _h_let(n, lvl, strict):
    if "in" not in n:
        raise YnxError(f"'let' missing 'in' at {_mark(n)}")
    binds = n["let"]
    if not isinstance(binds, dict):
        raise YnxError(f"'let' value must be mapping at {_mark(binds)}")
    binds_fmt = "\n".join(
        f"{IND * (lvl + 1)}{k} = {to_nix(v, strict=strict, lvl=lvl + 1)};"
        for k, v in binds.items()
    )
    body = to_nix(n["in"], strict=strict, lvl=lvl)
    return f"let\n{binds_fmt}\n{IND * lvl}in {body}"


def _h_with(n, lvl, strict):
    return (
        f"with {to_nix(n['with'], strict=strict, lvl=lvl)}; "
        f"{to_nix(n['in'], strict=strict, lvl=lvl)}"
    )


def _h_assert(n, lvl, strict):
    return (
        f"assert {to_nix(n['assert'], strict=strict, lvl=lvl)}; "
        f"{to_nix(n['in'], strict=strict, lvl=lvl)}"
    )


def _h_lambda(n, lvl, strict):
    if "lambda" not in n:
        raise YnxError(f"Lambda missing body at {_mark(n)}")
    params = n["args"]

    # Case A: list with optional '...' sentinel → positional OR attr-pattern w/ ellipsis
    if isinstance(params, list):
        if "..." in params:  # attr-pattern with ellipsis
            sentinel_index = params.index("...")
            names = params[:sentinel_index]
            pattern = ", ".join(map(str, names)) + ", ..."
            head = f"{{ {pattern} }}: "
        else:  # plain positional lambda
            head = ": ".join(map(str, params)) + ": "
    # Case B: single mapping → attr-pattern without ellipsis
    elif isinstance(params, dict):
        pattern = ", ".join(params.keys())
        head = f"{{ {pattern} }}: "
    else:
        raise YnxError(f"Invalid 'args' format at {_mark(params)}")

    # TODO.. thea always paranthesize should be a configuration option
    # It may help readability in some cases, but not always
    # Always parenthesize the lambda expression to ensure it parses correctly
    # body = to_nix(n["lambda"], strict=strict, lvl=lvl)
    # return f"({head}{body})"
    return head + to_nix(n["lambda"], strict=strict, lvl=lvl)


def _render_call_component(x, lvl, strict):
    if _is_scalar(x) and isinstance(x, str) and ID_REGEX.fullmatch(x):
        return x
    return to_nix(x, strict=strict, lvl=lvl)


def _h_call(n, lvl, strict):
    func_src = _render_call_component(n["call"], lvl, strict)
    arg_list = n.get("args", [])
    if not isinstance(arg_list, list):
        raise YnxError(f"'args' must be sequence at {_mark(n)}")
    rendered = " ".join(_render_call_component(a, lvl, strict) for a in arg_list)
    return func_src + (" " + rendered if rendered else "")


def _h_rec(n, lvl, strict):
    return _render_attrset(n["rec"], rec=True, lvl=lvl, strict=strict)


def _h_attrset(n, lvl, strict):
    return _render_attrset(n["attrset"], rec=False, lvl=lvl, strict=strict)


HANDLERS = {
    "if": _h_if,
    "let": _h_let,
    "with": _h_with,
    "assert": _h_assert,
    "args": _h_lambda,
    "call": _h_call,
    "rec": _h_rec,
    "attrset": _h_attrset,
    # single-key string wrapper handled inline, not here
}

# ---------------------------------------------------------------------------
# Main recursive converter
# ---------------------------------------------------------------------------


def to_nix(node: Any, *, strict: bool = True, lvl: int = 0) -> str:
    # Scalars ----------------------------------------------------------
    if _is_scalar(node):
        return _render_scalar(node)

    # Lists ------------------------------------------------------------
    if isinstance(node, list):
        return _render_list(node, lvl=lvl, strict=strict)

    # Mappings ---------------------------------------------------------
    if not isinstance(node, dict):
        raise YnxError(f"Unsupported node type at {_mark(node)}")

    keys = set(node.keys())
    for lead in LEADS:  # deterministic order
        if lead in node:
            req = LEADS[lead]
            if strict and not req <= node.keys():
                missing = ", ".join(req - node.keys())
                raise YnxError(f"'{lead}' missing {missing} at {_mark(node)}")
            return HANDLERS[lead](node, lvl, strict)

    # String wrapper: { str: value }
    if keys == {"str"}:
        if not _is_scalar(node["str"]):
            raise YnxError(f"'str' must wrap a scalar at {_mark(node)}")
        return _quote(str(node["str"]))

    # Plain attribute set ----------------------------------------------------
    return _render_attrset(node, rec=False, lvl=lvl, strict=strict)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: List[str] | None = None):
    ap = argparse.ArgumentParser(description="YNX → Nix converter")
    ap.add_argument("file")
    ap.add_argument("-m", "--mode", choices=["strict", "permissive"], default="strict")
    args = ap.parse_args(argv)

    data = yaml.load(Path(args.file).read_text(), Loader=MarkedLoader)
    try:
        print(to_nix(data, strict=(args.mode == "strict")))
    except YnxError as e:
        sys.stderr.write("error: " + str(e) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
