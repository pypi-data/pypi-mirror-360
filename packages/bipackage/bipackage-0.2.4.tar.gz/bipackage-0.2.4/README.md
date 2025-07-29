# BIPackage
Handles basic bioinformatics operations with a python package structure


## INSTALLATION


pip
```shell
pip install bipackage
```

pipx
```shell
pipx install bipackage
```

conda
```shell
conda env create -f env.yaml
```



## USAGE


On command line,
```shell
bip <subcommand> [params]
```
On python,
```python
import bipackage as bip

bip.function(args*,kwargs**)
```

Note that `params` are the parameters for the __subcommand__.

## TAB AUTOCOMPLETION

To enable tab autocompletion, run the following command:

bashrc (For Linux)   
run bip once and restart the shell
```shell
bip
```

add to zshrc (For MacOS)
```shell
autoload -U bashcompinit
bashcompinit
eval "$(register-python-argcomplete bip)"
```

This will enable tab autocompletion for the `bip` command.