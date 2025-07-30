from hypothesis import strategies as st
from strategy_helper import *


def keyword(child):
    return st.one_of(
        st.tuples(child, child).map(lambda t: {"if": True, "then": t[0], "else": t[1]}),
        child.map(lambda body: {"let": {"x": 1}, "in": body}),
        child.map(lambda body: {"args": ["x"], "lambda": body}),
        child.map(lambda body: {"args": ["x", "..."], "lambda": body}),
        st.just({"call": "import", "args": [{"str": "./dummy.nix"}]}),
        child.map(lambda v: {"rec": {"foo": v}}),
    )


# ─── recursive strategy built once — Hypothesis caches internally ─
def _tree(max_leaves: int):
    base = st.one_of(leaf_scalar, str_wrap, attrset_wrap)

    def expand(child):
        return st.one_of(
            st.lists(child, max_size=3),
            st.dictionaries(ident | dotted, child, min_size=1, max_size=3),
            keyword(child),
        )

    return st.recursive(base, expand, max_leaves=max_leaves)


def ynx_nodes(max_depth: int = 8, max_leaves: int = 60, kw_ratio: float = 0.8):
    """max_depth param kept only for signature parity; not used internally."""
    root = _tree(max_leaves)
    root_kw = keyword(root)
    container = st.one_of(
        st.dictionaries(ident | dotted, root, min_size=1, max_size=3),
        st.lists(root, max_size=3),
    )
    return st.one_of(
        *([root_kw] * int(kw_ratio * 10)),
        *([container] * int((1 - kw_ratio) * 6)),
        *([leaf_scalar] * int((1 - kw_ratio) * 4)),
    )
