from pathlib import Path

import yaml
from hypothesis import HealthCheck, given, settings
from strategy1 import ynx_nodes

import ynx

to_nix = ynx.convert.to_nix

# ── helper: run nix-instantiate --parse ───────────────────────────


# ── fuzz test: converter + parser must both succeed ──────────────
@given(node=ynx_nodes(max_depth=10, max_leaves=10, kw_ratio=0.8))
@settings(
    max_examples=10,  # 20 deep samples per run
    deadline=None,  # disable timeouts
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow,
    ],
)
def test_converter_and_parser(node, tmp_path):
    print("Testing node:", node)
    nix_code = to_nix(node, strict=False)  # convert once
    nix_parse(nix_code)  # parse with nix-instantiate
    # Uncomment next line if you want to keep every sample:
    # _dump_pair(tmp_path, node, nix_code)
