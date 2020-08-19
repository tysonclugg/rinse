Changelog
=========

0.5.0
-----
* Allow passing a ``timeout`` argument to the client.
* Add Python 3.6, 3.7 and 3.8 to test builds.

0.4.0
-----
* Use ``@cached_property`` to simplify property code.
* Fix ``AttributeError`` when debugging.
* Include missing XSD files in wheel distributions.
* Ensure XSD files exist in distributed files via tox test suite
  options.

0.3.0
-----
* Add 'SOAPAction' header to requests.
* Expose requests.Session.
* Include missing XSD files in package data.
* Add Python 3.4 to test builds.

0.2.0
-----
* Declared BETA status.
* Homepage URL set to https://rinse.readthedocs.org/.

0.1.3
-----
* Add links to README.

0.1.2
-----
* Added Sphinx documentation.

0.1.1
-----
* Add ElementMaker wrapper class and safe_parse_url function.
* Add travis-ci.org build configuration.
* Split features into submodules.

0.1.0
-----
* Support for WSDL.
* Simplified usage through use of SoapClient and SoapMessage classes.

0.0.5
-----
* Pylint/PEP8/pychecker fixes.

0.0.4
-----
* Remove reference to stale source (client.py).

0.0.3
-----
* Add defused.xml to requirements.

0.0.2
-----
* Validate messages against SOAP 1.1 Envelope and SOAP 1.2 XML schema.
* Add support for WSSE (Security) headers.

0.0.1
-----
* Generate SOAP requests and parse SOAP 1.1 responses.
