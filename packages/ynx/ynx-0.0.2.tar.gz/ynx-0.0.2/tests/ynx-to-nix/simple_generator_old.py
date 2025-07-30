import random
import string


def rand_ident(min_len=1, max_len=5):
    return "".join(
        random.choice(string.ascii_lowercase)
        for _ in range(random.randint(min_len, max_len))
    )


def rand_str(min_len=1, max_len=6):
    return "".join(
        random.choice(string.ascii_lowercase)
        for _ in range(random.randint(min_len, max_len))
    )


def gen_node(depth=0, max_depth=6):
    # If we’ve hit max depth, force a scalar
    if depth >= max_depth:
        return random.choice([random.randint(0, 200), random.choice([True, False])])

    # All possible constructors
    choices = [
        "int",
        "bool",
        "str_wrap",
        "attrset",
        "list",
        "dict",
        "if",
        "let",
        "lambda",
        "import",
        "rec",
    ]
    kind = random.choice(choices)

    if kind == "int":
        return random.randint(0, 200)

    if kind == "bool":
        return random.choice([True, False])

    if kind == "str_wrap":
        return {"str": rand_str()}

    if kind == "attrset":
        # small attrset with 1–3 entries
        n = random.randint(1, 3)
        return {
            "attrset": {rand_ident(): gen_node(depth + 1, max_depth) for _ in range(n)}
        }

    if kind == "list":
        # list of length 0–3
        return [gen_node(depth + 1, max_depth) for _ in range(random.randint(0, 3))]

    if kind == "dict":
        n = random.randint(1, 3)
        return {rand_ident(): gen_node(depth + 1, max_depth) for _ in range(n)}

    if kind == "if":
        return {
            "if": True,
            "then": gen_node(depth + 1, max_depth),
            "else": gen_node(depth + 1, max_depth),
        }

    if kind == "let":
        return {"let": {"x": 1}, "in": gen_node(depth + 1, max_depth)}

    if kind == "lambda":
        # choose 1 or 2 args, or varargs
        args = random.choice([["x"], ["x", "y"], ["x", "..."]])
        return {"args": args, "lambda": gen_node(depth + 1, max_depth)}

    if kind == "import":
        return {"call": "import", "args": [{"str": "./dummy.nix"}]}

    if kind == "rec":
        return {"rec": {"foo": gen_node(depth + 1, max_depth)}}

    # fallback
    return random.randint(0, 200)


import ynx

to_nix = ynx.convert.to_nix
from pathlib import Path

from helper import dump_pair, nix_parse


def main():
    # generate 20 random trees and test them
    for _ in range(20):
        tmp_path = Path("simple-generator-out")
        tmp_path.mkdir(exist_ok=True)
        node = gen_node(max_depth=30)
        nix_code = to_nix(node, strict=False)
        dump_pair(tmp_path, node, nix_code)
        try:
            nix_parse(nix_code)
        except CalledProcessError:
            # handle parse error if you expect some to fail
            pass


if __name__ == "__main__":
    main()
