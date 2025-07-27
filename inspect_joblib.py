import joblib

with open("joblib_details.txt", "w", encoding="utf-8") as f:
    # Category model and encoder
    category_model = joblib.load('category_svm_model.joblib')
    category_encoder = joblib.load('category_encoder.joblib')

    f.write("Category SVM Model Pipeline Steps:\n")
    f.write(str(category_model.named_steps) + "\n\n")

    f.write("Category SVM Model Parameters:\n")
    f.write(str(category_model.get_params()) + "\n\n")

    f.write("Category SVM Model TF-IDF Vocabulary (first 20):\n")
    f.write(str(list(category_model.named_steps['tfidf'].vocabulary_.items())[:20]) + "\n\n")

    f.write("Category SVM Model Coefficients (shape):\n")
    f.write(str(category_model.named_steps['svc'].coef_.shape) + "\n\n")

    f.write("Category Encoder Classes:\n")
    f.write(str(category_encoder.classes_) + "\n\n")

    # Priority model and encoder
    priority_model = joblib.load('priority_lr_model.joblib')
    priority_encoder = joblib.load('priority_encoder.joblib')

    f.write("Priority Logistic Regression Model Pipeline Steps:\n")
    f.write(str(priority_model.named_steps) + "\n\n")

    f.write("Priority Logistic Regression Model Parameters:\n")
    f.write(str(priority_model.get_params()) + "\n\n")

    f.write("Priority Logistic Regression TF-IDF Vocabulary (first 20):\n")
    f.write(str(list(priority_model.named_steps['tfidf'].vocabulary_.items())[:20]) + "\n\n")

    f.write("Priority Logistic Regression Coefficients (shape):\n")
    f.write(str(priority_model.named_steps['lr'].coef_.shape) + "\n\n")

    f.write("Priority Encoder Classes:\n")
    f.write(str(priority_encoder.classes_) + "\n\n") 