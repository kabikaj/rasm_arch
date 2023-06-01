################################################################################
#
# INSTALLATION AND TESTING FOR DEVELOPMENT
#
# MIT License
# 
# Copyright (c) 2022 Alicia González Martínez and Thomas Milo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

PYTHON := python3

.PHONY : all clean build_resources install install_man_page execute_tests help

all: clean install install_man_page execute_tests

dev_install: clean build_resources install_man_page execute_tests install

clean:
	@echo "\n>> Cleaning resources..."
	$(PYTHON) setup.py clean --all
	find . -name __pycache__ -prune -exec rm -rf {} +
	rm -rf MANIFEST build* dist*
	

build_resources:
	@echo "\n>> Building resources..."
	rm -f resources/mushaf_*.json
	bash scripts/_build_all.sh
		
install:
	@echo "\n>> Installing rasm library..."
	$(PYTHON) -m pip install --ignore-installed -e .

install_man_page:
	@echo "\n>> Installing man page..."
	sudo cp man/rasm-arch.1 /usr/share/man/man1/rasm-arch.1
	sudo gzip -f /usr/share/man/man1/rasm-arch.1
	mandb

execute_tests:
	@echo "\n>> Executing battery of tests..."
	$(PYTHON) tests/test_rasm_arch.py

help:
	@echo "    all"
	@echo "        Clean resources and install package"
	@echo "    install"
	@echo "        install rasm package"
	@echo "    install_man_page"
	@echo "        install man page."
	@echo "    dev_install"
	@echo "        compile data and install rasm package"
	@echo "    build_resources"
	@echo "        build resources"
	@echo "    clean"
	@echo "        remove build and dist"
	@echo "    execute_tests"
	@echo "        execute battery of tests"
	@echo ""
	@echo "usage: make [help] [all] [install] [install_man_page] [clean] [apply_test]"
