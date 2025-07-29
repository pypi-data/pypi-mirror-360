import sys
from pathlib import Path
from subprocess import run

# find the operating system
if sys.platform.startswith("linux"):
    ops = "Linux"
elif sys.platform.startswith("win"):
    ops = "Windows"
elif sys.platform.startswith("darwin"):
    ops = "MacOS"
else:
    ops = "Unknown OS"
# PATHS
home = Path().home().expanduser()
zsh = home / ".zshenv"
bsh = home / ".bash_completion"
# autocomplete text for bashrc or zshrc
text = "\n# BIPackage Autocomplete\n"
text += 'eval "$(register-python-argcomplete bip)"\n'
bshfile = str(Path.home() / ".bashrc")
# bshfile = "deneme.sh"


def _tab_autocomplete_mac():
    """Tab autocomplete for macOS."""
    command = ""
    command += "autoload -U bashcompinit\n"
    command += "bashcompinit\n"
    command += 'eval "$(register-python-argcomplete bip)"\n'
    command += 'eval "$(register-python-argcomplete bipipe)\n'
    # run([command])


def _check_bashrc():
    with open(bshfile) as b:
        bashrc = b.read()

    return text in bashrc


def _tab_autocomplete_linux():
    """Tab autocomplete for Linux."""
    if not (zsh.exists() and bsh.exists()):
        activate = "activate-global-python-argcomplete"
        run([activate])

    if not _check_bashrc():
        with open(bshfile, "a") as f:
            f.write(text)


def _tab_autocomplete():
    if ops == "Linux":
        _tab_autocomplete_linux()
    elif ops == "MacOS":
        _tab_autocomplete_mac()
    else:
        pass


if __name__ == "__main__":
    _tab_autocomplete()
