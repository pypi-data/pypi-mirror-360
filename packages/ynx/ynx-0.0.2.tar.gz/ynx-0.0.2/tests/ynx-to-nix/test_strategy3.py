from hypothesis import given, settings
from strategy3 import ynx_nodes


def _dump_pair(tmp, ynx_node, nix_src):
    print("Dumping pair to", tmp)
    stem = uuid.uuid4().hex[:8]
    (tmp / f"{stem}.ynx").write_text(yaml.dump(ynx_node))
    (tmp / f"{stem}.nix").write_text(nix_src)


# Smoke-test: draw and print ten examples
@given(node=ynx_nodes(max_depth=10))
@settings(max_examples=10, deadline=None)
def test_draw_cached(node):
    # Here you would call your real converter; we just assert it's a dict/list/scalar
    #
    _dump_pair(tmp_path, node, nix_code)
    assert isinstance(node, (dict, list, int, bool))
