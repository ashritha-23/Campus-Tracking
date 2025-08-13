import cv2
import numpy as np
import os
from pathlib import Path
import json

class FaceDataCollector:
    def __init__(self, data_dir='face_data', img_size=(92, 112), names_path='person_names.json'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.img_size = img_size
        self.names_path = names_path
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.person_names = self.load_person_names()

    def load_person_names(self):
        """Load existing person names if available and valid"""
        if os.path.exists(self.names_path):
            try:
                with open(self.names_path, 'r') as f:
                    data = f.read().strip()
                    if not data:
                        return {}
                    return json.loads(data)
            except json.JSONDecodeError:
                print(f"Warning: {self.names_path} is not a valid JSON. Resetting.")
                return {}
        return {}

    def collect_face_data(self, person_id, person_name, num_images=100):
        """Collect face data from webcam for a person"""
        person_id_str = str(person_id)
        person_dir = self.data_dir / f"person{person_id}"
        person_dir.mkdir(exist_ok=True)

        cap = cv2.VideoCapture(0)
        images_collected = 0
        save_name = False  # Track if we should update person_names.json

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        print(f"Collecting face data for {person_name} (ID: {person_id})")
        print("Press 'c' to capture image. Press 'q' to stop.")

        cv2.namedWindow('Collecting Face Data', cv2.WINDOW_NORMAL)

        while images_collected < num_images:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.putText(frame, f"{person_name}: {images_collected}/{num_images}", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Collecting Face Data', frame)

            key = cv2.waitKey(1)
            if key == ord('c') and len(faces) == 1:
                x, y, w, h = faces[0]
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, self.img_size)
                cv2.imwrite(str(person_dir / f"face{images_collected}.jpg"), face)
                images_collected += 1
                save_name = True
                print(f"Captured image {images_collected}/{num_images}")
            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if save_name:
            self.person_names[person_id_str] = person_name
            with open(self.names_path, 'w') as f:
                json.dump(self.person_names, f)
            print(f"Name saved to {self.names_path}")

        print(f"Data collection complete. Collected {images_collected} images.")

    def create_npz_dataset(self):
        """Create NPZ dataset from collected face images"""
        print("Creating dataset from collected face images...")
        images, labels = [], []
        label_map = {}  # Maps person ID to label index
        current_label = 0

        for person_dir in sorted(self.data_dir.glob("person*")):
            try:
            # Extract the numeric ID from directory name (e.g., "person1" -> 1)
                person_id = int(person_dir.name.replace("person", ""))
            
            # Assign a sequential label index for this person ID
                if person_id not in label_map:
                    label_map[person_id] = current_label
                    current_label += 1

                label = label_map[person_id]
            
                for img_path in person_dir.glob("face*.jpg"):
                    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, self.img_size)  # Ensure correct size
                        images.append(img)
                        labels.append(label)
            except Exception as e:
                print(f"Error processing {person_dir}: {e}")

        if not images:
            print("No images found. Please collect face data first.")
            return 0, 0

        X, y = np.array(images), np.array(labels)
        indices = np.random.permutation(len(X))
        split_idx = int(len(X) * 0.8)

        trainX, trainY = X[indices[:split_idx]], y[indices[:split_idx]]
        testX, testY = X[indices[split_idx:]], y[indices[split_idx:]]

        np.savez('face_dataset.npz', 
                trainX=trainX, trainY=trainY, 
                testX=testX, testY=testY,
                label_map=np.array(list(label_map.items())))  # Save the mapping too

    # Create a reverse mapping from label indices to person IDs for recognition
    # This is crucial for correct identification during recognition
        id_to_name = {}
        for person_id, label_idx in label_map.items():
            person_name = self.person_names.get(str(person_id), f"Person {person_id}")
            id_to_name[str(label_idx)] = person_name
    
        print(f"Label map: {label_map}")
        print(f"ID to name map: {id_to_name}")
    
    # Save the label-to-name mapping for the recognition phase
        with open(self.names_path, 'w') as f:
            json.dump(id_to_name, f)

        print(f"Dataset created successfully!")
        print(f"Training samples: {len(trainX)}")
        print(f"Testing samples: {len(testX)}")
        print(f"Classes: {len(label_map)}")

        return len(trainX), len(testX)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Face Data Collection Tool')
    parser.add_argument('--person-id', type=int, help='Person ID for data collection')
    parser.add_argument('--person-name', help='Person name for data collection')
    parser.add_argument('--num-images', type=int, default=100, help='Number of images to collect (default: 100)')
    parser.add_argument('--create-dataset', action='store_true', help='Create dataset from collected images')

    args = parser.parse_args()
    collector = FaceDataCollector()

    if args.create_dataset:
        collector.create_npz_dataset()
        return

    if args.person_id is not None and args.person_name:
        collector.collect_face_data(args.person_id, args.person_name, args.num_images)
        return

    while True:
        print("\n===== Face Data Collection =====")
        print("1. Collect face data")
        print("2. Create dataset")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            person_id = int(input("Enter person ID: "))
            person_name = input("Enter person name: ")
            num_images = int(input("Number of images to collect (default 100): ") or "100")
            collector.collect_face_data(person_id, person_name, num_images)

        elif choice == "2":
            collector.create_npz_dataset()

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
