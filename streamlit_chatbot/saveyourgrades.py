import streamlit as st
import pandas as pd
import random
import math
import wave
import io
import struct
import time as timer
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="Student Time Manager", layout="wide")

# ---------- HELPER: RINGTONE ----------
def make_ringtone(duration=1.2, frequency=880, sample_rate=44100):
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)

        total_frames = int(duration * sample_rate)

        for i in range(total_frames):
            cycle_position = (i / sample_rate) % 0.35

            if cycle_position < 0.25:
                value = int(
                    32767 * 0.35 * math.sin(2 * math.pi * frequency * i / sample_rate)
                )
            else:
                value = 0

            audio.writeframesraw(struct.pack("<h", value))

    buffer.seek(0)
    return buffer.read()


alarm_sound = make_ringtone()

# ---------- TIME SLOT OPTIONS ----------
def generate_time_slots():
    slots = []
    start_times = []

    for hour in range(7, 23):
        for minute in [0, 30]:
            start_times.append((hour, minute))

    durations = [30, 60, 90, 120]

    for hour, minute in start_times:
        start_dt = datetime(2024, 1, 1, hour, minute)

        for duration in durations:
            end_dt = start_dt + timedelta(minutes=duration)

            if end_dt.day == start_dt.day and end_dt.hour <= 23:
                slot = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
                slots.append(slot)

    return slots


time_slot_options = [""] + generate_time_slots()

# ---------- SESSION STATE ----------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

required_timetable_columns = [
    "Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
]

if (
    "school_timetable" not in st.session_state
    or not all(col in st.session_state.school_timetable.columns for col in required_timetable_columns)
):
    st.session_state.school_timetable = pd.DataFrame({
        "Time": [
            "09:00 - 10:30",
            "10:30 - 12:00",
            "13:00 - 14:30",
            "14:30 - 16:00"
        ],
        "Monday": ["Mathematics", "", "Programming", ""],
        "Tuesday": ["", "English", "", "Revision"],
        "Wednesday": ["Science", "", "", ""],
        "Thursday": ["", "Assignment", "", ""],
        "Friday": ["Quiz", "", "Study Group", ""]
    })

if "topics_df" not in st.session_state:
    st.session_state.topics_df = pd.DataFrame({
        "Topics": [
            "Chapter 7 Mathematics",
            "Chapter 5 Physics",
            "Python Loops"
        ]
    })

if "topics_version" not in st.session_state:
    st.session_state.topics_version = 0

if "wheel_result" not in st.session_state:
    st.session_state.wheel_result = ""

if "pomodoro_running" not in st.session_state:
    st.session_state.pomodoro_running = False

if "pomodoro_end_time" not in st.session_state:
    st.session_state.pomodoro_end_time = None

if "pomodoro_total_seconds" not in st.session_state:
    st.session_state.pomodoro_total_seconds = 0

if "pomodoro_subject" not in st.session_state:
    st.session_state.pomodoro_subject = "Mathematics"

if "pomodoro_alarm_played" not in st.session_state:
    st.session_state.pomodoro_alarm_played = False

# ---------- RANDOM POMODORO BENEFIT ----------
pomodoro_benefits = [
    "A Pomodoro timer helps you stay focused for a fixed study time.",
    "A Pomodoro timer reminds you to take short breaks so you do not feel too tired.",
    "A Pomodoro timer makes big tasks feel smaller and easier to start.",
    "A Pomodoro timer reduces procrastination by giving you a clear time limit.",
    "A Pomodoro timer improves time management during assignments and revision.",
    "A Pomodoro timer helps you avoid burnout during long study sessions."
]

if "pomodoro_benefit" not in st.session_state:
    st.session_state.pomodoro_benefit = random.choice(pomodoro_benefits)

# ---------- HELPER FUNCTIONS ----------
def remove_completed_tasks():
    st.session_state.tasks = [
        task for task in st.session_state.tasks
        if not task.get("Done", False)
    ]


def topics_to_list(df):
    topics = []

    if "Topics" not in df.columns:
        return topics

    for item in df["Topics"].tolist():
        if pd.isna(item):
            continue

        topic = str(item).strip()

        if topic != "":
            topics.append(topic)

    return topics[:100]


def list_to_topics_df(topics):
    return pd.DataFrame({"Topics": topics})


# ---------- THEMES ----------
themes = {
    "Lavender Dream 💜": {
        "bg": "linear-gradient(135deg, #f7e9ff 0%, #eef2ff 50%, #ffffff 100%)",
        "card": "#ffffffcc",
        "accent": "#8b5cf6",
        "soft": "#ede9fe",
        "text": "#3b0764"
    },
    "Peach Sunrise 🍑": {
        "bg": "linear-gradient(135deg, #fff1e6 0%, #ffe4e6 50%, #ffffff 100%)",
        "card": "#ffffffcc",
        "accent": "#fb7185",
        "soft": "#ffe4e6",
        "text": "#7c2d12"
    },
    "Mint Study 🌿": {
        "bg": "linear-gradient(135deg, #e8fff3 0%, #ecfeff 50%, #ffffff 100%)",
        "card": "#ffffffcc",
        "accent": "#10b981",
        "soft": "#d1fae5",
        "text": "#064e3b"
    },
    "Sky Blue ☁️": {
        "bg": "linear-gradient(135deg, #e0f2fe 0%, #eef6ff 50%, #ffffff 100%)",
        "card": "#ffffffcc",
        "accent": "#0ea5e9",
        "soft": "#dbeafe",
        "text": "#0c4a6e"
    },
    "Cozy Cream ☕": {
        "bg": "linear-gradient(135deg, #fff7ed 0%, #fef3c7 50%, #ffffff 100%)",
        "card": "#ffffffcc",
        "accent": "#f59e0b",
        "soft": "#fef3c7",
        "text": "#7a5c00"
    }
}

with st.sidebar:
    st.header("🎨 App Wallpaper")
    selected_theme = st.selectbox("Choose your colour theme", list(themes.keys()))

theme = themes[selected_theme]
sidebar_text_colour = "#000000" if selected_theme == "Lavender Dream 💜" else theme["text"]

# ---------- CSS ----------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: {theme["bg"]};
}}

[data-testid="stHeader"] {{
    background: rgba(255,255,255,0);
}}

html, body, p, span, label, div, h1, h2, h3, h4, h5, h6 {{
    color: {theme["text"]} !important;
}}

[data-testid="stMarkdownContainer"] * {{
    color: {theme["text"]} !important;
}}

[data-testid="stWidgetLabel"] * {{
    color: {theme["text"]} !important;
}}

[data-testid="stDataFrame"] * {{
    color: {theme["text"]} !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
    color: {sidebar_text_colour} !important;
}}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {{
    color: {sidebar_text_colour} !important;
}}

.main-title {{
    font-size: 40px;
    font-weight: 900;
    color: {theme["text"]} !important;
    margin-bottom: 4px;
}}

.subtitle {{
    font-size: 18px;
    color: {theme["text"]} !important;
    margin-bottom: 18px;
}}

.card {{
    background-color: {theme["card"]};
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.7);
    margin-bottom: 22px;
}}

.small-card {{
    background-color: {theme["soft"]};
    padding: 14px;
    border-radius: 18px;
    margin-bottom: 10px;
}}

.wheel-card {{
    background-color: {theme["soft"]};
    padding: 25px;
    border-radius: 50%;
    min-height: 220px;
    width: 220px;
    margin: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    border: 6px solid {theme["accent"]};
    box-shadow: 0px 8px 22px rgba(0,0,0,0.12);
    font-size: 20px;
    font-weight: 900;
}}

div.stButton > button:first-child {{
    background-color: {theme["soft"]};
    color: {theme["text"]} !important;
    border-radius: 999px;
    border: 2px solid {theme["accent"]};
    padding: 0.6rem 1.2rem;
    font-weight: 800;
}}

div.stButton > button:hover {{
    background-color: {theme["accent"]};
    color: white !important;
}}

.timer-display {{
    font-size: 58px;
    font-weight: 900;
    text-align: center;
    color: {theme["text"]} !important;
    padding: 15px;
}}

/* Make input boxes and dropdown options white */
[data-baseweb="input"] input {{
    background-color: white !important;
    color: #111111 !important;
}}

[data-baseweb="select"] > div {{
    background-color: white !important;
    color: #111111 !important;
}}

[data-baseweb="select"] span {{
    color: #111111 !important;
}}

[role="listbox"] {{
    background-color: white !important;
}}

[role="option"] {{
    background-color: white !important;
    color: #111111 !important;
}}

[role="option"] * {{
    background-color: white !important;
    color: #111111 !important;
}}

[data-baseweb="popover"] * {{
    background-color: white !important;
    color: #111111 !important;
}}

/* Timetable look */
[data-testid="stDataFrame"] {{
    border-radius: 18px;
    overflow: hidden;
}}

[data-testid="stDataFrame"] div {{
    font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

# ---------- PRODUCTIVITY TIPS ----------
tips = [
    "Break big tasks into smaller steps.",
    "Use the Pomodoro method: 25 minutes study, 5 minutes break.",
    "Start with the subject you find hardest.",
    "Write your top 3 priorities before studying.",
    "Keep your phone away while studying.",
    "Review your notes on the same day.",
    "Do not wait for motivation. Start with 5 minutes.",
    "Prepare your study space before starting."
]

# ---------- HEADER ----------
st.markdown(
    '<div class="main-title">📚 Student Time Management App</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">A planner for classes, tasks, reminders, topics, and Pomodoro study sessions.</div>',
    unsafe_allow_html=True
)

st.info("💡 Productivity Tip: " + random.choice(tips))

# ---------- NOTIFICATION CHECKER ----------
@st.fragment(run_every="1s")
def reminder_checker():
    now = datetime.now()
    due_tasks = []

    for task in st.session_state.tasks:
        if (
            not task.get("Done", False)
            and not task.get("Notified", False)
            and now >= task["Deadline"]
        ):
            task["Notified"] = True
            due_tasks.append(task)

    if due_tasks:
        st.toast("🔔 Reminder time! A task is due now.", icon="🔔")

        for task in due_tasks:
            st.warning(
                f"🔔 Reminder: {task['Task']} for {task['Subject']} is due now!"
            )

        st.audio(alarm_sound, format="audio/wav", autoplay=True)

    upcoming = [
        task for task in st.session_state.tasks
        if not task.get("Done", False) and now < task["Deadline"]
    ]

    if upcoming:
        upcoming = sorted(upcoming, key=lambda x: x["Deadline"])
        next_task = upcoming[0]
        remaining = next_task["Deadline"] - now
        total_seconds = max(0, int(remaining.total_seconds()))

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        st.success(
            f"⏳ Next reminder: {next_task['Task']} in "
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
    else:
        st.caption("No upcoming reminders.")

# ---------- POMODORO COUNTDOWN ----------
@st.fragment(run_every="1s")
def pomodoro_countdown():
    if st.session_state.pomodoro_running and st.session_state.pomodoro_end_time:
        now = datetime.now()
        remaining_seconds = int(
            (st.session_state.pomodoro_end_time - now).total_seconds()
        )

        if remaining_seconds > 0:
            minutes, seconds = divmod(remaining_seconds, 60)

            progress_value = 1 - (
                remaining_seconds / st.session_state.pomodoro_total_seconds
            )
            progress_value = min(max(progress_value, 0), 1)

            st.markdown(
                f"<div class='timer-display'>{minutes:02d}:{seconds:02d}</div>",
                unsafe_allow_html=True
            )

            st.progress(progress_value)

            st.markdown(
                f"<p style='text-align:center;'>Studying: <b>{st.session_state.pomodoro_subject}</b></p>",
                unsafe_allow_html=True
            )

        else:
            st.session_state.pomodoro_running = False

            if not st.session_state.pomodoro_alarm_played:
                st.session_state.pomodoro_alarm_played = True

                st.markdown(
                    "<div class='timer-display'>00:00</div>",
                    unsafe_allow_html=True
                )

                st.success(
                    f"🎉 Pomodoro completed for {st.session_state.pomodoro_subject}!"
                )

                st.toast("Pomodoro completed! Time for a break.", icon="⏰")
                st.audio(alarm_sound, format="audio/wav", autoplay=True)
                st.balloons()

    else:
        st.markdown(
            "<div class='timer-display'>Ready</div>",
            unsafe_allow_html=True
        )

        st.caption("Set your subject and minutes, then press Start Pomodoro.")

# ---------- MAIN LAYOUT ----------
left_col, right_col = st.columns([1.6, 1])

# ---------- LEFT COLUMN: MY TIMETABLE + WHEEL + POMODORO ----------
with left_col:
    # ---------- MY TIMETABLE ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏫 My Timetable")

    edited_timetable = st.data_editor(
        st.session_state.school_timetable,
        use_container_width=True,
        hide_index=True,
        row_height=48,
        num_rows="dynamic",
        column_config={
            "Time": st.column_config.SelectboxColumn(
                "Time",
                options=time_slot_options,
                help="Choose the time slot"
            ),
            "Monday": st.column_config.TextColumn("Monday"),
            "Tuesday": st.column_config.TextColumn("Tuesday"),
            "Wednesday": st.column_config.TextColumn("Wednesday"),
            "Thursday": st.column_config.TextColumn("Thursday"),
            "Friday": st.column_config.TextColumn("Friday")
        }
    )

    save_col, clear_col = st.columns(2)

    with save_col:
        if st.button("💾 Save Timetable"):
            st.session_state.school_timetable = edited_timetable
            st.success("Your timetable has been saved!")

    with clear_col:
        if st.button("🧹 Clear Timetable Subjects"):
            st.session_state.school_timetable = edited_timetable.copy()

            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                st.session_state.school_timetable[day] = ""

            st.success("Subjects cleared. Time slots are kept.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- THE WHEEL OF TOPICS ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎡 The Wheel Of Topics")

    st.write("Add topics into the list below. When the wheel picks a topic, that topic will be removed from the list.")

    edited_topics_df = st.data_editor(
        st.session_state.topics_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        row_height=42,
        key=f"topics_editor_{st.session_state.topics_version}",
        column_config={
            "Topics": st.column_config.TextColumn(
                "Topics",
                help="Add up to 100 topics"
            )
        }
    )

    current_topics = topics_to_list(edited_topics_df)

    st.caption(f"Topics available: {len(current_topics)} / 100")

    wheel_col1, wheel_col2 = st.columns([1, 1])

    with wheel_col1:
        if st.button("💾 Save Topics"):
            cleaned_topics = topics_to_list(edited_topics_df)
            st.session_state.topics_df = list_to_topics_df(cleaned_topics)
            st.session_state.topics_version += 1

            if len(cleaned_topics) > 100:
                st.warning("Only the first 100 topics were saved.")
            else:
                st.success("Topics saved!")

            st.rerun()

    with wheel_col2:
        if st.button("🎡 Spin The Wheel"):
            cleaned_topics = topics_to_list(edited_topics_df)

            if len(cleaned_topics) == 0:
                st.warning("Please add at least one topic before spinning.")
            else:
                spin_placeholder = st.empty()

                # Small spinning effect
                for _ in range(18):
                    temp_topic = random.choice(cleaned_topics)
                    spin_placeholder.markdown(
                        f"<div class='wheel-card'>🎡<br>{temp_topic}</div>",
                        unsafe_allow_html=True
                    )
                    timer.sleep(0.08)

                chosen_topic = random.choice(cleaned_topics)

                remaining_topics = cleaned_topics.copy()
                remaining_topics.remove(chosen_topic)

                st.session_state.wheel_result = chosen_topic
                st.session_state.topics_df = list_to_topics_df(remaining_topics)
                st.session_state.topics_version += 1

                st.rerun()

    if st.session_state.wheel_result:
        st.success(f"🎯 Topic selected: {st.session_state.wheel_result}")
        st.markdown(
            f"<div class='wheel-card'>🎯<br>{st.session_state.wheel_result}</div>",
            unsafe_allow_html=True
        )

    reset_col1, reset_col2 = st.columns(2)

    with reset_col1:
        if st.button("🧹 Clear All Topics"):
            st.session_state.topics_df = pd.DataFrame({"Topics": []})
            st.session_state.wheel_result = ""
            st.session_state.topics_version += 1
            st.success("All topics cleared.")
            st.rerun()

    with reset_col2:
        if st.button("❌ Clear Selected Result"):
            st.session_state.wheel_result = ""
            st.success("Selected result cleared.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- POMODORO ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⏰ Pomodoro Time!")

    pomo_col1, pomo_col2, pomo_col3 = st.columns(3)

    with pomo_col1:
        study_subject = st.text_input(
            "Study subject",
            value=st.session_state.pomodoro_subject
        )

    with pomo_col2:
        study_minutes = st.number_input(
            "Study minutes",
            min_value=1,
            max_value=180,
            value=25
        )

    with pomo_col3:
        break_minutes = st.number_input(
            "Break in between",
            min_value=1,
            max_value=60,
            value=5
        )

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("▶️ Start Pomodoro"):
            st.session_state.pomodoro_subject = study_subject
            st.session_state.pomodoro_total_seconds = int(study_minutes * 60)
            st.session_state.pomodoro_end_time = (
                datetime.now()
                + timedelta(seconds=st.session_state.pomodoro_total_seconds)
            )
            st.session_state.pomodoro_running = True
            st.session_state.pomodoro_alarm_played = False
            st.toast("Pomodoro started!", icon="▶️")

    with btn_col2:
        if st.button("⏹ Stop / Reset Timer"):
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_end_time = None
            st.session_state.pomodoro_alarm_played = False
            st.success("Pomodoro timer stopped.")

    pomodoro_countdown()

    st.caption(f"Suggested break: {break_minutes} minutes.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- RIGHT COLUMN: ADD TASK + CHECKLIST ----------
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Add Task + Checklist")

    now = datetime.now()
    default_due = now + timedelta(hours=1)

    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("Task / Reminder name")
        task_subject = st.text_input("Subject / Course")

        task_date = st.date_input(
            "Deadline date",
            value=default_due.date(),
            min_value=date.today()
        )

        task_time = st.time_input(
            "Deadline time",
            value=time(default_due.hour, default_due.minute)
        )

        priority = st.selectbox("Priority", ["Low", "Medium", "High"])

        submitted = st.form_submit_button("➕ Add Task")

    if submitted:
        deadline = datetime.combine(task_date, task_time)

        if task_name.strip() == "":
            st.warning("Please enter a task name.")

        elif deadline <= datetime.now():
            st.error("Please choose a future date and time. Past times are not allowed.")

        else:
            st.session_state.tasks.append({
                "ID": str(datetime.now().timestamp()),
                "Task": task_name.strip(),
                "Subject": task_subject.strip() if task_subject.strip() else "General",
                "Deadline": deadline,
                "Priority": priority,
                "Done": False,
                "Notified": False
            })

            st.success("Task added successfully!")

    st.markdown("### ✅ Current Checklist")

    if st.session_state.tasks:
        for i, task in enumerate(st.session_state.tasks):
            deadline_text = task["Deadline"].strftime("%d %b %Y, %I:%M %p")
            task_id = task.get("ID", str(i))

            if task["Done"]:
                status = "✅ Done"
            elif datetime.now() >= task["Deadline"]:
                status = "🔴 Due now / overdue"
            else:
                status = "🟢 Upcoming"

            st.markdown('<div class="small-card">', unsafe_allow_html=True)

            checked = st.checkbox(
                f"{task['Task']} | {task['Subject']}",
                value=task["Done"],
                key=f"task_done_{task_id}"
            )

            st.session_state.tasks[i]["Done"] = checked

            st.write(f"📅 Deadline: {deadline_text}")
            st.write(f"⭐ Priority: {task['Priority']}")
            st.write(f"Status: {status}")

            if not task["Done"] and datetime.now() < task["Deadline"]:
                time_left = task["Deadline"] - datetime.now()
                total_seconds_left = int(time_left.total_seconds())
                hours_left, remainder = divmod(total_seconds_left, 3600)
                minutes_left, seconds_left = divmod(remainder, 60)

                st.write(
                    f"⏳ Time left: {hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}"
                )

            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🧹 Remove Completed Tasks"):
            remove_completed_tasks()
            st.success("Completed tasks removed.")
            st.rerun()

    else:
        st.write("No tasks yet. Add your first task above.")

    st.divider()

    st.subheader("🔔 Active Reminder Notification")
    reminder_checker()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- POMODORO BENEFIT ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🍅 Pomodoro Benefit of the Day")

st.write(st.session_state.pomodoro_benefit)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.caption(
    "Made for college students to manage classes, deadlines, topics, reminders, and study sessions."
)