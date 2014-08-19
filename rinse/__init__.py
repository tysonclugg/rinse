# vim: set fileencoding=utf8 :
"""SOAP client."""
import abc
import collections
import os.path
import textwrap
import uuid

import defusedxml.lxml
from lxml.builder import ElementMaker
from lxml import etree
import requests

RINSE_DIR = os.path.dirname(__file__)
ENVELOPE_XSD = 'soap-1.1_envelope.xsd'
NS_MAP = {
    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
    'wsa': 'http://www.w3.org/2005/08/addressing',
    'wsse': 'http://docs.oasis-open.org/wss/2004/01/'
            'oasis-200401-wss-wssecurity-secext-1.0.xsd',
}


class SoapMessage(object):

    """SOAP message."""

    def __init__(self, body=None, headers=None, nsmap=None, body_schema=None):
        self.body = body
        self.headers = headers or []
        self.nsmap = nsmap or {}
        self.body_schema = body_schema
        self._ns = {}

        # create default namespaces
        self.soapenv = self.namespace('soapenv')
        self.wsa = self.namespace('wsa')

    def namespace(self, prefix, url=None):
        """Add namespace with specified prefix."""
        if prefix not in self._ns:
            if url is None:
                url = NS_MAP[prefix]
            self.nsmap[prefix] = url
            self._ns[prefix] = ElementMaker(namespace=url, nsmap={prefix: url})
        return self._ns[prefix]

    def append_auth_headers(self, username, password):
        """Add WSSE security headers."""
        # add WSSE headers
        wsse = self.namespace('wsse')
        self.headers.append(
            wsse.Security(
                wsse.UsernameToken(
                    wsse.Username(username),
                    wsse.Password(password),
                ),
            ),
        )

    def to_etree(self):
        """Generate a SOAP Envelope message with header and body elements."""
        headers = []
        NS = ElementMakerCache(self.nsmap)
        WSSE = NS['wsse']
        SOAPENV = NS['soapenv']
        WSA = NS['wsa']

        # insert WSSE security header
        try:
            headers.append(
                WSSE.Security(
                    WSSE.UsernameToken(
                        WSSE.Username(kwargs['wsse_user']),
                        WSSE.Password(kwargs['wsse_pass']),
                    ),
                )
            )
        except KeyError:
            pass  # either wsse_user or wsse_pass not given

        # insert WSA addressing headers
        headers.extend(
            [
                WSA.ReplyTo(
                    WSA.Address(
                        'http://www.w3.org/2005/08/addressing/anonymous'
                    ),
                ),
                WSA.Action(action),
                WSA.MessageID(message_id),
                WSA.To(to),
            ]
        )

        return SOAPENV.Envelope(
            SOAPENV.Header(*headers),
            SOAPENV.Body(body),
        )


    @classmethod
    def fromxml(cls, xml, **kwargs):


Response = collections.namedtuple('Response', ['msg', 'body', 'parsed'])


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
        doc = defusedxml.lxml.parse(xsd)
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


def printxml(doc):
    """Pretty print an lxml document tree."""
    wrapper = textwrap.TextWrapper(
        width=78,
        initial_indent='',
        subsequent_indent='        ',
        replace_whitespace=False,
        drop_whitespace=False,
        break_long_words=False,
        break_on_hyphens=False,
    )
    for line in etree.tostring(
        doc, pretty_print=True, encoding='unicode',
    ).split('\n'):
        print(wrapper.fill(line.rstrip('\n')).rstrip('\n'))


def recursive_dict(element):
    """Map an XML tree into a dict of dicts."""
    if isinstance(element, (tuple, list)):
        return tuple(
            recursive_dict(child)
            for child
            in element
        )
    return (
        (
            element.tag,
            tuple(element.attrib.items()),
        ),
        dict(
            map(recursive_dict, element)
        ) or element.text
    )


def new_maker(namespaces, nsmap=None):
    """Generate a new ElementMaker with nsmap generated from aliases."""
    if nsmap is None:
        nsmap = {}
    return ElementMaker(
        nsmap={
            name: nsmap.get(name, None) or NS_MAP[name]
            for name in list(namespaces) + NS_MAP.keys()
        },
    )


def soapmsg(to, action, message_id, body, nsmap=None, **kwargs):
    """Generate a SOAP Envelope message with header and body elements."""
    if not nsmap:
        nsmap = {}
    headers = []
    NS = ElementMakerCache(nsmap)
    WSSE = NS['wsse']
    SOAPENV = NS['soapenv']
    WSA = NS['wsa']

    # insert WSSE security header
    try:
        headers.append(
            WSSE.Security(
                WSSE.UsernameToken(
                    WSSE.Username(kwargs['wsse_user']),
                    WSSE.Password(kwargs['wsse_pass']),
                ),
            )
        )
    except KeyError:
        pass  # either wsse_user or wsse_pass not given

    # insert WSA addressing headers
    headers.extend([
        WSA.ReplyTo(
            WSA.Address('http://www.w3.org/2005/08/addressing/anonymous'),
        ),
        WSA.Action(action),
        WSA.MessageID(message_id),
        WSA.To(to),
    ])

    return SOAPENV.Envelope(
        SOAPENV.Header(*headers),
        SOAPENV.Body(body),
    )


def soapcall(url, action, message_id, body, nsmap=None, **kwargs):
    """Call a SOAP operation."""
    msg = soapmsg(
        url, action, message_id, body,
        nsmap=nsmap, **kwargs
    )
    if kwargs.get('debug', False):
        printxml(msg)
    session = requests.Session()
    resp = session.post(
        url,
        data=etree.tostring(msg, pretty_print=True),
        headers={
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': '"{}"'.format(action),
        },
    )
    root = defusedxml.lxml.fromstring(resp.content)
    # return root.xpath('/soapenv:Envelope/soapenv:Body', namespaces=NS_MAP)[0]
    return root


class SoapOperation(object):

    """Rinse SOAP operation proxy."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, client, action, body_callback=None,
                 response_callback=None, debug=False, body_schema=None,
                 response_schema=None):
        """Stash required attributes to generate a valid SOAP call later on."""
        self.client = client
        self.action = action
        self.debug = debug
        self.body_callback = body_callback
        self.response_callback = response_callback
        self.body_schema = body_schema
        self.response_schema = response_schema

    def build_body(self, *args, **kwargs):
        """Transform args into an lxml.etree doc."""
        body = self.body_callback(*args, **kwargs)
        if self.body_schema:
            self.body_schema.assertValid(body)
        return body

    def __call__(self, *args, **kwargs):
        body = self.build_body(*args, **kwargs)
        response = soapcall(
            self.client.url,
            self.action,
            'uuid:{}'.format(uuid.uuid4()),
            body,
            self.client.nsmap,
            **self.client.kwargs
        )
        return self.parse_response(response)

    def parse_response(self, msg):
        # validate msg against SOAP schema
        self.client.soap_schema.assertValid(msg)
        # extract the soapenv:Body
        body = msg.xpath(
            '/soapenv:Envelope/soapenv:Body',
            namespaces=self.client.nsmap,
        )[0]
        # validate the body if we know the response schema
        if self.response_schema:
            self.response_schema.assertValid(body)
        parsed = self.response_callback(msg, body)
        return Response(msg, body, parsed)


class SoapClient(object):

    """Rinse SOAP client."""

    def __init__(self, url, nsmap, **kwargs):
        self.url = url
        self.nsmap = NS_MAP.copy()
        self.nsmap.update(nsmap)
        self.kwargs = kwargs
        self.operations = {}
        self.soap_schema = SCHEMA[ENVELOPE_XSD]

    def make_operation(self, action, *args, **kwargs):
        if action not in self.operations:
            kwargs.setdefault('debug', self.kwargs.get('debug', False))
            return SoapOperation(self, action, *args, **kwargs)
            self.operations[action] = operation
        return self.operations[action]
