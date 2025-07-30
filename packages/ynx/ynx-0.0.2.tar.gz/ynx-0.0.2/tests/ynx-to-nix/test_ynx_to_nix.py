# tests/test_ynx_to_nix.py
# -------------------------------------------------------------------
# Run:  pytest -q
# Needs: pytest, hypothesis, pyyaml.  nix-instantiate optional.
# -------------------------------------------------------------------

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

import ynx

to_nix = ynx.convert.to_nix

# -------------------------------------------------------------------
# load converter
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# nix helper
# -------------------------------------------------------------------
HAS_NIX = (
    subprocess.run(["which", "nix-instantiate"], capture_output=True).returncode == 0
)


def nix_parse(src: str) -> None:
    if not HAS_NIX:
        pytest.skip("nix-instantiate not available")
    subprocess.run(["nix-instantiate", "--parse", "-"], input=src.encode(), check=True)


# -------------------------------------------------------------------
# deterministic tests
# -------------------------------------------------------------------
@pytest.mark.parametrize(
    "ynx, expected",
    [
        (42, "42"),
        (True, "true"),
        ("hello", "hello"),
        ({"if": True, "then": 1, "else": 2}, "if true then 1 else 2"),
    ],
)
def test_basic_examples(ynx, expected):
    assert to_nix(ynx) == expected


@pytest.mark.skipif(not HAS_NIX, reason="nix command not available")
def test_flake_example_roundtrip():
    cwd = Path(__file__).resolve().parent
    flake_path = cwd / "flake.ynx"
    assert flake_path.is_file(), "flake.ynx fixture missing"
    nix_code = to_nix(yaml.safe_load(flake_path.read_text()), strict=True)
    nix_parse(nix_code)


# -------------------------------------------------------------------
# Hypothesis strategy
# -------------------------------------------------------------------
simple_scalar = st.one_of(
    st.integers(min_value=0, max_value=9),
    st.booleans(),
    st.text(min_size=1, max_size=5, alphabet="abcxyz"),
)
key_name = st.text("abcxyz", min_size=1, max_size=4)


@st.composite
def ynx_nodes(draw, depth=0):
    if depth > 2:
        return draw(simple_scalar)

    branch = draw(st.integers(min_value=0, max_value=3))

    if branch == 0:  # scalar
        return draw(simple_scalar)

    if branch == 1:  # list
        return draw(st.lists(simple_scalar, min_size=0, max_size=3))

    if branch == 2:  # safe keyword constructs
        which = draw(st.sampled_from(["if", "let", "lambda"]))
        if which == "if":
            return {"if": True, "then": 1, "else": 0}
        if which == "let":
            return {"let": {"x": 1}, "in": 1}
        if which == "lambda":
            return {"args": ["x"], "lambda": "x"}

    # branch 3: plain attr-set
    keys = draw(st.lists(key_name, min_size=1, max_size=3, unique=True))
    return {k: draw(ynx_nodes(depth=depth + 1)) for k in keys}


# -------------------------------------------------------------------
# fuzz: converter never crashes in permissive mode
# -------------------------------------------------------------------
@given(node=ynx_nodes())
@settings(max_examples=200)
def test_permissive_never_crashes(node):
    to_nix(node, strict=False)


# -------------------------------------------------------------------
# fuzz: generated Nix parses (skip when free identifiers exist)
# -------------------------------------------------------------------
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_'-]*")
SKIP_WORDS = {"true", "false", "null"}


@given(node=ynx_nodes())
@settings(max_examples=50)
@pytest.mark.skipif(not HAS_NIX, reason="nix command not available")
def test_generated_nix_parses(node):
    src = to_nix(node, strict=False)
    bare = {tok for tok in IDENT.findall(src) if f'"{tok}"' not in src}
    if any(w not in SKIP_WORDS for w in bare):
        pytest.skip("free identifiers present")
    nix_parse(src)
