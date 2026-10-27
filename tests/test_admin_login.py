"""Credential reset, username enforcement and session invalidation checks."""
import io
import json
import os
import secrets
import tempfile
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults

import app
import cms


class ManagedAdminLogin(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'CMS_TEST_DIR': self.storage.name,
                                          'CMS_DEV_SETUP': '1', 'VERCEL_ENV': 'development'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.storage.cleanup)
        self.record = {'username': 'test-owner', 'salt': secrets.token_hex(16),
                       'key': secrets.token_hex(32)}
        self.record['password'] = cms.password_hash('test-only-password', self.record['salt'])

    def request(self, path, payload=None, cookie=''):
        environ = {}
        setup_testing_defaults(environ)
        raw = json.dumps(payload or {}).encode()
        environ.update(PATH_INFO=path, REQUEST_METHOD='POST' if payload is not None else 'GET',
                       HTTP_HOST='test.example', HTTP_ORIGIN='https://test.example',
                       HTTP_COOKIE=cookie, CONTENT_TYPE='application/json',
                       CONTENT_LENGTH=str(len(raw)), REMOTE_ADDR='test-admin')
        environ['wsgi.input'] = io.BytesIO(raw)
        result = []
        body = b''.join(app.app(environ, lambda status, headers: result.append((status, dict(headers)))))
        return result[0][0], json.loads(body), result[0][1]

    def configure(self, record=None):
        return patch.dict(os.environ, {'CMS_ADMIN_CREDENTIALS': json.dumps(record or self.record)})

    def test_username_and_password_required(self):
        with self.configure():
            self.assertTrue(self.request('/api/admin/status')[1]['username_required'])
            for username, password in [('', 'test-only-password'), ('other', 'test-only-password'),
                                       ('test-owner', 'wrong'), (None, 'test-only-password')]:
                self.assertEqual(self.request('/api/admin/login', {'username': username, 'password': password})[0], '401 Unauthorized')
            status, result, headers = self.request('/api/admin/login', {'username': 'test-owner', 'password': 'test-only-password'})
            self.assertEqual(status, '200 OK')
            self.assertIn('csrf', result)
            self.assertIn('HttpOnly', headers['Set-Cookie'])
            cookie = headers['Set-Cookie'].split(';')[0]
            self.assertEqual(self.request('/api/admin/content', cookie=cookie)[0], '200 OK')
            public = json.dumps(self.request('/api/admin/status')[1])
            self.assertNotIn(self.record['password'], public)
            self.assertNotIn(self.record['key'], public)

    def test_reset_overrides_old_login_and_revokes_session(self):
        self.assertEqual(self.request('/api/admin/setup', {'password': 'legacy-test-password'})[0], '201 Created')
        cookie = self.request('/api/admin/login', {'password': 'legacy-test-password'})[2]['Set-Cookie'].split(';')[0]
        with self.configure():
            self.assertFalse(self.request('/api/admin/status', cookie=cookie)[1]['authenticated'])
            self.assertEqual(self.request('/api/admin/login', {'password': 'legacy-test-password'})[0], '401 Unauthorized')
            self.assertEqual(self.request('/api/admin/setup', {'password': 'legacy-test-password'})[0], '409 Conflict')

    def test_invalid_configuration_fails_closed(self):
        for value in ('{', 'null', '{}', json.dumps({**self.record, 'key': 'bad'})):
            with patch.dict(os.environ, {'CMS_ADMIN_CREDENTIALS': value}):
                self.assertEqual(self.request('/api/admin/status')[0], '503 Service Unavailable')
                self.assertEqual(self.request('/api/admin/login', {'password': 'test-only-password'})[0], '503 Service Unavailable')

    def test_dashboard_has_username_and_no_saved_credentials(self):
        self.assertIn('autocomplete="username"', app.dashboard.PAGE)
        self.assertNotIn(self.record['password'], app.dashboard.PAGE)
