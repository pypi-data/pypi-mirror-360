from hypothesis import strategies as st

# ── primitive leaves
leaf_int = st.integers(0, 200)
leaf_bool = st.booleans()
leaf_text = st.text(min_size=1, max_size=6, alphabet="abcdefghijklmnopqrstuvwxyz")

leaf_scalar = st.one_of(leaf_int, leaf_bool)  # NO plain identifiers
str_wrap = leaf_text.map(lambda s: {"str": s})  # → "foo" in Nix
ident = st.text("abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=5)
dotted = st.builds(lambda a, b: f"{a}.{b}", ident, ident)

attrset_wrap = st.dictionaries(ident, leaf_scalar, max_size=3).map(
    lambda m: {"attrset": m}
)
