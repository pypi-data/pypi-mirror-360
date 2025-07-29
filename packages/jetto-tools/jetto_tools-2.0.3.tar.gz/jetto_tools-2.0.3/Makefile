# makefile for jetto-pythontools library
PYTHON?=python
PIP?=pip
ECHO?=$(shell which echo) -e
PRINTF?=$(shell which printf)

# Variables required for release and bugfix options
PROJECT=jetto-pythontools
PACKAGE=jetto_tools

# Other variables
SUBDIRS:=

#####################################################

.PHONY: default help all clean sdist bdist wheel docs install_package_jintrac install_module realclean

default: install_package_jintrac

help:
	@$(ECHO) "Recipes:"
	@$(ECHO) "  sdist                       - build package for source distribution"
	@$(ECHO) "  bdist                       - build package for binary distribution"
	@$(ECHO) "  wheel                       - build package for binary wheel distribution"
	@$(ECHO) "  docs                        - build documentation for package"
	@$(ECHO) "  clean                       - remove all build, test, doc, and Python artifacts"
	@$(ECHO) "  realclean                   - clean and remove build distributions "
	@$(ECHO) ""
	@$(ECHO) "Environment variables:"
	@$(ECHO) "  PYTHON                      - Python binary to use for commands [default: "$(shell grep -e PYTHON?\= Makefile | cut -d\= -f2)"]"
	@$(ECHO) "  PIP                         - Pip binary to use for commands [default: "$(shell grep -e PIP?\= Makefile | cut -d\= -f2)"]"
	@$(ECHO) "  JINTRAC_PYTHON_INSTALL_DIR  - JINTRAC install directory [default: "$(shell grep -e JINTRAC_PYTHON_INSTALL_DIR?\= Makefile | cut -d\= -f2)"]"
	@$(ECHO) "  PYTHONTOOLS_EXTRAS          - Extras to install [default: "$(shell grep -e PYTHONTOOLS_EXTRAS?\= Makefile | cut -d\= -f2)"]"

# Call `pip install` to install the package into /common/sim/jetto-pythontools/$VERSION_TAG/
all:
	@echo 'Nothing to compile for $(PROJECT)'

clean:
	@echo 'Cleaning $(PROJECT)...'
	$(PYTHON) setup.py clean --all
	$(MAKE) -C docs $@


# Build a 'sdist' or 'installable source distribution' with setuptools
# This creates a sdist package installable with pip
# On pip install this will re-compile from source compiled components
sdist:
	python setup.py sdist

# Build a 'bdist' or 'installable binary distribution' with setuptools
# This creates a bdist package installable with pip
# This should be pip-installable on the system it was compiled on
# Not recommended to use this! Use wheels instead
bdist:
	python setup.py bdist

# Build a 'wheel' or 'installable universial binary distribution' with setuptools
# This creates a wheel that can be used with pip
wheel:
	python setup.py bdist_wheel

# Build documentation using Sphinx
docs:
	$(MAKE) -C docs html

# Get the current version.
# The name will be generated from git, i.e.
# jetto_tools-0.1.dev240+g95f5f13.d20200904.tar.gz
# See https://pypi.org/project/setuptools-scm/
# Falls back to `JETTO_PYTHONTOOLS_VERSION` env variable if setup.py can't figure it out
# Falls back to 0.0.0 if _that_ does not exist
VERSION_STRING=$(shell $(PYTHON) setup.py --version)
WHEEL_NAME:=$(PACKAGE)-$(VERSION_STRING)-py3-none-any.whl
SDIST_NAME:=$(PACKAGE)-$(VERSION_STRING).tar.gz

# Install package in the common JINTRAC Python library directory
# As we know that we use py3 and do not have compiled components
# We can guess our generated wheel name
# EasyBuild pip installs like so: AL_CYTHON_VERSION=0.1.0 FORCE_USE_CYTHON=True pip install --prefix=/home/ITER/vandepk/.local/easybuild/software/AL-Cython/0.1.0-foss-2020a-Python-3.8.2  --no-deps  --ignore-installed  --no-build-isolation  .⋅
JINTRAC_PYTHON_INSTALL_DIR?=install
PYTHONTOOLS_EXTRAS?='gui,test,netcdf'
install_package_jintrac: wheel
	@echo [INFO] Installing version '$(VERSION_STRING)'
	@echo [INFO] With extras $(PYTHONTOOLS_EXTRAS)
	@echo [INFO] to $(JINTRAC_PYTHON_INSTALL_DIR)
	@echo [INFO] Assuming generated wheel is '$(WHEEL_NAME)'
	@echo [DEBUG] setuptools version=$(shell python -c "import setuptools; print(setuptools.__version__)")
	@echo [DEBUG] setuptools SCM detected version=$(shell python -c "from setuptools_scm import get_version; print(get_version(root='.'));")
	@echo [DEBUG] wheel version=$(shell python -c "import wheel; print(wheel.__version__)")
	PYTHONUSERBASE=$(JINTRAC_PYTHON_INSTALL_DIR) pip install dist/$(WHEEL_NAME)[$(PYTHONTOOLS_EXTRAS)] --cache-dir=$(JINTRAC_PYTHON_INSTALL_DIR)/pip_cache --user --upgrade

PYTHON_MODULE_DIR?=modules/jintrac-pylib/
# Deploy the module file to /common/sim/jetto-pythontools/modules
# Replace the TCL env variable by a hardcoded string dependening on the Python version
# This should be at least Python 3.7
# This assumes the JINTRAC_PYTHON_INSTALL_DIR environment variable is available on module load
PYTHON_VERSION?=3.7
install_module:
	mkdir -p $(PYTHON_MODULE_DIR)
	cat jintrac-pylib.tcl | sed --expression='s%$$env(PYTHON_VERSION)%$(PYTHON_VERSION)%' > $(PYTHON_MODULE_DIR)/heimdall.python$(PYTHON_VERSION)

realclean: clean
	@echo 'Real cleaning $(PROJECT)...'
	rm -f dist/*

#####################################################

# 'make release' and 'make bugfix' procedures

-include $(JINTRAC_DIR)/libs/release.mk
-include $(JINTRAC_DIR)/libs/bugfix.mk
