import hvac

from app.login import vault_login
from app.utils import call_rofi_dmenu, which, copy_to_clipboard, parse_yaml_user_config
from rich import print, pretty


def parse_vault_path(client: hvac.Client, mount_point: str, secret_path: str) -> str:
    all_secrets = client.secrets.kv.v2.list_secrets(mount_point=mount_point, path=secret_path)
    _selected = call_rofi_dmenu(options=all_secrets.get("data", {}).get("keys"), abort=True)
    if _selected.endswith("/"):
        all_secrets = client.secrets.kv.v2.list_secrets(mount_point=mount_point, path=f"{secret_path}/{_selected}")
        selected = call_rofi_dmenu(options=all_secrets.get("data", {}).get("keys"), abort=True)
        if selected.endswith("/"):
            _secret_path = f"{_selected}/{selected}"
            return parse_vault_path(client=client, mount_point=mount_point, secret_path=_secret_path)
        else:
            return f"{_selected}/{selected}"
    else:
        return _selected


def main():
    pretty.install()
    _config = parse_yaml_user_config()
    section_selected = call_rofi_dmenu(options=[*_config], abort=True)
    _config = _config[section_selected]
    _mount_point, _secret_path = _config["mount_point"], _config["secret_path"]
    client = vault_login(url=_config.get("url"), role_id=_config.get("role_id"), secret_id=_config.get("secret_id"))
    if client and client.is_authenticated():
        user_selection = parse_vault_path(client=client, mount_point=_mount_point, secret_path=_secret_path)
        _secret = client.secrets.kv.v2.read_secret_version(
            mount_point=_mount_point,
            path=f"{_secret_path}/{user_selection}",
            raise_on_deleted_version=False,
        )["data"]["data"]
        key_selected = call_rofi_dmenu(options=["All"] + [*_secret], abort=True)
        if key_selected == "All":
            print(_secret)
        else:
            secret_for_user = _secret[key_selected]
            if which("xsel"):
                copy_to_clipboard(str.encode(secret_for_user))

            print(secret_for_user)


if __name__ == "__main__":
    main()
