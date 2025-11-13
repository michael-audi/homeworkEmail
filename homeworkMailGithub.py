"""
Homework Creator
----------------
A Tkinter-based GUI app that automates generating and emailing
formatted homework summaries with customizable schedules.

Author: Michael Audi
License: MIT
Date: 2025-11-12
"""

# --------------------------- #
#           Imports
# --------------------------- #
from datetime import date, datetime
from email.mime.text import MIMEText
from PIL import Image, ImageTk
from dotenv import load_dotenv
from tkinter import ttk
import math
import os
import random
import re
import smtplib
import sys
import threading
import time
import tkinter as tk

# --------------------------- #
#      Establish Vars
# --------------------------- #

# <!> Set this to your own .env file path or leave blank if located in the same directory.
# .env file should contain:
#   GMAIL_USER=your_email@gmail.com
#   GMAIL_PASS=your_app_password
load_dotenv(dotenv_path=".env") # TODO

MESSAGES_SENT = 0

today = date.today()
now = datetime.now()
formatted_date = today.strftime("%A %m/%d/%Y")
formatted_date2 = today.strftime("%m/%d/%Y")

# change this to your image file path of your schedule(TODO)
img_path = "/YOUR/PATH/TO/colorSchedule.png"

quarter = "Q1"

# Used by background thread to communicate with main thread
send_thread_result = {"done": False, "success": False, "error": None}

# Example schedule (edit as needed)
# Orange, Yellow, Green, Tan, Red, Purple, Blue
schedule = [
    ["B", "C", "D", "~", "E", "~", "F"], # Day 1
    ["C", "B", "~", "D", "E", "F", "~"], # Day 2
    ["C", "~", "B", "D", "~", "E", "~"], # Day 3
    ["~", "C", "D", "B", "E", "~", "F"], # Day 4
    ["C", "D", "~", "~", "B", "E", "F"], # Day 5
    ["B", "~", "D", "E", "F", "AB", "~"], # Day 6
    ["~", "C", "D", "E", "~", "F", "B"]] # Day 7

# Default settings, again, change as needed (TODO) --> WHS Standard
color_blocks = {"Orange":"Math", 
                "Yellow":"Free", 
                "Green":"CSA", 
                "Tan":"English", 
                "Red":"History", 
                "Purple":"Bio", 
                "Blue":"Spanish"}

cb = color_blocks # Alias

# Default schedule --> WHS Standard
classes = [f"{cb['Orange']}, {cb['Yellow']}, {cb['Green']}, {cb['Red']}, {cb['Blue']}", # Day 1
           f"{cb['Yellow']}, {cb['Orange']}, {cb['Tan']}, {cb['Red']}, {cb['Purple']}", # Day 2
           f"{cb['Green']}, {cb['Orange']}, {cb['Tan']}, {cb['Purple']}, {cb['Blue']}", # Day 3
           f"{cb['Tan']}, {cb['Yellow']}, {cb['Green']}, {cb['Red']}, {cb['Blue']}", # Day 4
           f"{cb['Red']}, {cb['Orange']}, {cb['Yellow']}, {cb['Purple']}, {cb['Blue']}", # Day 5
           f"{cb['Purple']}, {cb['Orange']}, {cb['Green']}, {cb['Tan']}, {cb['Red']}", # Day 6
           f"{cb['Blue']}, {cb['Yellow']}, {cb['Green']}, {cb['Tan']}, {cb['Purple']}"] # Day 7

# Default drop clases --> WHS Standard
drops = [f"{cb['Tan']}, {cb['Purple']}", # Day 1
         f"{cb['Green']}, {cb['Blue']}", # Day 2
         f"{cb['Yellow']}, {cb['Red']}", # Day 3
         f"{cb['Orange']}, {cb['Purple']}", # Day 4
         f"{cb['Green']}, {cb['Tan']}", # Day 5
         f"{cb['Yellow']}, {cb['Blue']}", # Day 6
         f"{cb['Orange']}, {cb['Red']}"] # Day 7

# Default settings, again, change as needed (TODO) --> WHS Standard
lunches = ["1st", "2nd", "3rd", "2nd", "1st", "(Free)", "(Free)"]

recipient_email = "email@gmail.com" # Default recipient email (optional) TODO
name = "Name" # Default sender name (optional) TODO
myEmail = os.getenv("GMAIL_USER")
myPass = os.getenv("GMAIL_PASS")

smtp_server = 'smtp.gmail.com'
smtp_port = 587

# --------------------------- #
#       Helper Functions
# --------------------------- #

# Send through server then quit
def send_email(subject, message, password, recipient):
    """
    NOTE: This function is safe to run in a background thread.
    It sends the email and raises exceptions on failure.
    It MUST NOT update any Tk widgets.
    """
    global MESSAGES_SENT

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = myEmail
    msg['To'] = recipient

    # Use a timeout so the thread doesn't hang forever
    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
    server.starttls()
    server.login(myEmail, password)
    server.send_message(msg)
    server.quit()

    MESSAGES_SENT += 1
    # DO NOT touch Tk widgets here

def _thread_send_wrapper(subject, message, password, recipient):
    """
    Runs in background thread. Writes result into send_thread_result for the mainloop to read.
    """
    global send_thread_result
    # reset result
    send_thread_result["done"] = False
    send_thread_result["success"] = False
    send_thread_result["error"] = None

    try:
        send_email(subject, message, password, recipient)
        send_thread_result["success"] = True
    except smtplib.SMTPAuthenticationError:
        send_thread_result["error"] = "Authentication failed (check GMAIL_USER / GMAIL_PASS)"
        send_thread_result["success"] = False
    except smtplib.SMTPConnectError:
        send_thread_result["error"] = "SMTP connection failed"
        send_thread_result["success"] = False
    except Exception as e:
        send_thread_result["error"] = str(e)
        send_thread_result["success"] = False
    finally:
        send_thread_result["done"] = True


# Stops program
def quit_all():
    # Kills all threads
    for t in threading.enumerate():
        if t is not threading.main_thread():
            t.join(timeout=0.2)
    main_window.destroy()
    sys.exit()

# Find individaul hour and minute component from a string of "h:mm"
def findTime(timeString):
    hour = ""
    minute = ""
    
    isColon = False
    
    for i in range(0, len(timeString)):
        if timeString[i] == ":":
            isColon = True
        elif isColon:
            minute = minute + timeString[i]
        else:
            hour = hour + timeString[i]
    
    return [int(hour), int(minute)]

def military_to_regular(hour):
    return ((hour - 1) % 12) + 1

# Generates body text of email given all parameters
def generate_msg(math_hw, math_t, bio_hw, bio_t, history_hw, history_t, english_hw, english_t, electives_hw, electives_t, assessments, extra_notes, name, recipient, timeStart, day):
    global hour
    global minute
    # Calculate time & dates
    total_time = int(math_t) + int(bio_t) + int(history_t) + int(english_t) + int(electives_t)

    today = date.today()
    formatted_date = today.strftime("%A %m/%d/%Y")

    now = datetime.now()

    # Adds on how much time from starting time the homework would take
    minute = str((findTime(timeStart)[1] + (total_time % 60)) % 60)
    hour = military_to_regular((findTime(timeStart)[0] + math.floor((findTime(timeStart)[1] + total_time) / 60)))
   
    # makes sure its not 11:4 (should be 11:04)
    if len(minute) == 1:
        minute = "0" + minute
    
    # Get today's schedule's blocks and map it out to each class
    block_schedule = [schedule[int(day)-1][0], schedule[int(day)-1][5], schedule[int(day)-1][4], schedule[int(day)-1][3], (schedule[int(day)-1][2] + schedule[int(day)-1][6])]
    
    
    message = f'''𝐆𝐨𝐨𝐝 𝐚𝐟𝐭𝐞𝐫𝐧𝐨𝐨𝐧, {name}. 𝐇𝐞𝐫𝐞 𝐢𝐬 𝐲𝐨𝐮𝐫 𝐡𝐨𝐦𝐞𝐰𝐨𝐫𝐤 𝐟𝐨𝐫 {formatted_date} (Day {day}) :   
__________________________________________

      ({block_schedule[0]})  𝐏𝐫𝐞-𝐜𝐚𝐥𝐜: {math_hw} ({math_t})
      ({block_schedule[1]})  𝐁𝐢𝐨𝐥𝐨𝐠𝐲: {bio_hw} ({bio_t})
      ({block_schedule[2]})  𝐇𝐢𝐬𝐭𝐨𝐫𝐲: {history_hw} ({history_t})
      ({block_schedule[3]})  𝐄𝐧𝐠𝐥𝐢𝐬𝐡: {english_hw} ({english_t})
      ({block_schedule[4]}) 𝐄𝐥𝐞𝐜𝐭𝐢𝐯𝐞𝐬: {electives_hw} ({electives_t})

𝐓𝐨𝐭𝐚𝐥 𝐭𝐢𝐦𝐞: {math.floor(total_time / 60)}h {total_time % 60}m
𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐚𝐭 ({timeStart}) 𝐲𝐨𝐮 𝐰𝐨𝐮𝐥𝐝 𝐟𝐢𝐧𝐢𝐬𝐡 𝐚𝐭 ({hour}:{minute})

𝐂𝐥𝐚𝐬𝐬𝐞𝐬 𝐓𝐨𝐦𝐨𝐫𝐫𝐨𝐰: {classes[int(day)-1]} 
𝐃𝐫𝐨𝐩𝐩𝐞𝐝 𝐂𝐥𝐚𝐬𝐬𝐞𝐬: {drops[int(day) - 1]}
𝐋𝐮𝐧𝐜𝐡: {lunches[int(day)-1]}

𝐀𝐬𝐬𝐞𝐬𝐬𝐦𝐞𝐧𝐭𝐬 𝐭𝐡𝐢𝐬 𝐰𝐞𝐞𝐤: {assessments}

𝐄𝐱𝐭𝐫𝐚 𝐧𝐨𝐭𝐞𝐬: {extra_notes}
__________________________________________

Sent via Python @{now.strftime("%H:%M")} {today.strftime("%m/%d/%Y")}

From: {myEmail}
To: {recipient}
'''
    
    return message

def test_message(message):
    global state_label
    global time_start_entry

    global hour
    global minute

    state_label.config(text=f"Test Complete! ({time_start_entry.get()}) -> ({hour}:{minute})")

    print(message)

def is_valid_email(email):
    """
    Simple regex check to see if email is in a valid format.
    Returns True if valid, False otherwise.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def create_button(parent, text, command, width, height):
    return tk.Button(
        parent,
        text=text,
        bg="white",
        fg="#2D3E50",
        activebackground="#F4D35E",
        activeforeground="#2D3E50",
        highlightbackground="#BBBBBB",
        highlightcolor="#BBBBBB",
        highlightthickness=1,
        bd=0,
        width=width,
        height=height,
        padx=2, pady=2,
        command=command
    )

def submit_answers(class_entries, lunch_entries):
    # Change all class names
    i = 0
    for element in class_entries:
        color_blocks[list(color_blocks.keys())[i]] = element.get()
        element.delete(0, tk.END)
        i += 1

    # Change all lunches names
    i = 0
    for element in lunch_entries:
        lunches[i] = element.get()
        element.delete(0, tk.END)
        i += 1

def threaded_send_email():
    """
    Called by the Send button. Disables UI, starts the progress animation,
    launches the background thread, and starts polling for completion.
    """
    # Basic validation
    recipient = gmail_to_entry.get().strip()
    if not recipient or not is_valid_email(recipient):
        state_label.config(text="State: Enter valid email", fg="red")
        return

    # Disable UI and start animation
    send_button.config(state="disabled")
    state_label.config(text="State: Sending email...", fg="orange")
    progress.start(10)  # start indeterminate animation (10 ms tick)

    subject = f"Homework {formatted_date}"
    message = generate_msg(
        math_hw_entry.get(), math_time_entry.get(),
        bio_hw_entry.get(), bio_time_entry.get(),
        history_hw_entry.get(), history_time_entry.get(),
        english_hw_entry.get(), english_time_entry.get(),
        electives_hw_entry.get(), electives_time_entry.get(),
        assessments_entry.get(), extra_notes_entry.get(),
        name_entry.get(), recipient,
        time_start_entry.get(), day_entry.get()
    )

    # Start background thread
    t = threading.Thread(target=_thread_send_wrapper, args=(subject, message, myPass, recipient))
    t.daemon = True
    t.start()

    # Start polling for result
    main_window.after(200, lambda: check_thread_result(t))


def check_thread_result(thread):
    """
    Polls the shared send_thread_result. Runs on the main thread (via after).
    """
    if not send_thread_result["done"]:
        # still running : schedule another poll
        main_window.after(200, lambda: check_thread_result(thread))
        return

    # Thread finished -> stop animation and re-enable UI
    progress.stop()
    send_button.config(state="normal")

    if send_thread_result["success"]:
        state_label.config(text=f"State: Email sent! ({MESSAGES_SENT})", fg="#2A9D56")
    else:
        err = send_thread_result["error"] or "Unknown error"
        # Keep error short for UI
        state_label.config(text=f"State: Error sending email: {err}", fg="red")

# --------------------------- #
#        Side Windows
# --------------------------- #

def edit_classes():
    classes_window = tk.Toplevel(main_window)
    classes_window.title("Class & Lunch Schedules")
    classes_window.geometry("245x280")
    
    classes_bg_color = "#B73291"
    classes_window.configure(bg=classes_bg_color)

    title_frame = tk.Frame(classes_window, bg=classes_bg_color)
    title_frame.grid(row=0, column=0, pady=5, padx=25)

    title_label = tk.Label(title_frame, text=f"Edit Classes & Lunches", fg="black", bg="white", highlightbackground=classes_bg_color, font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0)

    quarter_label = tk.Label(title_frame, text=f"({quarter})", fg="black", bg="white", highlightbackground=classes_bg_color, font=("Arial", 14, "bold"))
    quarter_label.grid(row=0, column=1)

    classes_colors_frame = tk.Frame(classes_window, bg=classes_bg_color)
    classes_colors_frame.grid(row=1, column=0, pady=5, columnspan=4)

    # Orange, Yellow,... label (left)
    for i in range(7):
        class_label = tk.Label(classes_colors_frame, text=f"{list(color_blocks.keys())[i]}", bg=classes_bg_color, justify="left", anchor="w")
        class_label.grid(row=i, column=0, sticky="we")

    # Class entries

    classes_entries = []
    font_color = "black"
    for i in range(7):       
        # Get readable font color 
        if i >= 2 and i != 3:
            font_color = "white"
        else:
            font_color = "black"
        
        class_entry = tk.Entry(classes_colors_frame, width=6, bg=list(color_blocks.keys())[i], fg=font_color, highlightbackground=classes_bg_color)
        class_entry.grid(row=i, column=1)
        class_entry.insert(0, color_blocks.get(list(color_blocks.keys())[i]))

        classes_entries.append(class_entry)
    
    # Barrier + Day 1, Day 2, Day 3,... label
    for i in range(7):
        label_spacing = tk.Label(classes_colors_frame, text=f"  |  Day {i + 1}", bg=classes_bg_color)
        label_spacing.grid(row=i, column=2)

    # Lunch Schedule Entries
    lunches_entries = []

    for i in range(7):
        lunch_entry = tk.Entry(classes_colors_frame, width=4, bg="white", fg="black", highlightbackground=classes_bg_color)
        lunch_entry.grid(row=i, column=3)
        lunch_entry.insert(0, lunches[i])

        lunches_entries.append(lunch_entry)

    # Submit & Close buttons
    classes_buttons_frame = tk.Frame(classes_window, bg=classes_bg_color)
    classes_buttons_frame.grid(row=7, column=0, pady=5, padx=30)

    submit_button = create_button(classes_buttons_frame, "Submit", lambda: submit_answers(classes_entries, lunches_entries), 2, 1)
    submit_button.grid(row=0, column=0, padx=2)

    back_button = create_button(classes_buttons_frame, "Back", lambda: classes_window.destroy(), 2, 1)
    back_button.grid(row=0, column=1, padx=2)

    classes_window.bind("<Escape>", lambda e: classes_window.destroy())

    classes_window.mainloop()


def open_schedule_window():
    # Create a new top-level window
    scale = 0.6
    imgXsize = 1076
    imgYsize = 768

    schedule_window = tk.Toplevel()
    schedule_window.title("Schedule")
    schedule_window.geometry(f"{int(imgXsize * scale + 20)}x{int(imgYsize * scale + 20)}")  # adjust as needed
    schedule_window.configure(bg="black")

    # Load the image
    img = Image.open(img_path)

    img = img.resize((int(imgXsize * scale), int(imgYsize * scale)))  # adjust size if needed

    # Convert image to Tkinter format
    tk_img = ImageTk.PhotoImage(img)

    # Display image
    img_label = tk.Label(schedule_window, image=tk_img, bg="black")
    img_label.image = tk_img  # Keep a reference to avoid garbage collection
    img_label.pack(padx=10, pady=10)

    # Make Esc key close the window
    schedule_window.bind("<Escape>", lambda e: schedule_window.destroy())



# --------------------------- #
#         Main Window
# --------------------------- #

# Create tkinter window

main_window = tk.Tk()
main_window.title("Homework Creater")
main_window.geometry("270x358")

bg_color = "#3279B7"
main_window.configure(bg=bg_color)

# Decorate window

name_frame = tk.Frame(main_window, bg=bg_color)
name_frame.grid(row=0, column=0, columnspan=3)

name_entry = tk.Entry(name_frame, width=10, bg="white", fg="black", highlightbackground=bg_color)
name_entry.insert(0, name)
name_entry.grid(row=0, column=0)

name_label = tk.Label(name_frame, text=f"({formatted_date2})", fg="black", bg="white", highlightbackground=bg_color, font=("Arial", 14, "bold"))
name_label.grid(row=0, column=1)

# Math

math_hw_entry = tk.Entry(main_window, width=25, bg="#E63946", fg="white", highlightbackground=bg_color)
math_hw_entry.insert(0, "Math Homework")
math_hw_entry.grid(row=1,column=0)

math_time_entry = tk.Entry(main_window, width=2, bg="white", fg="black", highlightbackground=bg_color)
math_time_entry.insert(0, "0")
math_time_entry.grid(row=1,column=1)

# Science

bio_hw_entry = tk.Entry(main_window, width=25, bg="#2A9D56", fg="white", highlightbackground=bg_color)
bio_hw_entry.insert(0, "Science Homework")
bio_hw_entry.grid(row=2,column=0)

bio_time_entry = tk.Entry(main_window, width=2, bg="white", fg="black", highlightbackground=bg_color)
bio_time_entry.insert(0, "0")
bio_time_entry.grid(row=2,column=1)

# History

history_hw_entry = tk.Entry(main_window, width=25, bg="#8E44AD", fg="white", highlightbackground=bg_color)
history_hw_entry.insert(0, "History Homework")
history_hw_entry.grid(row=3,column=0)

history_time_entry = tk.Entry(main_window, width=2, bg="white", fg="black", highlightbackground=bg_color)
history_time_entry.insert(0, "0")
history_time_entry.grid(row=3,column=1)

# English

english_hw_entry = tk.Entry(main_window, width=25, bg="#F4D35E", fg="black", highlightbackground=bg_color)
english_hw_entry.insert(0, "English Homework")
english_hw_entry.grid(row=4,column=0)

english_time_entry = tk.Entry(main_window, width=2, bg="white", fg="#4B3B05", highlightbackground=bg_color)
english_time_entry.insert(0, "0")
english_time_entry.grid(row=4,column=1)

# Electives

electives_hw_entry = tk.Entry(main_window, width=25, bg="#F6AE2D", fg="black", highlightbackground=bg_color)
electives_hw_entry.insert(0, "Electives Homework")
electives_hw_entry.grid(row=5,column=0)

electives_time_entry = tk.Entry(main_window, width=2, bg="white", fg="black", highlightbackground=bg_color)
electives_time_entry.insert(0, "0")
electives_time_entry.grid(row=5,column=1)

# Assessments

extra_frames = tk.Frame(main_window, bg=bg_color)
extra_frames.grid(row=6, column=0, columnspan=4)

assessments_entry = tk.Entry(extra_frames, width=28, bg="#3A3A3A", highlightbackground=bg_color)
assessments_entry.insert(0, "Assessments")
assessments_entry.grid(row=0,column=0)

# Extra notes

extra_notes_entry = tk.Entry(extra_frames, width=28, bg="#3A3A3A", highlightbackground=bg_color)
extra_notes_entry.insert(0, "Extra notes")
extra_notes_entry.grid(row=1,column=0)

# Recipients

gmail_to_entry = tk.Entry(extra_frames, width=28, bg="white", fg="black", highlightbackground=bg_color)
gmail_to_entry.insert(0, recipient_email)
gmail_to_entry.grid(row=2,column=0)

# Time & Day Entry

time_day_frame = tk.Frame(main_window, bg=bg_color)
time_day_frame.grid(row=7, column=0, columnspan=4)

time_label = tk.Label(time_day_frame, text="Time", fg="#3A3A3A", bg=bg_color, highlightbackground=bg_color, font=("Arial", 16, "bold"))
time_label.grid(row=0, column=0)

h = military_to_regular(int(now.strftime("%H")))
m = now.strftime("%M")

time_start_entry = tk.Entry(time_day_frame, width=4, bg="#43AA8B", fg="white", highlightbackground=bg_color)
time_start_entry.insert(0, f"{h}:{m}")
time_start_entry.grid(row=0, column=1, padx=(0, 5))

day_label = tk.Label(time_day_frame, text="Day", fg="#3A3A3A", bg=bg_color, highlightbackground=bg_color, font=("Arial", 16, "bold"))
day_label.grid(row=0, column=2)

day_entry = tk.Entry(time_day_frame, width=1, bg="#FFCB77", fg="black", highlightbackground=bg_color)
day_entry.insert(0, str(random.randint(1,7)))
day_entry.grid(row=0, column=3)

# Buttons

buttons_frame = tk.Frame(main_window, bg=bg_color)
buttons_frame.grid(row=8, column=0, columnspan=4)

send_button = create_button(buttons_frame, "Send", threaded_send_email, 2, 1)
send_button.grid(row=0, column=0, padx=1)

edit_classes_button = create_button(buttons_frame, "Edit", lambda: edit_classes(), 2, 1)
edit_classes_button.grid(row=0, column=1, padx=1)

schedule_classes_button = create_button(buttons_frame, "Schedule", lambda: open_schedule_window(), 4, 1)
schedule_classes_button.grid(row=0, column=2, padx=1)

quit_button = create_button(buttons_frame, "Quit", quit_all, 2, 1)
quit_button.grid(row=0, column=3, padx=1)

# State / Progress

label_frame = tk.Frame(main_window, bg=bg_color)
label_frame.grid(row=10, column=0, columnspan=2)

state_label = tk.Label(label_frame, text="State: Awaiting Response...", fg="orange", bg=bg_color, highlightbackground=bg_color, font=("Arial", 15, "bold"))
state_label.grid(row=1)

# indeterminate progress bar (will animate while sending)
style = ttk.Style()
style.theme_use('clam')  # switch away from macOS aqua theme
style.configure("Custom.Horizontal.TProgressbar",
                troughcolor="#336699",
                background="#F4D35E",
                bordercolor="#336699",
                lightcolor="#F4D35E",
                darkcolor="#F4D35E")

progress = ttk.Progressbar(main_window, style="Custom.Horizontal.TProgressbar",
                           orient="horizontal", mode="indeterminate", length=220)
progress.grid(row=9, column=0, columnspan=4, pady=(6,0))

# Run main
if __name__ == "__main__":
    main_window.mainloop()
