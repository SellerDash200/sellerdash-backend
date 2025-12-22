# SETS Env Variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
import redis

from tasks import add
from auth import get_current_user
from amazon_spapi import get_sandbox_marketplace_participations

app = FastAPI()

# --------------------
# CORS
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# PUBLIC ROUTES
# --------------------
@app.get("/api/status")
def status():
    return {"backend": "connected"}

# --------------------
# PROTECTED ROUTES
# --------------------
@app.get("/api/protected")
def protected_route(user=Depends(get_current_user)):
    return {
        "status": "ok",
        "user_id": user["sub"],
    }

# --------------------
# AMAZON SP-API (SANDBOX)
# --------------------
@app.get("/api/amazon/sandbox/marketplaces")
def amazon_sandbox_marketplaces(user=Depends(get_current_user)):
    data = get_sandbox_marketplace_participations()

    return {
        "status": "ok",
        "clerk_user_id": user["sub"],
        "amazon_data": data,
    }

# --------------------
# DATABASE
# --------------------
@app.get("/db-test")
def db_test(user=Depends(get_current_user)):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.close()
    conn.close()
    return {"db": "connected"}

# --------------------
# REDIS
# --------------------
redis_client = redis.Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
)

@app.get("/redis-test")
def redis_test():
    redis_client.set("ping", "pong")
    val
