# Pending AI CLI

Command-line interface for accessing the Pending AI Platform - a comprehensive drug discovery platform
enabled by scalable artificial intelligence and quantum mechanics.

## Getting Started

Usage of the Pending AI CLI requires

* an account for the **Pending AI Platform** and
* a locally installed Python version `>=3.9`.

Once installed with

```sh
pip install pendingai
```
successful installation can be verified with

```bash
pendingai --version
```

which is expected to output the name and version of the Pending AI CLI.

## Documentation

Access to the [documentation](https://docs.pending.ai) requires an account for the Pending AI Platform.

## Hidden Options

### Environment

Specify the environment with `--env` or `-e`. Defaults to production, other options are listed
[here](https://github.com/pendingai/pendingai-cli/blob/main/src/pendingai/__init__.py).

### Logging

The verbosity of the logs can be adjusted by providing an int value to the argument `-v`.
Defaults to logging level `ERROR`, values of 1, 2 and 3 change the logging level  to
`WARNING`, `INFO` and `DEBUG`, respectively.

By default, logs are written to a file only. To also show log entries  in the console use the
flag `--log-to-console`.
