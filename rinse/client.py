"""SOAP client."""
from __future__ import print_function
import requests
from rinse import ENVELOPE_XSD
from rinse.util import SCHEMA
from rinse.response import RinseResponse


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
