from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())



def check_teacher_exists(username):
    # check for username if already exisits
    response=supabase.table("teacher").select("username").eq("username", username).execute()
    return len(response.data) > 0 


def create_teacher(username, password, name):
    data={"username": username, "password":hash_pass(password),"name":name}
    response=supabase.table("teacher").insert(data).execute()
    return response.data 


def teacher_login(username, password):
    response=supabase.table("teacher").select("*").eq("username", username).execute()
    if response.data:
        teacher=response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None
        

def get_all_students():
    response=supabase.table('student').select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    username = new_name.lower().replace(" ", "")
    password = "default123"   # ✅ add temporary password

    data = {
        "name": new_name,
        "username": username,
        "password": password,  # ✅ ADD THIS
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }

    response = supabase.table('student').insert(data).execute()
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data={"subject_code": subject_code, "name": name, "section": section, "teacher_id":teacher_id, "username": f"sub_{subject_code.lower()}"}
    response=supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects')\
        .select("*, subject_students(count)")\
        .eq("teacher_id", teacher_id)\
        .execute()

    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get('subject_students', [{}])[0].get('count', 0)

        attendance_res = supabase.table('attendence')\
            .select('timestamp')\
            .eq('subject_id', sub['subject_id'])\
            .execute()

        if attendance_res.data:
            unique_classes = len(set(row['timestamp'] for row in attendance_res.data))
            sub['total_classes'] = unique_classes
        else:
            sub['total_classes'] = 0

    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data={'student_id': student_id,"subject_id": subject_id}
    response=supabase.table('subject_students').insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
    response=supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()

    return response.data

def get_student_subjects(student_id):
    response=supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response=supabase.table('attendence').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data

def create_attendance(logs):
    response=supabase.table('attendence').insert(logs).execute()
    return response.data


def get_attendance_for_teacher(teacher_id):
    response=supabase.table('attendence').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    return response.data





  







