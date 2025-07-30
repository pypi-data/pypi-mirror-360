import subprocess
import uuid

import yaml

HAS_NIX = (
    subprocess.run(["which", "nix-instantiate"], capture_output=True).returncode == 0
)


def nix_parse(src: str) -> None:
    print("Parsing Nix source:")
    proc = subprocess.run(["nix-instantiate", "--parse", "-"], input=src.encode())

    # return proc.returncode, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    return proc.returncode


def dump_pair(tmp, ynx_node, nix_src):
    print("Dumping pair to", tmp)
    stem = uuid.uuid4().hex[:8]
    (tmp / f"{stem}.ynx").write_text(yaml.dump(ynx_node))
    (tmp / f"{stem}.nix").write_text(nix_src)
    print("Dumped pair to", tmp / f"{stem}.ynx", "and", tmp / f"{stem}.nix")
    return stem
