# Homework Creator

A Python Tkinter-based GUI app that automates generating and emailing formatted homework summaries with customizable schedules.

---

## Overview

Homework Creator allows users to quickly generate daily homework schedules and send them via email. Users can:

- Enter homework tasks for multiple subjects.
- Track estimated completion times.
- Customize class and lunch schedules.
- Send the schedule via Gmail in a formatted email.
- View a visual schedule image within the app.

The app uses a background thread to send emails so the GUI remains responsive during sending.

---

## Features

- Graphical interface using Tkinter.
- Email sending via Gmail with secure authentication.
- Customizable class schedules and lunch periods.
- Optional visual schedule display.
- Validation for recipient email addresses.
- Simple configuration through a `.env` file.

---

## Installation

1. **Clone or download the repository**:

    ```
    git clone https://github.com/michael-audi/homeworkEmail.git
    cd homework-creator
    ```

2. **Install dependencies**:

    ```
    pip install -r requirements.txt
    ```

Dependencies include:

- `tkinter` (usually included with Python)
- `Pillow` (for image display)
- `python-dotenv` (for environment variables)

3. **Setup your `.env` file**:

Create a `.env` file in the project root with the following content:

- Copy the example file `env.example` to `.env`:

      cp env.example .env

- Edit `.env` and replace the placeholders with your Gmail credentials:

      GMAIL_USER=your_email@gmail.com
      GMAIL_PASS=your_app_password

4. **Generate a Gmail App Password**:

To send emails securely, enable 2FA on your Google account and create an [App Password](https://support.google.com/accounts/answer/185833?hl=en). Use this password in your `.env` as `GMAIL_PASS`.

---

## Usage

1. Run the main Python file:

    ```
    python homework_creator.py
    ```

2. Fill in homework tasks and estimated times for each class.
3. Set the recipient email, start time, and day.
4. Click **Send** to email the schedule. Progress and success messages will display in the GUI.
5. Optionally, edit class and lunch schedules or view your schedule image.

---

## Notes

- Emails are sent via Gmail's SMTP server (`smtp.gmail.com`, port `587`).
- The app performs a simple regex validation for email addresses.
- The `.env` file keeps your credentials secure and out of version control.
- Always double-check the recipient email before sending.
