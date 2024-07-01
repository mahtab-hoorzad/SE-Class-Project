# SE-Class-Project
flask web application

# Rendez-vous

Rendez-vous is a web application that facilitates scheduling and coordination of group meetings based on member availability.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication:**
  - Users can register and login to the application securely.
  
- **Group Creation:**
  - Logged-in users can create new groups specifying the group name and date range for meetings.
  
- **Member Management:**
  - Automatic addition of users to groups upon creation, ensuring seamless collaboration.

- **Availability Selection:**
  - Group members can select their availability across specified date and time slots.
  
- **Common Availability Display:**
  - Displays common available time slots across all group members for efficient meeting scheduling.

## Installation

To run Rendez-vous locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mahtab-hoorzad/SE-Class-Project.git
   cd SE-Class-Project/
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Ensure you have Python and pip installed on your system.

3. **Database setup:**

   - Configure your database settings in `app.py`. The application is set up with SQLite by default.
   - Initialize the database:

     ```bash
     python app.py
     ```

   This will create the necessary tables in your database.

## Usage

Follow these steps to use Rendez-vous:

1. **Run the application:**

   ```bash
   python app.py
   ```

   Access the application at `http://localhost:5000` in your web browser.

2. **Login:**

   - Navigate to the login page and enter your credentials.
   - New users can register for an account if they don't have one.

3. **Create a Group:**

   - After logging in, create a new group by specifying the group name and the start and end dates for meetings.

4. **Group Details:**

   - View details of a specific group including its members and scheduled meetings.
   - Select your availability for meetings using the provided form.

5. **View Common Availability:**

   - See common available time slots across all group members for efficient meeting scheduling.

## Contributing

We welcome contributions to improve Rendez-vous. To contribute:

1. Fork the repository and create your branch (`git checkout -b feature/feature-name`).
2. Commit your changes (`git commit -am 'Add feature'`).
3. Push to the branch (`git push origin feature/feature-name`).
4. Create a new Pull Request.

---
