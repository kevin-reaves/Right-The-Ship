Right the Ship
=============
Right the Ship is a mobile game application designed to help individuals with ADHD and procrastination by providing
incentives to complete various tasks within a given time frame. The game transforms task management into an engaging and
rewarding experience, promoting organization and focus.

Purpose
=============

This project was inspired by my wife, who needed a tool to help her organize and complete tasks more efficiently. The
functionality and design of Right the Ship are based on her ideas and requirements, aiming to offer a practical solution
for those facing similar challenges.

Features
=============

Task Management: Create, organize, and track tasks with deadlines.

Incentivized Gameplay: Earn rewards and achievements for completing tasks on time.

Customizable Reminders: Set reminders to stay on track with your tasks.

User-Friendly Interface: Intuitive design for easy navigation and task management.

Technologies Used
=============


Backend: Django, Python

Frontend: TBD

Database: TBD


How to Use
================

* python manage.py migrate -- to create the database. You should only need to run this when you first clone the project
  or
  when large changes are made to the database schema.
* python manage.py createsuperuser -- to create an admin user. You will be prompted to enter a username, email, and
  password. The admin user is helpful for viewing the data in the admin panel.
* python manage.py runserver -- to start the server. You can then access the application at http://127.0.0.1:8000/. The
  admin panel is available at http://127.0.0.1:8000/admin/ with the credentials you created in the previous step.

* There is a postman collection at tests/postman/RightTheShip.postman_collection.json that you can use to test the API
  endpoints.

User
---------------	

This is the end user that will create and view tasks. Here is an example of the input data.

    "username": "Kevin",
    "password": "don't hack me bro",
    "email": "Kevin@email.com"

Single Task
---------------	

This is a single task that does not repeat. Here is an example of the input data.

    "user_id": "{{created_user}}",
    "title": "Make machos",
    "description": "Nachos are tasty.",
    "due_date": "2024-08-10",
    "completed": false

Recurring Task
---------------

This is a task that repeats (daily, weekly, monthly, etc.). Here is an example of the input data.

    "title": "Leg day",
    "description": "Lift them weights.",
    "completed": false,
    "frequency": "Weekly",
    "start_date": "2024-08-01",
    "end_date": "2024-12-31",
    "user_id": 1,
    "day": 1

Day is the day of the week that the task should be completed. The values will depend on the frequency field

Weekly : 0 is Sunday, 1 is Monday, etc.

Monthly: 1 is the first day of the month, 2 is the second day of the month, etc.

Yearly : 1 is January 1st, 2 is January 2nd, etc.

End date and due date are similar. A single task has a due date, while a recurring task has an end date. This
distinction is made bcause a recurring task will have several due dates, one each recurrence.