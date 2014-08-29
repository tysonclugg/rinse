"""Unit tests for rinse package."""
import doctest
import rinse
import rinse.client
import rinse.message
import rinse.response
import rinse.util
import rinse.wsa
import rinse.wsdl
import rinse.wsse
import rinse.xsd


def load_tests(loader, tests, ignore):
    """Load rinse.wsse test suite."""
    tests.addTests([
        doctest.DocTestSuite(rinse),
        doctest.DocTestSuite(rinse.client),
        doctest.DocTestSuite(rinse.message),
        doctest.DocTestSuite(rinse.response),
        doctest.DocTestSuite(rinse.util),
        doctest.DocTestSuite(rinse.wsa),
        doctest.DocTestSuite(rinse.wsdl),
        doctest.DocTestSuite(rinse.wsse),
        doctest.DocTestSuite(rinse.xsd),
    ])
    return tests
