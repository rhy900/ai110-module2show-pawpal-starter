"""
app.py — PawPal+ Streamlit UI
Run: streamlit run app.py
"""

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — Owner and Scheduler persist across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------

st.header("Owner & Pet Setup")

owner_name = st.text_input("Owner name", value="Jordan") # why value = jordan
if st.button("Set owner"):
    st.session_state.owner = Owner(owner_name)
    st.session_state.scheduler = Scheduler(st.session_state.owner)
    st.success(f"Owner set to **{owner_name}**")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi") #value?
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    existing = [p.name.lower() for p in owner.pets]
    if pet_name.lower() in existing:
        st.warning(f"'{pet_name}' is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added **{pet_name}** the {species}!")

if owner.pets:
    st.caption("Current pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.divider()

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    pet_options = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_options)

    c1, c2, c3 = st.columns(3)
    with c1:
        task_title = st.text_input("Task title", value="Morning walk")
    with c2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with c3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    c4, c5 = st.columns(2)
    with c4:
        scheduled_time = st.text_input("Time (HH:MM)", value="08:00")
    with c5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        try:
            # Validate HH:MM format
            h, m = scheduled_time.split(":")
            assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
        except Exception:
            st.error("Time must be in HH:MM format, e.g. 08:30")
        else:
            pet = next(p for p in owner.pets if p.name == selected_pet_name)
            pet.add_task(Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                scheduled_time=scheduled_time,
                frequency=frequency,
                due_date=date.today(),
            ))
            st.success(f"Task '{task_title}' added to {selected_pet_name}.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    schedule = scheduler.generate_schedule()
    conflicts = scheduler.detect_conflicts(schedule)

    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

    if not schedule:
        st.info("No pending tasks. Add some tasks above!")
    else:
        rows = []
        for task in schedule:
            rows.append({
                "Time": task.scheduled_time,
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Frequency": task.frequency,
            })
        st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Mark a task complete
# ---------------------------------------------------------------------------

st.subheader("Mark Task Complete")

all_pending = [t for pet in owner.pets for t in pet.get_pending_tasks()]
if not all_pending:
    st.info("No pending tasks to complete.")
else:
    task_labels = [f"{t.scheduled_time} — {t.title}" for t in all_pending]
    selected_label = st.selectbox("Select task to complete", task_labels)
    selected_task = all_pending[task_labels.index(selected_label)]

    if st.button("Mark complete"):
        scheduler.mark_task_complete(selected_task)
        if selected_task.frequency in ("daily", "weekly"):
            st.success(
                f"'{selected_task.title}' marked complete! "
                f"Next occurrence added for tomorrow."
            )
        else:
            st.success(f"'{selected_task.title}' marked complete!")
        st.rerun()
