import random
import string


class RandomNixTree:
    def __init__(
        self,
        max_depth: int,
        allow_valid: bool = True,
        allow_invalid: bool = True,
        rng: random.Random | None = None,
    ):
        self.max_depth = max_depth
        self.valid = True
        self.rng = rng or random.Random()
        self.allow_valid = allow_valid
        self.allow_invalid = allow_invalid

        # dispatch table
        self.generators = {
            "int": self._gen_int,
            "bool": self._gen_bool,
            "str_wrap": self._gen_str_wrap,
            "attrset": self._gen_attrset,
            "list": self._gen_list,
            "dict": self._gen_dict,
            "if": self._gen_if,
            "let": self._gen_let,
            "lambda": self._gen_lambda,
            "import": self._gen_import,
            "rec": self._gen_rec,
        }

    def generate(self, depth: int = 0):
        # At max depth, force a scalar
        if depth >= self.max_depth:
            return (
                self._gen_int(depth)
                if self.rng.choice([True, False])
                else self._gen_bool(depth)
            )

        # pick one of the generator methods at random
        kind = self.rng.choice(list(self.generators.keys()))
        return self.generators[kind](depth)

    # ── scalar generators ───────────────────────────────────────────
    def _gen_int(self, depth):
        # 10% chance to generate a “bad” int
        if False:
            if self.rng.random() < 0.1:
                self.valid = False
                return -self.rng.randint(1, 1000)
        return self.rng.randint(0, 200)

    def _gen_bool(self, depth):
        # booleans are always valid
        return self.rng.choice([True, False])

    # ── simple wrappers ─────────────────────────────────────────────
    def _random_ident(self):
        length = self.rng.randint(1, 5)
        return "".join(self.rng.choice(string.ascii_lowercase) for _ in range(length))

    def _random_str(self):
        length = self.rng.randint(1, 6)
        return "".join(self.rng.choice(string.ascii_lowercase) for _ in range(length))

    def _gen_str_wrap(self, depth):
        # 15% chance of too-long string = invalid
        if False:
            if self.rng.random() < 0.15:
                self.valid = False
                bad = "".join(
                    self.rng.choice(string.ascii_lowercase)
                    for _ in range(self.rng.randint(7, 12))
                )
                return {"str": bad}
        return {"str": self._random_str()}

    def _gen_attrset(self, depth):
        size = self.rng.randint(1, 3)
        d = {}
        for _ in range(size):
            key = self._random_ident()
            d[key] = self.generate(depth + 1)
        return {"attrset": d}

    # ── containers ─────────────────────────────────────────────────
    def _gen_list(self, depth):
        size = self.rng.randint(0, 3)
        return [self.generate(depth + 1) for _ in range(size)]

    def _gen_dict(self, depth):
        size = self.rng.randint(1, 3)
        return {
            (
                self._random_ident()
                if self.rng.random() > 0.2
                else f"{self._random_ident()}.{self._random_ident()}"
            ): self.generate(depth + 1)
            for _ in range(size)
        }

    # ── keyword constructs ──────────────────────────────────────────
    def _gen_if(self, depth):
        then = self.generate(depth + 1)
        els = self.generate(depth + 1)
        return {"if": True, "then": then, "else": els}

    def _gen_let(self, depth):
        body = self.generate(depth + 1)
        return {"let": {"x": 1}, "in": body}

    def _gen_lambda(self, depth):
        args = self.rng.choice([["x"], ["x", "y"], ["x", "..."]])
        body = self.generate(depth + 1)
        return {"args": args, "lambda": body}

    def _gen_import(self, depth):
        return {"call": "import", "args": [{"str": "./dummy.nix"}]}

    def _gen_rec(self, depth):
        inner = self.generate(depth + 1)
        return {"rec": {"foo": inner}}


import ynx

to_nix = ynx.convert.to_nix
from pathlib import Path

from helper import dump_pair, nix_parse


def main():
    for _ in range(50):
        tmp_path = Path("simple-generator-out")
        gen = RandomNixTree(max_depth=20)
        node = gen.generate()
        nix_code = to_nix(node, strict=False)
        dump_pair(tmp_path, node, nix_code)
        rc = nix_parse(nix_code)

        if False:
            if gen.valid:
                assert rc == 0, f"Valid node failed: {node}"
            else:
                assert rc != 0, f"Invalid node parsed: {node}"


if __name__ == "__main__":
    main()
