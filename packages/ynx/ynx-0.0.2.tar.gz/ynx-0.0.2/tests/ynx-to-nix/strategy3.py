from functools import lru_cache

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


# ─── recursive template, built once per depth ─────────────────
@lru_cache(maxsize=None)
def _node(max_depth: int, depth: int = 1):
    if depth >= max_depth:
        return leaf_scalar
    child = st.deferred(lambda: _node(max_depth, depth + 1))
    container = st.one_of(
        st.lists(child, max_size=3),
        st.dictionaries(ident | dotted, child, min_size=1, max_size=3),
    )
    return st.one_of(leaf_scalar, str_wrap, attrset_wrap, container, keyword(child))


# ─── public entrypoint ─────────────────────────────────────────
def ynx_nodes(max_depth: int = 8, max_leaves: int = 60, kw_ratio: float = 0.8):
    def build(md):
        deep_child = _node(md)  # cached by md
        root_kw = keyword(deep_child)
        container = st.one_of(
            st.dictionaries(ident | dotted, deep_child, min_size=1, max_size=3),
            st.lists(deep_child, max_size=3),
        )
        return st.one_of(
            *([root_kw] * int(kw_ratio * 10)),
            *([container] * int((1 - kw_ratio) * 6)),
            *([leaf_scalar] * int((1 - kw_ratio) * 4)),
        )

    return st.integers(1, max_depth).flatmap(build)
