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
    encodings=get_face_embeddings(class_image_np)
    
    model_data=get_trained_model()
    if not model_data:
        return [], [], len(encodings)
    clf=model_data['clf']
    X_train=model_data['X']
    y_train=model_data['y']
    all_students = sorted(list(set(y_train)))
    detected_student_ids = []

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]
        best_match_score = np.linalg.norm(student_embedding - encoding)

        threshold = 0.6
        if best_match_score <= threshold:
            if predicted_id not in detected_student_ids:
                detected_student_ids.append(predicted_id)

    return detected_student_ids, all_students, len(encodings)








              
 









