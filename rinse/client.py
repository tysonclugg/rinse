"""SOAP client."""
from __future__ import print_function
import requests
from rinse import ENVELOPE_XSD
from rinse.util import SCHEMA, cached_property
from rinse.response import RinseResponse


class SoapClient(object):

    """Rinse SOAP client."""

    def __init__(self, url, debug=False, **kwargs):
        """Set base attributes."""
        self.url = url
        self.debug = debug
        self.timeout = kwargs.pop('timeout', None)
        self.kwargs = kwargs
        self.operations = {}
        self.soap_schema = SCHEMA[ENVELOPE_XSD]

    @cached_property
    def _session(self):
        """Cached instance of requests.Session."""
        return requests.Session()

    def __call__(self, msg, action="", build_response=RinseResponse,
                 debug=False, **kwargs):
        """Post 'msg' to remote service."""
        # generate HTTP request from msg
        request = msg.request(self.url, action).prepare()
        if debug or self.debug:
            print('{} {}'.format(request.method, self.url))
            print(
                ''.join(
                    '{}: {}\n'.format(name, val)
                    for name, val
                    in sorted(request.headers.items())
                )
            )
            print(request.body.decode('utf-8'))

        # perform HTTP(s) POST
        resp = self._session.send(request, timeout=kwargs.get('timeout', self.timeout))
        return build_response(resp)
