import os
import sys
from subprocess import Popen, PIPE
from rofi import Rofi
import yaml
import dmenu


def copy_to_clipboard(text: bytes):
    p = Popen(["xsel", "-i"], stdin=PIPE)
    p.communicate(input=text)


def which(program: str):
    def is_exe(_fpath):
        return os.path.isfile(_fpath) and os.access(_fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def call_rofi_dmenu(options: list, abort: bool = True, prompt: str = None):
    if which("rofi"):
        _rofi = Rofi()
        index, key = _rofi.select(prompt or "Select:", options)
        if key == -1:
            sys.exit(0)
        return options[index]

    else:
        user_select = dmenu.show(options, lines=30, case_insensitive=True, fast=True, prompt=prompt)
        if not user_select and abort:
            sys.exit(0)
        return user_select


def parse_yaml_user_config():
    config_file = os.path.join(os.path.expanduser("~"), ".config", "vaultrun", "config.yaml")
    with open(config_file) as fs:
        _config = yaml.safe_load(fs)

    return _config
