"""
main.py — CLI demo script for PawPal+
Run: python main.py
"""

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def print_schedule(schedule, owner_name):
    print(f"\n{'='*45}")
    print(f"  Today's Schedule for {owner_name}")
    print(f"{'='*45}")
    if not schedule:
        print("  No pending tasks for today.")
    for task in schedule:
        status = "✓" if task.is_complete else "○"
        print(
            f"  [{status}] {task.scheduled_time}  {task.title:<22}"
            f"  {task.duration_minutes} min  [{task.priority}]  ({task.frequency})"
        )
    print(f"{'='*45}\n")


def main():
    # --- Set up owner ---
    owner = Owner("Jordan")

    # --- Set up pets ---
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Add tasks to Mochi ---
    mochi.add_task(Task("Morning walk",    30, "high",   "07:00", "daily"))
    mochi.add_task(Task("Evening walk",    20, "high",   "18:00", "daily"))
    mochi.add_task(Task("Flea treatment",  10, "medium", "09:00", "weekly"))

    # --- Add tasks to Luna ---
    luna.add_task(Task("Feeding",          5,  "high",   "07:30", "daily"))
    luna.add_task(Task("Grooming",        15,  "low",    "11:00", "weekly"))
    luna.add_task(Task("Playtime",        10,  "medium", "18:00", "daily"))  # same time as Evening walk → conflict

    # --- Create scheduler and print initial schedule ---
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()
    print_schedule(schedule, owner.name)

    # --- Conflict detection ---
    conflicts = scheduler.detect_conflicts(schedule)
    if conflicts:
        print("⚠️  Conflicts detected:")
        for warning in conflicts:
            print(f"   {warning}")
        print()

    # --- Mark a recurring task complete and show next occurrence ---
    morning_walk = mochi.tasks[0]
    print(f"Marking '{morning_walk.title}' complete...")
    scheduler.mark_task_complete(morning_walk)
    print(f"  Task complete: {morning_walk.is_complete}")
    next_task = [t for t in mochi.tasks if not t.is_complete and t.title == "Morning walk"]
    if next_task:
        print(f"  Next occurrence created for: {next_task[0].due_date}\n")

    # --- Show updated schedule (morning walk gone, next one added) ---
    schedule = scheduler.generate_schedule()
    print_schedule(schedule, owner.name)

    # --- Filtering: show only Luna's tasks ---
    all_tasks = owner.get_all_tasks()
    luna_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")
    print("Luna's tasks:")
    for t in luna_tasks:
        print(f"  {t.scheduled_time}  {t.title}")
    print()


if __name__ == "__main__":
    main()
