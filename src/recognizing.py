import cv2
import numpy as np
import os
import json
import datetime
import csv
import time
from tensorflow.keras.models import load_model
from pathlib import Path

def load_person_names(names_path='person_names.json'):
    """Load person names mapping from JSON file"""
    if os.path.exists(names_path):
        with open(names_path, 'r') as f:
            return json.load(f)
    else:
        print(f"Warning: {names_path} not found. Using empty dictionary.")
        return {}

def initialize_csv(csv_path='recognition_log.csv'):
    """Initialize CSV file with headers if it doesn't exist"""
    file_exists = os.path.isfile(csv_path)
    
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'person_id', 'person_name', 'confidence', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            print(f"Created new log file: {csv_path}")
    
    return csv_path

def log_recognition(csv_path, person_id, person_name, confidence, location="Unknown"):
    """Log recognition event to CSV file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'person_id', 'person_name', 'confidence', 'location'])
        writer.writerow({
            'timestamp': timestamp,
            'person_id': person_id,
            'person_name': person_name,
            'confidence': confidence,
            'location': location
        })

def start_recognition(model_path='face_recognition_model.h5', 
                      names_path='person_names.json',
                      csv_path='recognition_log.csv',
                      location="Main Entrance",
                      img_size=(92, 112),
                      confidence_threshold=0.5):
    """Start real-time face recognition with logging to CSV"""
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model file {model_path} not found. Please train the model first.")
        return

    # Initialize log file
    csv_path = initialize_csv(csv_path)
    print(f"Recognition events will be logged to: {csv_path}")
    print(f"Current location set to: {location}")

    # Load model and person names
    try:
        print(f"Loading model from {model_path}...")
        model = load_model(model_path)
        print("Model loaded successfully")
        
        person_names = load_person_names(names_path)
        print(f"Loaded {len(person_names)} person identities: {person_names}")
    except Exception as e:
        print(f"Error loading model or person names: {str(e)}")
        return

    # Initialize face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Set up camera
    print("Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Create window
    cv2.namedWindow('Face Recognition', cv2.WINDOW_NORMAL)
    print("Starting real-time face recognition. Press 'q' to quit.")
    
    # To avoid duplicate logs for the same person
    last_logged = {}  # {person_id: timestamp}
    log_cooldown = 5  # seconds between logs for same person

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame")
            break

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            # Prepare face for prediction
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, img_size).astype('float32') / 255.0
            face_img = face_img.reshape(1, img_size[1], img_size[0], 1)

            # Make prediction
            prediction = model.predict(face_img, verbose=0)[0]
            predicted_idx = np.argmax(prediction)
            confidence = float(prediction[predicted_idx])
            
            # Get person name or mark as unknown
            # The key is the label index as a string, which matches what we stored in names_path
            person_id = str(predicted_idx)
            name = person_names.get(person_id, "Unknown")
            
            # Debug info
            if confidence > 0.3:  # Show debug for significant predictions
                print(f"Prediction: index={predicted_idx}, confidence={confidence:.2f}, name={name}")
                print(f"Available IDs in person_names: {list(person_names.keys())}")

            # Set rectangle color based on confidence
            color = (0, 255, 0) if confidence > confidence_threshold else (0, 165, 255)
            
            # Display results
            label = f"{name} ({confidence:.2f})"
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Log recognition event with cooldown to avoid duplicate entries
            current_time = time.time()
            if confidence > confidence_threshold:
                if person_id not in last_logged or (current_time - last_logged[person_id]) > log_cooldown:
                    log_recognition(csv_path, person_id, name, confidence, location)
                    last_logged[person_id] = current_time
                    print(f"Logged: {name} (ID: {person_id}) at {location} with confidence {confidence:.2f}")

        # Display the resulting frame
        cv2.imshow('Face Recognition', frame)
        
        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Face recognition stopped")

def main():
    print("\n===== Face Recognition System =====")
    
    # Parse command line arguments if provided
    import argparse
    parser = argparse.ArgumentParser(description='Face Recognition System')
    parser.add_argument('--model', dest='model_path', default='face_recognition_model.h5',
                        help='Path to model file (default: face_recognition_model.h5)')
    parser.add_argument('--names', dest='names_path', default='person_names.json',
                        help='Path to names mapping file (default: person_names.json)')
    parser.add_argument('--csv', dest='csv_path', default='recognition_log.csv',
                        help='Path to CSV log file (default: recognition_log.csv)')
    parser.add_argument('--location', dest='location', default='Main Entrance',
                        help='Current location (default: Main Entrance)')
    parser.add_argument('--confidence', dest='confidence', type=float, default=0.5,
                        help='Confidence threshold (0-1, default: 0.5)')
    
    # If no arguments provided or running in interactive mode, use input prompts
    args, unknown = parser.parse_known_args()
    
    if '--interactive' in unknown or len(unknown) > 0 and unknown[0] == '--interactive':
        model_path = input("Enter model path (default: face_recognition_model.h5): ") or "face_recognition_model.h5"
        names_path = input("Enter names mapping path (default: person_names.json): ") or "person_names.json"
        csv_path = input("Enter log file path (default: recognition_log.csv): ") or "recognition_log.csv"
        location = input("Enter current location (default: Main Entrance): ") or "Main Entrance"
        confidence_threshold = float(input("Enter confidence threshold (0-1, default: 0.5): ") or "0.5")
    else:
        model_path = args.model_path
        names_path = args.names_path
        csv_path = args.csv_path
        location = args.location
        confidence_threshold = args.confidence
    
    start_recognition(model_path, names_path, csv_path, location, confidence_threshold=confidence_threshold)

if __name__ == "__main__":
    main()