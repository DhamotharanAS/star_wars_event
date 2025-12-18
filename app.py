import streamlit as st
import sqlite3
import random
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hashlib
import base64
import re
import requests
import time



# PAGE CONFIG

st.set_page_config(
    page_title=" Star Wars x Santa Zumba",
    page_icon="🎄",
    layout="centered"
)
st.markdown("""
<style>

/* ===== PAGE BACKGROUND ===== */
            
/* ===== ADMIN TITLE FIX ===== */
.admin-title {
    font-size: 3rem;
    font-weight: 900;
    color: #0f172a !important;
    text-align: center;
    margin: 2rem 0 1.5rem 0;
    text-shadow: 0 8px 25px rgba(0,0,0,0.25);
}
.stApp {
    background: linear-gradient(120deg,
        #eaffd0 0%,
        #d7f9ff 35%,
        #dbe7ff 65%,
        #f4d9ff 100%);
    font-family: 'Segoe UI', sans-serif;
}

/* ===== HERO CARD (WORKING VERSION) ===== */
.hero-card p {
    font-size: 13px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #475569 !important;  /* ⬅ darker */
    font-weight: 600;
    margin-bottom: 18px;        /* ⬅ separation */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}


/* Eyebrow text */
.hero-card p {
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #334155 !important;
    margin-bottom: 14px;
    opacity: 1 !important;
}

/* Main title */
.hero-card h1 {
    font-size: 56px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #0f172a !important;
    line-height: 1.15;
    margin: 0;
    opacity: 1 !important;
    text-shadow: 0 6px 20px rgba(15, 23, 42, 0.18);
}

/* Subtitle */
.hero-card .subtitle {
    margin-top: 4px;
    font-size: 18px;
    color: #b91c1c !important;
    font-weight: 600;
    opacity: 1 !important;
}
.centered-sub {
    text-align: center;
    width: 100%;
    margin: 14px auto 0 auto;
}

.hero-divider {
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #dc2626, #f87171);
    margin: 22px auto 18px;
    border-radius: 2px;
}


/* ===== INPUT LABELS ===== */
label, .stTextInput label, .stSelectbox label {
    color: #0f172a !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

/* ===== INPUT FIELDS ===== */
input, textarea, select {
    background: #1f2937 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    border: none !important;
    caret-color: #fffff !important;
}

/* ===== REGISTER BUTTON ===== */
.stButton > button {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    border-radius: 14px;
    padding: 0.7rem 1.8rem;
    font-weight: 700;
    border: none;
    box-shadow: 0 10px 25px rgba(220,38,38,0.35);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* ===== STATUS BOXES ===== */
.success-box {
    background: #dcfce7;
    color: #065f46;
    padding: 1rem 1.25rem;
    border-radius: 14px;
    font-weight: 700;
    margin: 1.5rem auto;
    max-width: 500px;
    text-align: center;
}

.warning-box {
    background: #fef3c7;
    color: #92400e;
    padding: 1rem;
    border-radius: 12px;
    margin-top: 1rem;
    font-weight: 600;
}

.info-box {
    background: #e0f2fe;
    color: #075985;
    padding: 1rem;
    border-radius: 12px;
    margin-top: 0.75rem;
    font-weight: 700;
}

/* ===== MOBILE ===== */
@media (max-width: 768px) {
    .hero-card h1 {
        font-size: 32px;
        letter-spacing: 1px;
    }
    .hero-card {
        padding: 36px 20px;
    }
}

</style>
""", unsafe_allow_html=True)




# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

DB_FILE = "event_data.db"
EXCEL_FILE = "event_data.xlsx"
DEFAULT_TITLE = "STAR WARS WITH SANTA"

POWER_AUTOMATE_URL = "https://1ae565bf7ac1e2f2a5e1d7c5013a0c.52.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2f6ba135f8064b74b9e5bdc798eb9314/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=XGgQC-T-vrP054EqoIGjAE7r7gIOGF00HFjewV9rgq4"

ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

DEPARTMENTS = [
    "Select Department",
    "Digital Team", "IT Team", "HR", "Finance",
    "Operations", "Marketing", "Sales",
    "Customer Support", "Admin", "Other"
]

ALLOWED_EMAIL_DOMAINS = ["gmail.com", "saipem.com"]

# --------------------------------------------------
# EMAIL VALIDATION (STRICT)
# --------------------------------------------------
# EMAIL_REGEX = re.compile(
#     r"^(?!.*\.\.)"
#     r"[a-zA-Z0-9._%+-]+"
#     r"@"
#     r"[a-zA-Z0-9-]+"
#     r"(?:\.[a-zA-Z]{2,6})$"
# )
EMAIL_REGEX = re.compile(
    # r"^[a-zA-Z0-9._%+-]+@(gmail\.com|saipem\.com)$"
    r"^[a-zA-Z0-9._%+-]+@(saipem\.com)$"
)


# def normalize_email(email: str) -> str:
#     return email.strip().lower().rstrip("., ")

def normalize_email(email: str) -> str:
    return email.strip().lower()


# def is_valid_email(email: str) -> bool:
#     return EMAIL_REGEX.fullmatch(email) is not None
def is_valid_email(email: str) -> bool:
    return EMAIL_REGEX.fullmatch(email) is not None


# def is_allowed_domain(email: str) -> bool:
#     return email.split("@")[-1] in ALLOWED_EMAIL_DOMAINS

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
def verify_admin_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_PASSWORD_HASH

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            department TEXT,
            timestamp TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = {
        "event_title": DEFAULT_TITLE,
        "event_date": "",
        "event_time": "",
        "event_location": ""
    }

    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", (k, v))

    conn.commit()
    return conn

def get_setting(conn, key):
    r = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r[0] if r else ""

def set_setting(conn, key, value):
    conn.execute("REPLACE INTO settings VALUES (?,?)", (key, value))
    conn.commit()

def generate_uuid(conn):
    while True:
        uid = "".join(str(random.randint(0, 9)) for _ in range(4))
        if not conn.execute("SELECT 1 FROM participants WHERE uuid=?", (uid,)).fetchone():
            return uid

def is_email_registered(conn, email):
    row = conn.execute(
        "SELECT uuid FROM participants WHERE email=?",
        (email,)
    ).fetchone()
    return row[0] if row else None

def add_participant(conn, name, email, dept):
    uid = generate_uuid(conn)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO participants(uuid,name,email,department,timestamp) VALUES (?,?,?,?,?)",
        (uid, name, email, dept, ts)
    )
    conn.commit()
    export_excel(conn)
    return uid

def get_all_participants(conn):
    return conn.execute("""
        SELECT id, uuid, name, email, department, timestamp
        FROM participants
        ORDER BY timestamp DESC
    """).fetchall()

def export_excel(conn):
    rows = get_all_participants(conn)
    df = pd.DataFrame(
        rows,
        columns=["ID", "UUID", "Name", "Email", "Department", "Timestamp"]
    )
    df.to_excel(EXCEL_FILE, index=False)

# 🔒 WINDOWS-SAFE RESET
def reset_all(conn):
    c = conn.cursor()
    c.execute("DELETE FROM participants")
    c.execute("DELETE FROM sqlite_sequence WHERE name='participants'")
    conn.commit()

    df_empty = pd.DataFrame(
        columns=["ID", "UUID", "Name", "Email", "Department", "Timestamp"]
    )
    df_empty.to_excel(EXCEL_FILE, index=False)

# --------------------------------------------------
# FONTS
# --------------------------------------------------
def fb(size):
    for f in ["DejaVuSans-Bold.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

def fr(size):
    for f in ["DejaVuSans.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

# --------------------------------------------------
# PASS DESIGN (UNCHANGED)
# --------------------------------------------------
# def make_pass(name, uuid, dept, title, date, time, location):
#     W, H = 1100, 650
#     img = Image.new("RGB", (W, H), "#020617")
#     d = ImageDraw.Draw(img)

#     for _ in range(220):
#         x, y = random.randint(0, W), random.randint(0, H)
#         d.ellipse((x, y, x+2, y+2), fill="#94a3b8")

#     d.rectangle((0, 0, W, 120), fill="#b91c1c")
#     # d.text((40, 32), title, font=fb(42), fill="white")
#     safe_title = re.sub(r"[^\w\s×]", "", title)
#     d.text((40, 32), safe_title, font=fb(42), fill="white")

#     d.text((40, 80), "Presented by Digital & IT", font=fr(22), fill="#fee2e2")

#     d.rounded_rectangle((50, 150, W-50, 320), radius=24, fill="white")
#     d.text((W//2 - 85, 170), "YOUR LUCKY ID", font=fr(22), fill="#666")

#     uuid_font = fb(100)
#     bbox = d.textbbox((0, 0), uuid, font=uuid_font)
#     tw = bbox[2] - bbox[0]

#     glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
#     gd = ImageDraw.Draw(glow)
#     gd.text(((W - tw)//2, 215), uuid, font=uuid_font, fill=(185, 28, 28, 90))
#     glow = glow.filter(ImageFilter.GaussianBlur(14))
#     img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
#     d = ImageDraw.Draw(img)

#     d.text(((W - tw)//2, 215), uuid, font=uuid_font, fill="#111")

#     d.rounded_rectangle((50, 350, 520, 580), radius=22, fill="white")
#     d.rounded_rectangle((580, 350, W-50, 580), radius=22, fill="white")

#     d.text((80, 370), "Attendee", font=fb(28), fill="#111")
#     d.text((80, 420), f"Name: {name}", font=fr(24), fill="#333")
#     d.text((80, 460), f"Department: {dept}", font=fr(24), fill="#333")

#     d.text((610, 370), "Event Details", font=fb(28), fill="#111")
#     d.text((610, 420), f"Date & Time: {date} {time}", font=fr(24), fill="#333")
#     d.text((610, 460), f"Location: {location}", font=fr(24), fill="#333")

#     d.text(
#         (W//2 - 260, H-40),
#         "Lights • Music • Zumba • May The Dance Be With You",
#         font=fr(20),
#         fill="#e5e7eb"
#     )

#     buf = BytesIO()
#     img.save(buf, format="PNG")
#     buf.seek(0)
#     return buf
def make_pass(name, uuid, dept, title, date, time, location):
    W, H = 1100, 650
    img = Image.new("RGB", (W, H), "#020617")
    d = ImageDraw.Draw(img)

    # Background stars
    for _ in range(220):
        x, y = random.randint(0, W), random.randint(0, H)
        d.ellipse((x, y, x+2, y+2), fill="#94a3b8")

    # Header
    d.rectangle((0, 0, W, 120), fill="#b91c1c")

    # ---- CENTERED TITLE + SUBTITLE ----
    safe_title = re.sub(r"[^\w\s×]", "", title)

    title_font = fb(42)
    subtitle_font = fr(22)

    title_bbox = d.textbbox((0, 0), safe_title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]

    subtitle = "Presented by Digital & IT"
    sub_bbox = d.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]

    title_x = (W - title_w) // 2
    sub_x = (W - sub_w) // 2

    d.text((title_x, 32), safe_title, font=title_font, fill="white")
    d.text((sub_x, 82), subtitle, font=subtitle_font, fill="#fee2e2")

    # ---- LUCKY ID CARD ----
    d.rounded_rectangle((50, 160, W-50, 330), radius=24, fill="white")
    d.text((W//2 - 90, 180), "YOUR LUCKY ID", font=fr(22), fill="#666")

    # Dynamic font sizing (prevents overlap)
    base_size = 90
    while True:
        uuid_font = fb(base_size)
        bbox = d.textbbox((0, 0), uuid, font=uuid_font)
        tw = bbox[2] - bbox[0]
        if tw < (W - 200) or base_size <= 70:
            break
        base_size -= 4

    uuid_x = (W - tw) // 2
    uuid_y = 220

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((uuid_x, uuid_y), uuid, font=uuid_font, fill=(185, 28, 28, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    d.text((uuid_x, uuid_y), uuid, font=uuid_font, fill="#111")

    # ---- INFO CARDS ----
    d.rounded_rectangle((50, 360, 520, 580), radius=22, fill="white")
    d.rounded_rectangle((580, 360, W-50, 580), radius=22, fill="white")

    d.text((80, 380), "Attendee", font=fb(28), fill="#111")
    d.text((80, 430), f"Name: {name}", font=fr(24), fill="#333")
    d.text((80, 470), f"Department: {dept}", font=fr(24), fill="#333")

    d.text((610, 380), "Event Details", font=fb(28), fill="#111")
    d.text((610, 430), f"Date & Time: {date} {time}", font=fr(24), fill="#333")
    d.text((610, 470), f"Location: {location}", font=fr(24), fill="#333")

    # Footer
    footer_text = "Lights • Music • Zumba • May The Dance Be With You"
    footer_bbox = d.textbbox((0, 0), footer_text, font=fr(20))
    footer_w = footer_bbox[2] - footer_bbox[0]
    d.text(((W - footer_w)//2, H-40), footer_text, font=fr(20), fill="#e5e7eb")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --------------------------------------------------
# INIT
# --------------------------------------------------
conn = init_db()
is_admin = st.query_params.get("admin") == "true"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# --------------------------------------------------
# ADMIN PANEL
# --------------------------------------------------
if is_admin and not st.session_state.admin_logged_in:
    st.markdown(
    "<div class='admin-title'>🔐 Admin Login</div>",
    unsafe_allow_html=True
)

    pwd = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if verify_admin_password(pwd):
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Wrong password")

elif is_admin and st.session_state.admin_logged_in:
    st.markdown(
    "<div class='admin-title'>🔧 Admin Panel</div>",
    unsafe_allow_html=True
)


    if st.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

    with st.form("settings"):
        title = st.text_input("Event Title", get_setting(conn, "event_title"))
        date = st.text_input("Event Date", get_setting(conn, "event_date"))
        time = st.text_input("Event Time", get_setting(conn, "event_time"))
        loc = st.text_input("Event Location", get_setting(conn, "event_location"))

        if st.form_submit_button("Save Settings"):
            set_setting(conn, "event_title", title)
            set_setting(conn, "event_date", date)
            set_setting(conn, "event_time", time)
            set_setting(conn, "event_location", loc)
            st.success("Settings saved")

    df = pd.DataFrame(
        get_all_participants(conn),
        columns=["ID","UUID","Name","Email","Department","Timestamp"]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)

    st.download_button(
        "📥 Export Excel",
        buf,
        "registrations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("⚠️ Reset EVERYTHING"):
        reset_all(conn)
        st.success("All data reset")
        st.rerun()

# --------------------------------------------------
# USER PAGE
# --------------------------------------------------
else:
    st.markdown("""
    <div class="hero-card">
        <p>🎄 DIGITAL & IT PRESENTS</p>
        <div class="hero-divider"></div>
        <h1>STAR WARS WITH SANTA</h1>
        <div class="subtitle centered-sub">
                Dance • Zumba • Celebration</div>
    </div>
    """, unsafe_allow_html=True)





    if "registered" not in st.session_state:
        st.session_state.registered = False

    if not st.session_state.registered:
        name = st.text_input("Full Name")
        if "email_input" not in st.session_state:
            st.session_state.email_input = ""

        if "reset_email" not in st.session_state:
            st.session_state.reset_email = False

        # Reset email field BEFORE rendering input
        if st.session_state.reset_email:
            st.session_state.email_input = ""
            st.session_state.reset_email = False

        email_input = st.text_input(
            "Email ID",
            key="email_input"
        )

        # email_input = st.text_input(
        #     "Email ID",
        #     key="email_input"
        # )

        dept = st.selectbox("Department", DEPARTMENTS)

        if st.button("Register"):
            email = normalize_email(email_input)

            if not name or dept == "Select Department" or not email:
                st.error("Please fill all fields")
            elif not is_valid_email(email):
                error_box = st.empty()
                error_box.error("❌ Please enter a valid Saipem Email ID")

                # Trigger reset for next run
                st.session_state.reset_email = True

                time.sleep(2.5)
                error_box.empty()

                st.rerun()



            else:
                existing = is_email_registered(conn, email)
                if existing:
                    st.markdown("<div class='warning-box'>⚠️ Already registered</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-box'>Your Lucky ID: {existing}</div>", unsafe_allow_html=True)

                else:
                    uid = add_participant(conn, name, email, dept)
                    st.session_state.registered = True
                    st.session_state.uid = uid
                    st.session_state.name = name
                    st.session_state.email = email
                    st.session_state.dept = dept
                    st.rerun()

    else:
        st.markdown("<div class='success-box'>🎉 Registration Successful!</div>", unsafe_allow_html=True)

        st.markdown(
            f"<h1 style='text-align:center;color:#b91c1c'>{st.session_state.uid}</h1>",
            unsafe_allow_html=True
        )

        pass_img = make_pass(
            st.session_state.name,
            st.session_state.uid,
            st.session_state.dept,
            get_setting(conn, "event_title"),
            get_setting(conn, "event_date"),
            get_setting(conn, "event_time"),
            get_setting(conn, "event_location")
        )

        st.download_button(
            "🎫 Download Event Pass",
            pass_img,
            f"pass_{st.session_state.uid}.png",
            "image/png"
        )

        # try:
        #     pass_b64 = base64.b64encode(pass_img.getvalue()).decode("ascii")
        #     payload = {
        #         "name": st.session_state.name,
        #         "email": st.session_state.email,
        #         "uuid": st.session_state.uid,
        #         "department": st.session_state.dept,
        #         "event": get_setting(conn, "event_title"),
        #         "pass_name": f"pass_{st.session_state.uid}.png",
        #         "pass_base64": pass_b64
        #     }
        #     requests.post(POWER_AUTOMATE_URL, json=payload, timeout=5)
        # except:
        #     st.info("Email will be sent shortly.")

        # if not st.session_state.email_sent:
        if "email_sent" not in st.session_state:
            st.session_state.email_sent = False

        if not st.session_state.email_sent:
            try:
                pass_b64 = base64.b64encode(pass_img.getvalue()).decode("ascii")
                payload = {
                    "name": st.session_state.name,
                    "email": st.session_state.email,
                    "uuid": st.session_state.uid,
                    "department": st.session_state.dept,
                    "event": get_setting(conn, "event_title"),
                    "pass_name": f"pass_{st.session_state.uid}.png",
                    "pass_base64": pass_b64
                }
                requests.post(POWER_AUTOMATE_URL, json=payload, timeout=5)
                st.session_state.email_sent = True   # 🔐 LOCK IT
            except:
                st.info("Email will be sent shortly.")



        st.snow()
