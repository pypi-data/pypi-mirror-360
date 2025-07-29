# vault-cli
Vault cli helper

# Requirements
[rofi](https://github.com/davatorium/rofi) or [dmenu](https://tools.suckless.org/dmenu/) needs to be installed.
Optionally, `xsel`, if exists, selected secrets will be copied to clipboard.

config file should be located at `/home/{user}/.config/vaultrun/config.yaml` with:

```yaml
name:
  mount_point: <Secret mount point>
  secret_path: <Secret path to query>
  # If role_id and secret_id are not provided, use OIDC login
  role_id: <Role ID>
  secret_id: <Secret ID>
```

# Installation

from Pypi:

```bash
python -m pip3 install vaultrun```
```

Local installation:

```bash
poetry install
```

# Usage

From Pypi:

```bash
vaultrun
```

Local run:

```bash
poetry run vaultrun
```
