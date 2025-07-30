# Bump-Setup
**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined
)[⚡️](https://readwithai.substack.com/s/technical-miscellany)[🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

A command-line tool to bump the version in place a `setup.py`  bumping major, minor, or patch versions.

## Notivation
I got bored of bumping versions but hand so made this tool.

## Alternatives and prior work
There is a tool called [bumpversion](https://github.com/peritus/bumpversion) which is quite similar but wants to take the files that get modified.


## Installation
You can install `bump-setup`  using [pipx](https://github.com/pypa/pipx):

```bash
pip install bump-setup
```
## Usage
To bump the version in setup.py, run the following command:
```bash
bump-setup <major|minor|patch>
```
## Examples
```bash
bump-setup major  # Increments the major version
bump-setup minor  # Increments the minor version
bump-setup patch  # Increments the patch version
```

## About me
I am **@readwithai**. I create tools for reading, research and agency sometimes using the markdown editor [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

I also create a [stream of tools](https://readwithai.substack.com/p/my-productivity-tools) that are related to carrying out my work. There are various python tools here.

I write about lots of things - including tools like this - on [X](https://x.com/readwithai).
My [blog](https://readwithai.substack.com/) is more about reading and research and agency.
