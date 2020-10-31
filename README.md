[![Documentation Status](https://readthedocs.org/projects/lets/badge/?version=latest)](https://lets.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/johneiser/lets.svg?branch=master)](https://travis-ci.com/johneiser/lets)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fjohneiser%2Flets.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fjohneiser%2Flets?ref=badge_shield)

# lets

A modular framework for arbitrary action, **lets** enables tasks of varying complexity to be chained together with a simple and consistent interface.

Each module accepts input and options, executes some functionality, and returns some output.

```
[input] | lets <module> [options]
```

In this manner, modules can be *chained* together, allowing completely unrelated functionality to work together seamlessly. Modules can be as simple as base64 encoding or reasonably complex with docker integration.

To learn more, take a look at the [docs](https://lets.readthedocs.io/en/latest/index.html) or explore the [modules](https://johneiser.github.io/lets/).

## Requirements

- [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- python >= 3.5
- python3-pip

## Install

**lets** is built on top of [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/), so make sure it is installed. You may need to log out and back in for this to take effect.

```
$ curl -fsSL https://get.docker.com | sudo sh
$ sudo usermod -aG docker $USER
```

Install **lets**

```
$ pip3 install docker-lets
```

Install **lets** extensions

```
$ git clone https://github.com/johneiser/lets_pentest
$ pip3 install ./lets_pentest
```

Activate **lets** *tab-completion* for bash.

```
$ lets support/autocomplete bash >> ~/.profile
$ source ~/.profile
$ lets sample/my[TAB][TAB]
sample/mydockermodule   sample/mymodule
```

## Usage

Quickstart:

```
$ echo SGVsbG8gd29ybGQhCg== | lets decode/base64
Hello world!
```

For further details, refer to the [docs](https://lets.readthedocs.io/en/latest/usage.html) and [modules](https://johneiser.github.io/lets/).

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fjohneiser%2Flets.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fjohneiser%2Flets?ref=badge_large)
