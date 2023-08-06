# onesync

## Introduction

Onesync is a linux package and configuration manage tool that help you easily install pre-defined packages and sync configuration between multiple devices

Onesync is still under development at the moment,
what here are what we plan to do:

- [ ] Sync package configuration through cloud drive such as onedrive
- [ ] Install packages using pre-defined commands in onesync.yaml\
- [ ] Providing a terminal textual-user-interface(tui)


## DEV-Plan

### create a bootstrap that does the following:
1. download and install miniconda, create a base env
2. install poetry
3. using poetry to install onesync dependencies to make onesync is usable

## Usage

```bash
onesync install neovim 
onesync sync neovim
```

## Install

onesync would be integrated into the pip system in near future, but for now one can try it with

```bash
git clone git@github.com:raceychan/onesync.git
python -m onesync
```

```python
class Packge:
    def install(self):
        ...
```
