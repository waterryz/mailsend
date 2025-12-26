from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SMTP_EMAIL = "applications.primefusion@gmail.com"
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

print("LOGIN:", SMTP_EMAIL)
print("PASS EXISTS:", bool(SMTP_PASSWORD))



@app.post("/apply")
async def apply(data: Dict[str, Any] = Body(...)):
    try:
        lines = []
        for key, value in data.items():
            if value in [None, ""]:
                value = "-"
            lines.append(f"{key}: {value}")

        body = "\n".join(lines)

        msg = MIMEMultipart()
        msg["From"] = f"Prime Fusion Website <{SMTP_EMAIL}>"
        msg["To"] = SMTP_EMAIL
        msg["Subject"] = "📥 New booking application (Waitlist)"

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return {"ok": True}

    except Exception as e:
        print("ERROR:", e)
        return JSONResponse({"ok": False}, status_code=500)
