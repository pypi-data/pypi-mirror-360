# `avysignal`

> ## 🚧 Work in progress 🚧

[![PyPI - Version](https://img.shields.io/pypi/v/avysignal.svg)](https://pypi.org/project/avysignal)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/avysignal.svg)](https://pypi.org/project/avysignal)

This project contains utilities for avalanche detection using seismic and infrasound data.

## Installation

Create and activate a virtual environment and then install `avysignal`:

```shell
pip install avysignal
```

Beamforming requires some additional dependencies. You can install them like so:

```shell
pip install avysignal[beamforming]
```

## Usage

Download and extract the example data

```shell
./scripts/download_example_data.sh
```

See the [example scripts](examples/signal_processing)

## Contributing

### Project Structure

```
avysignal/
├── archive/                # Legacy workflows (In particular firenze matlab implementation)
├── examples/               # Example data and usage demonstrations
│   ├── data/               # Sample seismic data files (.mseed)
│   └── signal_processing/  # Example processing scripts. Start here!
├── scripts/                # Utility and one-off scripts
├── src/avysignal/          # Main package source code
│   ├── plotting/           # Visualization utilities
│   ├── resources/          # Static metadata
│   │   └── stations/       # XML metadata files for sensor networks
│   ├── signal_processing/  # Signal processing algorithms such as beamforming.
│   └── slf_utils/          # SLF-specific utilities
```
