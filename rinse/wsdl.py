"""Rinse SOAP library: module providing WSDL functions."""
from lxml import etree
from rinse.util import (
    safe_parse_path, safe_parse_url, element_as_tree, cached_property,
)
from rinse.xsd import XSDValidator, NS_XSD

NS_WSDL = 'http://schemas.xmlsoap.org/wsdl/'
NS_MAP = {
    'wsdl': NS_WSDL,
    'xsd': NS_XSD,
}


class WSDL(object):

    """WSDL object."""

    _schema = None
    _xsd_validator = None

    @classmethod
    def from_file(cls, wsdl_path):
        """Make a WSDL instance from a file path."""
        return cls(safe_parse_path(wsdl_path))

    @classmethod
    def from_url(cls, wsdl_path):
        """Make a WSDL instance from a URL."""
        return cls(safe_parse_url(wsdl_path))

    def __init__(self, wsdl_root):
        """WSDL init."""
        self.root = wsdl_root

    @cached_property
    def schema(self):
        """Return schema element (used for XSD validation)."""
        schema_el = self.root.xpath(
            '/wsdl:definitions/wsdl:types/xsd:schema', namespaces=NS_MAP,
        )[0]
        return element_as_tree(schema_el)

    @cached_property
    def xsd_validator(self):
        """Extract XML Schema Definition (XSD) element tree."""
        return XSDValidator(self.schema)

    def is_valid(self, soapmsg):
        """Return True if SOAP message body validates against WSDL schema."""
        return self.xsd_validator.is_valid(soapmsg.body)

    def validate(self, soapmsg):
        """Raise exception if SOAP message body is invalid."""
        return self.xsd_validator.validate(soapmsg.body)
