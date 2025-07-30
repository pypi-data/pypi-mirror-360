# Quick Actions - Configure Your Action menus with hierarchical TOML files bringing your own scripts.

## Install

### Using pip
```sh
> pip install quick-actions
```


### Using nixpkgs
```nix
{
    ...
    inputs = {
        quick-actions = {
            url = "git+https://gitlab.com/leswell/quick-actions";
            inputs.nixpkgs.follows = "nixpkgs";
        };
        ...
    }
}
```

**AND** add the package to system or home-manager `quick-actions.packages.${pkgs.system}.quick-actions`
**OR**
use one of the modules.