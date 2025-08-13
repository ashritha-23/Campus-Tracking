import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import matplotlib.pyplot as plt
import cv2
from pathlib import Path
import json

# --- Dataset creation logic (added here) ---
def create_npz_dataset(data_dir='face_data', img_size=(92, 112), names_path='person_names.json'):
    print("Creating dataset from collected face images...")
    data_dir = Path(data_dir)
    images, labels = [], []
    label_map = {}  # Maps person ID to label index
    current_label = 0

    if not data_dir.exists():
        print(f"No face data directory found at '{data_dir}'. Please collect face images first.")
        return False

    # Load existing person names
    person_names = {}
    if os.path.exists(names_path):
        try:
            with open(names_path, 'r') as f:
                person_names = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {names_path} is not valid JSON. Starting with empty dictionary.")

    for person_dir in sorted(data_dir.glob("person*")):
        if not person_dir.is_dir():
            continue
            
        try:
            # Extract numeric person ID from directory name
            person_id = int(person_dir.name.replace("person", ""))
            
            # Create sequential label index for this person
            if person_id not in label_map:
                label_map[person_id] = current_label
                current_label += 1
            
            label = label_map[person_id]
            
            # Process all face images for this person
            for img_path in person_dir.glob("face*.jpg"):
                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, img_size)
                    images.append(img)
                    labels.append(label)
        except Exception as e:
            print(f"Error processing {person_dir}: {e}")

    if not images:
        print("No images found. Please collect face data first.")
        return False

    X, y = np.array(images), np.array(labels)
    indices = np.random.permutation(len(X))
    split_idx = int(len(X) * 0.8)

    trainX, trainY = X[indices[:split_idx]], y[indices[:split_idx]]
    testX, testY = X[indices[split_idx:]], y[indices[split_idx:]]

    np.savez('face_dataset.npz', 
             trainX=trainX, trainY=trainY, 
             testX=testX, testY=testY,
             label_map=np.array(list(label_map.items())))

    # Create a mapping from label indices to names for recognition
    id_to_name = {}
    for person_id, label_idx in label_map.items():
        person_name = person_names.get(str(person_id), f"Person {person_id}")
        id_to_name[str(label_idx)] = person_name
    
    print(f"Label map: {label_map}")
    print(f"ID to name map: {id_to_name}")
    
    # Save the label-to-name mapping for the recognition phase
    with open(names_path, 'w') as f:
        json.dump(id_to_name, f)

    print(f"Dataset created successfully!")
    print(f"Training samples: {len(trainX)}")
    print(f"Testing samples: {len(testX)}")
    print(f"Classes: {len(label_map)}")
    return True


# --- Your existing model and training code below ---

def create_model(num_classes, input_shape=(112, 92, 1)):
    tf.keras.mixed_precision.set_global_policy('mixed_float16')

    model = Sequential([
        Conv2D(32, 3, activation='relu', input_shape=input_shape, padding='same'),
        Conv2D(32, 3, activation='relu', padding='same'),
        MaxPooling2D(2),

        Conv2D(64, 3, activation='relu', padding='same'),
        Conv2D(64, 3, activation='relu', padding='same'),
        MaxPooling2D(2),

        Conv2D(128, 3, activation='relu', padding='same'),
        Conv2D(128, 3, activation='relu', padding='same'),
        MaxPooling2D(2),

        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=Adam(0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def train_model(model_path='face_recognition_model.h5', dataset_path='face_dataset.npz', epochs=50, batch_size=32):
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Attempting to create dataset automatically...")
        created = create_npz_dataset()
        if not created:
            print("Dataset creation failed. Cannot proceed with training.")
            return None, 0

    print(f"Loading dataset from {dataset_path}...")
    data = np.load(dataset_path)
    x_train, y_train = data['trainX'], data['trainY']
    x_test, y_test = data['testX'], data['testY']

    unique_classes = np.unique(y_train)
    if len(unique_classes) < 2:
        print(f"Not enough classes for training. Found only {len(unique_classes)} class(es). Need at least 2.")
        return None, 0

    x_train, x_test = x_train / 255.0, x_test / 255.0
    x_train = x_train.reshape(-1, 112, 92, 1)
    x_test = x_test.reshape(-1, 112, 92, 1)

    print(f"Training data shape: {x_train.shape} with {len(unique_classes)} classes")
    model = create_model(len(unique_classes))

    model.summary()

    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-6)
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    print(f"Starting training for {epochs} epochs...")
    try:
        history = model.fit(
            x_train, y_train,
            validation_split=0.2,
            batch_size=batch_size,
            epochs=epochs,
            callbacks=[reduce_lr, early_stop],
            verbose=1
        )

        model.save(model_path)
        print(f"Model saved to {model_path}")

        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        axs[0].plot(history.history['accuracy'], label='Train')
        axs[0].plot(history.history['val_accuracy'], label='Val')
        axs[0].set_title("Accuracy")
        axs[0].legend()

        axs[1].plot(history.history['loss'], label='Train')
        axs[1].plot(history.history['val_loss'], label='Val')
        axs[1].set_title("Loss")
        axs[1].legend()

        final_val_acc = history.history['val_accuracy'][-1]
        plt.tight_layout()
        plt.savefig('training_history.png')
        print(f"Training complete! Final validation accuracy: {final_val_acc:.4f}")
        print(f"Training history plot saved to training_history.png")

        test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
        print(f"Test accuracy: {test_acc:.4f}")

        return model, final_val_acc

    except Exception as e:
        print(f"Error during training: {str(e)}")
        return None, 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Face Recognition Model Training')
    parser.add_argument('--model', dest='model_path', default='face_recognition_model.h5',
                        help='Path to save model (default: face_recognition_model.h5)')
    parser.add_argument('--dataset', dest='dataset_path', default='face_dataset.npz',
                        help='Path to dataset (default: face_dataset.npz)')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training (default: 32)')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode with prompts')

    args = parser.parse_args()

    print("\n===== Face Recognition Model Training =====")
    print("This script will train a CNN model using the prepared face dataset.")

    if args.interactive:
        model_path = input("Enter model save path (default: face_recognition_model.h5): ") or "face_recognition_model.h5"
        dataset_path = input("Enter dataset path (default: face_dataset.npz): ") or "face_dataset.npz"
        epochs = int(input("Number of epochs (default: 50): ") or "50")
        batch_size = int(input("Batch size (default: 32): ") or "32")
    else:
        model_path = args.model_path
        dataset_path = args.dataset_path
        epochs = args.epochs
        batch_size = args.batch_size

    print(f"Training with the following parameters:")
    print(f"- Model path: {model_path}")
    print(f"- Dataset path: {dataset_path}")
    print(f"- Epochs: {epochs}")
    print(f"- Batch size: {batch_size}")

    train_model(model_path, dataset_path, epochs, batch_size)


if __name__ == "__main__":
    main()
