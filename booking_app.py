import streamlit as st
import pandas as pd
from datetime import datetime
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Gmail SMTP Setup ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ID = "uttamsaxena2017@gmail.com"         # replace with your Gmail
EMAIL_PASS = "myho nhfu tcmt fytj"         # replace with your app password
COORDINATOR_EMAIL = "uttameditor@cordova.co.in"

# --- Initial Setup ---
st.set_page_config(page_title="CORDOVA PUBLICATIONS | LIVE CLASSES AND PRODUCT TRAINING BOOKING")

st.title("CORDOVA PUBLICATIONS")
st.subheader("LIVE CLASSES AND PRODUCT TRAINING BOOKING")

# --- CSV File Setup ---
CSV_FILE = "slot_bookings.csv"
ABSENT_FILE = "absent_teachers.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "School Name", "Grade", "Curriculum", "Subject", "Slot", "Teacher",
                         "Salesperson", "Salesperson Number", "Salesperson Email", "Title Used by School"])

if not os.path.exists(ABSENT_FILE):
    with open(ABSENT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Teacher"])

# --- Time Slots ---
def generate_time_slots(start="10:00", end="16:00", duration=40):
    slots = []
    current = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while current + pd.Timedelta(minutes=duration) <= end_time:
        slot_start = current.strftime("%H:%M")
        current += pd.Timedelta(minutes=duration)
        slot_end = current.strftime("%H:%M")
        slots.append(f"{slot_start}-{slot_end}")
    return slots

time_slots = generate_time_slots()

# --- Teachers Setup ---
subjects = {
    "Hindi": ["Bharti"],
    "Mathematics": ["Vivek"],
    "GK": ["Dakshika", "Ishita"],
    "SST": ["Ishita", "Shivangi"],
    "Science": ["Kalpana", "Payal", "Sneha"],
    "English": ["Aparajita", "Deepanshi", "Megha"],
    "Pre Primary": ["Yaindrila"],
    "EVS": ["Yaindrila", "Kalpana"],
    "Computer": ["Arpit", "Geetanjali"]
}

teacher_limits = {
    "Aparajita": 2,
    "Deepanshi": 2,
    "Megha": 1,
    "Arpit": 2
}

teacher_emails = {
    "Bharti": "bharti@example.com",
    "Vivek": "vivek@example.com",
    "Dakshika": "dakshika@example.com",
    "Ishita": "ishita@example.com",
    "Shivangi": "shivangi@example.com",
    "Kalpana": "kalpana@example.com",
    "Payal": "payal@example.com",
    "Sneha": "sneha@example.com",
    "Aparajita": "aparajita@example.com",
    "Deepanshi": "deepanshi@example.com",
    "Megha": "megha@example.com",
    "Yaindrila": "yaindrila@example.com",
    "Arpit": "arpit@example.com",
    "Geetanjali": "geetanjali@example.com"
}

# --- Booking Logic ---
def is_teacher_absent(teacher, date):
    if not os.path.exists(ABSENT_FILE):
        return False
    df = pd.read_csv(ABSENT_FILE)
    return not df[(df["Date"] == date) & (df["Teacher"] == teacher)].empty

def get_available_teacher(subject, slot, date, df):
    for teacher in subjects[subject]:
        if is_teacher_absent(teacher, date):
            continue
        slot_count = df[(df["Date"] == date) & (df["Slot"] == slot) & (df["Teacher"] == teacher)].shape[0]
        day_count = df[(df["Date"] == date) & (df["Teacher"] == teacher)].shape[0]
        max_limit = teacher_limits.get(teacher, 2)
        if slot_count == 0 and day_count < max_limit:
            return teacher
    return None

def send_email(to_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ID
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ID, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        st.warning(f"Email not sent to {to_email}. Error: {e}")

# --- Booking Form ---
with st.form("booking_form"):
    date = st.date_input("📅 Select Date")
    salesperson = st.text_input("👤 Salesperson Name")
    salesperson_number = st.text_input("📱 Salesperson Number")
    salesperson_email = st.text_input("📧 Salesperson Email")
    school_name = st.text_input("🏫 School Name")
   
    curriculum = st.text_input("📚 Curriculum")
    title_used = st.text_input("🏷️ Title Name Used by School")
    grade = st.text_input("🎓 Grade")
    subject = st.selectbox("📖 Select Subject", ["Select"] + list(subjects.keys()))
    slot = st.selectbox("⏰ Select Slot", ["Select"] + time_slots)

    submit = st.form_submit_button("✅ Book Slot")

# --- Booking Action ---
if submit:
    if "" in [salesperson, salesperson_number, salesperson_email, school_name, grade, curriculum, title_used] or subject == "Select" or slot == "Select":
        st.error("❗ Please fill all fields and make valid selections.")
    else:
        df = pd.read_csv(CSV_FILE)
        date_str = date.strftime("%Y-%m-%d")

        teacher = get_available_teacher(subject, slot, date_str, df)

        if not teacher:
            st.error("❌ No teacher available for this subject at the selected time.")
        elif df[(df["Date"] == date_str) & (df["Slot"] == slot)].shape[0] >= 3:
            st.error("❌ Slot is already fully booked.")
        else:
            with open(CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([date_str, school_name, grade, curriculum, subject, slot, teacher,
                                 salesperson, salesperson_number, salesperson_email, title_used])

            # Email Messages
            teacher_msg = f"""Subject: {subject}
Time: {slot}
Date: {date_str}
School: {school_name}
Grade: {grade}
Curriculum: {curriculum}
Title Used: {title_used}
Please be ready to conduct the session."""

            salesperson_msg = f"""✅ Booking Confirmed!
Date: {date_str}
School: {school_name}
Grade: {grade}
Curriculum: {curriculum}
Title: {title_used}
Subject: {subject}
Slot: {slot}
The teacher has been notified."""

            coord_msg = f"""🔒 Booking Details:
Salesperson: {salesperson} ({salesperson_number})
Email: {salesperson_email}
Date: {date_str}
School: {school_name}
Grade: {grade}
Curriculum: {curriculum}
Title Used: {title_used}
Subject: {subject}
Slot: {slot}
Teacher: {teacher} ({teacher_emails.get(teacher, "N/A")})"""

            # Send emails
            send_email(teacher_emails.get(teacher, ""), f"Live Class Scheduled: {subject}", teacher_msg)
            send_email(salesperson_email, "Your Class Booking is Confirmed", salesperson_msg)
            send_email(COORDINATOR_EMAIL, "New Class Booking Logged", coord_msg)

            st.success("✅ Booking confirmed and email notifications sent!")

# --- Footer ---
st.markdown("""
<hr style="margin-top: 50px;">
<div style='text-align: center; font-size: 12px; color: #888;'>
    © 2025 Cordova Publication Pvt Ltd. All rights reserved. <br>
    Made by <b>Uttam</b>
</div>
""", unsafe_allow_html=True)
