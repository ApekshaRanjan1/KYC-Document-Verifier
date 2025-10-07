import face_recognition

def compare_faces(id_img_path, selfie_path):
    try:
        id_img = face_recognition.load_image_file(id_img_path)
        selfie_img = face_recognition.load_image_file(selfie_path)

        id_enc = face_recognition.face_encodings(id_img)
        selfie_enc = face_recognition.face_encodings(selfie_img)

        if not id_enc or not selfie_enc:
            return False  # face not detected

        results = face_recognition.compare_faces([id_enc[0]], selfie_enc[0])
        return results[0]
    except Exception as e:
        print("Face match error:", e)
        return False
