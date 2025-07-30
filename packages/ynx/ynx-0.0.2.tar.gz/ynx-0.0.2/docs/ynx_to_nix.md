

# YNX → Nix Reference

## Reserved keyword precedence


### Disambiguation rule — one sentence

If a mapping (root or nested) contains **any** lead keyword  
`if`, `let`, `with`, `assert`, `args`, `call`, `rec`, or `attrset`  
then that mapping is parsed as the corresponding construct **and must also carry any companion keys it requires** (`then/else`, `in`, `args`, etc.).  
Otherwise the mapping is treated as a plain attribute set.  
When you truly need an attribute set whose keys collide with a keyword set, wrap it under the single key `attrset:` and the converter will treat the inner mapping as attributes.


| Priority | Keys that **must all be present** | Parsed as |
|----------|-----------------------------------|-----------|
| 1 | `if`, `then`, `else` | conditional |
| 2 | `let`, `in` | let‑in |
| 3 | `with`, `in` | with expression |
| 4 | `assert`, `in` | assert expression |
| 5 | `args`, `lambda` | lambda literal |
| 6 | `call` (+ optional `args`) | function application |
| 7 | `rec` | recursive attr‑set |
| 8 | `attrset` | explicit attr‑set wrapper |
| 9 | _(anything else)_ | plain attribute set |

## Root expression cheat‑sheet

| Shape | Interpreted as | Example |
|-------|----------------|---------|
| Scalar | same scalar | `42` |
| Mapping matches a keyword set | that construct | `if true then 1 else 0` |
| Mapping with no keywords | attribute set | `{ foo = 1; }` |
| Mapping wants attrs but would clash | wrap with `attrset` | `{ let = "lit"; }` |

---

## 1 · Scalars

**YNX**
```ynx
42
```
**Nix**
```nix
42
```

## 2 · Lists

**YNX**
```ynx
[1, 2, 3]
```
**Nix**
```nix
[ 1 2 3 ]
```

## 3 · Plain attribute set

**YNX**
```ynx
name: "example"
value: 42
```
**Nix**
```nix
{
  name = "example";
  value = 42;
}
```

## 4 · Attribute set when keys *look like* keywords

**!!! Disambiguation needed**

**YNX**
```ynx
attrset:
  let: "literal"
```
**Nix**
```nix
{ let = "literal"; }
```

## 5 · Conditional

**YNX**
```ynx
if: true
then: 0
else: 1
```
**Nix**
```nix
if true then 0 else 1
```

## 6 · Let‑in

**YNX**
```ynx
let:
  x: 10
  y: 20
in: x + y
```
**Nix**
```nix
let
  x = 10;
  y = 20;
in x + y
```

## 7 · `with` expression

**YNX**
```ynx
with: scope
in: scope.attr
```
**Nix**
```nix
with scope; scope.attr
```

## 8 · `assert` expression

**YNX**
```ynx
assert: builtins.isBool flag
in: flag
```
**Nix**
```nix
assert builtins.isBool flag; flag
```

## 9 · Recursive attribute set (`rec`)

**YNX**
```ynx
rec:
  self: true
  other: self
```
**Nix**
```nix
rec {
  self  = true;
  other = self;
}
```

## 10 · Lambda

**YNX**
```ynx
args: [x, y]
lambda: x + y
```
**Nix**
```nix
x: y: x + y
```

## 11 · Function application (`call`)
### Calling an inline lambda

**YNX**
```ynx
call:
  args: [x]
  lambda: x + 1
args:
  - 5
```
**Nix**
```nix
(x: x + 1) 5
```


**YNX**
```ynx
call: import
args:
  - nixpkgs
  - system: "x86_64-linux"
```
**Nix**
```nix
import nixpkgs { system = "x86_64-linux"; }
```

## 12 · Nested constructs

**YNX**
```ynx
args: [x]
lambda:
  if: x
  then:
    let:
      y: 1
    in: y + x
  else:
    attrset:
      message: "fallback"
```
**Nix**
```nix
x:
  if x then
    (let
       y = 1;
     in y + x)
  else
    { message = "fallback"; }
```

---

