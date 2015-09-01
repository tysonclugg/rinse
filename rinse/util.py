"""rinse SOAP client utility functions."""
from __future__ import print_function
import collections
import os.path
import pprint
import textwrap

import defusedxml.lxml
import lxml.builder
from lxml import etree

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
    return defusedxml.lxml.fromstring(raw_xml, **kwargs)


def safe_parse_path(xml_path, **kwargs):
    """Safely parse XML content from path into an element tree."""
    return defusedxml.lxml.parse(xml_path, **kwargs)


def safe_parse_url(xml_url, **kwargs):
    """Safely parse XML content from path into an element tree."""
    return defusedxml.lxml.parse(xml_url, **kwargs)


class ElementMaker(lxml.builder.ElementMaker):

    """Wrapper around lxml ElementMaker that casts ints as strings."""

    def __getattr__(self, name):
        """Return a lambda that parses int args as strings."""
        _cls = super(ElementMaker, self).__getattr__(name)

        def __cls_wraper(*args, **kwargs):
            """Wrapper around Element class."""
            return _cls(
                *[
                    str(arg) if isinstance(arg, int) else arg
                    for arg
                    in args
                ],
                **kwargs
            )
        return __cls_wraper


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


class cached_property(object):
    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
