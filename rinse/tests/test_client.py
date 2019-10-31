#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for rinse.client module."""

import unittest

from lxml import etree
from mock import MagicMock, patch
from rinse.client import SoapClient
from rinse.message import SoapMessage

from .utils import captured_stdout


class TestSoapMessage(unittest.TestCase):
    def test_soap_action(self):
        """Test that SOAP-Action HTTP header is set correctly."""
        msg = SoapMessage(etree.Element('test'))
        req = msg.request('http://example.com', 'testaction')
        self.assertEqual(req.headers['SOAPAction'], 'testaction')

    def test_no_soap_action(self):
        """Test that SOAP-Action HTTP header is absent when no action given.
        """
        msg = SoapMessage(etree.Element('test'))
        req = msg.request('http://example.com')
        self.assertTrue('SOAPAction' not in req.headers)

    def test_soap_action_is_none(self):
        """Test that SOAP-Action HTTP header is absent when no action is None.
        """
        msg = SoapMessage(etree.Element('test'))
        req = msg.request('http://example.com', None)
        self.assertTrue('SOAPAction' not in req.headers)


class TestRinseClient(unittest.TestCase):
    def test_soap_action(self):
        """Test that SOAP action is passed on to SoapMessage.request()."""
        msg = SoapMessage(etree.Element('test'))
        msg.request = MagicMock()
        with patch('requests.Session'):
            client = SoapClient('http://example.com')
            client(msg, 'testaction', build_response=lambda r: r)
            msg.request.assert_called_once_with('http://example.com',
                                                'testaction')

    def test_soap_action_debug(self):
        msg = SoapMessage(etree.Element('test'))
        client = SoapClient('http://example.com', debug=True)
        client._session = MagicMock()
        with captured_stdout() as stdout:
            client(msg, 'testaction', build_response=lambda r: r)
        self.assertEqual(
            stdout.getvalue(),
            'POST http://example.com\n'
            'Content-Length: 164\n'
            'Content-Type: text/xml;charset=UTF-8\n'
            'SOAPAction: testaction\n'
            '\n'
            '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">\n'
            '  <soapenv:Header/>\n'
            '  <soapenv:Body>\n'
            '    <test/>\n'
            '  </soapenv:Body>\n'
            '</soapenv:Envelope>\n'
            '\n'
        )

    def test_no_soap_action(self):
        """Test that empty SOAP action is passed to SoapMessage.request()
           when no action given."""
        msg = SoapMessage(etree.Element('test'))
        msg.request = MagicMock()
        with patch('requests.Session'):
            client = SoapClient('http://example.com')
            client(msg, build_response=lambda r: r)
            msg.request.assert_called_once_with('http://example.com', '')

    def test_timeout(self):
        msg = SoapMessage(etree.Element('test'))
        msg.request = MagicMock()
        client = SoapClient('http://example.com', timeout=1)
        self.assertEqual(client.timeout, 1)

        with patch('requests.Session'):
            client(msg, 'testaction', build_response=lambda r: r)
            self.assertEqual(client._session.send.call_args[1]['timeout'], 1)

        with patch('requests.Session'):
            client(msg, 'testaction', build_response=lambda r: r, timeout=2)
            self.assertEqual(client._session.send.call_args[1]['timeout'], 2)

        with patch('requests.Session'):
            client(msg, 'testaction', build_response=lambda r: r, timeout=None)
            self.assertEqual(client._session.send.call_args[1]['timeout'], None)


if __name__ == '__main__':
    unittest.main()
