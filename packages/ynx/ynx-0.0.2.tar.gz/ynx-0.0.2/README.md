
# YNX ↔︎ Nix Converter

*A YAML‑flavoured gateway into the Nix ecosystem*

---

## Why this project exists
Nix expressions are powerful—but their syntax is alien to many DevOps and infrastructure engineers who already live in YAML for Helm charts, CI pipelines, `docker‑compose`, etc.  
**YNX** removes that cognitive speed‑bump by letting you write (or generate) a *tiny* YAML subset that compiles 1‑to‑1 into real Nix.

### Design forces

| Force | How YNX answers |
|-------|-----------------|
| **Familiar syntax** | YNX is plain YAML—no exotic front‑matter or new delimiters. |
| **Loss‑free round‑trip** | Every everyday Nix construct (conditionals, `let`, `with`, lambdas, function calls, recursive attr‑sets) has an unambiguous YAML form. |
| **Minimal keywords** | Exactly nine lead keywords do all the disambiguation. |
| **Readable output** | Converter pretty‑prints two‑space indented Nix so newcomers can cross‑check. |
| **Escape hatches** | `attrset:` and `str:` wrappers handle the rare collisions or forced literals without blowing up the grammar. |

### Problems & holes this covers
* **On‑boarding friction**: engineers can start in YAML and *see* the Nix that results, learning by comparison.
* **Template generators**: tools can emit YAML more easily than hand‑rolled `.nix`.
* **Code review fatigue**: reviewers can diff structured YAML instead of dense Nix.
* **Automation hooks**: YAML parsers exist in every language; feeding them into the converter unlocks CI/CD pipelines, linting, and documentation generators.

---

## 🛠️ Quick conversion rules (TL;DR)

* If a mapping’s keys match one of the lead‑keyword sets  
  (`if`, `let`, `with`, `assert`, `args+lambda`, `call`, `rec`, `attrset`) → parse that construct.
* Otherwise the mapping is an **attribute set**.
* Use `attrset:` to force an attr‑set when keys would collide.
* Use `str:` to force a literal Nix string (`system: { str: x86_64-linux }`).
* `args: [ self, nixpkgs, ... ]` renders `{ self, nixpkgs, ... }:`—ellipses supported.

A full, example‑driven table lives in **[docs/ynx‑to-nix.md](./docs/ynx-to-nix.md)**.

---

## Getting started

```bash
pip install pyyaml
python ynx_to_nix.py my-file.ynx          # strict mode
python ynx_to_nix.py -m permissive my.ynx # tolerant mode
```

---

## Example

```ynx
inputs:
  nixpkgs:
    url: github:NixOS/nixpkgs/nixpkgs-unstable

outputs:
  args: [ self, nixpkgs, ... ]
  lambda:
    let:
      pkgs:
        call: import
        args:
          - nixpkgs
          - system:
              str: x86_64-linux
    in:
      hello:
        call: pkgs.mkShell
        args:
          - attrset:
              buildInputs: [ pkgs.hello ]
```

Converts to:

```nix
{ self, nixpkgs, ... }:
let
  pkgs = import nixpkgs { system = "x86_64-linux"; };
in {
  hello = pkgs.mkShell {
    buildInputs = [ pkgs.hello ];
  };
}
```

---

## Roadmap

* **Better interpolation** (`"${pkgs.foo}/bin"` helpers)
* **VS Code extension** with live preview
* **Round‑trip test suite** in CI
* **Template gallery** for flakes, NixOS modules, devShells

Contributions & feedback welcome!

