import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import face_recognition
import os
import uuid
import time
import requests
import re  # Import regular expression module

# Path to the directory where face images are stored
faces_dir = "photos"

# Load known faces and their names
known_face_encodings = []
known_face_names = []

# Load existing face data
for file_name in os.listdir(faces_dir):
    name = os.path.splitext(file_name)[0]
    image = face_recognition.load_image_file(os.path.join(faces_dir, file_name))
    encoding = face_recognition.face_encodings(image)
    if encoding:
        known_face_encodings.append(encoding[0])
        known_face_names.append(name)

# URL to send the POST request for updating face information
update_face_post_url = "https://myc-sistech.com/sistem-absensi-uph/api/students.php"

# Initialize the video capture object for the default camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Function to register a face
def register_face(student_id):
    _, frame = cap.read()
    # Generate a unique code for the photo name
    unique_code = str(uuid.uuid4())[:8]  # Get the first 8 characters of a UUID
    current_time = int(time.time())  # Get the current timestamp
    photo_name = f"{student_id}_{unique_code}_{current_time}.jpg"
    file_path = os.path.join(faces_dir, photo_name)

    # Save the captured frame as an image
    cv2.imwrite(file_path, frame)

    # Send request to update face information
    response = send_post_update_face_request(student_id, f"{student_id}_{unique_code}_{current_time}")

    if response is None:
        print(response)
        print("Error: No response from server." )
        messagebox.showerror("Error", "No response from server.")
        # Remove the file if there's no response
        os.remove(file_path)
        return None

    if "error" in response:
        print("Error:", response["error"])
        messagebox.showerror("Error", response["error"])
        # Remove the file if an error occurred
        os.remove(file_path)
        return None

    # Load the image for face recognition
    image = face_recognition.load_image_file(file_path)
    encoding = face_recognition.face_encodings(image)

    if encoding:
        known_face_encodings.append(encoding[0])
        known_face_names.append(photo_name)  # Use the unique photo name as the identifier

        print("Face registered successfully!")
        messagebox.showinfo("Success", "Face registered successfully!")
        return file_path
    else:
        print("No face detected. Please try again.")
        messagebox.showerror("Error", "No face detected. Please try again.")
        # Remove the file if no face is detected
        os.remove(file_path)
        return None


def send_post_update_face_request(student_id, face_id):
    # Prepare the POST parameters
    data = {
        'updateFace': True,
        'studentId': student_id,
        'faceId': face_id
    }

    try:
        # Send the POST request
        response = requests.post("https://myc-sistech.com/sistem-absensi-uph/api/students.php", data=data)

        # Check if the response is successful
        if response.status_code == 200:
            return response.json()  # Return the response data as a dictionary
        else:
            print("Error: Unexpected response from server.")
            print("Response:", response.text)
            return None  # Return None if there's an error
    except Exception as e:
        print("Error:", e)
        return None  # Return None if an exception occurs

# Function to prompt for student ID
def prompt_for_student_id():
    student_id = simpledialog.askstring("Student ID", "Enter Student ID:")
    if student_id:
        # Validate student ID
        if not re.match("^\d{11,}$", student_id):
            messagebox.showerror("Error", "Student ID must consist of 11 or more digits.")
        else:
            file_path = register_face(student_id)
            if file_path:
                print("Displaying captured face:", file_path)
                display_captured_face(file_path)

# Function to display the captured face on the label widget
def display_captured_face(file_path):
    # Load the captured face image
    image = Image.open(file_path)
    image.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(image)

    # Display the image on the label widget
    captured_face_label.config(image=photo)
    captured_face_label.image = photo  # Keep a reference to prevent the image from being garbage collected

# Function to update the video stream with face detection
def update_video_stream():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(frame)
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Convert the frame to a PIL image
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update the canvas with the new image
        canvas.imgtk = imgtk
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    # Repeat the update after 10 ms
    canvas.after(10, update_video_stream)

# Create a GUI window
root = tk.Tk()
root.title("Registration System")

# Create a button to start the camera for registration
registration_button = tk.Button(root, text="Start Registration", command=prompt_for_student_id)
registration_button.pack()

# Create a canvas to display the video stream
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Create a label to display the captured face
captured_face_label = tk.Label(root)
captured_face_label.pack()

# Start updating the video stream
update_video_stream()

# Start the GUI event loop
root.mainloop()
