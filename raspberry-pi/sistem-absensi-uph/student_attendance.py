import nfc
import requests
from nfc.clf import RemoteTarget
import tkinter as tk
import subprocess
from tkinter import Canvas, Button, messagebox, PhotoImage
from pathlib import Path

# Import libraries for face recognition
import cv2
import numpy as np
import face_recognition
import os
import requests
import json
import logging

# Path to the assets directory
ASSETS_PATH = "/home/raspberry/Documents/sistem-absensi-uph/asset"


stop_camera = False


def relative_to_assets(path: str) -> Path:
	return ASSETS_PATH / Path(path)

def face_attendance():
	# Configure logging
	logging.basicConfig(filename='attendance_system.log', level=logging.INFO)

	# Path to the directory where face images are stored
	faces_dir = "/home/raspberry/Documents/sistem-absensi-uph/photos"

	# Load known faces and their names
	known_face_encodings = []
	known_face_names = []

	# Load existing face data
	for file_name in os.listdir(faces_dir):
    	name = os.path.splitext(file_name)[0]
    	image = face_recognition.load_image_file(os.path.join(faces_dir, file_name))
    	encodings = face_recognition.face_encodings(image)
    	if encodings:
        	known_face_encodings.extend(encodings)
        	known_face_names.extend([name] * len(encodings))

	# URL to send the POST request for matching
	match_post_url = "https://myc-sistech.com/sistem-absensi-uph-web-and-api/api/attendance/face.php"

	# Initialize the video capture object for the default camera
	cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    


	# Function to send a POST request with the face ID (picture name)
	def send_post_request(face_id):
    	global stop_camera  # Access the global stop_camera flag

    	# Prepare the POST parameters
    	data = {
        	'attendance': True,
        	'faceId': face_id
    	}
   	 
    	try:
        	# Mengirimkan permintaan POST
        	response = requests.post(match_post_url, data=data)
       	 
        	response_data = response.json()
        	message = response_data.get('message')
        	stop_camera = True
       	 
        	# Memeriksa kode status respons
        	if response.status_code == 200:
            	# Menampilkan pesan sukses menggunakan messagebox
            	messagebox.showinfo("Success", message)
        	elif response.status_code == 500:
            	# Menampilkan pesan error menggunakan messagebox
            	messagebox.showerror("Error", message)
        	else:
            	print("Error: Unexpected response from server.")
            	# Menampilkan pesan error menggunakan messagebox
            	messagebox.showerror("Error", "Unexpected response from server.")
           	 
        	# Mengambil pesan dari respons API
      	 
           	 
    	except Exception as e:
        	print("Error:", e)
        	messagebox.showerror("Error", str(e))

	# Function to start the camera view for attendance
	def start_attendance_camera():
    	global stop_camera  # Access the global stop_camera flag

    	tolerance = 0.6  # Lower the tolerance for stricter matching
    	confidence_threshold = 0.4  # Set a confidence threshold for matching
   	 
    	# Set the desired width and height for the window
    	width = 450
    	height = 320
    	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

   	 
    	while True:
        	ret, frame = cap.read()
        	if not ret:
            	continue
       	 
        	# Convert the frame from BGR to RGB
        	rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       	 
        	# Find all face locations and encodings in the current frame
        	face_locations = face_recognition.face_locations(rgb_frame)
        	face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        	for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            	# Compare the detected face with known faces using the adjusted tolerance
            	matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance)
            	face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
           	 
            	# Find the best match index and distance
            	best_match_index = np.argmin(face_distances)
            	best_match_distance = face_distances[best_match_index]

            	# Initialize name as "Unknown" by default
            	name = "Unknown"
           	 
            	# If a match is found and the best match distance is within the confidence threshold
            	if matches[best_match_index] and best_match_distance <= confidence_threshold:
                	name = known_face_names[best_match_index]
               	 
                	# Draw a box around the detected face
                	cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                	cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
               	 
                	# If a match is found and within threshold, send POST request after 3 seconds
                	cv2.waitKey(2000)
                	send_post_request(name)
               	 
                	if stop_camera:
                    	cap.release()
                    	cv2.destroyAllWindows()
                    	return
            	else:
                	# Draw a box around the detected face with label as "Unknown"
                	cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                	cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                	stop_camera = True
                	if stop_camera:
                    	messagebox.showinfo("Error", "Wajah mahasiswa tidak teridentifikasi!")

                    	cap.release()
                    	cv2.destroyAllWindows()
                    	return

            	# Draw a box around the faceq
            	cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
           	 
            	# Display the name of the detected face at the top of the box
            	cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        	# Display the frame
        	cv2.imshow("Attendance Camera", frame)
       	 
        	key = cv2.waitKey(1)
        	if key == ord("q"):
            	break

    	cap.release()
    	cv2.destroyAllWindows()
    
	start_attendance_camera()

def card_attendance():
	try:
    	clf = nfc.ContactlessFrontend()
    	assert clf.open('usb') is True
   	 
    	beforeTarget = "a"

    	while True:
        	try:
            	target = clf.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))
           	 
            	if target is not None:
                	target = str(target)
                	if target != beforeTarget:
                    	ssd_res = target.split()[1]
                    	index_of_equal_sign = ssd_res.index("=")
                   	 
                    	card_id = ssd_res[index_of_equal_sign + 1:]
                    	print(card_id)
                   	 
                    	# Call API to mark attendance
                    	mark_attendance_response = requests.post("https://myc-sistech.com/sistem-absensi-uph-web-and-api/api/attendance/card.php", data=
                        	{
                            	"attendance": True,
                            	"cardId": card_id
                        	})
                   	 
                    	response_data = mark_attendance_response.json()
                    	print(response_data)
                   	 
                    	if "error" in response_data:
                        	# Display error message box with the error message from API
                        	messagebox.showerror("Error", response_data["error"])
                    	else:
                        	# Display success message box
                        	messagebox.showinfo("Success", response_data["message"])

                    	beforeTarget = target
                   	 
                    	# Setelah menutup kotak pesan, biarkan pengguna memilih tombol berikutnya
                    	break

        	except Exception as e:
            	print("An error occurred:", e)
            	# Display failed attendance popup message
            	messagebox.showerror("Error", "Gagal melakukan absensi")

    	clf.close()
   	 
	except Exception as e:
    	print("An error occurred:", e)
    	# Display failed attendance popup message
    	messagebox.showerror("Error", "Gagal melakukan absensi")

def admin_login():
	subprocess.Popen(["python3", "/home/raspberry/Documents/sistem-absensi-uph/admin_login.py"])
	window.destroy()

def admin_login_enter(event=None):
	button_4.config(bg="#00264D")

def admin_login_leave(event=None):
	button_4.config(bg="#001B37")

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
	100.0,
	anchor="center",
	text="ABSENSI",
	fill="#FFFFFF",
	font=("NunitoSans Bold", 24)
)

canvas.create_text(
	240.0,
	30.0,
	anchor="center",
	text="Selamat datang di sistem",
	fill="#FFFFFF",
	font=("NunitoSans Bold", 14)
)

# Load the logo image
image = tk.PhotoImage(file=relative_to_assets("logo.png"))
# Resize the logo image
image = image.subsample(3)

# Display the logo image on the canvas
image_1 = canvas.create_image(
	240.0,
	160.0,
	image=image
)

# Place the canvas on the main window
canvas.place(x=0, y=0)

# Create and place button 1
face_image = PhotoImage(file=relative_to_assets("button1.png")).subsample(3)
face_button = Button(
	image=face_image,
	borderwidth=0,
	highlightthickness=0,
	command=face_attendance,
	relief="flat",
	bg="#001B37",
	highlightbackground="#001B37",
	highlightcolor="#001B37"
)
face_button.place(
	x=50.0,
	y=200.0,
	width=100.0,
	height=70.0
)

# Create and place button 2
fingerprint_image = PhotoImage(file=relative_to_assets("button2.png")).subsample(3)
fingerprint_button = Button(
	image=fingerprint_image,
	borderwidth=0,
	highlightthickness=0,
	command=lambda: print("fingerprint_button clicked"),
	relief="flat",
	bg="#001B37",
	highlightbackground="#001B37",
	highlightcolor="#001B37"
)
fingerprint_button.place(
	x=190.0,
	y=200.0,
	width=100.0,
	height=70.0
)

# Create and place button 3
card_image = PhotoImage(file=relative_to_assets("button3.png")).subsample(3)
card_button = Button(
	image=card_image,
	borderwidth=0,
	highlightthickness=0,
	command=card_attendance,
	relief="flat",
	bg="#001B37",
	highlightbackground="#001B37",
	highlightcolor="#001B37"
)
card_button.place(
	x=330.0,
	y=200.0,
	width=100.0,
	height=70.0
)

# Create and place button 4
button_image_4 = PhotoImage(file=relative_to_assets("button4.png")).subsample(3)
button_4 = Button(
	image=button_image_4,
	borderwidth=0,
	highlightthickness=0,
	command=admin_login,
	relief="flat",
	bg="#001B37",
)
button_4.bind("<Enter>", admin_login_enter)
button_4.bind("<Leave>", admin_login_leave)
button_4.place(
	x=430.0,
	y=10.0,
	width=40.0,
	height=40.0
)

# Disable window resizing
window.resizable(False, False)

# Start the main event loop
window.mainloop()
