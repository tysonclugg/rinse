"""SOAP client."""

NS_WSSE = 'http://docs.oasis-open.org/wss/2004/01/' \
    'oasis-200401-wss-wssecurity-secext-1.0.xsd'


def append_wsse_headers(msg, username, password):
    """Add WSSE (security) headers.

    >>> from rinse.wsse import append_wsse_headers
    >>> import lxml.usedoctest
    >>> from rinse.message import SoapMessage
    >>> from rinse.util import printxml
    >>> msg = SoapMessage()
    >>> f123 = msg.elementmaker(
    ...     'f123',
    ...     'http://www.fabrikam123.example/svc53',
    ... )
    >>> msg.body = f123.Delete(f123.maxCount('42'))
    >>> append_wsse_headers(msg, 'alice', '$uper-5ecret')
    >>> printxml(msg.etree())
    <soapenv:Envelope xmlns:f123="http://www.fabrikam123.example/svc53"
             xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
             xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header>
        <wsse:Security>
          <wsse:UsernameToken>
            <wsse:Username>alice</wsse:Username>
            <wsse:Password>$uper-5ecret</wsse:Password>
          </wsse:UsernameToken>
        </wsse:Security>
      </soapenv:Header>
      <soapenv:Body>
        <f123:Delete>
          <f123:maxCount>42</f123:maxCount>
        </f123:Delete>
      </soapenv:Body>
    </soapenv:Envelope>
    """
    # add WSSE headers
    wsse = msg.elementmaker('wsse', NS_WSSE)
    msg.headers.append(
        wsse.Security(
            wsse.UsernameToken(
                wsse.Username(username),
                wsse.Password(password),
            ),
        ),
    )
