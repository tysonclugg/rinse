"""Rinse SOAP library: XML Schema Definition (XSD) functions."""
from lxml import etree
from rinse.util import element_as_tree

NS_XSD = 'http://www.w3.org/2001/XMLSchema'
NS = {
    'xsd': NS_XSD,
}


class XSDValidator(object):

    """XSD Schema Validation."""

    _parser = None

    def __init__(self, schema_root):
        """XSDValidator init."""
        self.root = element_as_tree(schema_root)
        self.schema = etree.XMLSchema(self.root)

    def validate(self, doc):
        """Validate doc against schema, raises exception if doc is invalid."""
        self.schema.assertValid(doc)

    def is_valid(self, doc):
        """Validate doc against schema, return True if doc is valid."""
        return self.schema.validate(doc)
