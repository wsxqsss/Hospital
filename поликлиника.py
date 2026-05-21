import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date, time

# =========================
# ПРОВЕРКА tkcalendar
# =========================
try:
    from tkcalendar import DateEntry
except ImportError:
    print("Ошибка: установите tkcalendar")
    print("pip install tkcalendar")
    exit()

# =========================
# МОДЕЛИ
# =========================
class Patient:
    def __init__(
        self,
        patient_id,
        name,
        dob,
        phone="",
        snils="",
        policy=""
    ):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob
        self.phone = phone
        self.snils = snils
        self.policy = policy


class Doctor:
    def __init__(
        self,
        doctor_id,
        name,
        specialization
    ):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization


class Appointment:
    def __init__(
        self,
        appointment_id,
        patient_id,
        doctor_id,
        appointment_datetime
    ):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_datetime = appointment_datetime


class DoctorSchedule:
    def __init__(
        self,
        doctor_id,
        days_of_week,
        start_time,
        end_time
    ):
        self.doctor_id = doctor_id
        self.days_of_week = days_of_week
        self.start_time = start_time
        self.end_time = end_time


# =========================
# БАЗЫ ДАННЫХ
# =========================
patients_db = {
    1: Patient(
        1,
        "Иван Иванов",
        date(1990, 5, 20),
        "+7-900-111-11-11",
        "123-456-789 00",
        "1111222233334444"
    ),

    2: Patient(
        2,
        "Петр Петров",
        date(1985, 8, 15),
        "+7-900-222-22-22",
        "987-654-321 00",
        "5555666677778888"
    )
}

doctors_db = {
    1: Doctor(
        1,
        "Анна Иванова",
        "Терапевт"
    ),

    2: Doctor(
        2,
        "Сергей Смирнов",
        "Кардиолог"
    ),

    3: Doctor(
        3,
        "Дмитрий Козлов",
        "Невролог"
    )
}

doctor_schedule_db = {
    1: DoctorSchedule(
        1,
        ["Понедельник", "Среда", "Пятница"],
        time(9, 0),
        time(17, 0)
    ),

    2: DoctorSchedule(
        2,
        ["Вторник", "Четверг"],
        time(10, 0),
        time(18, 0)
    ),

    3: DoctorSchedule(
        3,
        ["Суббота"],
        time(9, 0),
        time(14, 0)
    )
}

appointments_db = []

next_appointment_id = 1

days_ru = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]

# =========================
# СТИЛИ
# =========================
def setup_styles():

    style = ttk.Style()

    style.theme_use("clam")

    style.configure(
        "Treeview",
        rowheight=25,
        font=("Arial", 10)
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 10, "bold")
    )


# =========================
# ПРИЛОЖЕНИЕ
# =========================
class ClinicApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Медицинская информационная система"
        )

        self.root.geometry("1400x800")

        setup_styles()

        self.time_slots_map = {}

        self.notebook = ttk.Notebook(root)

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.create_booking_tab()
        self.create_patients_tab()
        self.create_doctors_tab()
        self.create_appointments_tab()

    # ======================================
    # ВКЛАДКА ЗАПИСИ
    # ======================================
    def create_booking_tab(self):

        frame = ttk.Frame(self.notebook)

        self.notebook.add(
            frame,
            text="Запись на прием"
        )

        # ПОИСК
        ttk.Label(
            frame,
            text="Поиск пациента"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.search_booking_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.search_booking_var,
            width=40
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        ttk.Button(
            frame,
            text="Найти",
            command=self.search_patient_booking
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        # ПАЦИЕНТ
        ttk.Label(
            frame,
            text="Пациент"
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.patient_var = tk.StringVar()

        self.patient_combobox = ttk.Combobox(
            frame,
            textvariable=self.patient_var,
            state="readonly",
            width=50
        )

        self.patient_combobox.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        self.patient_combobox.bind(
            "<<ComboboxSelected>>",
            self.on_patient_selected
        )

        # СНИЛС
        ttk.Label(
            frame,
            text="СНИЛС"
        ).grid(
            row=2,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.snils_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.snils_var,
            state="readonly",
            width=53
        ).grid(
            row=2,
            column=1,
            padx=5,
            pady=5
        )

        # ПОЛИС
        ttk.Label(
            frame,
            text="Полис"
        ).grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.policy_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.policy_var,
            state="readonly",
            width=53
        ).grid(
            row=3,
            column=1,
            padx=5,
            pady=5
        )

        # ВРАЧ
        ttk.Label(
            frame,
            text="Врач"
        ).grid(
            row=4,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.doctor_var = tk.StringVar()

        self.doctor_combobox = ttk.Combobox(
            frame,
            textvariable=self.doctor_var,
            state="readonly",
            width=50
        )

        self.doctor_combobox.grid(
            row=4,
            column=1,
            padx=5,
            pady=5
        )

        self.doctor_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self.update_available_times()
        )

        # ДАТА
        ttk.Label(
            frame,
            text="Дата"
        ).grid(
            row=5,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.date_entry = DateEntry(
            frame,
            width=50,
            date_pattern="yyyy-mm-dd"
        )

        self.date_entry.grid(
            row=5,
            column=1,
            padx=5,
            pady=5
        )

        self.date_entry.bind(
            "<<DateEntrySelected>>",
            lambda e: self.update_available_times()
        )

        # ВРЕМЯ
        ttk.Label(
            frame,
            text="Время"
        ).grid(
            row=6,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.time_var = tk.StringVar()

        self.time_combobox = ttk.Combobox(
            frame,
            textvariable=self.time_var,
            state="readonly",
            width=50
        )

        self.time_combobox.grid(
            row=6,
            column=1,
            padx=5,
            pady=5
        )

        # КНОПКА
        ttk.Button(
            frame,
            text="Записать",
            command=self.create_appointment
        ).grid(
            row=7,
            column=1,
            pady=10
        )

        self.refresh_comboboxes()

    # ======================================
    # ВКЛАДКА ПАЦИЕНТОВ
    # ======================================
    def create_patients_tab(self):

        frame = ttk.Frame(self.notebook)

        self.notebook.add(
            frame,
            text="Пациенты"
        )

        ttk.Label(
            frame,
            text="Поиск (ФИО / СНИЛС / Полис)"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )

        self.patient_search_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.patient_search_var,
            width=40
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        ttk.Button(
            frame,
            text="Найти",
            command=self.search_patients
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        columns = (
            "ID",
            "ФИО",
            "Дата рождения",
            "Телефон",
            "СНИЛС",
            "Полис"
        )

        self.patient_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.patient_tree.heading(
                col,
                text=col
            )

            self.patient_tree.column(
                col,
                width=180
            )

        self.patient_tree.grid(
            row=1,
            column=0,
            columnspan=5,
            sticky="nsew",
            padx=5,
            pady=5
        )

        self.load_patients()

    # ======================================
    # ВКЛАДКА ВРАЧЕЙ
    # ======================================
    def create_doctors_tab(self):

        frame = ttk.Frame(self.notebook)

        self.notebook.add(
            frame,
            text="Врачи"
        )

        columns = (
            "ID",
            "ФИО",
            "Специализация"
        )

        self.doctor_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.doctor_tree.heading(
                col,
                text=col
            )

            self.doctor_tree.column(
                col,
                width=250
            )

        self.doctor_tree.pack(
            fill="both",
            expand=True
        )

        self.load_doctors()

    # ======================================
    # ВКЛАДКА ЗАПИСЕЙ
    # ======================================
    def create_appointments_tab(self):

        frame = ttk.Frame(self.notebook)

        self.notebook.add(
            frame,
            text="Записи"
        )

        ttk.Label(
            frame,
            text="Поиск (ФИО / СНИЛС / Полис)"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )

        self.appointment_search_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.appointment_search_var,
            width=40
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        ttk.Button(
            frame,
            text="Найти",
            command=self.search_appointments
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        columns = (
            "ID",
            "Пациент",
            "СНИЛС",
            "Полис",
            "Врач",
            "Дата"
        )

        self.appointment_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.appointment_tree.heading(
                col,
                text=col
            )

            self.appointment_tree.column(
                col,
                width=220
            )

        self.appointment_tree.grid(
            row=1,
            column=0,
            columnspan=5,
            sticky="nsew",
            padx=5,
            pady=5
        )

        self.load_appointments()

    # ======================================
    # ОБНОВЛЕНИЕ
    # ======================================
    def refresh_comboboxes(self):

        self.patient_combobox["values"] = [
            f"{p.patient_id} - {p.name}"
            for p in patients_db.values()
        ]

        self.doctor_combobox["values"] = [
            f"{d.doctor_id} - {d.name} ({d.specialization})"
            for d in doctors_db.values()
        ]

    # ======================================
    # ЗАГРУЗКА ПАЦИЕНТОВ
    # ======================================
    def load_patients(self):

        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        for p in patients_db.values():

            self.patient_tree.insert(
                "",
                tk.END,
                values=(
                    p.patient_id,
                    p.name,
                    p.dob.strftime("%Y-%m-%d"),
                    p.phone,
                    p.snils,
                    p.policy
                )
            )

    # ======================================
    # ЗАГРУЗКА ВРАЧЕЙ
    # ======================================
    def load_doctors(self):

        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)

        for d in doctors_db.values():

            self.doctor_tree.insert(
                "",
                tk.END,
                values=(
                    d.doctor_id,
                    d.name,
                    d.specialization
                )
            )

    # ======================================
    # ЗАГРУЗКА ЗАПИСЕЙ
    # ======================================
    def load_appointments(self):

        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)

        for app in appointments_db:

            patient = patients_db[app.patient_id]
            doctor = doctors_db[app.doctor_id]

            self.appointment_tree.insert(
                "",
                tk.END,
                values=(
                    app.appointment_id,
                    patient.name,
                    patient.snils,
                    patient.policy,
                    doctor.name,
                    app.appointment_datetime.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )
            )

    # ======================================
    # ПОИСК ПАЦИЕНТОВ
    # ======================================
    def search_patients(self):

        query = self.patient_search_var.get().lower()

        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        for p in patients_db.values():

            if (
                query in p.name.lower()
                or query in p.snils.lower()
                or query in p.policy.lower()
            ):

                self.patient_tree.insert(
                    "",
                    tk.END,
                    values=(
                        p.patient_id,
                        p.name,
                        p.dob.strftime("%Y-%m-%d"),
                        p.phone,
                        p.snils,
                        p.policy
                    )
                )

    # ======================================
    # ПОИСК ЗАПИСЕЙ
    # ======================================
    def search_appointments(self):

        query = self.appointment_search_var.get().lower()

        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)

        for app in appointments_db:

            patient = patients_db[app.patient_id]
            doctor = doctors_db[app.doctor_id]

            if (
                query in patient.name.lower()
                or query in patient.snils.lower()
                or query in patient.policy.lower()
            ):

                self.appointment_tree.insert(
                    "",
                    tk.END,
                    values=(
                        app.appointment_id,
                        patient.name,
                        patient.snils,
                        patient.policy,
                        doctor.name,
                        app.appointment_datetime.strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    )
                )

    # ======================================
    # ПОИСК ПАЦИЕНТА В ЗАПИСИ
    # ======================================
    def search_patient_booking(self):

        query = self.search_booking_var.get().lower()

        for p in patients_db.values():

            if (
                query in p.name.lower()
                or query in p.snils.lower()
                or query in p.policy.lower()
            ):

                self.patient_var.set(
                    f"{p.patient_id} - {p.name}"
                )

                self.snils_var.set(
                    p.snils
                )

                self.policy_var.set(
                    p.policy
                )

                return

        messagebox.showwarning(
            "Не найдено",
            "Пациент не найден"
        )

    # ======================================
    # ВЫБОР ПАЦИЕНТА
    # ======================================
    def on_patient_selected(self, event=None):

        if not self.patient_var.get():
            return

        patient_id = int(
            self.patient_var.get().split(" - ")[0]
        )

        patient = patients_db[patient_id]

        self.snils_var.set(
            patient.snils
        )

        self.policy_var.set(
            patient.policy
        )

    # ======================================
    # СВОБОДНОЕ ВРЕМЯ
    # ======================================
    def update_available_times(self):

        self.time_combobox["values"] = []

        self.time_slots_map = {}

        if not self.doctor_var.get():
            return

        doctor_id = int(
            self.doctor_var.get().split(" - ")[0]
        )

        selected_date = self.date_entry.get_date()

        weekday = days_ru[
            selected_date.weekday()
        ]

        schedule = doctor_schedule_db.get(
            doctor_id
        )

        if not schedule:
            return

        if weekday not in schedule.days_of_week:
            return

        start_dt = datetime.combine(
            selected_date,
            schedule.start_time
        )

        end_dt = datetime.combine(
            selected_date,
            schedule.end_time
        )

        current = start_dt

        slots = []

        while current < end_dt:

            occupied = False

            for app in appointments_db:

                if (
                    app.doctor_id == doctor_id
                    and app.appointment_datetime == current
                ):
                    occupied = True

            if not occupied:

                label = current.strftime(
                    "%H:%M"
                )

                slots.append(label)

                self.time_slots_map[label] = current

            current += timedelta(
                minutes=30
            )

        self.time_combobox["values"] = slots

    # ======================================
    # СОЗДАНИЕ ЗАПИСИ
    # ======================================
    def create_appointment(self):

        global next_appointment_id

        if not self.patient_var.get():

            messagebox.showwarning(
                "Ошибка",
                "Выберите пациента"
            )

            return

        if not self.doctor_var.get():

            messagebox.showwarning(
                "Ошибка",
                "Выберите врача"
            )

            return

        if not self.time_var.get():

            messagebox.showwarning(
                "Ошибка",
                "Выберите время"
            )

            return

        patient_id = int(
            self.patient_var.get().split(" - ")[0]
        )

        doctor_id = int(
            self.doctor_var.get().split(" - ")[0]
        )

        appointment_datetime = self.time_slots_map.get(
            self.time_var.get()
        )

        if not appointment_datetime:

            messagebox.showwarning(
                "Ошибка",
                "Некорректное время"
            )

            return

        appointment = Appointment(
            next_appointment_id,
            patient_id,
            doctor_id,
            appointment_datetime
        )

        appointments_db.append(
            appointment
        )

        next_appointment_id += 1

        self.load_appointments()

        self.update_available_times()

        messagebox.showinfo(
            "Успех",
            "Пациент успешно записан"
        )


# =========================
# ЗАПУСК
# =========================
if __name__ == "__main__":

    root = tk.Tk()

    app = ClinicApp(root)

    root.mainloop()
