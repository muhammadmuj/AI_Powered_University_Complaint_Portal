import joblib

# Load the priority encoder
priority_encoder = joblib.load('priority_encoder.joblib')

# Get the classes
classes = priority_encoder.classes_

# Write the classes to a text file
with open('priority_encoder_classes.txt', 'w', encoding='utf-8') as f:
    for label in classes:
        f.write(f"{label}\n")

print("Priority encoder classes have been saved to priority_encoder_classes.txt") 