# C: A tool for quick directory traversal with fzf for the `fish` shell

## Description

A simple fish function that help with directory traversal. It is made of 3 commands: `c`, `C`, and `c -s`.
- `c` is a drop-in replacement for `cd` that can display a fuzzy-search interface if the directory doesn't exist
- `C` is meant to replace `cd -` and allows the user to quickly go to recently visited directories
- `c -s` updates the index used by `c`

This script will use the following files in `$HOME`:
- `~/paths`: An index of all the dirs to use for autocomplete
- `~/paths.history`: An index of all the directories that have been visited recently
- `~/paths.ignore`: a list of regex that can be used to filter out entries from the index in ~/paths [Optional]

## Dependencies

This tool requires the packages `sponge` (usually in moreutils) and `fzf` (usually in its own package)

## Examples:

- `c PATH` to go to the path like `cd` and save the new directory in `~/paths.history`
- `c -s` to build an index of the current directory and the subdirectories. Paths that should be ignored can be configured in `~/paths.ignore` and in the `c.fish` file itself
- `c PSEUDO_PATH` to open a fuzzy search dialog on the content of the index
- `C PSEUDO_PATH` to open a fuzzy search dialog on the last 100 directories visited via `c`
