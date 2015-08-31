#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for rinse.client module."""

import unittest

from lxml import etree
from mock import MagicMock, patch
from rinse.client import SoapClient
from rinse.message import SoapMessage


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
        with patch('requests.Session') as mock:
            client = SoapClient('http://example.com')
            response = client(msg, 'testaction', build_response=lambda r: r)
            msg.request.assert_called_once_with('http://example.com',
                                                 'testaction')
    def test_no_soap_action(self):
        """Test that empty SOAP action is passed to SoapMessage.request()
           when no action given."""
        msg = SoapMessage(etree.Element('test'))
        msg.request = MagicMock()
        with patch('requests.Session') as mock:
            client = SoapClient('http://example.com')
            response = client(msg, build_response=lambda r: r)
            msg.request.assert_called_once_with('http://example.com', '')


if __name__ == '__main__':
    unittest.main()
