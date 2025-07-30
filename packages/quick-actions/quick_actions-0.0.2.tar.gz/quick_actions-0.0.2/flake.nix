{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs } :
let 
  forAllSystems = nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" ];
  lib = nixpkgs.lib;

  python-dependencies = (ps: [
    # ps.pyyaml
    ps.python-benedict
  ]);
in
{
    devShells = forAllSystems (system:
    let 
        pkgs = import nixpkgs { inherit system; };
    in {
      default = pkgs.mkShell {
        buildInputs = [
          (pkgs.python313.withPackages python-dependencies).out
        ];
      };
    });
  };

  packages = forAllSystems (system: 
  let
    pkgs = import nixpkgs { inherit system; };
  in {
    quick-menu = pkgs.python3Packages.buildPythonPackage rec {
			pname="quick-menu";
			version="0.0.2";
			pyproject = true;

			nativeBuildInputs = [ pkgs.python3Packages.hatchling ];
			propagatedBuildInputs = (python-dependencies pkgs.python3Packages);

			src = pkgs.fetchPypi {
				inherit pname version;
				# hash = "sha256-WAYcndl4EXvRIJJwTtJabNN/jHxDAPneMZiN1TnzJyg=";
				hash = lib.fakeHash;
			};
		};
  })
}