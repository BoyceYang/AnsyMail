#!/usr/bin/env python
# -*- coding: utf-8 -*-


class EmailMessage(object):
    """
    A container for email information.
    """
    content_subtype = 'plain'
    mixed_subtype = 'mixed'
    encoding = None     # None => use settings default

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None, reply_to=None):
        """
        Initialize a single email message (which can be sent to multiple recipients).
        """
        if to:
            assert not isinstance(to, basestring), '"to" argument must be a list or tuple'
            self.to = list(to)
        else:
            self.to = []
        if cc:
            assert not isinstance(cc, basestring), '"cc" argument must be a list or tuple'
            self.cc = list(cc)
        else:
            self.cc = []
        if bcc:
            assert not isinstance(bcc, basestring), '"bcc" argument must be a list or tuple'
            self.bcc = list(bcc)
        else:
            self.bcc = []
        self.from_email = from_email or 'noreply@localhost'
        self.reply_to = reply_to
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.extra_headers = headers or {}
        self.connection = connection