"""SOAP client."""
from __future__ import print_function
import collections
import os.path
import pprint
import textwrap

import defusedxml.lxml
from lxml.builder import ElementMaker
from lxml import etree
import requests

RINSE_DIR = os.path.dirname(__file__)
ENVELOPE_XSD = 'soap-1.1_envelope.xsd'

NS_SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'

NS_MAP = {
    'soapenv': NS_SOAPENV,
}


def element_as_tree(element):
    """Convert an element from within an ElementTree to its own tree."""
    # XXX: this is a crude hack, but it works - got any better ideas?
    return safe_parse_string(
        etree.tostring(
            etree.ElementTree(element),
        ),
    )


def safe_parse_string(raw_xml, **kwargs):
    """Safely parse raw XML content into an element tree."""
    try:
        return defusedxml.lxml.fromstring(raw_xml, **kwargs)
    except:
        print(raw_xml)
        raise


def safe_parse_path(xml_path, **kwargs):
    """Safely parse XML content from path into an element tree."""
    return defusedxml.lxml.parse(xml_path, **kwargs)


class SoapMessage(object):

    """SOAP message.

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

    def request(self, url=None):
        """Genereate a requests.Request instance."""
        return requests.Request(
            'POST',
            url or self.url,
            data=self.tostring(pretty_print=True, encoding='utf-8'),
            headers=self.http_headers,
        )

    def __bytes__(self):
        """Generate XML (bytes)."""
        return self.tostring()

    def __str__(self):
        """Generate XML (unicode)."""
        return self.tostring(encoding='unicode')


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


class SchemaCache(collections.defaultdict):

    """Cache of lxml.etree.XMLSchema instances, keyed by XSD basename."""

    def get(self, xsd, xpath=None, namespaces=None):
        """Generate XMLSchema instances as specified."""
        if xsd.startswith('/'):
            pass  # absolute path
        elif ':' in xsd:
            pass  # URL - defused should help protect us.
        else:
            # assume XSD is in res/ subdir of rinse project.
            xsd = os.path.join(RINSE_DIR, 'res', xsd)
        doc = safe_parse_path(xsd)
        if xpath:
            doc = doc.xpath(xpath, namespaces=namespaces)[0]
        self[xsd] = schema = etree.XMLSchema(doc)
        return schema

    def __missing__(self, xsd):
        """Generate XMLSchema instances on demand."""
        return self.get(xsd)


SCHEMA = SchemaCache()


class ElementMakerCache(collections.defaultdict):

    """Cache of ElementMaker instances for the given nsmap."""

    def __init__(self, nsmap):
        """Keep reference to the nsmap we're given."""
        super(ElementMakerCache, self).__init__()
        self.nsmap = {
            name: url
            for name, url
            in list(NS_MAP.items()) + list(nsmap.items())
        }

    def __missing__(self, ns_prefix):
        """Generate ElementMaker instances as required."""
        return ElementMaker(
            namespace=self.nsmap[ns_prefix],
            nsmap=self.nsmap,
        )


PRETTY_PARSER = etree.XMLParser(
    remove_blank_text=True,
)
PRETTY_TEXT_WRAPPER = textwrap.TextWrapper(
    width=78,
    initial_indent='',
    subsequent_indent='        ',
    replace_whitespace=False,
    drop_whitespace=False,
    break_long_words=False,
    break_on_hyphens=False,
)


def printxml(doc):
    """Pretty print an lxml document tree.

    The XML printed may not be exactly equivalent to the doc provided, as blank
    text within elements will be stripped to allow etree.tostring() to work with
    the 'pretty_print' option set.
    """
    pretty_tree = safe_parse_string(
        etree.tostring(doc), parser=PRETTY_PARSER,
    )
    pretty_xml = etree.tostring(
        pretty_tree, pretty_print=True, encoding='unicode',
    ).replace('\t', '        ').rstrip('\n')

    for line in pretty_xml.split('\n'):
        line = PRETTY_TEXT_WRAPPER.fill(line.rstrip('\n')).rstrip('\n')
        for subline in line.split('\n'):
            if not subline.strip():
                continue
            print(subline)


def recursive_dict(element):
    """Map an XML tree into a dict of dicts."""
    if isinstance(element, (tuple, list)):
        return tuple(
            recursive_dict(child)
            for child
            in element
        )
    return (
        '{}{}'.format(
            element.tag,
            pprint.pformat(element.attrib, compact=True, width=10000),
        ),
        dict(
            map(recursive_dict, element)
        ) or element.text
    )


class SoapClient(object):

    """Rinse SOAP client."""

    __session = None

    def __init__(self, url, debug=False, **kwargs):
        """Set base attributes."""
        self.url = url
        self.debug = debug
        self.kwargs = kwargs
        self.operations = {}
        self.soap_schema = SCHEMA[ENVELOPE_XSD]

    @property
    def _session(self):
        """Cached instance of requests.Session."""
        if self.__session is None:
            self.__session = requests.Session()
        return self.__session

    def __call__(self, msg, build_response=RinseResponse, debug=False):
        """Post 'msg' to remote service."""
        # generate HTTP request from msg
        request = msg.request(self.url).prepare()
        if debug or self.debug:
            print('{} {}'.format(request.method, self.url))
            print(
                ''.join(
                    '{}: {}\n'.format(name, val)
                    for name, val
                    in sorted(request.headers.items())
                )
            )
            print(request.content)

        # perform HTTP(s) POST
        resp = self._session.send(request)
        return build_response(resp)
