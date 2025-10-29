# file: auth_server_example.py
from flask import Flask, request, jsonify, render_template_string, redirect, send_file
from functools import wraps
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os, secrets, re
from dotenv import load_dotenv

load_dotenv()


APP = Flask(__name__)
APP.config['JWT_ACCESS_SECRET'] = os.getenv('JWT_ACCESS_SECRET', 'dev-access-secret')
APP.config['JWT_REFRESH_SECRET'] = os.getenv('JWT_REFRESH_SECRET', 'dev-refresh-secret')
ALGO = 'HS256'
ACCESS_MIN = int(os.getenv('ACCESS_MIN', '15'))
REFRESH_DAYS = int(os.getenv('REFRESH_DAYS', '7'))


USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
        "email": "admin@example.com",
        "name": "Administrator",
        "active": True
    },
    "user1": {
        "id": 2,
        "username": "user1",
        "password_hash": generate_password_hash("user123"),
        "role": "user",
        "email": "user1@example.com",
        "name": "John Doe",
        "active": True
    }
}


REFRESH_STORE = {}
REVOKED_ACCESS = set()

# OAuth client sample
OAUTH_CLIENTS = {
    "sample_client": {
        "client_secret": "topsecret",
        "name": "Sample Client",
        "redirects": ["http://localhost:5001/callback"],
        "allowed_scopes": ["profile", "email"]
    }
}

AUTH_CODES = {} 


def _is_email(addr):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', addr) is not None

def _validate_password(pw: str):
    if len(pw) < 8:
        return False, "Password must be >= 8 chars"
    if not re.search(r'[A-Z]', pw): return False, "Requires uppercase"
    if not re.search(r'[a-z]', pw): return False, "Requires lowercase"
    if not re.search(r'\d', pw): return False, "Requires a number"
    return True, ""

def _now():
    return datetime.utcnow()

def create_access(user):
    payload = {
        "sub": user['id'],
        "usr": user['username'],
        "role": user['role'],
        "typ": "access",
        "iat": _now(),
        "exp": _now() + timedelta(minutes=ACCESS_MIN)
    }
    return jwt.encode(payload, APP.config['JWT_ACCESS_SECRET'], algorithm=ALGO)

def create_refresh(user):
    tid = secrets.token_hex(18)
    payload = {
        "sub": user['id'],
        "usr": user['username'],
        "typ": "refresh",
        "tid": tid,
        "iat": _now(),
        "exp": _now() + timedelta(days=REFRESH_DAYS)
    }
    token = jwt.encode(payload, APP.config['JWT_REFRESH_SECRET'], algorithm=ALGO)
    REFRESH_STORE[tid] = {"user_id": user['id'], "created": _now(), "last_used": _now()}
    return token

def decode_access(token):
    try:
        if token in REVOKED_ACCESS:
            return None
        data = jwt.decode(token, APP.config['JWT_ACCESS_SECRET'], algorithms=[ALGO])
        if data.get('typ') != 'access': return None
        return data
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def decode_refresh(token):
    try:
        data = jwt.decode(token, APP.config['JWT_REFRESH_SECRET'], algorithms=[ALGO])
        if data.get('typ') != 'refresh': return None
        tid = data.get('tid')
        if not tid or tid not in REFRESH_STORE:
            return None
        REFRESH_STORE[tid]['last_used'] = _now()
        return data
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_token(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        hdr = request.headers.get('Authorization', '')
        if not hdr.startswith('Bearer '):
            return jsonify({"error": "missing_authorization"}), 401
        token = hdr.split(" ", 1)[1]
        payload = decode_access(token)
        if not payload:
            return jsonify({"error": "invalid_or_expired_token"}), 401
        username = payload.get('usr')
        user = USERS.get(username)
        if not user or not user['active']:
            return jsonify({"error": "user_inactive"}), 401
        request.user = payload
        return fn(*a, **kw)
    return wrapper

def require_admin(fn):
    @wraps(fn)
    @require_token
    def wrapper(*a, **kw):
        if request.user.get('role') != 'admin':
            return jsonify({"error": "admin_only"}), 403
        return fn(*a, **kw)
    return wrapper


@APP.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    u = data.get('username'); p = data.get('password')
    if not u or not p:
        return jsonify({"error": "username_and_password_required"}), 400
    user = USERS.get(u)
    if not user or not check_password_hash(user['password_hash'], p):
        return jsonify({"error": "invalid_credentials"}), 401
    if not user.get('active', True):
        return jsonify({"error": "account_disabled"}), 403

    access = create_access(user)
    refresh = create_refresh(user)
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": ACCESS_MIN * 60
    }), 200

@APP.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json() or {}
    rt = data.get('refresh_token')
    if not rt:
        return jsonify({"error": "refresh_token_required"}), 400
    payload = decode_refresh(rt)
    if not payload:
        return jsonify({"error": "invalid_or_expired_refresh"}), 401
    username = payload.get('usr')
    user = USERS.get(username)
    if not user or not user['active']:
        return jsonify({"error": "user_inactive"}), 401
    new_access = create_access(user)
    return jsonify({
        "access_token": new_access,
        "token_type": "Bearer",
        "expires_in": ACCESS_MIN * 60
    }), 200

@APP.route('/logout', methods=['POST'])
@require_token
def logout():
    hdr = request.headers.get('Authorization'); token = hdr.split(" ", 1)[1]
    REVOKED_ACCESS.add(token)
    body = request.get_json() or {}
    rt = body.get('refresh_token')
    if rt:
        try:
            decoded = jwt.decode(rt, APP.config['JWT_REFRESH_SECRET'], algorithms=[ALGO])
            tid = decoded.get('tid')
            if tid and tid in REFRESH_STORE:
                del REFRESH_STORE[tid]
        except Exception:
            pass
    return jsonify({"message": "logged_out"}), 200

@APP.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    for f in ('username','password','email','name'):
        if not data.get(f):
            return jsonify({"error": f"{f}_required"}), 400
    if data['username'] in USERS:
        return jsonify({"error": "username_exists"}), 409
    if not _is_email(data['email']): return jsonify({"error": "invalid_email"}), 400
    ok, em = _validate_password(data['password'])
    if not ok: return jsonify({"error": em}), 400
    new_id = max(u['id'] for u in USERS.values()) + 1
    USERS[data['username']] = {
        "id": new_id,
        "username": data['username'],
        "password_hash": generate_password_hash(data['password']),
        "role": "user",
        "email": data['email'],
        "name": data['name'],
        "active": True
    }
    return jsonify({"message": "registered"}), 201


@APP.route('/me')
@require_token
def me():
    uname = request.user.get('usr')
    u = USERS.get(uname)
    return jsonify({
        "id": u['id'],
        "username": u['username'],
        "email": u['email'],
        "role": u['role'],
        "name": u['name']
    }), 200

@APP.route('/admin/users', methods=['GET'])
@require_admin
def list_users():
    return jsonify({"users":[{"id":v['id'],"username":v['username'],"email":v['email'],"active":v['active']} for v in USERS.values()]}), 200


@APP.route('/oauth/authorize', methods=['GET','POST'])
def oauth_authorize():
    client_id = request.values.get('client_id')
    redirect = request.values.get('redirect_uri')
    client = OAUTH_CLIENTS.get(client_id)
    if not client or redirect not in client['redirects']:
        return jsonify({"error":"invalid_client_or_redirect"}), 400

    if request.method == 'GET':
        html = f"""
        <form method="post">
            <input name="username" value="admin"/><br/>
            <input name="password" type="password" value="admin123"/><br/>
            <input type="hidden" name="client_id" value="{client_id}"/>
            <input type="hidden" name="redirect_uri" value="{redirect}"/>
            <button type="submit">Approve</button>
        </form>
        """
        return render_template_string(html)
    username = request.form.get('username'); pw = request.form.get('password')
    user = USERS.get(username)
    if not user or not check_password_hash(user['password_hash'], pw):
        return "invalid credentials", 401
    code = secrets.token_urlsafe(24)
    AUTH_CODES[code] = {"client_id": client_id, "username": username, "exp": _now()+timedelta(minutes=10)}
    return redirect(f"{redirect}?code={code}")

@APP.route('/oauth/token', methods=['POST'])
def oauth_token():
    data = request.get_json() or request.form
    grant = data.get('grant_type')
    if grant != 'authorization_code':
        return jsonify({"error":"unsupported_grant"}), 400
    code = data.get('code'); cid = data.get('client_id'); secret = data.get('client_secret')
    client = OAUTH_CLIENTS.get(cid)
    if not client or client['client_secret'] != secret:
        return jsonify({"error":"invalid_client"}), 401
    meta = AUTH_CODES.get(code)
    if not meta or meta['client_id'] != cid or meta['exp'] < _now():
        return jsonify({"error":"invalid_or_expired_code"}), 400
    user = USERS.get(meta['username'])
    access = create_access(user)
    del AUTH_CODES[code]
    return jsonify({"access_token": access, "token_type":"Bearer", "expires_in": ACCESS_MIN * 60}), 200

@APP.route('/oauth/revoke', methods=['POST'])
def oauth_revoke():
    data = request.get_json() or request.form
    cid = data.get('client_id'); secret = data.get('client_secret'); token = data.get('token')
    client = OAUTH_CLIENTS.get(cid)
    if not client or client['client_secret'] != secret:
        return jsonify({"error":"invalid_client"}), 401
    try:
        decoded = jwt.decode(token, APP.config['JWT_ACCESS_SECRET'], algorithms=[ALGO])
        if decoded.get('typ') == 'access':
            REVOKED_ACCESS.add(token)
    except Exception:
        pass
    return ('', 200)


if __name__ == '__main__':
    print("Demo Auth Server (educational).")
    APP.run(debug=True, port=5000)
