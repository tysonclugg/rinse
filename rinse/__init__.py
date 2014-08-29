"""SOAP client."""
import os.path


RINSE_DIR = os.path.dirname(__file__)
ENVELOPE_XSD = 'soap-1.1_envelope.xsd'

NS_SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'

NS_MAP = {
    'soapenv': NS_SOAPENV,
}
