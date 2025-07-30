# sungazer

**Documentation**: https://sungazer.readthedocs.org

`sungazer` is a web based interface to the monitoring data output by the SunPower PVS6
monitoring device installed with a SunPower solar insallation.

## Installation

`sungazer` supports Python 3.9+.

To install from PyPI:

```shell
pip install sungazer
```

## Usage

Example usage of the command line interface:

```bash
# Get help
sungazer --help
sungazer device --help
sungazer network get-power-production --help

# Use JSON output (default)
sungazer status get-ess

# Use table output
sungazer status get-ess --output table
```

## Autocomplete

To enable autocomplete of the `sungazer` command line interface, do:

```bash
# For bash
echo 'eval "$(_SUNGAZER_COMPLETE=bash_source sungazer)"' >> ~/.bashrc

# For zsh
echo 'eval "$(_SUNGAZER_COMPLETE=zsh_source sungazer)"' >> ~/.zshrc

# For fish
echo 'eval (env _SUNGAZER_COMPLETE=fish_source sungazer)' >> ~/.config/fish/config.fish
```
