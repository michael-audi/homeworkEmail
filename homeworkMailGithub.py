import math
import smtplib
import sys
from email.mime.text import MIMEText
from datetime import date, datetime
import tkinter as tk

today = date.today()
now = datetime.now()
formatted_date = today.strftime("%A %m/%d/%Y")

myEmail = "yourgmail@gmail.com" # ACTION REQUIRED : enter in your email (who sends the message)
recipient_email = "recipientgmail@gmail.com" # ACTION REQUIRED : enter in email to who it gets sent to
name = "Name"
myPass = "#### #### #### ####" # ACTION REQUIRED : add "App Password" for gmail

# IMPORTANT : Make sure you have 2FA enabled or this may become a security risk !!!

smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Send through server then quit
def send_email(subject, message, password, recipient):
    msg = MIMEText(message)
    msg['Subject'] = subject

    msg['From'] = myEmail
    msg['To'] = recipient

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(myEmail, password)

    server.send_message(msg)
    server.quit()

# Stops program
def quit_all():
    root.destroy()
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
def generate_msg(math_hw, math_t, bio_hw, bio_t, history_hw, history_t, english_hw, english_t, electives_hw, electives_t, assessments, extra_notes, name, recipient, timeStart):
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
    
    # Craft message
    message = f'''𝐆𝐨𝐨𝐝 𝐚𝐟𝐭𝐞𝐫𝐧𝐨𝐨𝐧, {name}. 𝐇𝐞𝐫𝐞 𝐢𝐬 𝐲𝐨𝐮𝐫 𝐡𝐨𝐦𝐞𝐰𝐨𝐫𝐤 𝐟𝐨𝐫 {formatted_date}:
__________________________________________

𝐏𝐫𝐞-𝐜𝐚𝐥𝐜: {math_hw} ({math_t})
𝐁𝐢𝐨𝐥𝐨𝐠𝐲: {bio_hw} ({bio_t})
𝐇𝐢𝐬𝐭𝐨𝐫𝐲: {history_hw} ({history_t})
𝐄𝐧𝐠𝐥𝐢𝐬𝐡: {english_hw} ({english_t})
𝐄𝐥𝐞𝐜𝐭𝐢𝐯𝐞𝐬: {electives_hw} ({electives_t})

𝐓𝐨𝐭𝐚𝐥 𝐭𝐢𝐦𝐞: {math.floor(total_time / 60)}h {total_time % 60}m
𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐚𝐭 ({timeStart}) 𝐲𝐨𝐮 𝐰𝐨𝐮𝐥𝐝 𝐟𝐢𝐧𝐢𝐬𝐡 𝐚𝐭 ({hour}:{minute})

𝐀𝐬𝐬𝐞𝐬𝐬𝐦𝐞𝐧𝐭𝐬 𝐭𝐡𝐢𝐬 𝐰𝐞𝐞𝐤: {assessments}

𝐄𝐱𝐭𝐫𝐚 𝐧𝐨𝐭𝐞𝐬: {extra_notes}
__________________________________________

Sent via Python @{now.strftime("%H:%M")} {today.strftime("%m/%d/%Y")}

From: {myEmail}
To: {recipient}
'''
    
    return message



# Create tkinter window

root = tk.Tk()
root.title("Homework Creater")
root.geometry("270x370")

bg_color = "#3273a8"
root.configure(bg=bg_color)

# Decorate window - feel free to change colors - bg = background color, fg = font color

name_entry = tk.Entry(root, width=25, bg="white", fg="black", highlightbackground=bg_color)
name_entry.insert(0, name)
name_entry.grid(row=0, column=0)

# Math

math_hw_entry = tk.Entry(root, width=25, bg="red", fg="white", highlightbackground=bg_color)
math_hw_entry.insert(0, "Math Homework")
math_hw_entry.grid(row=1,column=0)

math_time_entry = tk.Entry(root, width=2, bg="white", fg="black", highlightbackground=bg_color)
math_time_entry.insert(0, "0")
math_time_entry.grid(row=1,column=1)

# Science

bio_hw_entry = tk.Entry(root, width=25, bg="green", fg="white", highlightbackground=bg_color)
bio_hw_entry.insert(0, "Biology Homework")
bio_hw_entry.grid(row=2,column=0)

bio_time_entry = tk.Entry(root, width=2, bg="white", fg="black", highlightbackground=bg_color)
bio_time_entry.insert(0, "0")
bio_time_entry.grid(row=2,column=1)

# History

history_hw_entry = tk.Entry(root, width=25, bg="purple", fg="white", highlightbackground=bg_color)
history_hw_entry.insert(0, "History Homework")
history_hw_entry.grid(row=3,column=0)

history_time_entry = tk.Entry(root, width=2, bg="white", fg="black", highlightbackground=bg_color)
history_time_entry.insert(0, "0")
history_time_entry.grid(row=3,column=1)

# English

english_hw_entry = tk.Entry(root, width=25, bg="yellow", fg="black", highlightbackground=bg_color)
english_hw_entry.insert(0, "English Homework")
english_hw_entry.grid(row=4,column=0)

english_time_entry = tk.Entry(root, width=2, bg="white", fg="black", highlightbackground=bg_color)
english_time_entry.insert(0, "0")
english_time_entry.grid(row=4,column=1)

# Electives

electives_hw_entry = tk.Entry(root, width=25, bg="orange", fg="black", highlightbackground=bg_color)
electives_hw_entry.insert(0, "Electives Homework")
electives_hw_entry.grid(row=5,column=0)

electives_time_entry = tk.Entry(root, width=2, bg="white", fg="black", highlightbackground=bg_color)
electives_time_entry.insert(0, "0")
electives_time_entry.grid(row=5,column=1)

# Assessments

assessments_entry = tk.Entry(root, width=25, highlightbackground=bg_color)
assessments_entry.insert(0, "Assessments")
assessments_entry.grid(row=6,column=0)

# Extra notes

extra_notes_entry = tk.Entry(root, width=25, highlightbackground=bg_color)
extra_notes_entry.insert(0, "Extra notes")
extra_notes_entry.grid(row=7,column=0)

# Recipients

gmail_to_entry = tk.Entry(root, width=25, bg="white", fg="black", highlightbackground=bg_color)
gmail_to_entry.insert(0, recipient_email)
gmail_to_entry.grid(row=8,column=0)

# Start time

h = military_to_regular(int(now.strftime("%H")))
m = now.strftime("%M")

time_start_entry = tk.Entry(root, width=4, bg="green", fg="blue", highlightbackground=bg_color)
time_start_entry.insert(0, f"{h}:{m}")
time_start_entry.grid(row=9,column=0)

# Buttons

send_button = tk.Button(root, text="Send", command=lambda: send_email(f"Homework {formatted_date}", generate_msg(math_hw_entry.get(), math_time_entry.get(), bio_hw_entry.get(), bio_time_entry.get(), history_hw_entry.get(), history_time_entry.get(), english_hw_entry.get(), english_time_entry.get(), electives_hw_entry.get(), electives_time_entry.get(), assessments_entry.get(), extra_notes_entry.get(), name_entry.get(), gmail_to_entry.get(), time_start_entry.get()), myPass, gmail_to_entry.get()), highlightbackground=bg_color)
send_button.grid(row=10)

# Body text sent to terminal - used for decoding bugs or if you want to see what the msg would look like
#test_button = tk.Button(root, text="Test", command=lambda: print(generate_msg(math_hw_entry.get(), math_time_entry.get(), bio_hw_entry.get(), bio_time_entry.get(), history_hw_entry.get(), history_time_entry.get(), english_hw_entry.get(), english_time_entry.get(), electives_hw_entry.get(), electives_time_entry.get(), assessments_entry.get(), extra_notes_entry.get(), name_entry.get(), gmail_to_entry.get(), time_start_entry.get())), highlightbackground=bg_color)
#test_button.grid(row=11)

quit_button = tk.Button(root, text="Quit", command=quit_all, highlightbackground=bg_color)
quit_button.grid(row=12)


# Run Main Loop
root.mainloop()