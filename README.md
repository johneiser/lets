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

- [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/>)
- Python >= 3.5

## Install

Install [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/>).  Make sure to log out and back in for this to take effect.

```
$ curl -fsSL https://get.docker.com | sudo sh
$ sudo usermod -aG docker $USER
```

Install **lets**.

```
$ pip3 install docker-lets
```

Activate **lets** *tab-completion* for bash.

```
$ lets generate/support/completion/bash >> ~/.profile
$ source ~/.profile
```

## Usage

Quickstart:

```
$ echo SGVsbG8gd29ybGQhCg== | lets decode/base64
Hello world!
```

For further usage, refer to the [docs](https://lets.readthedocs.io/en/latest/usage.html)

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fjohneiser%2Flets.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fjohneiser%2Flets?ref=badge_large)