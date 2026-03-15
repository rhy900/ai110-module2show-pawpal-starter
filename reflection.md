# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    Task (dataclass): title, duration_minutes, priority, scheduled_time, frequency, is_complete, due_date
    Pet (dataclass): name, species, list of tasks
    Owner: name, list of pets — can add pets, get all tasks across all pets
    Scheduler: takes an Owner, generates/sorts/filters the daily plan, detects conflicts

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
yes changing the sortign of the schudal to be based of deu date first to enure tgghat the tasks that are requireed to ginsh first get done first rather than based on when i was schedualed 

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
 i made due date matter most because keepig late submission to a minimum is a prioity 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    the schedualr looks for overlaps in the durantion of task isntead of looking at exact matches because the overlaps will also catch the exact match this is a bit slower but much more acturate

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
    - questing the ai abotu the trade off and using it as a sort of wall to bounce ideas of of was the most helpful 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
    - AI first made conflict detection only check exact time matches. I rejected that and had it use actual time windows instead. Verified it with a test for overlapping durations.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
    - mark_complete, adding tasks, sort order, conflict detection, recurring tasks, and edge cases like empty pets. Important because they cover everything the scheduler depends on.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
    - Pretty confident, 14 tests pass. Next I'd test tasks that span midnight and owners with no pets.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - The conflict detection — it went from a basic check to a real overlap algorithm because I pushed back on the first AI output.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - Add priority-based scheduling so high-priority tasks get suggested first when conflicts happen.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - AI speeds things up but you still have to make the actual design decisions and push back when the first answer isn't right.
