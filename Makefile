ENV = $$VIRTUAL_ENV

# older version was 1.0.7rel
BASEMAP_VERSION = 1.1.0
BASEMAP_URL = https://github.com/matplotlib/basemap/archive/v$(BASEMAP_VERSION).tar.gz
BASEMAP = basemap-$(BASEMAP_VERSION)

$(BASEMAP).tar.gz:
	wget $(BASEMAP_URL) -O $@

$(BASEMAP): $(BASEMAP).tar.gz
	mkdir -p $@
	tar -zxf $(BASEMAP).tar.gz -C $@ --strip-components 1

GEOS_DIR = $(abspath $(ENV))
GEOS_SO = $(GEOS_DIR)/lib/libgeos.so
GEOS_SRC = $(BASEMAP)/geos-3.3.3
$(GEOS_SO):
	@echo 'installing geos...'
	cd $(GEOS_SRC) && GEOS_DIR="$(GEOS_DIR)" && \
		./configure --prefix=$(GEOS_DIR) && make && make install
geos-install: $(BASEMAP) $(GEOS_SO)

BASEMAP_EGGINFO = $(ENV)/lib/python2.7/site-packages/basemap-$(BASEMAP_VERSION)-py2.7.egg-info
$(BASEMAP_EGGINFO):
	@echo 'installing basemap $(BASEMAP_VERSION)...'
	@[ $(ENV)/bin/python = $(shell which python) ] || \
		{ echo "expected python to be at $(ENV)/bin/python but it's at $(shell which python)"; exit 1; }
	cd $(BASEMAP) && GEOS_DIR=$(GEOS_DIR) python setup.py install

basemap-install: geos-install $(BASEMAP_EGGINFO)
	pip show basemap

.PHONY: basemap-install geos-install
