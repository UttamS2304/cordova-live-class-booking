import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ----------------------- CONFIG -----------------------
st.set_page_config(page_title="CORDOVA PUBLICATIONS | LIVE CLASSES AND PRODUCT TRAINING BOOKING")

st.markdown("<h4 style='text-align:center;'>📚 <b>CORDOVA PUBLICATIONS</b><br>LIVE CLASSES AND PRODUCT TRAINING BOOKING</h4>", unsafe_allow_html=True)

st.markdown("---")

st.header("📝 Book Your Slot") 

# Teacher email mapping
teacher_email_map = {
    "Bharti": "bharti.teacher@example.com",
    "Vivek": "vivek.teacher@example.com",
    "Dakshika": "dakshika.teacher@example.com",
    "Ishita": "ishita.teacher@example.com",
    "Shivangi": "shivangi.teacher@example.com",
    "Kalpana": "kalpana.teacher@example.com",
    "Payal": "payal.teacher@example.com",
    "Sneha": "sneha.teacher@example.com",
    "Aparajita": "aparajita.teacher@example.com",
    "Deepanshi": "deepanshi.teacher@example.com",
    "Megha": "khannamegha153@gmail.com",
    "Yaindrila": "dasguptay@gmail.com"
}

# ----------------------- EMAIL CONFIG -----------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ID = "uttamsaxena2017@gmail.com"           # Your Gmail
EMAIL_PASS = "myho nhfu tcmt fytj"            # Your App Password
COORDINATOR_EMAIL = "uttamsaxena2024@gmail.com"  # Coordinator email

def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ID
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASS)
        server.sendmail(EMAIL_ID, to, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Email failed to send to {to}: {e}")
        return False

# ----------------------- FORM UI -----------------------

with st.form("booking_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name")
        number = st.text_input("Number")
        school = st.text_input("School Name")
        grade = st.text_input("Grade")
    with col2:
        curriculum = st.text_input("Curriculum")
        title_name = st.text_input("Title Name Used by School")
        email = st.text_input("Your Email (for confirmation)")
        date = st.date_input("Date (DD/MM/YYYY)")
    
    subject = st.selectbox("Subject", ["Hindi", "Mathematics", "GK", "SST", "Science", "English", "Pre Primary", "EVS"])
    slot = st.selectbox("Slot", ["10:00-10:40", "11:00-11:40", "12:00-12:40", "1:00-1:40", "2:00-2:40", "3:00-3:40"])
    
    submitted = st.form_submit_button("📅 Book Slot")

# ----------------------- BOOKING LOGIC -----------------------

if submitted:
    # Validate form
    if not all([name, number, school, grade, curriculum, title_name, email, subject, slot]):
        st.error("❌ Please fill in all the fields.")
    else:
        # Assign teacher and fallback logic
        teacher = ""
        if subject == "Hindi":
            teacher = "Bharti"
        elif subject == "Mathematics":
            teacher = "Vivek"
        elif subject == "GK":
            teacher = "Dakshika"
        elif subject == "SST":
            teacher = "Ishita"
        elif subject == "Science":
            teacher = "Kalpana"
        elif subject == "English":
            teacher = "Aparajita"
        elif subject == "Pre Primary":
            teacher = "Yaindrila"
        elif subject == "EVS":
            teacher = "Yaindrila"

        date_str = date.strftime("%Y-%m-%d")

        # Append booking to CSV
        df = pd.DataFrame([{
            "Date": date_str,
            "School Name": school,
            "Grade": grade,
            "Curriculum": curriculum,
            "Title Name": title_name,
            "Subject": subject,
            "Slot": slot,
            "Teacher": teacher,
            "Salesperson": name,
            "Salesperson Number": number,
            "Salesperson Email": email
        }])
        df.to_csv("slot_bookings.csv", mode='a', index=False, header=not pd.read_csv("slot_bookings.csv").empty if "slot_bookings.csv" else True)

        # ------------------ Send Emails ------------------
        msg_sales = f"""✅ Class Booking Confirmed:

School: {school}, Grade: {grade}, Curriculum: {curriculum}
Title: {title_name}
Subject: {subject}, Time: {slot}, Date: {date_str}
Teacher: {teacher}

Regards,
Cordova"""

        msg_teacher = f"""🧑‍🏫 Class Reminder

Dear {teacher},

You are assigned to conduct a class on:

Subject: {subject}
Date: {date_str}, Time: {slot}
School: {school} (Grade {grade})

Please be prepared.

– Cordova"""

        msg_coord = f"""📋 NEW CLASS BOOKING

Salesperson: {name}
Number: {number}
Email: {email}

School: {school}, Grade: {grade}, Curriculum: {curriculum}
Title Name: {title_name}
Subject: {subject}, Time: {slot}, Date: {date_str}
Assigned Teacher: {teacher}
"""

        success1 = send_email(email, "✅ Cordova Class Booking Confirmation", msg_sales)
        success2 = send_email(COORDINATOR_EMAIL, "📋 New Class Booking Logged", msg_coord)

        teacher_email = teacher_email_map.get(teacher)
        if teacher_email:
            success3 = send_email(teacher_email, "🧑‍🏫 Upcoming Class Reminder", msg_teacher)
        else:
            success3 = False
            st.warning("⚠️ Teacher email not found. Skipped sending teacher email.")

        if success1 and success2:
            st.success("✅ Booking Confirmed and Emails Sent Successfully!")
# --- Copyright Footer ---
st.markdown("""
    <hr style="margin-top: 50px;">
    <div style='text-align: center; font-size: 12px; color: #888;'>
        © 2025 Cordova Publication Pvt Ltd. All rights reserved. <br>
        Made by <b>Uttam</b>
    </div>
""", unsafe_allow_html=True)

