"""Rinse SOAP library: module providing WSDL functions."""
from lxml import etree
from rinse.util import safe_parse_path, safe_parse_url, element_as_tree
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

    @property
    def schema(self):
        """Return schema element (used for XSD validation)."""
        if self._schema is None:
            schema_el = self.root.xpath(
                '/wsdl:definitions/wsdl:types/xsd:schema', namespaces=NS_MAP,
            )[0]
            self._schema = element_as_tree(schema_el)
        return self._schema

    @property
    def xsd_validator(self):
        """Extract XML Schema Definision (XSD) element tree."""
        if self._xsd_validator is None:
            self._xsd_validator = XSDValidator(self.schema)
        return self._xsd_validator

    def is_valid(self, soapmsg):
        """Return True if SOAP message body validates against WSDL schema."""
        return self.xsd_validator.is_valid(soapmsg.body)

    def validate(self, soapmsg):
        """Raise exception if SOAP message body is invalid."""
        return self.xsd_validator.validate(soapmsg.body)
