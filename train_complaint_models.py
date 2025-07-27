import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import joblib

# Sample data
complaints = [
    {"text": "My professor hasn't returned graded papers for 3 weeks", "category": "Academic", "priority": "Medium"},
    {"text": "Leaky roof in D-12 classroom damaging equipment", "category": "Infrastructure", "priority": "High"},
    {"text": "Wi-Fi disconnects every 15 minutes in library", "category": "IT Services", "priority": "High"},
    {"text": "Bullying incident near cafeteria on March 5", "category": "Harassment", "priority": "Urgent"},
    {"text": "Food poisoning from campus cafeteria meal", "category": "Health/Safety", "priority": "Urgent"},
    {"text": "No wheelchair ramp in Chemistry building", "category": "Accessibility", "priority": "High"},
    {"text": "Incorrect grade recorded in student portal", "category": "Academic", "priority": "Medium"},
    {"text": "Overcrowded buses causing safety hazards", "category": "Transportation", "priority": "High"},
    {"text": "Missing books from reserved course materials", "category": "Library", "priority": "Low"},
    {"text": "Sexual harassment complaint against TA", "category": "Harassment", "priority": "Urgent"},
]
df = pd.DataFrame(complaints)

# Encode categories and priorities
category_encoder = LabelEncoder()
df['category_encoded'] = category_encoder.fit_transform(df['category'])
priority_encoder = LabelEncoder()
df['priority_encoded'] = priority_encoder.fit_transform(df['priority'])

# SVM for category
category_clf = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('svc', LinearSVC())
])
category_clf.fit(df['text'], df['category_encoded'])

# Logistic Regression for priority
priority_clf = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('lr', LogisticRegression(max_iter=1000))
])
priority_clf.fit(df['text'], df['priority_encoded'])

# Save models and encoders
joblib.dump(category_clf, 'category_svm_model.joblib')
joblib.dump(category_encoder, 'category_encoder.joblib')
joblib.dump(priority_clf, 'priority_lr_model.joblib')
joblib.dump(priority_encoder, 'priority_encoder.joblib')

print('Models and encoders saved.') 