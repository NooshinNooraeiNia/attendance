from threading import Thread
import sqlite3
import cv2
import face_recognition
import os

class FaceRecognitionThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):

        known_encodings = []
        known_names = []

        for file_name in os.listdir('static/student_images'):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                name = os.path.splitext(file_name)[0]
                image_path = os.path.join(os.getcwd() + '/static/student_images', file_name)
                student_image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(student_image)[0]

                known_encodings.append(encoding)
                known_names.append(name)

        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()

            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                student_info_arr = name.split('_')
                if len(student_info_arr) == 2:

                    connection = sqlite3.connect('info.db')
                    cursor = connection.cursor()
                
                    cursor.execute('UPDATE students SET Present = ? WHERE student_name = ? AND student_no = ?', ('Yes', student_info_arr[1], student_info_arr[0]))

                    connection.commit()

                    if cursor.rowcount > 0:
                        print("Update successful. Rows affected:", cursor.rowcount)
                    else:
                        print("No matching rows found. Update not performed.")

                    connection.close()

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()


