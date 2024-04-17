import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import face_recognition
import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(filename='attendance_system.log', level=logging.INFO)

# Path to the directory where face images are stored
faces_dir = "photos"

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
match_post_url = "https://myc-sistech.com/sistem-absensi-uph/api/attendance/face.php"

# Initialize the video capture object for the default camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Function to send a POST request with the face ID (picture name)
def send_post_request(face_id):
    # Prepare the POST parameters
    data = {
        'attendance': True,
        'faceId': face_id
    }
    
    try:
        # Send the POST request
        response = requests.post(match_post_url, data=data)
        
        # Check the response status code
        if response.status_code == 200:
            print("Attendance updated successfully.")
        elif response.status_code == 500:
            print("Error: Unknown error occurred.")
        else:
            print("Error: Unexpected response from server.")
        
        # Extract message from API response
        response_data = response.json()
        message = response_data.get('message')
        if message:
            print("API Message:", message)
        
    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", str(e))

# Function to start the camera view for attendance
def start_attendance_camera():
    tolerance = 0.6  # Lower the tolerance for stricter matching
    confidence_threshold = 0.4  # Set a confidence threshold for matching
    
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
                print(name)
                
                # Send a POST request when a face match is found
                send_post_request(name)
            else:
                # Log unknown face detected with the best match distance
                logging.warning(f"Unknown face detected. Best match distance: {best_match_distance:.2f}")

            # Draw a box around the face
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

# Create a GUI window
root = tk.Tk()
root.title("Attendance System")

# Create a button to start the camera for attendance
attendance_button = tk.Button(root, text="Start Attendance", command=start_attendance_camera)
attendance_button.pack()

# Start the GUI event loop
root.mainloop()
