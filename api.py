import sqlite3
import json
import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Дозволяємо фронтенду (Next.js) стукати до нашого бекенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "sites.db"

def get_color(name: str) -> str:
    if not name:
        return "#000000"
    hex_hash = hashlib.md5(name.encode()).hexdigest()
    return f"#{hex_hash[:6]}"

def get_initials(name: str) -> str:
    if not name: 
        return "?"
    return name[0].upper()

@app.get("/api/startups")
def get_startups():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM startups ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    startups = []
    for row in rows:
        tags_raw = row["tags"]
        tags = json.loads(tags_raw) if tags_raw else []
        
        startups.append({
            "id": str(row["id"]), 
            "name": row["name"],
            "websiteUrl": row["website_url"],
            "tagline": row["tagline"] or "",
            "description": row["tagline"] or "", 
            "tags": tags,
            "status": "tracking" if row["status"] == "scraped" else "watching",
            "color": get_color(row["name"]),
            "initials": get_initials(row["name"]),
            "lastActivity": row["created_at"][:10],
            "pricing": [] # Поки залишаємо пустим, бо структуру прайсів ще не парсимо
        })
    return startups

@app.get("/api/insights")
def get_insights():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insights ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    insights_list = []
    for row in rows:
        summary = row["ai_summary"] or ""
        
        # Мікро-костиль, щоб підігнати під строгі типи фронта
        change_type = "feature"
        if any(keyword in summary.lower() for keyword in ["pric", "$", "цін", "tariff", "план"]):
            change_type = "pricing"
        elif any(keyword in summary.lower() for keyword in ["позиц", "pivot", "mission"]):
            change_type = "positioning"
            
        insights_list.append({
            "id": f"i{row['id']}",
            "startupId": str(row["startup_id"]),
            "type": change_type,
            "headline": "Оновлення стартапу", # Дефолтний заголовок, поки не витягнемо його окремо
            "summary": summary,
            "createdAt": row["created_at"][:10],
            "impact": "Medium impact" 
        })
    return insights_list    