import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# CONFIGURATION
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ID = "uttamsaxena2017@gmail.com"
EMAIL_PASS = "myho nhfu tcmf fytj"
COORDINATOR_EMAIL = "uttamsaxena2024@gmail.com"

BOOKING_FILE = "slot_bookings.csv"
ABSENT_FILE = "teacher_absentees.csv"

# EMAIL FUNCTION
def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ID
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASS)
        server.send_message(msg)

# LOAD DATA
if os.path.exists(BOOKING_FILE):
    bookings_df = pd.read_csv(BOOKING_FILE)
else:
    bookings_df = pd.DataFrame(columns=[
        "Date", "School Name", "Grade", "Curriculum", "Title Name Used by School",
        "Subject", "Slot", "Teacher", "Salesperson", "Salesperson Number",
        "Salesperson Email", "Teacher Email"
    ])

if os.path.exists(ABSENT_FILE):
    absent_df = pd.read_csv(ABSENT_FILE)
else:
    absent_df = pd.DataFrame(columns=["Date", "Teacher"])

# STREAMLIT SETUP
st.set_page_config(page_title="CORDOVA PUBLICATIONS | LIVE CLASSES AND PRODUCT TRAINING BOOKING")
st.title("📊 Coordinator Dashboard")
st.caption("Made by Utt@m for Cordova Publications 2025")

tab1, tab2, tab3 = st.tabs(["📋 View Bookings", "🚫 Mark Teacher Absent", "🗑️ Delete Booking"])

# TAB 1: VIEW BOOKINGS
with tab1:
    st.subheader("All Bookings")
    if bookings_df.empty:
        st.info("No bookings available.")
    else:
        st.dataframe(bookings_df)

    if st.button("📩 Send Email for Latest Booking"):
        latest = bookings_df.iloc[-1]
        body = f"""🔔 Booking Summary:

Date: {latest['Date']}
School: {latest['School Name']}
Grade: {latest['Grade']}
Curriculum: {latest['Curriculum']}
Title: {latest['Title Name Used by School']}
Subject: {latest['Subject']}
Time Slot: {latest['Slot']}
Teacher: {latest['Teacher']} ({latest['Teacher Email']})
Salesperson: {latest['Salesperson']} ({latest['Salesperson Email']})
"""
        send_email(COORDINATOR_EMAIL, "New Class Booking Summary", body)

        if pd.notna(latest["Teacher Email"]):
            send_email(latest["Teacher Email"], f"Reminder: {latest['Subject']} Class",
                       f"Dear {latest['Teacher']},\nPlease be ready for your class on {latest['Date']} at {latest['Slot']}.\nSchool: {latest['School Name']}, Grade: {latest['Grade']}, Curriculum: {latest['Curriculum']}.\nThank you!")

        if pd.notna(latest["Salesperson Email"]):
            send_email(latest["Salesperson Email"], "✅ Class Booking Confirmed", body)

        st.success("📧 Emails sent successfully.")

# TAB 2: MARK ABSENT + DELETE ABSENT
with tab2:
    st.subheader("Mark Teacher Absent")
    teacher_list = [
        "Bharti", "Vivek", "Dakshika", "Ishita", "Shivangi", "Kalpana",
        "Payal", "Sneha", "Aparajita", "Deepanshi", "Megha", "Yaindrila"
    ]
    selected_teacher = st.selectbox("Select Teacher", teacher_list)
    selected_date = st.date_input("Select Date")

    if st.button("Mark Absent"):
        date_str = selected_date.strftime("%Y-%m-%d")
        if not ((absent_df['Date'] == date_str) & (absent_df['Teacher'] == selected_teacher)).any():
            new_row = pd.DataFrame([[date_str, selected_teacher]], columns=["Date", "Teacher"])
            absent_df = pd.concat([absent_df, new_row], ignore_index=True)
            absent_df.to_csv(ABSENT_FILE, index=False)
            st.success(f"{selected_teacher} marked absent on {date_str}")
        else:
            st.warning("Teacher already marked absent on this date.")

    st.markdown("---")
    st.subheader("🗒️ Current Absentees")
    if not absent_df.empty:
        st.dataframe(absent_df)

        st.subheader("❌ Remove Absentee Entry")
        absent_entries = absent_df.apply(lambda row: f"{row['Teacher']} on {row['Date']}", axis=1).tolist()
        selected_entry = st.selectbox("Select entry to remove", absent_entries)

        if st.button("Delete Absent"):
            teacher_name, date_val = selected_entry.split(" on ")
            absent_df = absent_df[~((absent_df["Teacher"] == teacher_name) & (absent_df["Date"] == date_val))]
            absent_df.to_csv(ABSENT_FILE, index=False)
            st.success(f"Deleted absent entry for {teacher_name} on {date_val}")
    else:
        st.info("No absentees recorded yet.")

# TAB 3: DELETE BOOKING
with tab3:
    st.subheader("Delete a Booking")
    if bookings_df.empty:
        st.warning("No bookings to delete.")
    else:
        row_to_delete = st.selectbox("Select Booking Row to Delete", bookings_df.index.tolist())
        if st.button("Delete Booking"):
            bookings_df.drop(index=row_to_delete, inplace=True)
            bookings_df.to_csv(BOOKING_FILE, index=False)
            st.success("Booking deleted successfully.")
