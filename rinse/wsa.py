"""WSA (Addressing) support for rinse SOAP client."""

NS_WSA = 'http://www.w3.org/2005/08/addressing'
URI_ANONYMOUS = \
    'http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous'
URI_UNSPECIFIED = \
    'http://schemas.xmlsoap.org/ws/2004/08/addressing/id/unspecified'


def append_wsa_headers(
        msg, to, action,
        message_id=None,
        relates_to=None,
        relationship_type=None,
        reply_to=None,
        from_endpoint=None,
        fault_to=None,
):
    """Add WSA (addressing) headers.

    >>> from rinse.wsa import append_wsa_headers
    >>> import lxml.usedoctest
    >>> from rinse.message import SoapMessage
    >>> from rinse.util import printxml
    >>> msg = SoapMessage()
    >>> f123 = msg.elementmaker(
    ...     'f123',
    ...     'http://www.fabrikam123.example/svc53',
    ... )
    >>> msg.body = f123.Delete(f123.maxCount('42'))
    >>> append_wsa_headers(
    ...     msg,
    ...     'mailto:joe@fabrikam123.example',
    ...     'http://fabrikam123.example/mail/Delete',
    ...     message_id='uuid:aaaabbbb-cccc-dddd-eeee-ffffffffffff',
    ...     reply_to='http://business456.example/client1',
    ... )
    >>> print(msg['SOAPAction'])
    "http://fabrikam123.example/mail/Delete"
    >>> printxml(msg.etree())
    <soapenv:Envelope xmlns:f123="http://www.fabrikam123.example/svc53"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsa="http://www.w3.org/2005/08/addressing">
      <soapenv:Header>
        <wsa:MessageID>uuid:aaaabbbb-cccc-dddd-eeee-ffffffffffff</wsa:MessageID>
        <wsa:To>mailto:joe@fabrikam123.example</wsa:To>
        <wsa:Action>http://fabrikam123.example/mail/Delete</wsa:Action>
        <wsa:ReplyTo>
          <wsa:Address>http://business456.example/client1</wsa:Address>
        </wsa:ReplyTo>
      </soapenv:Header>
      <soapenv:Body>
        <f123:Delete>
          <f123:maxCount>42</f123:maxCount>
        </f123:Delete>
      </soapenv:Body>
    </soapenv:Envelope>
    """
    # perform simple validation on WSA headers
    if reply_to and not message_id:
        raise ValueError(
            'wsa:ReplyTo set so wsa:MessageID MUST be present.',
        )
    if fault_to and not message_id:
        raise ValueError(
            'wsa:FaultTo set so wsa:MessageID MUST be present.',
        )
    if relationship_type and not relates_to:
        raise ValueError(
            '/wsa:RelatesTo/@RelationshipType set '
            'so wsa:RelatesTo MUST be present.',
        )

    # add 'SOAPAction' HTTP request header
    msg['SOAPAction'] = '"{}"'.format(action)

    # add WSA elements to SOAP headers
    relation_attrs = {}
    if relationship_type:
        relation_attrs['RelationshipType'] = relationship_type
    wsa = msg.elementmaker('wsa', NS_WSA)
    msg.headers.extend(
        header
        for header
        in [
            wsa.MessageID(message_id) if message_id else None,
            wsa.RelatesTo(relates_to, **relation_attrs) if relates_to else None,
            wsa.To(to),
            wsa.Action(action),
            wsa.From(from_endpoint) if from_endpoint else None,
            wsa.ReplyTo(wsa.Address(reply_to)) if reply_to else None,
            wsa.FaultTo(wsa.Address(fault_to)) if fault_to else None,
        ]
        if header is not None
    )
