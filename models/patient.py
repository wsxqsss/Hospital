class Patient:
    def __init__(self, patient_id: int, name: str, age: int, gender: str):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.medical_records = [] # Список объектов MedicalRecord
def add_medical_record(self, record):
    self.medical_records.append(record)

def __str__(self):
    return f"Patient(ID: {self.patient_id}, Name: {self.name}, Age: {self.age}, Gender: {self.gender})"