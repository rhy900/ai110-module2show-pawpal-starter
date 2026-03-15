# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

---

## Features

- **Owner & pet management** — Create an owner profile and add multiple pets (dog, cat, or other)
- **Task scheduling** — Assign tasks to pets with a time, duration, priority, and frequency
- **Smarter Scheduling** — See below
- **Mark complete** — Mark tasks done; recurring tasks automatically re-schedule themselves

---

## Smarter Scheduling

The `Scheduler` class provides the following algorithmic features:

| Feature | Description |
|---|---|
| **Sort by due date + time** | Tasks are ordered by due date first, then by scheduled time within the same day |
| **Filter by pet or status** | Retrieve only the tasks for a specific pet, or only pending/completed tasks |
| **Recurring tasks** | Daily tasks reschedule for tomorrow; weekly tasks reschedule for 7 days later |
| **Conflict detection** | Warns when two or more tasks are scheduled at the exact same time — no crashes, just warnings |

---

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

---

## Testing PawPal+

```bash
python -m pytest
```

The test suite covers:

- `mark_complete()` changes task status
- Adding a task increases a pet's task count
- Sort correctness: tasks ordered by due date, then time
- Conflict detection flags tasks at the same time
- Daily and weekly recurrence creates the correct next occurrence
- Non-recurring tasks do not produce a follow-up
- Edge cases: pet with no tasks, filtering by pet name, removing tasks

**Confidence level: ⭐⭐⭐⭐ (4/5)**
All core behaviors are covered. The main gap is that conflict detection only checks for exact time matches — overlapping durations (e.g., a 60-min task at 08:00 vs. a task at 08:30) are not currently flagged.

---

## 📸 Demo

<a href="/course_images/ai110/Screenshot 2026-03-15 at 5.37.56 PM.png" target="_blank"><img src='/course_images/ai110/Screenshot 2026-03-15 at 5.37.56 PM.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
