
Changelog
=========

2.0.2
^^^^^

April 12, 2020

- Remove version references after install
- Increase logging threshold when testing
- Changed ModuleNotFoundError to ImportError, for python 3.5 compatibility

2.0.1
^^^^^

April 11, 2020

- Fix github integrations
- Sort module explorer data

2.0.0
^^^^^

April 10, 2020

- Completely rewritten
- Added iterate and generate
- Added module explorer (https://johneiser.github.io/lets/)
- Changed HTTP API from django to flask

1.0.3
^^^^^

August 24, 2019

- Add pip3 as a requirement in documentation

1.0.2
^^^^^

August 18, 2019

- Minor documentation fixes
- Fixed missing import in combined_windows_messagebox workflow

1.0.1
^^^^^

August 17, 2019

- Changed sslscan base image from debian to kali
- Removed bash coloring from README.md, again

1.0.0
^^^^^

August 17, 2019

- Added modules: generate/support/completion/bash, listen/serve/lets/http (api)
- Moved default temporary directory from /tmp to <package>/data
- Added LETS_NOCACHE environment variable
- Split listen/serve/database/postgres from launch/c2/metasploit module
- Added resource files and commands as input to launch/c2/metasploit module
- Removed encrypt/rc4 module, key usage too unclear
- Modules can now limit the platforms on which they should be made available
- Docker extensions now check for docker and warn of its absence
- Docker ResourceWarning "unclosed" errors are now ignored during unit tests
- Extended 'confirm' log option to info
- Removed contenttpes app from api
- Changed lets.list() to produce a generator
- Moved main functionality to lets.__main__
- Moved test functionality to lets.__test__
- Added setup.py and MANIFEST.in for pip installation
- Updated documenation and workflows to match new pip installation

0.2.7
^^^^^

August 16, 2019

- Added 'confirm' option to warning and error logs
- Added environment-variable customization capability and documentation 

0.2.6
^^^^^

August 14, 2019

- Added modules: listen/serve/http
- Added modules: launch/c2/metasploit, generate/payload/msfvenom
- Added workflow: combined_windows_messagebox.py
- Replaced local/kali/metasploit image with metasploitframework/metasploit-framework:latest
- Added help(path), list(), and exists(path) to python api
- Removed more powershell tests breaking due to missing variables in docker container

0.2.5
^^^^^

August 12, 2019

- Labeled additional modules that won't work with api as interactive
- Restored zlib compatibility with Python 3.5

0.2.4
^^^^^

August 11, 2019

- Added modules: assert/hash, calculate/hash
- Added modules: scan/dns/subdomains, scan/http/directories
- Added images: local/kali/gobuster
- Refactored powershell obfuscation modules

0.2.3
^^^^^

August 4, 2019

- Added modules: launch/scanner/openvas

0.2.2
^^^^^

August 3, 2019

- Removed codecov
- Added images: local/tools/invoke-obfuscation, local/linux/sslscan
- Added modules: encode/powershell/obfuscate/*, format/powershell/obfuscate/*, scan/ssl/config
- Improved testing on various encode and format modules
- Simplified commands various docker modules with 'entrypoint'

0.2.1
^^^^^

July 27, 2019

- Refactored docker extension to use a function decorator for image preparation
- Added codecov
- Moved Django database to in-memory only
- Added modules: encrypt/rc4
- Added modules: format/bash/python, format/bash/osx/x86, format/bash/osx/x64
- Added modules: format/osx/x64/python, format/osx/x86/python
- Added modules: format/python/bash

0.1.11
^^^^^^

July 5, 2019

- Added pycryptodome to requirements
- Allowed for use of docker extension without prep
- Modified some tests to exclude irrelevant information
- Added modules: encode/bash/compress, encode/python/compress, encode/powershell/compress
- Added modules: encode/python/rc4, encode/powershell/rc4

0.1.10
^^^^^^

July 2, 2019

- Hide samples from doc module list
- Added modules: encode/bash/base64, encode/python/base64, encode/powershell/base64
- Added "_" directories for private development

0.1.9
^^^^^

July 1, 2019

- Added modules: scan/http/version, scan/dns/lookup
- Allow for global specification of temporary directory

0.1.8
^^^^^

June 21, 2019

- Moved some docker images to "kali" folder
- Moved docker cleanup from __exit__ to __del__

0.1.7
^^^^^

May 16, 2019

- Moved local images to images/local
- Adjusted sample api workflow
- Replaced django SECRET_KEY with random generator
- Removed some default django accessories from api
- Improved logging for docker image retrieval

0.1.6
^^^^^

May 15, 2019

- Fixed .travis.yml (update ubuntu dist for sqlite3 upgrade)
- Fixed requirements.txt (django produced "pkg-resources==0.0.0")

0.1.5
^^^^^

May 14, 2019

- Enabled input validation for various modules
- Added [bool]interactive attribute to module
- Added Django REST API with tests
- Added licenses for included docker images
- Added modules: listen/serve/smb

0.1.4
^^^^^

April 15, 2019

- Restore Sphinx (readthedocs failed)

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
