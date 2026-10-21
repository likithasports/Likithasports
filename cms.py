"""Private Blob content storage and password-protected dashboard endpoints."""
import base64
import copy
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import time
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit

from catalog import SERVICES

PREFIX = 'likitha-cms/'
MAX_IMAGE = 2 * 1024 * 1024
MAX_BODY = 3 * 1024 * 1024
COOKIE = 'likitha_admin'


class CmsError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def defaults():
    return {'revision': 'default', 'updated_at': None,
            'hero': {'line1': 'Great spaces.', 'line2': 'Greater games.', 'description': 'Courts, turfs and sports infrastructure. From your first idea to the first game.'},
            'slides': [
                {'title': 'More room for your game.', 'category': 'FIELDS & TURFS / 01', 'image': 'football-truf.webp', 'alt': 'Football turf'},
                {'title': 'Built for the next big shot.', 'category': 'BASKETBALL COURTS / 02', 'image': 'basketball.webp', 'alt': 'Basketball court'},
                {'title': 'A fresh surface. A new game.', 'category': 'OUTDOOR TENNIS COURTS / 03', 'image': 'tennis.webp', 'alt': 'Outdoor tennis court'}],
            'services': [dict(copy.deepcopy(s), published=True) for s in SERVICES]}


def test_dir():
    return os.environ.get('CMS_TEST_DIR') if not os.environ.get('VERCEL') else None


def storage_ready():
    return bool(os.environ.get('BLOB_READ_WRITE_TOKEN') or test_dir())


def read_object(path):
    if test_dir():
        p = Path(test_dir()) / path
        return p.read_bytes() if p.exists() else None
    if not storage_ready():
        raise CmsError('Content storage is not connected.', 503)
    from vercel.blob import sync, BlobNotFoundError
    try:
        return sync.get_blob(PREFIX + path, access='private').body
    except BlobNotFoundError:
        return None


def write_object(path, body, content_type='application/json'):
    if test_dir():
        p = Path(test_dir()) / path
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f:
            f.write(body)
        return
    from vercel.blob import sync
    sync.put_blob(PREFIX + path, body, access='private', content_type=content_type, allow_overwrite=False, cache_control_max_age=60)


def list_objects(prefix):
    if test_dir():
        root = Path(test_dir())
        return [str(p.relative_to(root)) for p in (root / prefix).rglob('*') if p.is_file()] if (root / prefix).exists() else []
    if not storage_ready():
        raise CmsError('Content storage is not connected.', 503)
    from vercel.blob import sync
    return [b.pathname[len(PREFIX):] for b in sync.query_blobs(prefix=PREFIX + prefix, page_size=1000)]


def load_content(strict=False):
    if not storage_ready() and not strict:
        return defaults()
    try:
        versions = sorted(list_objects('published/'))
        if not versions:
            return defaults()
        return json.loads(read_object(versions[-1]))
    except Exception:
        if strict:
            raise CmsError('Content storage could not be read. Please retry.', 503)
        return defaults()


def published_services(data):
    return [s for s in data['services'] if s.get('published', True)]


def image_url(image):
    if not image:
        return ''
    if image.startswith('/media/'):
        return image
    return 'https://likithasports.com/assets/home/' + image


def text(value, label, limit, required=True):
    if not isinstance(value, str) or len(value.strip()) > limit or (required and not value.strip()):
        raise CmsError(f'{label} must contain ' + (f'1–{limit}' if required else f'up to {limit}') + ' characters.')
    return value.strip()


def image_value(value, required=False):
    if not value and not required:
        return None
    if not isinstance(value, str) or not (re.fullmatch(r'/media/[a-f0-9]{32}\.(png|jpg|webp)', value) or re.fullmatch(r'[a-zA-Z0-9_-]+\.(png|jpg|jpeg|webp)', value)):
        raise CmsError('Choose an uploaded image or an existing website image.')
    return value


def validate_content(raw):
    if not isinstance(raw, dict):
        raise CmsError('Invalid content.')
    hero = raw.get('hero', {})
    if not isinstance(hero, dict):
        raise CmsError('Invalid homepage content.')
    data = {'hero': {'line1': text(hero.get('line1'), 'Headline line 1', 60), 'line2': text(hero.get('line2'), 'Headline line 2', 60), 'description': text(hero.get('description'), 'Homepage description', 300)}}
    slides = raw.get('slides')
    if not isinstance(slides, list) or not 1 <= len(slides) <= 6:
        raise CmsError('Add between one and six carousel slides.')
    data['slides'] = []
    for s in slides:
        if not isinstance(s, dict):
            raise CmsError('Invalid slide.')
        data['slides'].append({'title': text(s.get('title'), 'Slide title', 100), 'category': text(s.get('category'), 'Slide category', 70), 'alt': text(s.get('alt'), 'Image description', 150), 'image': image_value(s.get('image'), True)})
    services = raw.get('services')
    if not isinstance(services, list) or not 1 <= len(services) <= 30:
        raise CmsError('Add between one and thirty services.')
    data['services'], slugs = [], set()
    for s in services:
        if not isinstance(s, dict):
            raise CmsError('Invalid service.')
        slug = s.get('slug', '')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or len(slug) > 70 or slug in slugs:
            raise CmsError('Each service needs a unique URL name using lowercase letters, numbers and hyphens.')
        slugs.add(slug)
        if s.get('category') not in ('court', 'field', 'facility'):
            raise CmsError('Choose a valid service category.')
        scopes = s.get('scope')
        if not isinstance(scopes, list) or not 1 <= len(scopes) <= 6:
            raise CmsError('Each service needs one to six scope items.')
        if not isinstance(s.get('published'), bool):
            raise CmsError('Choose whether the service is published.')
        data['services'].append({'slug': slug, 'title': text(s.get('title'), 'Service title', 100), 'category': s['category'], 'summary': text(s.get('summary'), 'Service summary', 300), 'scope': [text(item, 'Scope item', 180) for item in scopes], 'prompt': text(s.get('prompt'), 'Project guidance', 300), 'image': image_value(s.get('image')), 'published': s['published']})
    if not any(s['published'] for s in data['services']):
        raise CmsError('Keep at least one service published.')
    return data


def admin_record():
    body = read_object('auth/admin.json')
    return json.loads(body) if body else None


def setup_allowed(environ):
    return os.environ.get('VERCEL_ENV') == 'preview' or (test_dir() and os.environ.get('CMS_DEV_SETUP') == '1')


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600000).hex()


def session_for(environ, record):
    if not record:
        return None
    try:
        cookies = SimpleCookie(environ.get('HTTP_COOKIE', ''))
        value = cookies[COOKIE].value
        payload, signature = value.split('.')
        expected = hmac.new(bytes.fromhex(record['key']), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
        return data if isinstance(data.get('exp'), int) and data['exp'] > time.time() else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def session_cookie(record, environ):
    session = {'exp': int(time.time()) + 8 * 3600, 'csrf': secrets.token_hex(24)}
    payload = base64.urlsafe_b64encode(json.dumps(session).encode()).decode().rstrip('=')
    signature = hmac.new(bytes.fromhex(record['key']), payload.encode(), hashlib.sha256).hexdigest()
    secure = '; Secure' if os.environ.get('VERCEL') or environ.get('wsgi.url_scheme') == 'https' else ''
    return f'{COOKIE}={payload}.{signature}; Path=/; Max-Age=28800; HttpOnly; SameSite=Strict{secure}', session


def same_origin(environ):
    origin = urlsplit(environ.get('HTTP_ORIGIN', ''))
    host = environ.get('HTTP_HOST', '')
    return origin.scheme in ('http', 'https') and origin.netloc == host


def read_json(environ):
    if not environ.get('CONTENT_TYPE', '').startswith('application/json'):
        raise CmsError('Send JSON content.', 415)
    try:
        size = int(environ.get('CONTENT_LENGTH') or '0')
    except ValueError:
        raise CmsError('Invalid request size.')
    if size < 1 or size > MAX_BODY:
        raise CmsError('The upload is too large. Images must be under 2 MB.', 413)
    try:
        data = json.loads(environ['wsgi.input'].read(size))
    except (ValueError, UnicodeError):
        raise CmsError('Invalid JSON content.')
    if not isinstance(data, dict):
        raise CmsError('Invalid request.')
    return data


def response(start_response, status, payload, extra=()):
    labels = {200: 'OK', 201: 'Created', 400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 409: 'Conflict', 413: 'Content Too Large', 415: 'Unsupported Media Type', 429: 'Too Many Requests', 503: 'Service Unavailable'}
    body = json.dumps(payload, ensure_ascii=False).encode()
    headers = [('Content-Type', 'application/json; charset=utf-8'), ('Content-Length', str(len(body))), ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'), *extra]
    start_response(f'{status} {labels[status]}', headers)
    return [body]


def handle(environ, start_response):
    path, method = environ.get('PATH_INFO', ''), environ.get('REQUEST_METHOD', 'GET')
    try:
        if path.startswith('/media/'):
            if method not in ('GET', 'HEAD'):
                return response(start_response, 405, {'error': 'Use GET or HEAD.'}, [('Allow', 'GET, HEAD')])
            if not re.fullmatch(r'/media/[a-f0-9]{32}\.(png|jpg|webp)', path):
                raise CmsError('Image not found.', 404)
            body = read_object(path.lstrip('/'))
            if body is None:
                raise CmsError('Image not found.', 404)
            content_type = {'png': 'image/png', 'jpg': 'image/jpeg', 'webp': 'image/webp'}[path.rsplit('.', 1)[1]]
            start_response('200 OK', [('Content-Type', content_type), ('Content-Length', str(len(body))), ('Cache-Control', 'public, max-age=31536000, immutable'), ('X-Content-Type-Options', 'nosniff')])
            return [b'' if method == 'HEAD' else body]
        if path == '/api/admin/status':
            if method != 'GET':
                return response(start_response, 405, {'error': 'Use GET.'}, [('Allow', 'GET')])
            record = admin_record()
            session = session_for(environ, record)
            return response(start_response, 200, {'configured': bool(record), 'authenticated': bool(session), 'csrf': session['csrf'] if session else None, 'setup_allowed': bool(setup_allowed(environ)), 'setup_url': os.environ.get('CMS_SETUP_URL') if not record else None})
        if path == '/api/admin/content' and method == 'GET':
            if not session_for(environ, admin_record()):
                raise CmsError('Sign in to manage website content.', 401)
            return response(start_response, 200, load_content(strict=True))
        if method != 'POST':
            return response(start_response, 405, {'error': 'Use POST.'}, [('Allow', 'POST')])
        if not same_origin(environ):
            raise CmsError('This request must come from the dashboard.', 403)
        data = read_json(environ)
        record = admin_record()
        if path == '/api/admin/setup':
            if not setup_allowed(environ):
                raise CmsError('First-time setup is only available on the private Vercel setup deployment.', 403)
            if record:
                raise CmsError('An admin password has already been created. Sign in instead.', 409)
            password = data.get('password')
            if not isinstance(password, str) or not 14 <= len(password) <= 200:
                raise CmsError('Choose a password between 14 and 200 characters.')
            record = {'salt': secrets.token_hex(16), 'key': secrets.token_hex(32)}
            record['password'] = password_hash(password, record['salt'])
            try:
                write_object('auth/admin.json', json.dumps(record).encode())
            except Exception:
                raise CmsError('Setup could not be saved. If setup was already completed, sign in instead.', 409)
            cookie, session = session_cookie(record, environ)
            return response(start_response, 201, {'ok': True, 'csrf': session['csrf']}, [('Set-Cookie', cookie)])
        if path == '/api/admin/login':
            if not record:
                raise CmsError('Complete first-time setup on your private Vercel deployment.', 403)
            identity = environ.get('HTTP_X_VERCEL_FORWARDED_FOR') or environ.get('REMOTE_ADDR', 'unknown')
            identity = hashlib.sha256(identity.encode()).hexdigest()[:32]
            bucket = int(time.time()) // 900
            attempt_prefix = f'login/{identity}/{bucket}/'
            if len(list_objects(attempt_prefix)) >= 10:
                raise CmsError('Too many sign-in attempts. Try again in 15 minutes.', 429)
            write_object(attempt_prefix + secrets.token_hex(8) + '.json', b'{}')
            password = data.get('password')
            if not isinstance(password, str) or len(password) > 200 or not hmac.compare_digest(password_hash(password, record['salt']), record['password']):
                raise CmsError('The password is incorrect.', 401)
            cookie, session = session_cookie(record, environ)
            return response(start_response, 200, {'ok': True, 'csrf': session['csrf']}, [('Set-Cookie', cookie)])
        session = session_for(environ, record)
        if not session:
            raise CmsError('Your session has expired. Sign in again.', 401)
        if not hmac.compare_digest(environ.get('HTTP_X_CSRF_TOKEN', ''), session['csrf']):
            raise CmsError('Refresh the dashboard and try again.', 403)
        if path == '/api/admin/logout':
            return response(start_response, 200, {'ok': True}, [('Set-Cookie', f'{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict; Secure')])
        if path == '/api/admin/upload':
            from PIL import Image
            try:
                raw = base64.b64decode(data.get('data', ''), validate=True)
            except (ValueError, TypeError):
                raise CmsError('Choose a valid image file.')
            if not raw or len(raw) > MAX_IMAGE:
                raise CmsError('Images must be under 2 MB.', 413)
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    fmt = image.format
                    if fmt not in ('PNG', 'JPEG', 'WEBP') or image.width * image.height > 20000000:
                        raise ValueError()
                    image.verify()
            except Exception:
                raise CmsError('Choose a PNG, JPEG or WebP image under 20 megapixels.')
            extension, mime = {'PNG': ('png', 'image/png'), 'JPEG': ('jpg', 'image/jpeg'), 'WEBP': ('webp', 'image/webp')}[fmt]
            pathname = 'media/' + secrets.token_hex(16) + '.' + extension
            write_object(pathname, raw, mime)
            return response(start_response, 201, {'url': '/' + pathname})
        if path == '/api/admin/content':
            current = load_content(strict=True)
            if data.get('revision') != current['revision']:
                raise CmsError('The website changed in another tab. Reload its latest content before saving.', 409)
            content = validate_content(data)
            content['revision'] = secrets.token_hex(16)
            content['updated_at'] = int(time.time())
            filename = f'published/{time.time_ns():020d}-{content["revision"]}.json'
            write_object(filename, json.dumps(content, ensure_ascii=False).encode())
            return response(start_response, 200, {'ok': True, 'revision': content['revision'], 'updated_at': content['updated_at']})
        raise CmsError('Endpoint not found.', 404)
    except CmsError as error:
        return response(start_response, error.status, {'error': str(error)})
    except Exception:
        return response(start_response, 503, {'error': 'The storage service could not complete this request. Please retry.'})
