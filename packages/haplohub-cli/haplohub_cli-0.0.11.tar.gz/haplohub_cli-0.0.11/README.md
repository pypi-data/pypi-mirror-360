# HaploHub CLI

HaploHub is a platform for haplotype data storage and analysis. This CLI provides a way to interact with the HaploHub API.

## Installation

To install the CLI, run the following command:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install haplohub-cli
```

You can ensure that the CLI is installed correctly by running the following command:

```bash
haplohub version

# HaploHub CLI version 0.1.0
```

## Usage

```bash
haplohub --help
```

### Login

The first time you run the CLI, you will be prompted to login.

```bash
haplohub login
```

This will open a browser window to the HaploHub login page. Once you login, you will be redirected to the CLI.
```bash
Your browser has been opened to authenticate with HaploHub.

    https://xxx.us.auth0.com/authorize...

Successfully authenticated with HaploHub.
```
