import tkinter as tk
from tkinter import ttk, messagebox
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from models.department import Department
from models.medical_record import MedicalRecord
from models.doctor_schedule import DoctorSchedule

# main.py (или 112.py)

# Импортируем классы из пакета models
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from models.department import Department
from models.medical_record import MedicalRecord
from models.doctor_schedule import DoctorSchedule

from datetime import datetime, time

if __name__ == "__main__":
    # Пример использования:

    # Создаем пациента
    patient1 = Patient(patient_id=1, name="Иван Петров", age=30, gender="Мужской")
    print(patient1)

    # Создаем доктора
    doctor1 = Doctor(doctor_id=101, name="Анна Смирнова", specialty="Терапевт")
    print(doctor1)

    # Создаем расписание для доктора
    schedule1 = DoctorSchedule(schedule_id=1, doctor_id=101, work_start_time=time(9, 0), work_end_time=time(17, 0), days_of_week=["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
    print(doctor1.schedule)

    # Создаем запись на прием
    appointment_time = datetime(2026, 5, 15, 11, 30)
    appointment1 = Appointment(appointment_id=501, patient_id=patient1.patient_id, doctor_id=doctor1.doctor_id, appointment_time=appointment_time)
    print(appointment1)

    # Создаем медицинскую запись
    record_date = datetime(2026, 5, 10)
    medical_record1 = MedicalRecord(record_id=201, patient_id=patient1.patient_id, diagnosis="ОРВИ", prescription="Постельный режим, обильное питье", record_date=record_date)
    print(medical_record1)

    # Создаем отдел
    department1 = Department(department_id=1, name="Поликлиника №5")
    print(department1)

    print("\n--- Информация о пациенте ---")
    print(f"Имя: {patient1.name}")
    print("Медицинские записи:")
    for record in patient1.medical_records:
        print(f"- {record}") # Будет использован __str__ из MedicalRecord


# --- Примерные данные (в реальном приложении это будет база данных) ---
patients_db = {
    1: Patient(1, "Иванов Иван Иванович", "1990-05-15"),
    2: Patient(2, "Петрова Анна Сергеевна", "1985-11-20"),
}
doctors_db = {
    101: Doctor(101, "Смирнов Дмитрий Петрович", "Терапевт"),
    102: Doctor(102, "Кузнецова Елена Викторовна", "Кардиолог"),
}
departments_db = {
    1: Department(1, "Терапевтическое"),
    2: Department(2, "Кардиологическое"),
}
appointments_db = []
medical_records_db = {
    201: MedicalRecord(201, 1, "ОРВИ, грипп"),
    202: MedicalRecord(202, 2, "Гипертония"),
}
doctor_schedule_db = {
    1: DoctorSchedule(1, 101, "09:00"),
    2: DoctorSchedule(2, 101, "10:00"),
    3: DoctorSchedule(3, 102, "11:00"),
}

# --- Counters for IDs ---
next_appointment_id = 1

class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Запись в поликлинику")
        self.root.geometry("800x600")

        # --- Styling ---
        self.style = ttk.Style()
        self.style.theme_use("clam") # Можно попробовать "alt", "default", "classic"
        self.style.configure("TFrame", background="#e0f7fa") # Светло-голубой фон
        self.style.configure("TLabel", background="#e0f7fa", foreground="#004d40", font=("Helvetica", 10))
        self.style.configure("TButton", background="#0077c2", foreground="white", font=("Helvetica", 10, "bold"))
        self.style.map("TButton",
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '#0056b3'), ('active', '#0288d1')])
        self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#004d40", font=("Helvetica", 10))
        self.style.configure("TCombobox", fieldbackground="#ffffff", foreground="#004d40", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#004d40", background="#e0f7fa")

        self.create_widgets()

    def create_widgets(self):
        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Header ---
        header_label = ttk.Label(main_frame, text="Добро пожаловать в систему записи поликлиники", style="Header.TLabel")
        header_label.pack(pady=20)

        # --- Booking Frame ---
        booking_frame = ttk.LabelFrame(main_frame, text="Запись на прием", padding="15", relief=tk.RIDGE, borderwidth=2)
        booking_frame.pack(pady=10, padx=10, fill=tk.X, expand=True)

        # Patient Selection
        ttk.Label(booking_frame, text="Пациент:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.patient_var = tk.StringVar()
        self.patient_combobox = ttk.Combobox(booking_frame, textvariable=self.patient_var, state="readonly", width=40)
        self.patient_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.update_patient_combobox()

        # Doctor Selection
        ttk.Label(booking_frame, text="Врач:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.doctor_var = tk.StringVar()
        self.doctor_combobox = ttk.Combobox(booking_frame, textvariable=self.doctor_var, state="readonly", width=40)
        self.doctor_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.update_doctor_combobox()

        # Time Selection
        ttk.Label(booking_frame, text="Время приема:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.time_var = tk.StringVar()
        self.time_combobox = ttk.Combobox(booking_frame, textvariable=self.time_var, width=40)
        self.time_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.time_combobox.set("Выберите врача сначала")

        # Booking Button
        book_button = ttk.Button(booking_frame, text="Записаться", command=self.create_appointment)
        book_button.grid(row=3, column=0, columnspan=2, pady=15)

        # Update comboboxes when doctor is selected
        self.doctor_combobox.bind("<<ComboboxSelected>>", self.update_time_combobox)

        # --- Display Appointments ---
        appointments_frame = ttk.LabelFrame(main_frame, text="Записи", padding="15", relief=tk.RIDGE, borderwidth=2)
        appointments_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.appointment_tree = ttk.Treeview(appointments_frame, columns=("AppointmentID", "PatientName", "DoctorName", "Time"), show="headings")
        for col in ("AppointmentID", "PatientName", "DoctorName", "Time"):
            self.appointment_tree.heading(col, text=col)
            self.appointment_tree.column(col, width=150, anchor=tk.CENTER)
        self.appointment_tree.heading("PatientName", text="Пациент")
        self.appointment_tree.heading("DoctorName", text="Врач")
        self.appointment_tree.heading("Time", text="Время")

        self.appointment_tree.pack(fill=tk.BOTH, expand=True)
        self.update_appointments_tree()

        # --- Make columns resizable ---
        booking_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1) # For appointments_frame

    def update_patient_combobox(self):
        patient_names = [f"{p.patient_id} - {p.full_name}" for p in patients_db.values()]
        self.patient_combobox['values'] = patient_names

    def update_doctor_combobox(self):
        doctor_names = [f"{d.doctor_id} - {d.full_name} ({d.specialization})" for d in doctors_db.values()]
        self.doctor_combobox['values'] = doctor_names

    def update_time_combobox(self, event=None):
        selected_doctor_info = self.doctor_var.get()
        if not selected_doctor_info:
            self.time_combobox.set("")
            self.time_combobox['values'] = []
            return

        try:
            selected_doctor_id = int(selected_doctor_info.split(" - ")[0])
            available_times = [f"{ds.time}" for ds in doctor_schedule_db.values() if ds.doctor_id == selected_doctor_id]
            self.time_combobox['values'] = available_times
            self.time_combobox.set("") # Clear selection
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ID врача.")
        except IndexError:
            messagebox.showerror("Ошибка", "Неверный формат идентификатора врача.")


    def create_appointment(self):
        global next_appointment_id
        try:
            selected_patient_info = self.patient_var.get()
            selected_doctor_info = self.doctor_var.get()
            selected_time = self.time_var.get()

            if not all([selected_patient_info, selected_doctor_info, selected_time]):
                messagebox.showwarning("Внимание", "Пожалуйста, выберите пациента, врача и время приема.")
                return

            patient_id = int(selected_patient_info.split(" - ")[0])
            doctor_id = int(selected_doctor_info.split(" - ")[0])

            # Проверка, занято ли время (очень упрощенная)
            for app in appointments_db:
                doctor_id_app = app.doctor_id
                time_app = app.time # Нужно, чтобы время было добавлено в данные об записи

                # Чтобы эта проверка работала, нужно добавить время в Appointment
                # Для этого пока сделаем простую имитацию, где время хранится в объекте Appointment
                # В более сложном приложении время лучше хранить отдельно или привязывать к конкретной дате
                if doctor_id_app == doctor_id and time_app == selected_time:
                    messagebox.showwarning("Извините", f"Время {selected_time} для врача {doctors_db[doctor_id].full_name} уже занято.")
                    return

            new_appointment = Appointment(next_appointment_id, patient_id, doctor_id)
            # В реальном приложении время приема должно быть частью объекта Appointment или связанного объекта
            # Для демонстрации, пока добавим его "виртуально"
            new_appointment.time = selected_time # Добавляем время для проверки занятости
            appointments_db.append(new_appointment)
            next_appointment_id += 1

            messagebox.showinfo("Успех", f"Пациент {patients_db[patient_id].full_name} успешно записан к врачу {doctors_db[doctor_id].full_name} на {selected_time}.")
            self.update_appointments_tree()
            self.clear_booking_fields()

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат ID пациента или врача.")
        except IndexError:
            messagebox.showerror("Ошибка", "Неверный формат идентификатора пациента или врача.")
        except KeyError as e:
            messagebox.showerror("Ошибка", f"Не найден ID: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def clear_booking_fields(self):
        self.patient_var.set("")
        self.doctor_var.set("")
        self.time_var.set("")
        self.time_combobox['values'] = []

    def update_appointments_tree(self):
        # Очищаем старые записи
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)

        # Добавляем новые записи
        for appointment in appointments_db:
            patient_name = patients_db.get(appointment.patient_id, Patient(0, "Неизвестный", "N/A")).full_name
            doctor_name = doctors_db.get(appointment.doctor_id, Doctor(0, "Неизвестный", "N/A")).full_name
            # Используем "виртуально" добавленное время
            time_str = getattr(appointment, 'time', 'N/A')
            self.appointment_tree.insert("", tk.END, values=(appointment.appointment_id, patient_name, doctor_name, time_str))

if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicApp(root)
    root.mainloop()