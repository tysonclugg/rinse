rinse
=====

Rinse_ is a Python SOAP client using lxml_, requests_ and defusedxml_.

.. image:: https://img.shields.io/pypi/v/rinse.svg
    :target: https://pypi.python.org/pypi/rinse/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/rinse.svg
    :target: https://pypi.python.org/pypi/rinse/
    :alt: Latest Version

.. image:: https://readthedocs.org/projects/rinse/badge/?version=latest
    :target: https://rinse.readthedocs.org/
    :alt: Documentation

.. image:: https://img.shields.io/travis/tysonclugg/rinse.svg
    :target: https://travis-ci.org/tysonclugg/rinse
    :alt: Build Status

.. image:: https://img.shields.io/coveralls/tysonclugg/rinse.svg
   :target: https://coveralls.io/github/tysonclugg/rinse
   :alt: Coverage

Rinse_ works with both Python 2 and Python 3.  Continuous integration 
testing is performed against the latest python 2.7, python 3.3 and
python 3.4 releases.

The name "rinse" refers to its dictionary meaning, such as the act of 
removing soap suds from something using water.

The goal of rinse is to be a SOAP client that focuses on the minimum set 
of features required to make SOAP calls to services over HTTP/HTTPS.  
Support for common SOAP extensions including WSA (WS-Addressing) and 
WSSE (WS-Security) is provided.  Rinse supports the WS-I Basic Profile 
Version 2.0 specification *in principle*, but takes a pragmatic approach 
to achieving compliance based upon further goals and constraints 
outlined below.

Using rinse as part of a SOAP service (SOAP server) is *not supported*.  
We recommend servers should use JSON for data interchange over RESTful 
HTTP(S) rather than providing SOAP services.  And we're not the only 
ones - Google announced its plans to abandon SOAP way back in 2009.

Security is improved by using the defusedxml_ library to parse XML data 
thereby minimising risks associated with parsing and processing data 
from untrusted sources.  TODO: SSL certificate pinning to ensure that 
clients using rinse only disclose information to and parse information 
from intended servers.

Rinse has support for validating SOAP messages against the schema 
specified in XSD (XML schema definition) format within a given WSDL 
file, but is not capable of generating SOAP service bindings at runtime.  
Future development may provide support for generating bindings from WSDL 
in the form of Python source files.  Dynamic (runtime) binding is 
unlikely to be supported.

.. _Rinse: https://rinse.readthedocs.org/en/latest/
.. _requests: http://docs.python-requests.org/en/latest/
.. _lxml: http://lxml.de/
.. _defusedxml: https://pypi.python.org/pypi/defusedxml
