import requests
import tkinter as tk
import subprocess
from tkinter import Canvas, Button, Entry, messagebox, PhotoImage

# Path to the assets directory
ASSETS_PATH = "/home/raspberry/Documents/sistem-absensi-uph/asset"

# Path to the login status file
LOGIN_STATUS_FILE = "/home/raspberry/Documents/sistem-absensi-uph/login_status.txt"

def relative_to_assets(path: str) -> str:
	return f"{ASSETS_PATH}/{path}"

def student_attendance_click():
	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/student_attendance.py"])
	window.destroy()

def student_attendance_enter(event=None):
	logout_button.config(bg="#00264D")

def student_attendance_leave(event=None):
	logout_button.config(bg="#001B37")

def save_login_status(status):
	with open(LOGIN_STATUS_FILE, 'w') as file:
    	file.write(status)

def get_login_status():
	try:
    	with open(LOGIN_STATUS_FILE, 'r') as file:
        	status = file.read().strip()
        	return status == "True"
	except FileNotFoundError:
    	return False

def login():
	email = entry_email.get()
	password = entry_password.get()
    
	# Call the login API
	response = requests.post("https://myc-sistech.com/sistem-absensi-uph-web-and-api/api/authentication.php", data={"email": email, "password": password, "login": True})
    
	# Check the API response
	if response.status_code == 200:
    	data = response.json()
    	if "success" in data:
        	# Login successful, show success message
        	messagebox.showinfo("Success", data["success"])
        	save_login_status("True")
        	# Pindah ke halaman student_data_register.py dan tutup jendela sebelumnya
        	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/student_data_register.py"])
        	window.destroy()
    	elif "error" in data:
        	# Login failed, show error message
        	messagebox.showerror("Error", data["error"])
	else:
    	# API request failed, show error message
    	messagebox.showerror("Error", "Failed to connect to the server")

# Create the main window
window = tk.Tk()
window.geometry("480x320")  # Set the window size to fit a 9-inch screen
window.configure(bg="#001B37")
window.title("Sistem Absensi UPH")

# Create a canvas to display text and images
canvas = Canvas(
	window,
	bg="#001B37",
	height=320,
	width=480,
	bd=0,
	highlightthickness=0,
	relief="ridge"
)
canvas.place(x=0, y=0)

# Create text elements
canvas.create_text(
	240.0,
	70.0,
	anchor="center",
	text="ABSENSI",
	fill="#FFFFFF",
	font=("NunitoSans Bold", 20)
)

canvas.create_text(
	240.0,
	30.0,
	anchor="center",
	text="Selamat datang di sistem",
	fill="#FFFFFF",
	font=("NunitoSans Bold", 12)
)

# Create entry fields for email and password
entry_email = Entry(
	window,
	bd=0,
	bg="#FFFFFF",
	fg="#000716",
	font=("NunitoSans Regular", 10),
	highlightthickness=0
)
canvas.create_window(
	240.0,
	150.0,
	window=entry_email,
	width=200,
	height=20
)

entry_password = Entry(
	window,
	bd=0,
	bg="#FFFFFF",
	fg="#000716",
	font=("NunitoSans Regular", 10),
	highlightthickness=0
)
canvas.create_window(
	240.0,
	200.0,
	window=entry_password,
	width=200,
	height=20
)

canvas.create_text(
	110.0,
	120.0,
	anchor="nw",
	text="Email : ",
	fill="#FFFFFF",
	font=("NunitoSans Regular", 10)
)

canvas.create_text(
	110.0,
	170.0,
	anchor="nw",
	text="Password : ",
	fill="#FFFFFF",
	font=("NunitoSans Regular", 10)
)

# Create and place logout button
logout_image = PhotoImage(file=relative_to_assets("button5.png")).subsample(2)
logout_button = Button(
	image=logout_image,
	borderwidth=0,
	highlightthickness=0,
	command=student_attendance_click,
	relief="flat",
	bg="#001B37",
)
logout_button.bind("<Enter>", student_attendance_enter)  # Add event binding for mouse hover
logout_button.bind("<Leave>", student_attendance_leave)  # Add event binding for mouse leave
logout_button.place(
	x=420.0,
	y=10.0,
	width=40.0,  # Adjust button width
	height=40.0  # Adjust button height
)

# Create and place button for login
button_login = Button(
	window,
	text="Login",
	bg="white",
	fg="#001B37",
	font=("NunitoSans Regular", 10),
	command=login,
	relief="flat"
)
button_login.place(
	x=190.0,
	y=240.0,
	width=100.0,  # Width button
	height=30.0  # Height button
)

# Check login status and take action accordingly
if get_login_status():
	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/student_data_register.py"])
	window.destroy()

# Disable window resizing
window.resizable(False, False)

# Start the main event loop
window.mainloop()
