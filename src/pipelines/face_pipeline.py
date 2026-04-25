import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from src.database.db import get_all_students

@st.cache_resource
# dlib has 3 values--> 1) Face detecotr which detects face 
# 2) sp--> convert it into facial landmarks
#3) facerec--> # helps in proper face recegnintion
def load_dlib_models():
    detector=dlib.get_frontal_face_detector()
    sp=dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec=dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()

    )

    return detector, sp, facerec


# ladnmarks--> embeddings 128 Dimensional Sparse Vector
def get_face_embeddings(image_np):
    detector, sp, facerec= load_dlib_models()
    faces=detector(image_np,1) # 1 for only 1 iteration(image pre-processing)
    encoding=[] # list of embeddings
    for face in faces:
        shape=sp(image_np, face)
        face_descriptor=facerec.compute_face_descriptor(image_np, shape, 1) # 128 dimensional embeddings
        encoding.append(np.array(face_descriptor)) #add embeddings in this list

    return encoding

@st.cache_resource
def get_trained_model():
    X=[]
    y=[]
    student_db=get_all_students()
    if not student_db:
        return None
    for student in student_db:
        embedding= student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))
    if len(X)==0:
        return 0
    
    clf=SVC(kernel='linear', probability=True, class_weight='balanced')  # balanced--> if there are multiple picture of a person, it scales all the pictures of that person to a single picture
    try:
        clf.fit(X,y)
    except ValueError:
        pass
    return{'clf': clf, 'X':X, "y":y}

def train_classifier(): # When a new student is added
    st.cache_resource.clear()
    model_data=get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    if not encodings:
        return [], [], 0
    
    model_data = get_trained_model()
    if model_data is None or model_data == 0 or not isinstance(model_data, dict):
        return [], [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    detected = []
    detected_student_ids = []
    unique_students = list(set(y_train))

    # YOU NEED THIS LOOP: encodings is a list, encoding is a single face
    for encoding in encodings:
        predicted_id = None
        
        if len(unique_students) == 1:
            predicted_id = int(unique_students[0])
        else:
            # Pass [encoding] as a 2D array for the classifier
            predicted_id = int(clf.predict([encoding])[0])

        # Get all embeddings for the predicted student to check distance
        student_embeddings = [
            X_train[i] for i, sid in enumerate(y_train)
            if sid == predicted_id
        ]

        # Find the smallest distance (Euclidean distance)
        min_distance = min(
            np.linalg.norm(embedding - encoding)
            for embedding in student_embeddings
        )

        # FINAL VERIFICATION
        if min_distance <= 0.55: 
            detected.append(True)
            detected_student_ids.append(predicted_id)
        else:
            detected.append(False)
            detected_student_ids.append(None)

    # Move the return outside the for loop
    return detected, detected_student_ids, len(encodings)

    
    








              
 









