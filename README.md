[![Documentation Status](https://readthedocs.org/projects/lets/badge/?version=latest)](https://lets.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/johneiser/lets.svg?branch=master)](https://travis-ci.com/johneiser/lets)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fjohneiser%2Flets.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fjohneiser%2Flets?ref=badge_shield)

# lets

A modular framework for arbitrary action, **lets** enables tasks of varying complexity to be chained together with a consistent and simple interface.

Each module accepts input and options, executes some functionality, and returns some output.

```
[input] | lets <module> [options]
```

In this manner, modules can be *chained* together, allowing completely unrelated functionality to work together seamlessly.  Modules can be as simple as base64 encoding or reasonably complex with docker integration.

To learn more, take a look at the [docs](https://lets.readthedocs.io/en/latest/index.html).

## Requirements

- Linux (tested with Ubuntu 16.04)
- [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/>)
- Python >= 3.5

## Install

It is highly recommended that you use a [python virtual environment](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) for this project; then use *pip* to install the requirements.

```
$ git clone https://github.com/johneiser/lets
$ cd lets
~/lets $ pip install -r requirements.txt
```

## Usage

Refer to the [docs](https://lets.readthedocs.io/en/latest/usage.html)

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fjohneiser%2Flets.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fjohneiser%2Flets?ref=badge_large)