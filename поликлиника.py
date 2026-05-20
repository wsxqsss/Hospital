import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, date, time
import sqlite3
import json

# --- Модели данных ---
class Patient:
    def __init__(self, patient_id: int, name: str, dob: date):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob

class Doctor:
    def __init__(self, doctor_id: int, name: str, specialization: str):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization

class DoctorSchedule:
    def __init__(self, schedule_id: int, doctor_id: int, days_of_week: list, work_start_time: time, work_end_time: time):
        self.schedule_id = schedule_id
        self.doctor_id = doctor_id
        self.days_of_week = days_of_week
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time

class Appointment:
    def __init__(self, appointment_id: int, patient_id: int, doctor_id: int, appointment_datetime: datetime):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_datetime = appointment_datetime

# --- Симуляция базы данных ---
patients_db = {
    1: Patient(1, "Иван Петров", date(1990, 5, 15)),
    2: Patient(2, "Мария Сидорова", date(1985, 11, 20)),
    3: Patient(3, "Алексей Иванов", date(2000, 1, 1))
}

doctors_db = {
    101: Doctor(101, "Андрей Смирнов", "Терапевт"),
    102: Doctor(102, "Елена Попова", "Кардиолог"),
    103: Doctor(103, "Сергей Кузнецов", "Невролог")
}

days_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

doctor_schedule_db = {
    1: DoctorSchedule(1, 101, ["Понедельник", "Среда", "Пятница"], time(9, 0), time(17, 0)),
    2: DoctorSchedule(2, 102, ["Вторник", "Четверг"], time(10, 0), time(18, 0)),
    3: DoctorSchedule(3, 103, ["Суббота"], time(9, 0), time(13, 0))
}

appointments_db = []
next_appointment_id = 1

# --- Работа с базой SQLite ---
conn = sqlite3.connect('polyclinic.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS Patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    birth_date TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    specialization TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    FOREIGN KEY(patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES Doctors(doctor_id)
)
''')
conn.commit()

# --- Основное приложение ---
class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система записи на прием и управление базой")
        self._time_slots_map = {}

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TCombobox", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=1, fill='both')

        # Вкладки
        self.create_booking_tab()
        self.create_patients_tab()
        self.create_doctors_tab()
        self.create_appointments_tab()

        # Инициализация данных
        today = date.today()
        self.date_entry.set_date(today)
        self.date_var.set(today.strftime('%Y-%m-%d'))

        self.update_appointments_tree()

    # --- Вкладка записи на приём ---
    def create_booking_tab(self):
        self.booking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.booking_frame, text='Запись на прием')

        # Переменные
        self.patient_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()

        # Пациент
        ttk.Label(self.booking_frame, text="Пациент:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.patient_combobox = ttk.Combobox(self.booking_frame, textvariable=self.patient_var, state="readonly", width=40)
        self.patient_combobox.grid(row=0, column=1, pady=2, padx=5)
        self.patient_combobox['values'] = [f"{p.patient_id} - {p.name}" for p in patients_db.values()]
        self.patient_combobox.bind("<<ComboboxSelected>>", self.on_selection_change)

        # Врач
        ttk.Label(self.booking_frame, text="Врач:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.doctor_combobox = ttk.Combobox(self.booking_frame, textvariable=self.doctor_var, state="readonly", width=40)
        self.doctor_combobox.grid(row=1, column=1, pady=2, padx=5)
        self.doctor_combobox['values'] = [f"{d.doctor_id} - {d.name} ({d.specialization})" for d in doctors_db.values()]
        self.doctor_combobox.bind("<<ComboboxSelected>>", self.on_selection_change)

        # Дата
        ttk.Label(self.booking_frame, text="Дата приема:").grid(row=2, column=0, sticky=tk.W, pady=2)
        from tkcalendar import DateEntry
        self.date_entry = DateEntry(self.booking_frame, selectmode='day', textvariable=self.date_var, width=37, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, pady=2, padx=5)
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_select)

        # Время
        ttk.Label(self.booking_frame, text="Время приема:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.time_combobox = ttk.Combobox(self.booking_frame, textvariable=self.time_var, state="readonly", width=40)
        self.time_combobox.grid(row=3, column=1, pady=2, padx=5)
        self.time_combobox.set("Выберите врача и дату сначала")

        # Кнопка
        self.book_button = ttk.Button(self.booking_frame, text="Записаться на прием", command=self.create_appointment)
        self.book_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Таблица записей
        self.appointment_tree = ttk.Treeview(
            self.booking_frame, columns=("ID", "Пациент", "Врач", "Время"), show="headings"
        )
        self.appointment_tree.heading("ID", text="ID")
        self.appointment_tree.heading("Пациент", text="Пациент")
        self.appointment_tree.heading("Врач", text="Врач")
        self.appointment_tree.heading("Время", text="Время")
        self.appointment_tree.column("ID", width=50, anchor=tk.CENTER)
        self.appointment_tree.column("Пациент", width=200)
        self.appointment_tree.column("Врач", width=200)
        self.appointment_tree.column("Время", width=150, anchor=tk.CENTER)
        tree_scrollbar = ttk.Scrollbar(self.booking_frame, orient="vertical", command=self.appointment_tree.yview)
        self.appointment_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.appointment_tree.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.booking_frame.grid_columnconfigure(0, weight=1)
        self.booking_frame.grid_rowconfigure(5, weight=1)

        # Связь событий
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.update_available_times())
        self.patient_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_available_times())
        self.doctor_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_available_times())

    def on_date_select(self, event=None):
        self.update_available_times()

    def on_selection_change(self, event=None):
        if self.patient_var.get() and self.doctor_var.get():
            self.update_available_times()

    def update_available_times(self):
        selected_doctor_info = self.doctor_var.get()
        selected_date_str = self.date_var.get()

        # Сброс
        self._time_slots_map = {}
        self.time_var.set("")
        self.time_combobox['values'] = []

        if not selected_doctor_info or not selected_date_str:
            self.time_combobox.set("Выберите врача и дату сначала")
            return

        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            day_index = selected_date.weekday()
            current_day_of_week_ru = days_ru[day_index]

            selected_doctor_id = int(selected_doctor_info.split(" - ")[0])
            schedule = None
            for sched in doctor_schedule_db.values():
                if sched.doctor_id == selected_doctor_id and current_day_of_week_ru in sched.days_of_week:
                    schedule = sched
                    break

            if not schedule:
                self.time_combobox.set(f"Врач не работает в {current_day_of_week_ru}")
                return

            slot_duration = timedelta(minutes=30)
            start_dt = datetime.combine(selected_date, schedule.work_start_time)
            end_dt = datetime.combine(selected_date, schedule.work_end_time)

            display_labels = []
            current_slot = start_dt
            while current_slot < end_dt:
                # Проверяем, не занят ли слот
                is_booked = any(
                    app.doctor_id == selected_doctor_id and app.appointment_datetime == current_slot
                    for app in appointments_db
                )
                if not is_booked:
                    label = current_slot.strftime("%H:%M")
                    self._time_slots_map[label] = current_slot
                    display_labels.append(label)
                current_slot += slot_duration

            if display_labels:
                self.time_combobox['values'] = display_labels
                self.time_combobox.set("Выберите время")
            else:
                self.time_combobox.set("Нет доступных слотов")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def create_appointment(self):
        global next_appointment_id
        try:
            selected_patient_info = self.patient_var.get()
            selected_doctor_info = self.doctor_var.get()
            selected_time_label = self.time_var.get()

            if not selected_patient_info or not selected_doctor_info:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите пациента и врача.")
                return

            if selected_time_label not in self._time_slots_map:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите доступное время приема.")
                return

            patient_id = int(selected_patient_info.split(" - ")[0])
            doctor_id = int(selected_doctor_info.split(" - ")[0])
            appointment_datetime = self._time_slots_map[selected_time_label]

            # Проверка на занятость
            for app in appointments_db:
                if app.doctor_id == doctor_id and app.appointment_datetime == appointment_datetime:
                    messagebox.showwarning("Занято", f"Время {selected_time_label} уже занято. Выберите другое.")
                    self.update_available_times()
                    return

            new_app = Appointment(
                appointment_id=next_appointment_id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_datetime=appointment_datetime
            )
            appointments_db.append(new_app)
            next_appointment_id += 1

            messagebox.showinfo(
                "Успех",
                f"Запись оформлена:\nПациент: {patients_db[patient_id].name}\n"
                f"Врач: {doctors_db[doctor_id].name}\n"
                f"Время: {appointment_datetime.strftime('%Y-%m-%d %H:%M')}"
            )
            self.update_appointments_tree()
            self.update_available_times()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_appointments_tree(self):
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        now = datetime.now()
        upcoming = sorted(
            [app for app in appointments_db if app.appointment_datetime >= now],
            key=lambda x: x.appointment_datetime
        )
        for app in upcoming:
            patient = patients_db.get(app.patient_id)
            doctor = doctors_db.get(app.doctor_id)
            if patient and doctor:
                self.appointment_tree.insert("", tk.END, values=(
                    app.appointment_id,
                    f"{patient.name} (ID:{patient.patient_id})",
                    f"{doctor.name} ({doctor.specialization})",
                    app.appointment_datetime.strftime('%Y-%m-%d %H:%M')
                ))

    # --- Таблица пациентов ---
    def create_patients_tab(self):
        self.patients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.patients_tab, text='Пациенты')

        ttk.Label(self.patients_tab, text="Поиск по ФИО или ID").grid(row=0, column=0, padx=5, pady=5)
        self.patient_search_entry = ttk.Entry(self.patients_tab)
        self.patient_search_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.patients_tab, text="Найти", command=self.search_patients).grid(row=0, column=2, padx=5, pady=5)

        self.patient_tree = ttk.Treeview(self.patients_tab, columns=("ФИО", "Дата рождения", "ID"), show='headings')
        self.patient_tree.heading("ФИО", text="ФИО")
        self.patient_tree.heading("Дата рождения", text="Дата рождения")
        self.patient_tree.heading("ID", text="ID")
        self.patient_tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.patient_tree.bind('<<TreeviewSelect>>', self.on_patient_select)
        self.load_patients()

        ttk.Button(self.patients_tab, text="Редактировать", command=self.edit_patient).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.patients_tab, text="Удалить", command=self.delete_patient).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.patients_tab, text="Добавить", command=self.add_patient).grid(row=2, column=2, padx=5, pady=5)

        # Импорт/Экспорт
        ttk.Button(self.patients_tab, text="Импортировать из JSON", command=self.import_patients_json).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.patients_tab, text="Экспортировать в JSON", command=self.export_patients_json).grid(row=3, column=1, padx=5, pady=5)

        self.selected_patient_id = None

    def load_patients(self):
        self.patient_tree.delete(*self.patient_tree.get_children())
        cursor.execute("SELECT full_name, birth_date, patient_id FROM Patients")
        for row in cursor.fetchall():
            self.patient_tree.insert('', 'end', values=row)

    def search_patients(self):
        search_term = self.patient_search_entry.get()
        self.patient_tree.delete(*self.patient_tree.get_children())
        cursor.execute('''
            SELECT full_name, birth_date, patient_id FROM Patients
            WHERE full_name LIKE ? OR patient_id LIKE ?
        ''', ('%' + search_term + '%', '%' + search_term + '%'))
        for row in cursor.fetchall():
            self.patient_tree.insert('', 'end', values=row)

    def on_patient_select(self, event):
        selected = self.patient_tree.focus()
        if selected:
            values = self.patient_tree.item(selected, 'values')
            self.selected_patient_id = values[2]
        else:
            self.selected_patient_id = None

    def edit_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Внимание", "Выберите пациента для редактирования")
            return
        messagebox.showinfo("Редактировать", f"Редактировать пациента с ID {self.selected_patient_id}")

    def delete_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Внимание", "Выберите пациента для удаления")
            return
        cursor.execute('DELETE FROM Patients WHERE patient_id=?', (self.selected_patient_id,))
        conn.commit()
        self.load_patients()

    def add_patient(self):
        def save_new_patient():
            name = name_entry.get()
            birth_date = birth_entry.get()
            if name and birth_date:
                cursor.execute("INSERT INTO Patients (full_name, birth_date) VALUES (?, ?)", (name, birth_date))
                conn.commit()
                self.load_patients()
                add_window.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля")

        add_window = tk.Toplevel()
        add_window.title("Добавить пациента")
        ttk.Label(add_window, text="ФИО").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(add_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(add_window, text="Дата рождения").grid(row=1, column=0, padx=5, pady=5)
        birth_entry = ttk.Entry(add_window)
        birth_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(add_window, text="Сохранить", command=save_new_patient).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def import_patients_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                cursor.execute("INSERT INTO Patients (full_name, birth_date) VALUES (?, ?)", (item['full_name'], item['birth_date']))
            conn.commit()
            self.load_patients()

    def export_patients_json(self):
        cursor.execute("SELECT full_name, birth_date FROM Patients")
        data = [{'full_name': row[0], 'birth_date': row[1]} for row in cursor.fetchall()]
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    # --- Вкладка врачи ---
    def create_doctors_tab(self):
        self.doctors_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.doctors_tab, text='Врачи')

        ttk.Label(self.doctors_tab, text="Поиск по ФИО или ID").grid(row=0, column=0, padx=5, pady=5)
        self.doctor_search_entry = ttk.Entry(self.doctors_tab)
        self.doctor_search_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.doctors_tab, text="Найти", command=self.search_doctors).grid(row=0, column=2, padx=5, pady=5)

        self.doctor_tree = ttk.Treeview(self.doctors_tab, columns=("ФИО", "Специализация", "ID"), show='headings')
        self.doctor_tree.heading("ФИО", text="ФИО")
        self.doctor_tree.heading("Специализация", text="Специализация")
        self.doctor_tree.heading("ID", text="ID")
        self.doctor_tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.doctor_tree.bind('<<TreeviewSelect>>', self.on_doctor_select)
        self.load_doctors()

        ttk.Button(self.doctors_tab, text="Редактировать", command=self.edit_doctor).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.doctors_tab, text="Удалить", command=self.delete_doctor).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.doctors_tab, text="Добавить", command=self.add_doctor).grid(row=2, column=2, padx=5, pady=5)

        ttk.Button(self.doctors_tab, text="Импортировать из JSON", command=self.import_doctors_json).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.doctors_tab, text="Экспортировать в JSON", command=self.export_doctors_json).grid(row=3, column=1, padx=5, pady=5)

        self.selected_doctor_id = None

    def load_doctors(self):
        self.doctor_tree.delete(*self.doctor_tree.get_children())
        cursor.execute("SELECT full_name, specialization, doctor_id FROM Doctors")
        for row in cursor.fetchall():
            self.doctor_tree.insert('', 'end', values=row)

    def search_doctors(self):
        search_term = self.doctor_search_entry.get()
        self.doctor_tree.delete(*self.doctor_tree.get_children())
        cursor.execute('''
            SELECT full_name, specialization, doctor_id FROM Doctors
            WHERE full_name LIKE ? OR doctor_id LIKE ?
        ''', ('%' + search_term + '%', '%' + search_term + '%'))
        for row in cursor.fetchall():
            self.doctor_tree.insert('', 'end', values=row)

    def on_doctor_select(self, event):
        selected = self.doctor_tree.focus()
        if selected:
            values = self.doctor_tree.item(selected, 'values')
            self.selected_doctor_id = values[2]
        else:
            self.selected_doctor_id = None

    def edit_doctor(self):
        if not self.selected_doctor_id:
            messagebox.showwarning("Внимание", "Выберите врача для редактирования")
            return
        messagebox.showinfo("Редактировать", f"Редактировать врача с ID {self.selected_doctor_id}")

    def delete_doctor(self):
        if not self.selected_doctor_id:
            messagebox.showwarning("Внимание", "Выберите врача для удаления")
            return
        cursor.execute('DELETE FROM Doctors WHERE doctor_id=?', (self.selected_doctor_id,))
        conn.commit()
        self.load_doctors()

    def add_doctor(self):
        def save_new_doctor():
            name = name_entry.get()
            spec = spec_entry.get()
            if name and spec:
                cursor.execute("INSERT INTO Doctors (full_name, specialization) VALUES (?, ?)", (name, spec))
                conn.commit()
                self.load_doctors()
                add_window.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля")

        add_window = tk.Toplevel()
        add_window.title("Добавить врача")
        ttk.Label(add_window, text="ФИО").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(add_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(add_window, text="Специализация").grid(row=1, column=0, padx=5, pady=5)
        spec_entry = ttk.Entry(add_window)
        spec_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(add_window, text="Сохранить", command=save_new_doctor).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def import_doctors_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                cursor.execute("INSERT INTO Doctors (full_name, specialization) VALUES (?, ?)", (item['full_name'], item['specialization']))
            conn.commit()
            self.load_doctors()

    def export_doctors_json(self):
        cursor.execute("SELECT full_name, specialization FROM Doctors")
        data = [{'full_name': row[0], 'specialization': row[1]} for row in cursor.fetchall()]
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    # --- Вкладка приёмов ---
    def create_appointments_tab(self):
        self.appointments_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.appointments_tab, text='Записи')

        ttk.Label(self.appointments_tab, text="Поиск по ID или пациенту или врачу").grid(row=0, column=0, padx=5, pady=5)
        self.appointment_search_entry = ttk.Entry(self.appointments_tab)
        self.appointment_search_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.appointments_tab, text="Найти", command=self.search_appointments).grid(row=0, column=2, padx=5, pady=5)

        self.appointment_tree = ttk.Treeview(self.appointments_tab, columns=("ID", "Пациент", "Врач"), show='headings')
        self.appointment_tree.heading("ID", text="ID")
        self.appointment_tree.heading("Пациент", text="Пациент")
        self.appointment_tree.heading("Врач", text="Врач")
        self.appointment_tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.appointment_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        self.load_appointments()

        ttk.Button(self.appointments_tab, text="Редактировать", command=self.edit_appointment).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.appointments_tab, text="Удалить", command=self.delete_appointment).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.appointments_tab, text="Добавить", command=self.add_appointment).grid(row=2, column=2, padx=5, pady=5)

        ttk.Button(self.appointments_tab, text="Импортировать из JSON", command=self.import_appointments_json).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.appointments_tab, text="Экспортировать в JSON", command=self.export_appointments_json).grid(row=3, column=1, padx=5, pady=5)

        self.selected_appointment_id = None

    def load_appointments(self):
        self.appointment_tree.delete(*self.appointment_tree.get_children())
        cursor.execute("SELECT appointment_id, patient_id, doctor_id FROM Appointments")
        for row in cursor.fetchall():
            self.appointment_tree.insert('', 'end', values=row)

    def search_appointments(self):
        search_term = self.appointment_search_entry.get()
        self.appointment_tree.delete(*self.appointment_tree.get_children())
        cursor.execute('''
            SELECT appointment_id, patient_id, doctor_id FROM Appointments
            WHERE appointment_id LIKE ? OR patient_id LIKE ? OR doctor_id LIKE ?
        ''', ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
        for row in cursor.fetchall():
            self.appointment_tree.insert('', 'end', values=row)

    def on_appointment_select(self, event):
        selected = self.appointment_tree.focus()
        if selected:
            values = self.appointment_tree.item(selected, 'values')
            self.selected_appointment_id = values[0]
        else:
            self.selected_appointment_id = None

    def edit_appointment(self):
        if not self.selected_appointment_id:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        messagebox.showinfo("Редактировать", f"Редактировать запись с ID {self.selected_appointment_id}")

    def delete_appointment(self):
        if not self.selected_appointment_id:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        cursor.execute('DELETE FROM Appointments WHERE appointment_id=?', (self.selected_appointment_id,))
        conn.commit()
        self.load_appointments()

    def add_appointment(self):
        def save_new_appointment():
            patient_id = patient_id_entry.get()
            doctor_id = doctor_id_entry.get()
            if patient_id and doctor_id:
                cursor.execute("INSERT INTO Appointments (patient_id, doctor_id) VALUES (?, ?)", (patient_id, doctor_id))
                conn.commit()
                self.load_appointments()
                add_window.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля")

        add_window = tk.Toplevel()
        add_window.title("Добавить запись")
        ttk.Label(add_window, text="ID пациента").grid(row=0, column=0, padx=5, pady=5)
        patient_id_entry = ttk.Entry(add_window)
        patient_id_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(add_window, text="ID врача").grid(row=1, column=0, padx=5, pady=5)
        doctor_id_entry = ttk.Entry(add_window)
        doctor_id_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(add_window, text="Сохранить", command=save_new_appointment).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def import_appointments_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                cursor.execute("INSERT INTO Appointments (patient_id, doctor_id) VALUES (?, ?)", (item['patient_id'], item['doctor_id']))
            conn.commit()
            self.load_appointments()

    def export_appointments_json(self):
        cursor.execute("SELECT patient_id, doctor_id FROM Appointments")
        data = [{'patient_id': row[0], 'doctor_id': row[1]} for row in cursor.fetchall()]
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файлы", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def update_appointments_tree(self):
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        cursor.execute("SELECT appointment_id, patient_id, doctor_id FROM Appointments")
        for row in cursor.fetchall():
            self.appointment_tree.insert('', 'end', values=row)

# --- Запуск ---
if __name__ == "__main__":
    try:
        from tkcalendar import DateEntry
    except ImportError:
        print("Ошибка: модуль tkcalendar не найден.")
        print("Установите его: pip install tkcalendar")
        exit()

    root = tk.Tk()
    app = ClinicApp(root)
    root.mainloop()
