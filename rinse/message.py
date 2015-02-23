"""SOAP client."""
from __future__ import print_function
from lxml import etree
import requests
from rinse import NS_SOAPENV
from rinse.util import ElementMaker


class SoapMessage(object):

    """SOAP message.

    >>> from rinse.message import SoapMessage
    >>> from lxml import etree
    >>> from rinse.util import printxml
    >>> body = etree.Element('test')
    >>> msg = SoapMessage(body)
    >>> printxml(msg.etree())
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header/>
      <soapenv:Body>
        <test/>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    elementmaker_cls = ElementMaker

    def __init__(self, body=None):
        """Set base attributes."""
        # XML namespace map
        self._nsmap = {}
        # cache of lxml.etree.ElementMaker instances by namespace prefix
        self._elementmaker_cache = {}
        # SOAP headers
        self.headers = []
        # SOAP body
        self.body = body
        # HTTP headers
        self.http_headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
        }

    def __getitem__(self, key):
        """Dict style access to http_headers."""
        return self.http_headers[key]

    def __setitem__(self, key, val):
        """Dict style access to http_headers."""
        self.http_headers[key] = val

    def __delitem__(self, key):
        """Dict style access to http_headers."""
        del self.http_headers[key]

    def elementmaker(self, prefix, url):
        """Register namespace and return ElementMaker bound to the namespace."""
        try:
            old_url = self._nsmap[prefix]
            if url != old_url:
                raise ValueError(
                    'Namespace {!r} already defined as {!r}.'.format(
                        prefix,
                        old_url,
                    ),
                )
        except KeyError:
            self._nsmap[prefix] = url
            self._elementmaker_cache[prefix] = self.elementmaker_cls(
                namespace=url, nsmap=self._nsmap,
            )
        return self._elementmaker_cache[prefix]

    def etree(self):
        """Generate a SOAP Envelope message with header and body elements."""
        soapenv = self.elementmaker('soapenv', NS_SOAPENV)
        return soapenv.Envelope(
            soapenv.Header(*self.headers),
            soapenv.Body(self.body),
        )

    def tostring(self, **kwargs):
        """Generate XML representation of self."""
        return etree.tostring(self.etree(), **kwargs)

    def request(self, url=None, action=None):
        """Generate a requests.Request instance."""
        headers = self.http_headers.copy()
        if action is not None:
            headers['SOAPAction'] = action
        return requests.Request(
            'POST',
            url or self.url,
            data=self.tostring(pretty_print=True, encoding='utf-8'),
            headers=headers,
        )

    def __bytes__(self):
        """Generate XML (bytes)."""
        return self.tostring()

    def __str__(self):
        """Generate XML (unicode)."""
        return self.tostring(encoding='unicode')
