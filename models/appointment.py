from datetime import datetime
# Предполагается, что классы Patient и Doctor уже импортированы где-то или будут импортированы при необходимости

class Appointment:
    def __init__(self, appointment_id: int, patient_id: int, doctor_id: int, appointment_time: datetime):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_time = appointment_time
        self.is_completed = False
def mark_as_completed(self):
    self.is_completed = True

def __str__(self):
    status = "Completed" if self.is_completed else "Pending"
    return f"Appointment(ID: {self.appointment_id}, PatientID: {self.patient_id}, DoctorID: {self.doctor_id}, Time: {self.appointment_time.strftime('%Y-%m-%d %H:%M')}, Status: {status})"