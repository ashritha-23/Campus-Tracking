import os
import re
import json
from pathlib import Path

def verify_face_dataset():
    """Verify face dataset structure and fix any issues with naming consistency"""
    data_dir = Path('face_data')
    names_path = Path('person_names.json')
    
    if not data_dir.exists():
        print("Face data directory not found.")
        return False
    
    # Check for person directories
    person_dirs = list(data_dir.glob("person*"))
    if not person_dirs:
        print("No person directories found in face_data/")
        return False
    
    # Load person names
    person_names = {}
    if names_path.exists():
        try:
            with open(names_path, 'r') as f:
                person_names = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {names_path} is not valid JSON. Starting with empty dictionary.")
    
    # Count images and verify structure
    print("\n==== Face Dataset Information ====")
    print(f"Found {len(person_dirs)} person directories:")
    
    for person_dir in sorted(person_dirs):
        try:
            # Extract person ID
            match = re.match(r"person(\d+)", person_dir.name)
            if not match:
                print(f"  - Warning: Invalid directory name format: {person_dir.name}")
                continue
                
            person_id = match.group(1)
            face_images = list(person_dir.glob("face*.jpg"))
            
            # Get person name
            person_name = person_names.get(person_id, f"Person {person_id}")
            
            print(f"  - Person {person_id}: {person_name} ({len(face_images)} images)")
        except Exception as e:
            print(f"  - Error processing {person_dir}: {str(e)}")
    
    print("\n==== Names File Information ====")
    print(f"Names file: {names_path}")
    print(f"Total entries: {len(person_names)}")
    for person_id, name in person_names.items():
        print(f"  - ID {person_id}: {name}")
    
    # Check for potential issues
    potential_issues = []
    
    # Check for directories without entries in names file
    for person_dir in person_dirs:
        match = re.match(r"person(\d+)", person_dir.name)
        if match:
            person_id = match.group(1)
            if person_id not in person_names:
                potential_issues.append(f"Directory person{person_id} has no entry in names file")
    
    # Check for names entries without directories
    for person_id in person_names:
        if not (data_dir / f"person{person_id}").exists():
            potential_issues.append(f"Name entry for ID {person_id} has no directory")
    
    if potential_issues:
        print("\n==== Potential Issues ====")
        for issue in potential_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No potential issues found in dataset structure.")
    
    return True

def rebuild_names_file():
    """Rebuild person_names.json based on directories in face_data/"""
    data_dir = Path('face_data')
    names_path = Path('person_names.json')
    
    if not data_dir.exists():
        print("Face data directory not found.")
        return False
    
    # Load existing names if available
    existing_names = {}
    if names_path.exists():
        try:
            with open(names_path, 'r') as f:
                existing_names = json.load(f)
        except:
            print("Warning: Could not read existing names file.")
    
    # Build new person_names dictionary based on directories
    new_names = {}
    for person_dir in sorted(data_dir.glob("person*")):
        match = re.match(r"person(\d+)", person_dir.name)
        if match:
            person_id = match.group(1)
            # Keep existing name if available, otherwise use default
            if person_id in existing_names:
                new_names[person_id] = existing_names[person_id]
            else:
                new_names[person_id] = f"Person {person_id}"
    
    # Save the updated names file
    with open(names_path, 'w') as f:
        json.dump(new_names, f, indent=2)
    
    print(f"✅ Rebuilt {names_path} with {len(new_names)} entries")
    return True

def main():
    print("===== Face Recognition System - Dataset Verification Tool =====")
    print("This tool will help diagnose issues with your face dataset.")
    
    print("\n1. Verifying dataset structure...")
    verify_face_dataset()
    
    print("\nWould you like to rebuild the person_names.json file based on directories? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        rebuild_names_file()
        print("\nVerifying dataset after rebuild...")
        verify_face_dataset()
    
    print("\nDone!")

if __name__ == "__main__":
    main()