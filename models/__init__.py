# Этот файл может быть пустым.
# Его наличие означает, что папка 'models' является пакетом Python.
# Можно также импортировать сюда классы для удобного доступа извне:
# from .patient import Patient
# from .doctor import Doctor
# ... и так далее
self.time_var = tk.StringVar()
self.time_combobox = ttk.Combobox(self.appointment_frame, textvariable=self.time_var)
self.time_var = tk.StringVar()
self.time_combobox = ttk.Combobox(
    self.appointment_frame,
    textvariable=self.time_var, # <-- Убедитесь, что это здесь
    values=[],
    state="readonly", # Или "normal", в зависимости от логики
    width=20
)
