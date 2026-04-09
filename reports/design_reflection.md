# Design Reflection - Sprint 3A

## Executive Summary

<!-- TODO: -->
<!-- A description of how you approached this deliverable in terms of tools used (if none, clearly state that), manual analysis done, and team member responsibilities -->

## Design Diagrams

<!-- TODO: -->
<!-- Include design diagrams once we finalize them -->

<!-- class diagram to show main classes and their associations -->

<!-- sequence diagram that captures the current flow for your book a class endpoint -->

<!-- sequence diagram that captures the current flow for your endpoint for sending reminders -->

## Analysis of the Reflection on Design Principles

### Identified SOLID Principle violations

**Principle:** Open/Closed Principle (OCP) Violation

**File:** `app/api/classes.py`

**Line Numbers:** 138-144

**Method Name:** CreateClass.post (and others like ClassBooking.post, ClassMembers.get)

![code screenshot](./img/solid1.png)

**Explanation:** The code does not allow for easy extension because role-based permissions are hardcoded with string comparisons ("trainer", "member"). Adding new roles or changing permission logic requires modifying existing code rather than extending it through polymorphism or configuration.

**Refactoring:** We can replace the conditional logic with a Role Factory that maps user types to specific objects. Instead of each method performing string comparisons to determine permissions, it delegates the decision to a strategy object retrieved from the factory, which implements a unified interface (e.g., role.can_create_class()). This allows us to add a new role, such as an "Admin" which only requires creating a new class and registering it with the factory, leaving the core logic in classes.py unchanged.

---

**Principle:** Single Responsibility Principle (SRP)
**File:** `app/api/classes.py`
**Lines:** 321-360
**Method Name:** ClassReminder.post

[code screenshot](./img/solid2.png)

**Explanation:** The endpoint method handles auth checks, trainer ownership checks, class date validation, member lookup, email sending, error aggregation, and HTTP response shaping in one place. The method has multiple independent reasons to change: JWT/role policy changes, class-validation rules, email-delivery behavior, and response-contract changes. That concentration makes it harder to test and modify safely because unrelated concerns are coupled in a single function.

**Refactoring:** Extract a ReminderService with focused methods like validate_trainer_access, load_reminder_targets, validate_class_time_window, and send_reminders. Keep ClassReminder.post as a thin transport adapter that maps service results to HTTP codes.

---
**Principle:** Dependency Inversion Principle (DIP)
**File:** `app/apis/classes.py`
**Lines:** 176-181
**Class/Method:** CreateClass.post

![code screenshot](./img/solid3.png)

**Explanation:** CreateClass.post directly instantiates UserResource() and ClassResource() inside the method body. On lines 176 and 181, two database objects are created: user_resource, class_resource. It is hardcoded, there is no way to change this without editing the method. For example, if we wanted to swap out UserResource for a different implementation, or use a mock in tests, we cannot, the real MongoDB version is always created by this method.

**Refactoring:** Instead of creating new dependencies inside the method, they should be passed in from outside. The handler would just use whatever it receives, without knowing what the specific implementation is. This way the database layer can be altered and this method does not have to change.

---

<!-- add others here -->

<!-- Detailed written analysis of the reflection on design principles for Task 2. See task description for what should be provided for each violation -->

## Identified Code Smells

**Duplicate Code:** Identical validation logic for checking if string fields are non-empty.

**File and line number:** `app/apis/auth.py:76-87`

**Method Name**: `Register Endpoint`

![smell_1_1](./img/smell_1_1.png)

**File and line number:** `app/apis/auth.py:145-153`

**Method Name**: `Login Endpoint`

![smell_1_2](./img/smell_1_2.png)

**File and line number:** `app/apis/classes.py:139-161`

**Method Name**: `Create Class Endpoint`

![smell_1_3](./img/smell_1_3.png)

---

**Comments:** Redundant comment that could be explained with just code.

**File and line number:** `app/apis/classes.py:244-278`

**Method Name**: `ClassMembers`

![smell_2_1](./img/smell_2_1.png)

---

**Long Method:** One endpoint method handles authorization, ownership checks, class lookup, date validation, email iteration, error aggregation, and response construction in a single block.

**File and line number:** `app/apis/classes.py:319-381`
**Method Name**: `ClassReminder.post in ClassReminder`

![smell_3_1_1](./img/smell_3_1_1.png)
![smell_3_2_1](./img/smell_3_2_2.png)

---

**Primitive Obsession:** Usage of primitive types instead of small objects for simple tasks.

**File and line number:** `app/apis/classes.py:32-40`
**Method Name**: `ClassResource.get_class_by_id`


---

## Reflection on Current Design for New Features

<!-- Task 4 reflection of how your current design (especially the identified violations) may help or hinder the implementation of the two new features above, especially while keeping maintainability and extensibility in mind -->
