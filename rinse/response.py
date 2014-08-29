"""SOAP client."""
import collections
from rinse import NS_MAP
from rinse.util import safe_parse_string


class Response(object):

    """Rinse Response object."""

    def __init__(self, response):
        """Response init."""
        self._response = response
        # parse response
        self._doc = safe_parse_string(response.content)
        self._body = self._doc.xpath(
            '/soapenv:Envelope/soapenv:Body', namespaces=NS_MAP,
        )[0]

    def __str__(self):
        """String representation of Response is the HTTP body content."""
        return self._response.content.decode('utf-8')


RinseResponse = collections.namedtuple('RinseResponse', ['response', 'doc'])
