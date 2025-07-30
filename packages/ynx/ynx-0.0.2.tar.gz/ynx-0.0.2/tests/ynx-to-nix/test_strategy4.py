import uuid
from pathlib import Path

import yaml
from helper import *
from hypothesis import given, settings
from strategy4 import ynx_nodes

import ynx

to_nix = ynx.convert.to_nix


@given(node=ynx_nodes(max_depth=10))
@settings(max_examples=10, deadline=None)
def test_draw_recursive(node):
    assert isinstance(node, (dict, list, int, bool))

    nix_code = to_nix(node, strict=False)  # convert once
    (ret_code, out) = nix_parse(nix_code)  # parse with nix-instantiate

    output_path = Path("test_out")
    stem = dump_pair(output_path, node, nix_code)

    assert (
        ret_code == 0
    ), f"Failed to parse Nix code, check result under :{output_path/stem}"
