
Changelog
=========

0.1.3
^^^^^

April 15, 2019

- Enable FOSSA automated license and vulnerability management
- Remove Sphinx from requirements

0.1.2
^^^^^

April 12, 2019

- Enabled interactive modules by restoring stdin to tty
- Added modules: analyze/disassemble/x86, analyze/disassemble/x64
- Added images: tools/radare2
- Changed image: tools/capstone (and thus modules: disassemble/) to return only instructions, nothing else - leave the formatted disassembly to analyze/disassemble/
- Enabled test.py to handle errors gracefully

0.1.1
^^^^^

April 07, 2019

- Refactored to consider docker (and other) module extensions as mixins
- Adjusted existing docker modules to use DockerExtension
- Added auto-generating extension documentation
- Added IO context manager to DockerExtension
- Added images: tools/keystone, tools/capstone
- Added extensions: AssemblyExtension, DisassemblyExtension
- Added modules: assemble/x86, assemble/x64, disassemble/x86, disassemble/x64

0.0.3
^^^^^

April 07, 2019

- Enabled generator output for python interface
- Fixed utility absolute path calculation
- Added unit tests for bash and python interfaces
- Added modules: encode/hex, decode/hex
- Improved options available to existing msfvenom-based modules
- Added ability to handle null data value (for python interface)

0.0.2
^^^^^

April 06, 2019

- Slightly increased verbosity of README.md
- Increased version accuracy in documentation
- Added ability to handle a module that produces no results
- Module now prepopulates self.options with defaults from usage argument parser
- Increased coverage and verbosity of tests in existing modules
- Added ability to test a single module at a time


0.0.1
^^^^^

April 04, 2019

- Initial upload