"""
PawPal+ backend logic layer.
Classes: Task, Pet, Owner, Scheduler
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""
    title: str
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    scheduled_time: str    # "HH:MM" 24-hour format, e.g. "08:30"
    frequency: str         # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.is_complete = True

    def next_due_date(self) -> Optional["Task"]:
        """Return a new Task for the next occurrence, or None if non-recurring."""
        if self.frequency == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            due_date=next_date,
            is_complete=False,
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet belonging to an owner."""
    name: str
    species: str           # "dog" | "cat" | "other"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task whose title matches (case-insensitive)."""
        self.tasks = [t for t in self.tasks if t.title.lower() != title.lower()]

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks."""
        return [t for t in self.tasks if not t.is_complete]


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Generates and manages the daily schedule for all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_schedule(self) -> List[Task]:
        """Build the schedule: pending tasks sorted by due_date, then scheduled_time."""
        all_pending = []
        for pet in self.owner.pets:
            all_pending.extend(pet.get_pending_tasks())
        return self.sort_tasks_by_time(all_pending)

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by due_date first, then scheduled_time within the same day."""
        return sorted(tasks, key=lambda t: (t.due_date, t.scheduled_time))

    def filter_tasks(
        self,
        tasks: List[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        result = tasks
        if pet_name is not None:
            # Build a lookup: task -> pet name
            task_to_pet = {}
            for pet in self.owner.pets:
                for task in pet.tasks:
                    task_to_pet[id(task)] = pet.name
            result = [
                t for t in result
                if task_to_pet.get(id(t), "").lower() == pet_name.lower()
            ]
        if completed is not None:
            result = [t for t in result if t.is_complete == completed]
        return result

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """
        Return warning strings for tasks whose time windows overlap.
        Two tasks conflict if one starts before the other finishes.
        Does not raise — always returns a (possibly empty) list.
        """
        def to_minutes(hhmm: str) -> int:
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        warnings = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                a_start = to_minutes(a.scheduled_time)
                a_end   = a_start + a.duration_minutes
                b_start = to_minutes(b.scheduled_time)
                b_end   = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: \"{a.title}\" ({a.scheduled_time}, {a.duration_minutes} min) "
                        f"overlaps with \"{b.title}\" ({b.scheduled_time}, {b.duration_minutes} min)"
                    )
        return warnings

    def mark_task_complete(self, task: Task) -> None:
        """
        Mark a task complete. If it recurs, add the next occurrence
        to the correct pet's task list.
        """
        task.mark_complete()
        next_task = task.next_due_date()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(next_task)
                    break
