class Doctor:
    def __init__(self, doctor_id: int, name: str, specialty: str):
        self.doctor_id = doctor_id
        self.name = name
        self.specialty = specialty
        self.schedule = None # Объект DoctorSchedule
def set_schedule(self, schedule):
    self.schedule = schedule

def __str__(self):
    return f"Doctor(ID: {self.doctor_id}, Name: {self.name}, Specialty: {self.specialty})"