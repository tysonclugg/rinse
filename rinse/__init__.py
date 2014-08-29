"""SOAP client."""
import os.path
from pkg_resources import get_distribution, DistributionNotFound


RINSE_DIR = os.path.dirname(__file__)
ENVELOPE_XSD = 'soap-1.1_envelope.xsd'

NS_SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'

NS_MAP = {
    'soapenv': NS_SOAPENV,
}

try:
    _dist = get_distribution('rinse')
    if not __file__.startswith(os.path.join(_dist.location, 'rinse', '')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'development'
else:
    __version__ = _dist.version
