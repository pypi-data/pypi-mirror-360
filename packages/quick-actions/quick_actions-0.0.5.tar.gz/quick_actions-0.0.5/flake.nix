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

    packages = forAllSystems (system: 
    let
      pkgs = import nixpkgs { inherit system; };
      version-number = "0.0.5";
    in {
      quick-actions = pkgs.python3Packages.buildPythonPackage rec {
        pname="quick_actions";
        version="${version-number}-local";
        pyproject = true;

        nativeBuildInputs = [ pkgs.python3Packages.hatchling ];
        propagatedBuildInputs = (python-dependencies pkgs.python3Packages);

        src = self;
      };

      quick-actions-pypi = pkgs.python3Packages.buildPythonPackage rec {
        pname="quick_actions";
        version=version-number;
        pyproject = true;

        nativeBuildInputs = [ pkgs.python3Packages.hatchling ];
        propagatedBuildInputs = (python-dependencies pkgs.python3Packages);

        src = pkgs.fetchPypi {
          inherit pname version;
          hash = "sha256-1BUBm8Wfq6cUUwzHWZZQ2/ZCwPWPfCyBfvURdyyp+rY=";
          # hash = lib.fakeHash;
        };
      };
    });

    nixosModules =
    {
			default = {config, pkgs, lib, ...}: {
				config = {
          environment.systemPackages = [
						self.packages.${pkgs.system}.quick_actions
					];
				};
			};
		};

    homeManagerModules =
    {
			default = {pkgs, ...}: {
          home.packages = [
            self.packages.${pkgs.system}.quick-actions
          ];
			};
		};
  };

}