{
  description = "Flake with a custom dev shell combining nix.dev and LLVM tooling";

  inputs = {
    nixpkgs.url     = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        stdenv =
          if pkgs.stdenv.isDarwin
          then pkgs.clangStdenv                # macOS
          else pkgs.llvmPackages.libcxxStdenv; # Linux

        myShell = stdenv.mkDerivation {
          name = "clang-libcxx-nix-shell";
          buildInputs = [
            pkgs.llvmPackages.clang
            pkgs.llvmPackages.clang-tools
            pkgs.llvmPackages.lld
            pkgs.gcc 
            pkgs.go 
            pkgs.curl 
            pkgs.git
            pkgs.cmake 
            pkgs.pkg-config
            pkgs.python314 
            pkgs.boost.dev 
            pkgs.lldb
            pkgs.lua 
            pkgs.nodejs 
            pkgs.bear 
            pkgs.entr
            pkgs.fzf 
            pkgs.gh 
            pkgs.zsh 
            pkgs.neovim
            pkgs.nix.dev
          ];
          shellHook = ''
            echo "Entering custom nix-expr-c + LLVM shell"
            export TERM=xterm-256color
          '';
        };
      in {
        packages.default     = myShell;  # nix build
        devShells.default    = myShell;  # nix develop
        defaultPackage       = myShell;  # legacy alias
      });
}

