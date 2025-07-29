
PROJECT_OWNER := AccidentallyTheCable
PROJECT_EMAIL := cableninja@cableninja.net
PROJECT_FIRST_YEAR := 2024
PROJECT_LICENSE := GPLv3
PROJECT_NAME := ycct
PROJECT_DESCRIPTION := You Cant Change That - A File Monitoring and change prevention process
PROJECT_VERSION := 1.1.0

## Enable Feature 'Python'
BUILD_PYTHON := 1
## Enable Feature 'Shell'
BUILD_SHELL := 0
## Enable Feature 'Docker'
BUILD_DOCKER := 0
## Enable python `dist` Phase for Projects destined for PYPI
PYTHON_PYPI_PROJECT := 1
## Additional Flags for pylint. EX --ignore-paths=mypath
PYLINT_EXTRA_FLAGS := 

CHECKSUM_IGNORE := (\.toml|\.service)$$
### Any Further Project-specific make targets can go here

#### CHECKSUM a5f35276ba0c0d867125ced40ea37b60f40a09cce569c5174b7327234fb2bfc9
