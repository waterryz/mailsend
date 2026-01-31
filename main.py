from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os
import requests

# ================= APP =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # потом можно сузить до домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "Prime Fusion <onboarding@resend.dev>"
TO_EMAIL = "applications.primefusion@gmail.com"

if not RESEND_API_KEY:
    print("❌ RESEND_API_KEY is not set")

# ================= EMAIL =================

def send_email(subject: str, content: str):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": FROM_EMAIL,
            "to": [TO_EMAIL],
            "subject": subject,
            "text": content
        },
        timeout=10
    )

    if response.status_code >= 400:
        print("❌ RESEND ERROR:", response.text)
        response.raise_for_status()

def notify_ai_message(message: str, lang: str):
    send_email(
        subject="💬 New AI Assistant message",
        content=f"""
New message in AI Assistant

Language: {lang}

Message:
{message}
        """.strip()
    )


# ================= ROUTES =================

@app.post("/apply")
async def apply(data: Dict[str, Any] = Body(...)):
    try:
        # Формируем тело письма
        body_lines = []
        for key, value in data.items():
            if value in [None, "", False]:
                value = "-"
            body_lines.append(f"{key}: {value}")

        body = "\n".join(body_lines)

        send_email(
            subject="📥 New booking application (Waitlist)",
            content=body
        )

        return {"ok": True}

    except Exception as e:
        print("❌ APPLY ERROR:", e)
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "email_failed"}
        )
@app.post("/ai-notify")
async def ai_notify(data: Dict[str, Any] = Body(...)):
    try:
        message = (data.get("message") or "").strip()
        lang = data.get("lang", "unknown")

        if not message:
            return {"ok": False}

        send_email(
            subject="💬 New AI Assistant message",
            content=f"""
New message in AI Assistant

Language: {lang}

Message:
{message}
            """.strip()
        )

        return {"ok": True}

    except Exception as e:
        print("❌ AI NOTIFY ERROR:", e)
        return JSONResponse(
            status_code=500,
            content={"ok": False}
        )

# ================= HEALTHCHECK =================

@app.get("/")
def root():
    return {"status": "ok"}
