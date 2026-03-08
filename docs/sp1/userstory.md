**\[sp1- US1\] View Four-Quadrant Board**

**As a user, I want to view tasks organized in a four-quadrant Eisenhower Matrix board,**  
**so that I can immediately understand task priorities at a glance.**

**Acceptance Criteria**

**Given** the user navigates to the task board  
**When** the page loads successfully  
**Then** four quadrants are displayed  
**And** each quadrant is labeled as:

- Urgent & Important
- Not Urgent & Important
- Urgent & Not Important
- Not Urgent & Not Important

You can check the Design section for visual style references; it is for inspiration only and does not need to be matched exactly.

**Elicitation → Analysis → Specification → Validation:**

Our group summarised the discussion in a mind map. Please check the issue on GitLab for details.

**\[sp1- US2\] Add Task**

**Acceptance Criteria**

**Scenario 1** - Open Creation Form

Given the user is viewing the four-quadrant board When the user clicks the "+" button Then a task creation form is displayed

**Scenario 2** - Required Information

Given the task creation form is open When the user attempts to save the task Then the system requires: A non-empty task title

**Scenario 3** - Successful Task Creation

Given the user enters a valid title and selects a quadrant When the user submits the form Then the task appears immediately in the selected quadrant And the task appears only once on the board

**Scenario 4** - Validation Error

Given the task title is empty When the user attempts to submit Then the system prevents submission And an error message is displayed

**Elicitation → Analysis → Specification → Validation:**

Our group summarised the discussion in a mind map. Please check the issue on GitLab for details.

**\[sp1- US3\] delete Task**

**As a user, I want to delete a task from the board, so that completed or outdated tasks do not clutter the interface and reduce clarity.**

**Acceptance Criteria**

**Scenario 1** - Delete Action Available

Given a task is displayed in any quadrant  
When the board is rendered  
Then a delete button is visibly displayed on each task card

**Scenario 2** - Confirmation Prompt Appears

Given a task is displayed  
When the user clicks the delete button  
Then a confirmation dialog is displayed And the task is not removed until confirmation

**Scenario 3** - Confirm Deletion

Given the confirmation dialog is displayed  
When the user selects "Confirm"  
Then the task is removed from its quadrant And the task no longer appears anywhere on the board

**Scenario 4** - Cancel Deletion

Given the confirmation dialog is displayed  
When the user selects "Cancel"  
Then the task remains unchanged

**Elicitation → Analysis → Specification → Validation:**

Our group summarised the discussion in a mind map. Please check the issue on GitLab for details.

**\[sp1- US4\] Manage Requirement Changes**

**As a team member responsible for maintaining the system requirements,**  
**I want to record and track user requirement changes as issues,**  
**so that all modifications are documented, reviewed, and traceable throughout the development process.**

**Acceptance Criteria**

**Scenario 1** - Record All Proposed Changes

Given a new requirement change is identified

When a team member updates the requirement change issue

Then the Description section must include: 1. A clear explanation of the proposed modification 2.The reason for the change 3.The date of the update

**Scenario 2** - Create Linked Implementation Task

Given a requirement change has been reviewed and approved

When the team decides to implement the change

Then a new development task must be created And the task ID must be recorded in the requirement change issue Description

**Scenario 3** - Update Status After Implementation

Given the implementation task has been completed

When the team verifies the change

Then the requirement change issue must be updated to reflect its completion status

**Elicitation & Analysis & Specification & Validation**

**Elicitation**：During team discussions, we identified that user requirements may change over time.Previously, changes were discussed informally, leading to confusion and lack of traceability.

**Analysis：**

The team analysed that requirement changes:

- Must be documented centrally.
- Must be linked to implementation tasks.
- Should prevent uncontrolled scope changes.

To balance clarity and simplicity, we decided to use a dedicated issue as a change log.

**Specification：**

please read us and acceptance criteria

**Validation:**

The process was reviewed by the team to ensure it is practical and not overly complex.

The solution:

- Prevents undocumented requirement changes.
- Ensures traceability between requirements and tasks.
- Clearly defines when a change is considered complete.