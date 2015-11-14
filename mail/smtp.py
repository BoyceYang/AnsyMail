#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from utils import smtplib
from tornado import gen

from utils.helper import DNS_NAME, sanitize_address


class BaseEmailBackend(object):
    """
    Base class for email backend implementations.
    Subclasses must at least overwrite send_messages().
    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def open(self, callback=False):
        """
        Open a network connection.

        This method can be overwritten by backend implementations to
        open a network connection.

        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.

        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        send_messages() method of the SMTP backend for a reference
        implementation.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """
        Close a network connection.
        """
        pass

    def send_messages(self, email_messages, callback=False):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        raise NotImplementedError


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the SMTP network connection.
    """
    def __init__(self, host=None, port=None, username=None,
                 password=None, use_tls=None, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.host = host or '127.0.0.1'
        self.port = port or 25
        self.username = username or None
        self.password = password or None
        self.use_tls = use_tls
        self.connection = None
        self.template_loader = kwargs.get('template_loader', None)

    @gen.engine
    def open(self, callback):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            callback(False)
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.

            self.connection = smtplib.SMTP(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())
            yield gen.Task(self.connection.connect, self.host, self.port)

            if self.use_tls:
                yield gen.Task(self.connection.ehlo)
                yield gen.Task(self.connection.starttls)
                yield gen.Task(self.connection.ehlo)
            if self.username and self.password:
                yield gen.Task(self.connection.login, self.username, self.password)
            callback(True)
        except:
            if not self.fail_silently:
                raise

    @gen.engine
    def close(self):
        """Closes the connection to the email server."""
        try:
            try:
                yield gen.Task(self.connection.quit)
            except socket.sslerror:
                # This happens when calling quit() on a TLS connection
                # sometimes.
                self.connection.close()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    @gen.engine
    def send_messages(self, email_messages, callback=None):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return

        new_conn_created = yield gen.Task(self.open)
        print "OK"
        if not self.connection:
            # We failed silently on open().
            # Trying to send would be pointless.
            return
        num_sent = 0
        for message in email_messages:
            sent = yield gen.Task(self._send, message)
            if sent:
                num_sent += 1
        if new_conn_created:
            yield gen.Task(self.close)
        if callback:
            callback(num_sent)

    @gen.engine
    def _send(self, email_message, callback=None):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            if callback:
                callback(False)
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        print from_email
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        try:
            yield gen.Task(self.connection.sendmail, from_email, recipients, email_message.message().as_string())
        except:
            if not self.fail_silently:
                raise
            if callback:
                callback(False)
        if callback:
            callback(True)

if __name__ == '__main__':
    email_back = EmailBackend(
        'smtp.163.com', 25, 'yangziyi05001', 'aa123456',
        True
    )
    print email_back
    email_back.send_messages("hdheu")