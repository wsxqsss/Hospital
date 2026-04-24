from datetime import datetime

class MedicalRecord:
    def __init__(self, record_id: int, patient_id: int, diagnosis: str, prescription: str, record_date: datetime):
        self.record_id = record_id
        self.patient_id = patient_id
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.record_date = record_date
def __str__(self):
    return f"MedicalRecord(ID: {self.record_id}, PatientID: {self.patient_id}, Date: {self.record_date.strftime('%Y-%m-%d')}, Diagnosis: {self.diagnosis})"