[![Build Status](https://travis-ci.com/johneiser/lets.svg?branch=master)](https://travis-ci.com/johneiser/lets)

# lets

A modular framework for arbitrary action, **lets** enables tasks of varying complexity to be chained together with a consistent and simple interface.

As a modular framework, each module accepts input and options, executes some functionality, and returns some output.

```
   [input] | lets <module> [options]
```

In this manner, modules can be *chained* together, allowing completely unrelated functionality to work together seamlessly.  Modules can be as simple as base64 encoding or reasonably complex with docker integration.

To learn more, take a look at the [docs](https://lets.readthedocs.io/en/latest/index.html).