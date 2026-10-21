import base64
import copy
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults
from PIL import Image
import app
import cms

class DashboardFlow(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'CMS_TEST_DIR':self.temp.name,'CMS_DEV_SETUP':'1','VERCEL_ENV':'development'})
  self.env.start();self.cookie='';self.csrf=''
 def tearDown(self):self.env.stop();self.temp.cleanup()
 def request(self,path,method='GET',payload=None,auth=False,origin='https://test.example',csrf=True):
  e={};setup_testing_defaults(e);e.update(PATH_INFO=path,REQUEST_METHOD=method,HTTP_HOST='test.example',wsgi_url_scheme='https',REMOTE_ADDR='test-ip')
  e['wsgi.url_scheme']='https';e['HTTP_ORIGIN']=origin
  if auth:e['HTTP_COOKIE']=self.cookie
  if csrf:e['HTTP_X_CSRF_TOKEN']=self.csrf
  raw=json.dumps(payload or {}).encode();e['wsgi.input']=io.BytesIO(raw);e['CONTENT_LENGTH']=str(len(raw));e['CONTENT_TYPE']='application/json'
  result=[];body=b''.join(app.app(e,lambda status,headers:result.append((int(status.split()[0]),dict(headers)))))
  status,headers=result[0]
  if 'Set-Cookie' in headers:self.cookie=headers['Set-Cookie'].split(';')[0]
  data=json.loads(body) if headers['Content-Type'].startswith('application/json') else body
  if isinstance(data,dict) and data.get('csrf'):self.csrf=data['csrf']
  return status,data,headers
 def setup_owner(self):
  result=self.request('/api/admin/setup','POST',{'password':'a-long-test-only-password'})
  self.assertEqual(result[0],201);return result
 def test_public_cannot_write_or_bootstrap_production(self):
  self.assertEqual(self.request('/api/admin/content')[0],401)
  self.assertEqual(self.request('/api/admin/content','POST',cms.defaults())[0],401)
  with patch.dict(os.environ,{'VERCEL_ENV':'production','CMS_DEV_SETUP':'0'}):
   self.assertEqual(self.request('/api/admin/setup','POST',{'password':'a-long-test-only-password'})[0],403)
 def test_owner_setup_and_login(self):
  _,_,headers=self.setup_owner();self.assertIn('HttpOnly',headers['Set-Cookie']);self.assertIn('SameSite=Strict',headers['Set-Cookie']);self.assertIn('Secure',headers['Set-Cookie'])
  self.assertEqual(self.request('/api/admin/setup','POST',{'password':'a-long-test-only-password'})[0],409)
  self.assertTrue(self.request('/api/admin/status',auth=True)[1]['authenticated'])
  self.assertEqual(self.request('/api/admin/login','POST',{'password':'wrong'})[0],401)
  self.assertEqual(self.request('/api/admin/login','POST',{'password':'a-long-test-only-password'})[0],200)
  self.assertEqual(self.request('/api/admin/content',auth=True)[0],200)
 def test_csrf_and_origin(self):
  self.setup_owner()
  self.assertEqual(self.request('/api/admin/content','POST',cms.defaults(),auth=True,csrf=False)[0],403)
  self.assertEqual(self.request('/api/admin/content','POST',cms.defaults(),auth=True,origin='https://other.example')[0],403)
 def test_publish_persists_and_updates_pages(self):
  self.setup_owner();data=self.request('/api/admin/content',auth=True)[1];old=copy.deepcopy(data)
  data['hero']['line1']='A new homepage title';data['services'][0]['title']='Updated basketball courts';data['services'][1]['published']=False
  status,result,_=self.request('/api/admin/content','POST',data,auth=True);self.assertEqual(status,200)
  self.assertNotEqual(result['revision'],'default');self.assertEqual(self.request('/api/admin/content',auth=True)[1]['hero']['line1'],'A new homepage title')
  self.assertIn(b'A new homepage title',self.request('/')[1]);self.assertIn(b'Updated basketball courts',self.request('/services/basketball-courts')[1])
  self.assertEqual(self.request('/services/outdoor-tennis-courts')[0],404)
  self.assertEqual(self.request('/api/admin/content','POST',old,auth=True)[0],409)
  self.assertEqual(len(cms.list_objects('published/')),1)
 def test_upload_validation_and_delivery(self):
  self.setup_owner()
  self.assertEqual(self.request('/api/admin/upload','POST',{'data':base64.b64encode(b'<svg><script/></svg>').decode()},auth=True)[0],400)
  im=Image.new('RGBA',(20,20),(39,187,54,160));out=io.BytesIO();im.save(out,'PNG');raw=out.getvalue()
  status,data,_=self.request('/api/admin/upload','POST',{'data':base64.b64encode(raw).decode()},auth=True);self.assertEqual(status,201)
  status,body,headers=self.request(data['url']);self.assertEqual(status,200);self.assertEqual(body,raw);self.assertEqual(headers['Content-Type'],'image/png')
  content=self.request('/api/admin/content',auth=True)[1];content['services'][0]['image']=data['url'];self.assertEqual(self.request('/api/admin/content','POST',content,auth=True)[0],200)
  self.assertIn(data['url'].encode(),self.request('/services/basketball-courts')[1])
 def test_invalid_content_and_no_public_secrets(self):
  self.setup_owner();data=cms.defaults();data['hero']['line1']='<script>alert(1)</script>'
  self.assertEqual(self.request('/api/admin/content','POST',data,auth=True)[0],200)
  self.assertIn(b'&lt;script&gt;alert(1)&lt;/script&gt;',self.request('/')[1]);self.assertNotIn(b'<script>alert(1)</script>',self.request('/')[1])
  data=cms.load_content();data['services'][0]['image']='https://evil.example/image.png';self.assertEqual(self.request('/api/admin/content','POST',data,auth=True)[0],400)
  data=cms.load_content();data['services'][0]['slug']='../../auth/admin';self.assertEqual(self.request('/api/admin/content','POST',data,auth=True)[0],400)
  self.assertNotIn('password',json.dumps(self.request('/api/services')[1]))
 def test_dashboard_and_logout(self):
  status,body,headers=self.request('/dashboard');self.assertEqual(status,200);self.assertEqual(headers['Cache-Control'],'no-store');self.assertIn('noindex',headers['X-Robots-Tag'])
  self.setup_owner();self.assertEqual(self.request('/api/admin/logout','POST',{},auth=True)[0],200);self.assertFalse(self.request('/api/admin/status',auth=True)[1]['authenticated'])
 def test_login_throttle(self):
  self.setup_owner()
  for _ in range(10):self.assertEqual(self.request('/api/admin/login','POST',{'password':'wrong'})[0],401)
  self.assertEqual(self.request('/api/admin/login','POST',{'password':'wrong'})[0],429)
if __name__=='__main__':unittest.main()
