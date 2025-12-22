import requests
import datetime
import hashlib
import hmac
import os

# ============================
# CONFIG (FROM .env)
# ============================

LWA_CLIENT_ID = os.getenv("LWA_CLIENT_ID")
LWA_CLIENT_SECRET = os.getenv("LWA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("AMAZON_SANDBOX_REFRESH_TOKEN")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

HOST = "sandbox.sellingpartnerapi-na.amazon.com"
REGION = "us-east-1"
SERVICE = "execute-api"

# ============================
# 1) GET LWA ACCESS TOKEN
# ============================

def get_access_token():
    url = "https://api.amazon.com/auth/o2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": LWA_CLIENT_ID,
        "client_secret": LWA_CLIENT_SECRET,
    }

    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

# ============================
# 2) AWS SIGNING HELPERS
# ============================

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(secret, date, region, service):
    k_date = sign(("AWS4" + secret).encode("utf-8"), date)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, "aws4_request")
    return k_signing

# ============================
# 3) PUBLIC FUNCTION
# ============================

def get_sandbox_marketplace_participations():
    access_token = get_access_token()

    method = "GET"
    canonical_uri = "/sellers/v1/marketplaceParticipations"
    url = f"https://{HOST}{canonical_uri}"

    now = datetime.datetime.utcnow()
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    canonical_headers = (
        f"host:{HOST}\n"
        f"x-amz-access-token:{access_token}\n"
        f"x-amz-date:{amz_date}\n"
    )

    signed_headers = "host;x-amz-access-token;x-amz-date"
    payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()

    canonical_request = "\n".join([
        method,
        canonical_uri,
        "",
        canonical_headers,
        signed_headers,
        payload_hash
    ])

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"

    string_to_sign = "\n".join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    ])

    signing_key = get_signature_key(AWS_SECRET_KEY, date_stamp, REGION, SERVICE)
    signature = hmac.new(
        signing_key,
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "x-amz-access-token": access_token,
        "x-amz-date": amz_date,
        "Authorization": (
            f"{algorithm} Credential={AWS_ACCESS_KEY}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        ),
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
