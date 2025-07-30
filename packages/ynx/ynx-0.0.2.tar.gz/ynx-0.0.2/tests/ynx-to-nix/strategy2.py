from functools import lru_cache
from hypothesis import strategies as st


@lru_cache(maxsize=None)
def _tree(max_depth):
    # build the deep recursive strategy exactly **once**
    def _node(depth):
        if depth >= max_depth:
            return leaf_scalar
        child = st.deferred(lambda: _node(depth + 1))
        container = st.one_of(
            st.lists(child, max_size=3),
            st.dictionaries(ident | dotted, child, min_size=1, max_size=3),
        )
        return st.one_of(leaf_scalar, str_wrap, attrset_wrap, container, keyword(child))

    return _node(1)


def ynx_nodes(max_depth=8, kw_ratio=0.8):
    root = _tree(max_depth)  # reused for every example
    root_kw = keyword(root)
    container = st.one_of(
        st.dictionaries(ident | dotted, root, min_size=1, max_size=3),
        st.lists(root, max_size=3),
    )
    scalar = leaf_scalar
    return st.one_of(
        *([root_kw] * int(kw_ratio * 10)),
        *([container] * int((1 - kw_ratio) * 6)),
        *([scalar] * int((1 - kw_ratio) * 4)),
    )
