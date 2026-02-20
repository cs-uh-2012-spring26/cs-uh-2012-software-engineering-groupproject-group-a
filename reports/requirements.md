# Requirements Elicitation and Analysis

Date met with client: 10 February, 2026

## Elicitation Techniques Used

Before meeting the client, we met with our group to carefully review the details for Sprint 1.

The main elicitation technique used was a semi-structured interview. We had prepared questions to clarify each feature before meeting with the client.

1. Feature 1: Create Class
   1. Who is authorized to create a class?
   1. Do classes have fixed capacity?
   1. What is the information needed for the creation of each fitness class?
   1. Can two classes be in the same room at overlapping times?
   1. ⁠What happens when capacity is reached: block booking vs. allow waitlist?
   1. ⁠Can a class have multiple trainers?

1. View Class List (Public Page)
   1. Is there a difference between a member and guest?
   1. Should users be logged in to view the classes?
   1. ⁠Do we show capacity and “spots remaining” publicly, or only “available/full”?

1. Feature 3: Book a Class
   1. Should we prevent users from joining clashing classes? Is there a limit on how many classes a user can join?

1. Feature 4: View Member/Guest List of a Class
   1. Can class trainer or center admin remove people from classes / ban them from the system?
   1. Should users be authorized to view the classes?
   1. Can trainers only see member lists for classes they created, or any class?

We also asked general questions regarding the roles and the app in general:

- Can you clarify the roles we have?
- Should we have different registration options for a member and a trainer?
- Is a frontend required?
- Can classes be dropped?
- Can we restrict certain classes to different ages?

## Reflection on Techniques and Important Clarifications

<!-- TODO -->

- include a short reflection on (1) whether your selected techniques were useful or if you'd change them in retrospect and (2) one example of important clarifications gained through the meeting.

# Requirements Specification

<!-- this section needs to have:
    - use case diagram
    - and fleshed out use cases for all four features -->

## UML use case diagram for Sprint 1 Features

![Use Case Diagram](./UML.jpg)

## Fleshed out use cases for all four features

### Feature 1: Create Class

---

**Use Case Name**: use case name

**Preconditions**

- points

**Main Success Scenario**

1. points

**Alternative Flows / Extensions**

1. point
   1. point
2. point
   1. point

**Success Guarantee / Postconditions**

- points

### Feature 2: View Class List

---

**Use Case Name**: use case name

**Preconditions**

- points

**Main Success Scenario**

1. points

**Alternative Flows / Extensions**

1. point
   1. point
2. point
   1. point

**Success Guarantee / Postconditions**

- points

### Feature 3: Book a Class

---

**Use Case Name**: Book Fitness Class

**Preconditions**

- User is authenticated (valid JWT token).
- User role is `member` or `trainer`.
- The target class exists.
- User is not already booked in the class.
- If user is a trainer, they are not the creator of that class.

**Main Success Scenario**
1. User sends a booking request for a class (`POST /classes/{class_id}/book`).
2. System validates authentication token.
3. System validates that role is allowed (`member` or `trainer`).
4. System validates class id format and confirms class exists.
5. System adds the user to the class member list.
6. System returns success message.

**Alternative Flows / Extensions**
1. Invalid class id format
   1. System returns `422 Unprocessable Entity` with message "Invalid class id".
2. Class not found
   1. System returns `404 Not Found`.
3. User already booked this class
   1. System returns `409 Conflict`.
4. Role not allowed
   1. System returns `403 Forbidden`.
5. Trainer attempts to book their own class
   1. System returns `403 Forbidden`.
6. Unexpected booking failure
   1. System returns `400 Bad Request`.

**Success Guarantee / Postconditions**
- Username is stored in the class `member_list`.
- Booking is visible in later class/member-list queries.
- Duplicate booking is not created.

### Feature 4: View Member/Guest List of a class

---

**Use Case Name**: use case name

**Preconditions**

- points

**Main Success Scenario**

1. points

**Alternative Flows / Extensions**

1. point
   1. point
2. point
   1. point

**Success Guarantee / Postconditions**

- points
