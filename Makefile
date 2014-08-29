SOURCES := \
	rinse/__init__.py \
	rinse/client.py \
	rinse/message.py \
	rinse/response.py \
	rinse/util.py \
	rinse/wsa.py \
	rinse/wsdl.py \
	rinse/wsse.py \
	rinse/xsd.py

DOCS := \
	README.rst \
	docs/index.rst \
	docs/rinse.rst \
	docs/rinse.client.rst \
	docs/rinse.message.rst \
	docs/rinse.response.rst \
	docs/rinse.util.rst \
	docs/rinse.wsa.rst \
	docs/rinse.wsdl.rst \
	docs/rinse.wsse.rst \
	docs/rinse.xsd.rst

.PHONY: all test clean clean-docs

all: docs

test:
	python setup.py test

clean: clean-docs

clean-docs:
	rm -rf docs/_build/

docs: docs/_build/

docs/_build/: ${DOCS} ${SOURCES} docs/conf.py setup.py
	rm -rf docs/_build/
	cd docs && $(MAKE) html doctest
