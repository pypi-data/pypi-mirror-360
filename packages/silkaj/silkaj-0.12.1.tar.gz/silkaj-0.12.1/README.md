<img src="https://git.duniter.org/clients/python/silkaj/raw/main/docs/images/silkaj_logo.svg" width="250" />

# Silkaj

[![Version](https://img.shields.io/pypi/v/silkaj.svg)](https://pypi.python.org/pypi/silkaj)
[![License](https://img.shields.io/pypi/l/silkaj.svg)](https://pypi.python.org/pypi/silkaj)
[![Python versions](https://img.shields.io/pypi/pyversions/silkaj.svg?logo=python&label=Python&logoColor=gold)](https://pypi.python.org/pypi/silkaj)
[![Code format](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Coverage report](https://git.duniter.org/clients/python/silkaj/badges/main/coverage.svg)](https://silkaj.duniter.org/latest/coverage/)
[![Website](https://img.shields.io/website/https/silkaj.duniter.org.svg)](https://silkaj.duniter.org)
[![Dev pipeline status](https://git.duniter.org/clients/python/silkaj/badges/main/pipeline.svg)](https://git.duniter.org/clients/python/silkaj/)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](http://www.mypy-lang.org/)
[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)

Command line client for Ğ1 libre-currency powered by Duniter

- [Website](https://silkaj.duniter.org)

## Install

### Distribution

Install with your favorite package manager. See below the [packaging status paragraph](#packaging-status).

### Pipx

If you want a more recent version [install with pipx](https://silkaj.duniter.org/latest/install/):

```bash
sudo apt install pipx
pipx install silkaj
```

### Docker images

There is two kind of images. One build with `pip` for user purposes, and one using Poetry for developer purposes.

- [Docker images](https://silkaj.duniter.org/latest/contributing/container_usage/)

### For contributing purposes

- [Install the Poetry development environment](https://silkaj.duniter.org/latest/contributing/install_poetry/)
- Check out the [contributing guidelines](https://silkaj.duniter.org/latest/contributing/)

## Usage

- Get help usage with `-h` or `--help` options, then run:

```bash
silkaj <sub-command>
```

Silkaj command line interface (CLI) is structured by groups of commands:

```sh
silkaj blockchain -h
silkaj money -h
silkaj money transfer -h
silkaj wot revocation -h
```

You can find commands at the root, such as `silkaj license`

- Will automatically request and post data on https://g1.duniter.org/node/summary official Ğ1 endpoint.

- Specify a custom node with `-ep` option where `<port>` and `<path>` are optional:

```bash
silkaj -ep <hostname>:<port>/<path> <sub-command>
```

## Features

### Currency information & blockchain exploration

- Check the present currency information stand
- Display current proof of work difficulty level to generate the next block
- Explore the blockchain block by block

### Money management

- Transaction emission
    - Multi-recipients transaction support
    - Read transaction recipients and amounts from a file
- Consult wallets balances
- Consult wallet history

### Web-of-Trust management

- Look up for public keys and identities
- Check sent and received certifications and consult the membership status of any given identity in the Web of Trust
- Certification emission
- Membership emission
- Revocation file handling
- [DeathReaper: exclusions reports on Discourse forums](https://silkaj.duniter.org/latest/usage/deathreaper/)

### Authentication

- Authentication methods: Scrypt, Seedhex, PubSec, and (E)WIF

### Others

- Account storage
- Display Ğ1 monetary license
- Public key checksum

## Wrappers

- [Multi-recipients transfers and automation](https://silkaj.duniter.org/latest/usage/multi-recipients_transfers_and_automation)
- [Transaction generator written in Shell](https://gitlab.com/jytou/tgen)
- [Ğ1Cotis](https://git.duniter.org/matograine/g1-cotis)
- [G1pourboire](https://git.duniter.org/matograine/g1pourboire)
- [Ğ1SMS](https://git.duniter.org/clients/G1SMS/)
- [Ğmixer](https://git.duniter.org/tuxmain/gmixer-py/)
- [printqrjune](https://github.com/jbar/printqrjune)

### Dependencies

Silkaj is based on following Python modules:

- [Click](https://click.palletsprojects.com/): Composable command line interface toolkit
- [DuniterPy](https://git.duniter.org/clients/python/duniterpy/): Most complete client oriented Python library for Duniter/Ğ1 ecosystem
- [Pendulum](https://pendulum.eustace.io/): Datetimes made easy
- [texttable](https://github.com/foutaise/texttable/): Creation of simple ASCII tables

### Names

I wanted to call that program:

- bamiyan
- margouillat
- lsociety
- cashmere

I finally called it `Silkaj` as `Silk` in esperanto.

## Packaging status

[![Packaging status](https://repology.org/badge/vertical-allrepos/silkaj.svg?columns=2)](https://repology.org/project/silkaj/versions)
