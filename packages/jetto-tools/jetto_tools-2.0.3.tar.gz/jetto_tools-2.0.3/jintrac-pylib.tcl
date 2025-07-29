#%Module########################################################################
##
## jintrac modulefile for the Python tools
##
################################################################################
proc ModulesHelp { } {
    puts stderr "   Loads the environment for Python tools of JINTRAC on Heimdall."
    puts stderr "   "
    puts stderr "   To load this module, type:"
    puts stderr "   "
    puts stderr "      module use /home/OWNER/jintrac-pylib/modules"
    puts stderr "      module load jintrac-pylib/heimdall.PYTHON_VERSION"
    puts stderr "   "
    puts stderr "   where OWNER and PYTHON_VERSION define which module to load."
    puts stderr "   PYTHON_VERSION is for example python37."
    puts stderr "   "
}

module-whatis   "loads the Heimdall environment for Python tools of JINTRAC"

# _probably_ A JINTRAC module does not need to be loaded
# Needs python loaded. Versions for different compilers under investigation.
prereq python/$env(PYTHON_VERSION)

# Assume recent pip, install packages using isolated build and the new dependency resolver
# For compiled components this might result in broken packages! TODO: Investigate
# pip install --isolated --upgrade --use-feature=2020-resolver --target ~/jintrac-pylib/python3.7/site-packages/ .
# This is how EasyBuild builds packages (sorry)

# Let JINTRAC binaries take precedence over other-install binaries
prepend-path PYTHONPATH $env(JINTRAC_PYTHON_INSTALL_DIR)/lib/python$env(PYTHON_VERSION)/site-packages/
prepend-path PATH $env(JINTRAC_PYTHON_INSTALL_DIR)/bin/
