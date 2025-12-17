from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def status():
    return {"backend": "connected"}

@app.get("/db-test")
def db_test():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.close()
    conn.close()
    return {"db": "connected"}

## import redis
import redis

redis_client = redis.Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True
)

@app.get("/redis-test")
def redis_test():
    redis_client.set("ping", "pong")
    value = redis_client.get("ping")
    return {"redis": value}
