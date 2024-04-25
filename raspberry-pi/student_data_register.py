import subprocess
import tkinter as tk
import requests
from tkinter import Canvas, Button, messagebox, PhotoImage, ttk
from pathlib import Path
import json
import nfc
from nfc.clf import RemoteTarget
import atexit  # Import the atexit module

# import libraries for face recognition
from PIL import Image, ImageTk

# Path to the assets directory
ASSETS_PATH = "/home/raspberry/Documents/sistem-absensi-uph/asset"
listBoxSelectId = None

# Path to the login status file
LOGIN_STATUS_FILE = "/home/raspberry/Documents/sistem-absensi-uph/login_status.txt"

def relative_to_assets(path: str) -> Path:
	return ASSETS_PATH / Path(path)


def face_register():
	global listBoxSelectId

	# Check if a student is selected
	if listBoxSelectId is None:
    	messagebox.showerror("Error", "Silahkan select mahasiswa yang ingin didaftarkan!")
    	return

	# Open the student face registration script with the selected student ID as argument
	script_path = '/home/raspberry/Documents/sistem-absensi-uph/student_face_register.py'
	try:
    	subprocess.Popen(["python3", script_path, str(listBoxSelectId)])
	except Exception as e:
    	print("An error occurred:", e)



def card_register():
	global listBoxSelectId

	try:
    	clf = nfc.ContactlessFrontend()

    	assert clf.open('usb') is True

    	try:
        	target = clf.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))

        	if target is not None:
            	target = str(target)
            	ssd_res = target.split()[1]
            	index_of_equal_sign = ssd_res.index("=")

            	card_id = ssd_res[index_of_equal_sign + 1:]

            	if listBoxSelectId is not None:
                	student_id = listBoxSelectId
            	else:
                	messagebox.showerror("Error", "Silahkan select mahasiswa yang ingin didaftarkan!")
                	return

            	# Call API to register card
            	update_card = requests.post("https://myc-sistech.com/sistem-absensi-uph-web-and-api/api/students.php",
                                        	data={
                                            	"updateCard": True,
                                            	"studentId": student_id,
                                            	"cardId": ssd_res[index_of_equal_sign + 1:]
                                        	})

            	response_data = update_card.json()

            	if "error" in response_data:
                	# Display error message box with the error message from API
                	messagebox.showerror("Error", response_data["error"])
            	else:
                	# Display success message box
                	messagebox.showinfo("Success", response_data["success"])

            	# Update table
            	show()

            	listBoxSelectId = None
        	else:
            	messagebox.showerror("Error", "Kartu tidak teridentifikasi, silahkan tap kartu mahasiswa!")
            	listBoxSelectId = None

    	except Exception as e:
        	print("An error occurred:", e)

    	clf.close()

	except Exception as e:
    	print("An error occurred:", e)


def logout():
	update_login_status(False)  # Set login status to False
	if window:  # Check if window exists before trying to modify it
    	window.resizable(False, False)  # Set resizable property before destroying the window
	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/admin_login.py"])
	if window:  # Check if window exists before trying to destroy it
    	window.destroy()



def logout_enter(event=None):
	logout_button.config(bg="#00264D")


def logout_leave(event=None):
	logout_button.config(bg="#001B37")


def fetchData():
	try:
    	url = "https://myc-sistech.com/sistem-absensi-uph-web-and-api/api/fetchData.php"
    	payload = {'action': 'fetchData'}
    	response = requests.post(url, data=payload)
    	if response.status_code == 200:
        	data = json.loads(response.text)
        	return data
    	else:
        	return None
	except Exception as e:
    	messagebox.showerror("Error", f"Failed to fetch data: {e}")
    	return None


def show():
	try:
    	records = fetchData()
    	if records is None:
        	return

    	for row in listBox.get_children():
        	listBox.delete(row)

    	for record in records:
        	listBox.insert("", "end",
                       	values=(record['Name'], record['StudentId'], record['YearIn'], record['Face'],
                               	record['Fingerprint'], record['Card']))
	except Exception as e:
    	messagebox.showerror("Error", f"Error: {e}")


def on_select(event):
	global listBoxSelectId

	# Get the selected item, if any
	selected_items = listBox.selection()
	if selected_items:
    	item = selected_items[0]  # Get the first selected item
    	selected_item = listBox.item(item)['values']  # Get the values of the selected item
    	listBoxSelectId = "0" + str(selected_item[1])
    	messagebox.showinfo("Success", "Berhasil memilih mahasiswa " + selected_item[0])

	else:
    	# No item selected, reset listBoxSelectId to None or handle it accordingly
    	listBoxSelectId = None


#def run_register_student():
	#global listBoxSelectId

	#try:
    	# Your existing card registration logic here
   	 
    	# After successful registration, launch student_face_register.py
    	#subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/student_face_register.py", str(listBoxSelectId)])
   	 
    	# Reset listBoxSelectId
    	#listBoxSelectId = None

	#except Exception as e:
    	#print("An error occurred:", e)



def get_login_status():
	try:
    	with open(LOGIN_STATUS_FILE, 'r') as file:
        	status = file.read().strip()
        	return status == "True"
	except FileNotFoundError:
    	return False

def update_login_status(status):
	with open(LOGIN_STATUS_FILE, 'w') as file:
    	file.write(str(status))

# Create the main window
window = tk.Tk()
window.geometry("480x320")  # Set the window size to 480x320
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
	20.0,
	anchor="center",
	text="Silahkan melakukan register",
	fill="#FFFFFF",
	font=("NunitoSans Bold", 14)
)

# Create and place buttons
face_image = PhotoImage(file=relative_to_assets("button1.png")).subsample(2)
face_button = Button(
	image=face_image,
	borderwidth=0,
	highlightthickness=0,
	command=face_register,
	relief="flat",
	bg="#001B37",
)
face_button.place(x=40, y=50)

fingerprint_image = PhotoImage(file=relative_to_assets("button2.png")).subsample(2)
fingerprint_button = Button(
	image=fingerprint_image,
	borderwidth=0,
	highlightthickness=0,
	command=lambda: print("fingerprint_button clicked"),
	relief="flat",
	bg="#001B37",
)
fingerprint_button.place(x=185, y=50)

card_image = PhotoImage(file=relative_to_assets("button3.png")).subsample(2)
card_button = Button(
	image=card_image,
	borderwidth=0,
	highlightthickness=0,
	command=card_register,
	relief="flat",
	bg="#001B37",
)
card_button.place(x=330, y=50)

logout_image = PhotoImage(file=relative_to_assets("button5.png")).subsample(2)
logout_button = Button(
	image=logout_image,
	borderwidth=0,
	highlightthickness=0,
	command=logout,  # Run admin login first
	relief="flat",
	bg="#001B37",
)
logout_button.bind("<Enter>", logout_enter)
logout_button.bind("<Leave>", logout_leave)
logout_button.place(x=420, y=10)

# Create and place table
cols = ('Name', 'StudentId', 'YearIn', 'Face', 'Fingerprint', 'Card')
listBox = ttk.Treeview(window, columns=cols, show='headings')

for col in cols:
	listBox.heading(col, text=col, anchor=tk.CENTER)
	listBox.column(col, width=80)
	listBox.place(x=10, y=150, width=460, height=100)

# Bind the Button-1 event to handle row selection
listBox.bind("<Button-1>", on_select)

# Create button to update table
update_button = Button(
	window,
	text="Reload",
	command=show,
	relief="flat",
	bg="#001B37",
	fg="#FFFFFF",
)
update_button.place(x=380, y=255, width=80.0, height=20.0)

# Check login status and take action accordingly
if not get_login_status():
	messagebox.showerror("Error", "Anda belum login. Silakan login terlebih dahulu.")
	update_login_status(False)
	window.destroy()
	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/admin_login.py"])
else:
	window.resizable(False, False)

	# Update and start the main event loop
	show()
	window.mainloop()

# Function to update login status to False when program stops
def on_program_exit():
	update_login_status(False)

# Register the function to be called when the program exits
atexit.register(on_program_exit)
