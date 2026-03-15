"""
tests/test_pawpal.py — automated tests for PawPal+ core behaviors
Run: python -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(title="Walk", time="08:00", frequency="once", priority="high"):
    return Task(
        title=title,
        duration_minutes=20,
        priority=priority,
        scheduled_time=time,
        frequency=frequency,
        due_date=date.today(),
    )


def make_scheduler():
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    return Scheduler(owner), owner, pet


# ---------------------------------------------------------------------------
# Task: mark_complete
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should set is_complete to True."""
    task = make_task()
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


# ---------------------------------------------------------------------------
# Pet: add_task increases count
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list by 1."""
    pet = Pet(name="Luna", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Feeding"))
    assert len(pet.tasks) == 1
    pet.add_task(make_task("Grooming"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Scheduler: sorting
# ---------------------------------------------------------------------------

def test_sort_tasks_by_time():
    """Tasks should come back sorted by due_date first, then scheduled_time."""
    from datetime import timedelta
    scheduler, _, pet = make_scheduler()
    today = date.today()
    tomorrow = today + timedelta(days=1)

    t1 = make_task("Evening walk", "18:00")
    t1.due_date = today
    t2 = make_task("Morning walk", "07:00")
    t2.due_date = today
    t3 = make_task("Next-day task", "06:00")
    t3.due_date = tomorrow

    sorted_tasks = scheduler.sort_tasks_by_time([t1, t2, t3])
    assert sorted_tasks[0].title == "Morning walk"   # today 07:00
    assert sorted_tasks[1].title == "Evening walk"   # today 18:00
    assert sorted_tasks[2].title == "Next-day task"  # tomorrow 06:00


# ---------------------------------------------------------------------------
# Scheduler: conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_time():
    """Two tasks at the exact same time should produce a conflict warning."""
    scheduler, _, _ = make_scheduler()
    t1 = make_task("Walk",    "09:00")
    t2 = make_task("Feeding", "09:00")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1


def test_detect_conflicts_flags_overlapping_durations():
    """A task starting during another task's duration should be flagged."""
    scheduler, _, _ = make_scheduler()
    # Walk starts 08:00, lasts 60 min → ends 09:00
    t1 = Task("Long walk", 60, "high", "08:00", "once")
    # Feeding starts 08:30 — overlaps with walk
    t2 = Task("Feeding",   10, "high", "08:30", "once")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1


def test_detect_conflicts_no_false_positives():
    """Tasks that finish before the next one starts should not conflict."""
    scheduler, _, _ = make_scheduler()
    # Walk starts 08:00, lasts 20 min → ends 08:20
    t1 = Task("Walk",    20, "high", "08:00", "once")
    # Feeding starts 08:30 — no overlap
    t2 = Task("Feeding", 10, "high", "08:30", "once")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert warnings == []


# ---------------------------------------------------------------------------
# Scheduler: recurring task creates next occurrence
# ---------------------------------------------------------------------------

def test_recurring_task_creates_next_occurrence():
    """Completing a daily task should add a new task due tomorrow."""
    scheduler, owner, pet = make_scheduler()
    task = make_task("Morning walk", frequency="daily")
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert task.is_complete is True
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].due_date == date.today() + timedelta(days=1)
    assert pending[0].title == "Morning walk"


def test_once_task_does_not_recur():
    """Completing a 'once' task should not add a new task."""
    scheduler, owner, pet = make_scheduler()
    task = make_task("Vet visit", frequency="once")
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert task.is_complete is True
    assert len(pet.get_pending_tasks()) == 0


def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task should add a new task due 7 days later."""
    scheduler, owner, pet = make_scheduler()
    task = make_task("Flea treatment", frequency="weekly")
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].due_date == date.today() + timedelta(days=7)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_produces_empty_schedule():
    """A pet with no tasks should not break generate_schedule."""
    scheduler, owner, pet = make_scheduler()
    schedule = scheduler.generate_schedule()
    assert schedule == []


def test_get_pending_tasks_excludes_completed():
    """get_pending_tasks should not return completed tasks."""
    pet = Pet(name="Mochi", species="dog")
    t1 = make_task("Walk")
    t2 = make_task("Feeding")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)

    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].title == "Feeding"


def test_remove_task_removes_by_title():
    """remove_task should remove the matching task (case-insensitive)."""
    pet = Pet(name="Luna", species="cat")
    pet.add_task(make_task("Grooming"))
    pet.add_task(make_task("Feeding"))
    pet.remove_task("grooming")  # lowercase — should still match
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feeding"


def test_filter_by_pet_name():
    """filter_tasks should return only tasks belonging to the named pet."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    walk = make_task("Walk")
    feeding = make_task("Feeding")
    mochi.add_task(walk)
    luna.add_task(feeding)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()
    luna_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")

    assert len(luna_tasks) == 1
    assert luna_tasks[0].title == "Feeding"


def test_multiple_conflicts_detected():
    """Three tasks at the same time should produce three conflict warnings (one per pair)."""
    scheduler, _, _ = make_scheduler()
    t1 = make_task("Walk",    "10:00")
    t2 = make_task("Feeding", "10:00")
    t3 = make_task("Meds",    "10:00")
    warnings = scheduler.detect_conflicts([t1, t2, t3])
    assert len(warnings) == 3
