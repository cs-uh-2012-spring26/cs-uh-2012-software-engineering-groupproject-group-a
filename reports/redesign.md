# Redesign Documentation - Sprint 3B

## Fixing Violated Design Principles and Code Smells

**Design Principle Violations and Fixes:**

- Open/Closed Principle (OCP) Violation CreateClass.post (and others like ClassBooking.post, ClassMembers.get)

  Fix: The hardcoded role checks in ClassBooking.post and ClassMembers.get were replaced with the @require_roles(TRAINER, MEMBER) decorator. Adding a new role now only requires changing the decorator argument, without modifying the method body.

- Single Responsibility Principle (SRP) ClassReminder.post

  Fix: _TODO: add ur fix explanation here_

- Dependency Inversion Principle (DIP) CreateClass.post

  Fix: Fixed the DIP issue by moving the creation of UserResource and ClassResource out of the post() method and into the constructor. The endpoint now uses self.user_resource and self.class_resource, which can be passed in from outside or default to the real implementations. This makes the method less hardcoded, easier to test with mocks, and more flexible if the database/resource layer changes later.

- Open/Closed Principle (OCP) ClassResource.book\*class

  Fix: _TODO: add ur fix explanation here_

- Open/Closed Principle (OCP) ClassBooking.post

  Fix: _TODO: add ur fix explanation here_

**Code Smells and Fixes:**

- Duplicate Code: Identical validation logic for checking if string fields are non-empty

  Fix: I fixed the duplicate code by moving the repeated string validation logic into a helper function, are_non_empty_strings(). This removed redundancy, made the endpoints cleaner, and ensures any future changes to validation only need to be made in one place.


- Long Method: One endpoint method handles authorization, ownership checks, class lookup, date validation, email iteration, error aggregation, and response construction in a single block

  Fix: _TODO: add ur fix explanation here_

- Primitive Obsession: Usage of primitive types instead of small objects for simple tasks

  Fix: _TODO: add ur fix explanation here_

- Duplicate Code: same three-line block

  Fix: The four-line block that fetches user and extracts their trainer ID was copy-pasted in both ClassMembers.get and ClassReminder.post. Extracted this code into helper function _get_trainer_id() and replaced both duplicates with a call to it.

- Dead Code: redundant validation - password field validated twice

  Fix: In Register.post in auth.py, the password field was being validated twice in the same if condition. Deleted the redundant second check since it could not change the outcome.

## Design Patterns for new Features

> **Feature 6: Create Recurring Class** <br>
> As a trainer, I want to create recurring classes (e.g., daily or monthly) so that I don’t have to manually re-enter the same class multiple times.

**Design Pattern Used:** Strategy

**Explanation and Refactoring**

The CreateClass.post method needed to handle two distinct cases, one for single classes and one for recurring ones. Without the Strategy pattern, this would have meant a growing if/else block containing both algorithms, making it harder to extend (like adding another recurrence type) and test.

The refactor extracted each algorithm into its own class (SingleClassStrategy, RecurringClassStrategy) with a shared create interface. The post method now just selects the right strategy based on is_recurring Boolean variable, does notneed to know the details of either implementation. This keeps post clean while each strategy has its own creation logic.

> **Feature 7: Configure Notifications** <br>
> As someone registered in a class, I want to choose how I receive reminders (e.g., email and/or Telegram and/or SMS etc) so I can stay informed in the ways that suit me.

**Design Pattern Used:** Strategy

**Explanation and Refactoring**

For the new notification feature, we had to completely rework our logic, and decided to utilize the Strategy design. To adhere to overall design principles, we created a general “send_reminders” function, abstracting the logic away from the ClassReminder endpoint. We implemented an interface NotificationStrategy with a single send() method which both EmailNotification and TelegramNotification along with future services will have to implement. The NotificationEngine is the actual brain responsible for delegating which services to call based on the available strategies. In the current implementation, it calls all the services available in the strategies, but this is easily adaptable to call specific services when needed. It also keeps track of the number of successful and unsuccessful notifications and returns them in a clear results array.

## New Class Diagram and It's Changes

![new_class_diagram](./img/new_class_diagram.png)

**Explanation of Changes**

The main differences in the new class diagram is that we now have a much cleaner and organized separation of logic, as well as additional helper elements which we used for the refactor and new features. Some examples of these helper elements include the enums we used to simplify response and result logic, such as ClassResult. The most significant changes, however, are evident through the new design strategies we implemented for features 6 and 7. Key changes per feature are the following:

_Feature 6_

For Recurring Class feature: the updated diagram introduces a Strategy Pattern for class creation, where CreateClass routes to either SingleClassStrategy or RecurringClassStrategy based on the is_recurring boolean. The recurring strategy takes two additional parameters: recurrence_type (either DAILY, WEEKLY or MONTHLY) and recurrence_count, how many times the class should reoccur. ClassResource.create_recurring_classes() method generates each new class assigning a recurrence_group_id, as well as the timings for each class with respect to the recurrence interval chosen. Return types across both strategies are standardized through ClassResult Enum.

_Feature 7_

_TODO: Add class diagram difference explanation_

## Member Responsibilities

To ensure everyone collaborates equally, similarly to Sprint 3A, we started by creating a composite Google Doc where we assigned responsibilies. For each task, we separated our responsibilities as such:

**Task 1**

- Each member contributed to fixing 1 or 2 design principle violations and 1 or 2 code smells
- For each new feature, we discussed together the appropriate design patterns and split up into two groups to work on the features. Dijar and Viestur were responsible for feature 6, Oleksandr and Tokla were responsible for feature 7.

**Task 2**

- With the groups established and violations + smells fixed, we worked together to implement each feature.

**Task 3**

- Adding tests were part of the individual features, Viesturs and Dijar added tests for feature 6, Oleksandr and Tokla added tests for feature 7.

**Task 4**

- TODO: check CI pipeline

**Task 5**

- We collaborated on adding changes to the new class diagram, each member pointing out what is missing, what needs to be changes, etc.
- Then we added more specific explanation of changes based on feature implementation groups.
