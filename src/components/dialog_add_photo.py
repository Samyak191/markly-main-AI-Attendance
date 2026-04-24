import streamlit as st
from src.database.db import create_subject
from PIL import Image


@st.dialog("Capture or Upload photos")
def add_photos_dialog(teacher_id):
    st.write("Add classroom photos to scan for attendance")

    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "camera"

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("Camera", type=type_camera, width="stretch"):
            st.session_state.photo_tab = "camera"
            st.rerun()

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("Upload Photos", type=type_upload, width="stretch"):
            st.session_state.photo_tab = "upload"
            st.rerun()

    if st.session_state.photo_tab == "camera":
        cam_photo = st.camera_input("Take Snapshot", key="dialog_cam")
        if cam_photo is not None:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast("Photo captured")
            st.rerun()

    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader(
            "Upload Pictures",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast(f"{len(uploaded_files)} photo(s) uploaded")
            st.rerun()

    st.divider()

    if st.button("Done", type="primary", width="stretch"):
        st.rerun()
    
            

            




    
