from datetime import datetime, timedelta
from collections import defaultdict
import csv
import os

# --- Slot Setup ---
def generate_time_slots(start="10:00", end="16:00", duration=40):
    slots = []
    current = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while current + timedelta(minutes=duration) <= end_time:
        slot_start = current.strftime("%H:%M")
        current += timedelta(minutes=duration)
        slot_end = current.strftime("%H:%M")
        slots.append(f"{slot_start}-{slot_end}")
    return slots

time_slots = generate_time_slots()

# --- Subject-Teacher Mapping ---
subjects = {
    "Hindi": ["Bharti"],
    "Mathematics": ["Vivek"],
    "GK": ["Dakshika", "Ishita"],
    "SST": ["Ishita", "Shivangi"],
    "Science": ["Kalpana", "Payal", "Sneha"],
    "English": ["Aparajita", "Deepanshi", "Megha"],
    "Pre Primary": ["Yaindrila"],
    "EVS": ["Yaindrila", "Kalpana"]
}

teacher_numbers = {
    "Bharti": "+911111111111",
    "Vivek": "+912222222222",
    "Dakshika": "+913333333333",
    "Ishita": "+914444444444",
    "Shivangi": "+915555555555",
    "Kalpana": "+916666666666",
    "Payal": "+917777777777",
    "Sneha": "+918888888888",
    "Aparajita": "+919999999999",
    "Deepanshi": "+910000000001",
    "Megha": "+910000000002",
    "Yaindrila": "+910000000003"
}

# --- Booking Limits ---
MAX_PER_SLOT = 3
MAX_PER_TEACHER = 2
MAX_ENGLISH_FALLBACK = 1

bookings_per_slot = defaultdict(list)
teacher_daily_count = defaultdict(int)

# --- CSV Setup ---
spreadsheet_file = "slot_bookings.csv"
if not os.path.exists(spreadsheet_file):
    with open(spreadsheet_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "School Name", "Grade", "Curriculum", "Subject", "Slot", "Teacher", "Salesperson", "Salesperson Number"])

# --- Get Date ---
def get_date_from_input():
    date_str = input("Enter Date (DD/MM/YYYY): ").strip()
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("❌ Invalid date format. Try again.")
        return get_date_from_input()

# --- Teacher Selection Logic ---
def get_available_teacher(subject, slot, date):
    for teacher in subjects[subject]:
        limit = MAX_ENGLISH_FALLBACK if subject == "English" and teacher != "Aparajita" else MAX_PER_TEACHER
        if teacher_daily_count[(teacher, date)] < limit and teacher not in [t for _, t in bookings_per_slot[(date, slot)]]:
            return teacher
    return None

# --- Booking Process ---
def book_slot():
    print("\n===== Cordova Live Class Slot Booking System =====")

    date = get_date_from_input()
    salesperson_name = input("Enter Your Name: ").strip()
    salesperson_number = input("Enter Your Number: ").strip()

    if not salesperson_name or not salesperson_number:
        print("❌ Name and Number are required.")
        return

    school_name = input("Enter School Name: ").strip()
    grade = input("Enter Grade of School: ").strip()
    curriculum = input("Enter Curriculum: ").strip()

    if not school_name or not grade or not curriculum:
        print("❌ All school details are required.")
        return

    print("\nAvailable Subjects:")
    for idx, subject in enumerate(subjects.keys(), 1):
        print(f"{idx}. {subject}")
    subject_choice = int(input("Select Subject (number): "))
    subject = list(subjects.keys())[subject_choice - 1]

    print("\nAvailable Time Slots:")
    for idx, slot in enumerate(time_slots, 1):
        print(f"{idx}. {slot}")
    slot_choice = int(input("Select Slot (number): "))
    slot = time_slots[slot_choice - 1]

    if len(bookings_per_slot[(date, slot)]) >= MAX_PER_SLOT:
        print("❌ This time slot is fully booked.")
        return

    teacher = get_available_teacher(subject, slot, date)
    if not teacher:
        print("❌ No available teacher for this subject at this time.")
        return

    bookings_per_slot[(date, slot)].append((subject, teacher))
    teacher_daily_count[(teacher, date)] += 1

    # Save to CSV
    with open(spreadsheet_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, school_name, grade, curriculum, subject, slot, teacher, salesperson_name, salesperson_number])

    # --- Messages ---
    print("\n📩 Message to Teacher:")
    print(f"""
Date: {date}
Subject: {subject}
Time: {slot}
School: {school_name}
Grade: {grade}
Curriculum: {curriculum}
Please be ready to conduct the session.
""")

    print("✅ Booking Confirmed!")
    print("📩 Message to Salesperson:")
    print(f"""
Date: {date}
School Name: {school_name}
Grade: {grade}
Curriculum: {curriculum}
Subject: {subject}
Scheduled Slot: {slot}
The teacher has been notified.
""")

# --- Menu Loop ---
while True:
    print("\n--- MENU ---")
    print("1. Book a Live Class Slot")
    print("2. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        book_slot()
    elif choice == '2':
        print("👋 Exiting. Thank you!")
        break
    else:
        print("❌ Invalid option. Try again.")
