from datetime import time

class DoctorSchedule:
    def __init__(self, schedule_id: int, doctor_id: int, work_start_time: time, work_end_time: time, days_of_week: list):
        self.schedule_id = schedule_id
        self.doctor_id = doctor_id
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time
        self.days_of_week = days_of_week # Например: ["Monday", "Tuesday", "Wednesday", ...]
def __str__(self):
    return f"Schedule(ID: {self.schedule_id}, DoctorID: {self.doctor_id}, WorkHours: {self.work_start_time.strftime('%H:%M')}-{self.work_end_time.strftime('%H:%M')}, Days: {', '.join(self.days_of_week)})"