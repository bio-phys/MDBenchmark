# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS      = --ignore .doctrees/environment.pickle
SPHINXBUILD     = sphinx-build
SPHINXAUTOBUILD = sphinx-autobuild
SPHINXPROJ      = MDBenchmark
SOURCEDIR       = .
BUILDDIR        = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

build:
	@$(SPHINXBUILD) "$(SOURCEDIR)" "$(BUILDDIR)"

livehtml:
	@$(SPHINXAUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: help build Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
