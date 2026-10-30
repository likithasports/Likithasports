import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import cms

class SupabaseStorage(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ, {'SUPABASE_CMS_URL':'https://example.supabase.co/functions/v1/storage','SUPABASE_CMS_SECRET':'server-only-secret','BLOB_READ_WRITE_TOKEN':'','CMS_TEST_DIR':''})
        self.env.start()
    def tearDown(self):
        self.env.stop()
    def test_requests_keep_secret_in_server_header(self):
        with patch('cms.urlopen') as call:
            call.return_value.__enter__.return_value.read.return_value=b'{"body":{"revision":"one"}}'
            call.return_value.__enter__.return_value.headers={'Content-Type':'application/json'}
            self.assertEqual(json.loads(cms.read_object('published/one.json')),{'revision':'one'})
            request=call.call_args.args[0]
            self.assertEqual(request.get_header('X-cms-secret'),'server-only-secret')
            self.assertNotIn(b'server-only-secret',request.data)
    def test_storage_failure_never_falls_back_to_blob_write(self):
        with patch('cms.urlopen',side_effect=HTTPError('https://example',503,'unavailable',{},None)), patch('vercel.blob.sync.put_blob') as blob:
            with self.assertRaises(cms.CmsError):
                cms.write_object('published/one.json',b'{}')
            blob.assert_not_called()
    def test_missing_object_is_not_a_connection_failure(self):
        with patch('cms.urlopen') as call:
            call.return_value.__enter__.return_value.read.return_value=b'{"missing":true}'
            call.return_value.__enter__.return_value.headers={'Content-Type':'application/json'}
            self.assertIsNone(cms.read_object('auth/admin.json'))
