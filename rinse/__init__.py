# vim: set fileencoding=utf8 :
"""SOAP client."""
import collections
import os.path
import uuid

import defusedxml.lxml
from lxml.builder import ElementMaker
from lxml import etree
import requests

SOAP_XSD_FILE = os.path.join(
    os.path.dirname(__file__),
    'res',
    'soap-1.1.xsd',
)

NS_MAP = {
    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
    'wsa': 'http://www.w3.org/2005/08/addressing',
    'wsse': 'http://docs.oasis-open.org/wss/2004/01/'
            'oasis-200401-wss-wssecurity-secext-1.0.xsd',
}


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
    print(
        etree.tostring(doc, pretty_print=True).decode('utf-8'),
    )


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
    #return root.xpath('/soapenv:Envelope/soapenv:Body', namespaces=NS_MAP)[0]
    return root


class SoapOperation(object):

    """Rinse SOAP operation proxy."""

    def __init__(self, client, action, body_callback=None, response_callback=None):
        self.client = client
        self.action = action
        if callable(body_callback):
            self.build_body = body_callback
        if callable(response_callback):
            self.parse_response = response_callback

    def build_body(self, *args, **kwargs):
        raise NotImplemented

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

    def parse_response(self, response):
        return response


class SoapClient(object):

    """Rinse SOAP client."""

    def __init__(self, url, nsmap, **kwargs):
        self.url = url
        self.nsmap = NS_MAP.copy()
        self.nsmap.update(nsmap)
        self.kwargs = kwargs
        self.operations = {}

    def make_operation(self, action, *args, **kwargs):
        if action not in self.operations:
            return SoapOperation(self, action, *args, **kwargs)
            self.operations[action] = operation
        return self.operations[action]
