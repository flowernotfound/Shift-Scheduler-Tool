import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
import os
import random

class ShiftScheduler:
    def __init__(self):
        self.shift_schedule = None

    def load_preferences(self, file_path):
        try:
            preferences = pd.read_csv(file_path)
            return preferences
        except Exception as e:
            raise Exception(f"ファイルの読み込みに失敗しました: {e}")

    def assign_shifts_for_day(self, preferences, day, early_shift_count, late_shift_count):
        early_shift_candidates = preferences[preferences[day] == '早番']['名前'].tolist()
        late_shift_candidates = preferences[preferences[day] == '遅番']['名前'].tolist()
        all_day_candidates = preferences[preferences[day] == '終日可能']['名前'].tolist()
        assigned_early_shift = random.sample(early_shift_candidates, min(early_shift_count, len(early_shift_candidates)))
        assigned_late_shift = random.sample(late_shift_candidates, min(late_shift_count, len(late_shift_candidates)))
        while len(assigned_early_shift) < early_shift_count:
            if all_day_candidates:
                candidate = random.choice(all_day_candidates)
                assigned_early_shift.append(candidate)
                all_day_candidates.remove(candidate)
            else:
                break
        while len(assigned_late_shift) < late_shift_count:
            if all_day_candidates:
                candidate = random.choice(all_day_candidates)
                assigned_late_shift.append(candidate)
                all_day_candidates.remove(candidate)
            else:
                break
        shift_assignments = {
            '早番': assigned_early_shift,
            '遅番': assigned_late_shift,
            '休み': [name for name in preferences['名前'] if name not in assigned_early_shift + assigned_late_shift]
        }
        return shift_assignments

    def create_shift_schedule(self, preferences, early_shift_count, late_shift_count):
        new_columns = []
        for col in preferences.columns:
            if '希望日 [' in col:
                new_col = col.replace('希望日 [', '').replace(']', '')
                new_columns.append(new_col)
            else:
                new_columns.append(col)
        preferences.columns = new_columns

        shift_schedule = pd.DataFrame(index=preferences['名前'].unique())
        shortage_list = []
        for day in [f'{i}日' for i in range(1, 32) if f'{i}日' in preferences.columns]:
            daily_shifts = self.assign_shifts_for_day(preferences, day, early_shift_count, late_shift_count)
            if len(daily_shifts['早番']) < early_shift_count or len(daily_shifts['遅番']) < late_shift_count:
                shortage_list.append(day)
            for shift_type, names in daily_shifts.items():
                for name in names:
                    shift_schedule.loc[name, day] = shift_type
            shift_schedule[day] = shift_schedule[day].fillna('休み')
        shift_schedule.loc['不足'] = ['不足' if day in shortage_list else '' for day in shift_schedule.columns]
        self.shift_schedule = shift_schedule

class ShiftSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.scheduler = ShiftScheduler()
        self.selected_file_path = None
        self.early_shift_count = 2
        self.late_shift_count = 2
        self.setup_ui()

    def is_valid_number(self, value):
        try:
            return int(value) >= 0
        except ValueError:
            return False

    def setup_ui(self):
        self.root.title("シフトスケジュール作成ツール")
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 12), padding=10)
        self.file_path_label = ttk.Label(self.root, text="ファイルが選択されていません")
        self.file_path_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")
        self.select_file_button = ttk.Button(self.root, text="ファイルを選択", command=self.select_file)
        early_shift_label = ttk.Label(self.root, text="早番の必要人数")
        early_shift_label.grid(row=3, column=0, pady=10, padx=10, sticky="e")
        self.early_shift_spinner = ttk.Spinbox(self.root, from_=0, to=10, increment=1, wrap=True)
        self.early_shift_spinner.set(self.early_shift_count)
        self.early_shift_spinner.grid(row=3, column=1, pady=10, padx=10, sticky="w")
        late_shift_label = ttk.Label(self.root, text="遅番の必要人数")
        late_shift_label.grid(row=4, column=0, pady=10, padx=10, sticky="e")
        self.late_shift_spinner = ttk.Spinbox(self.root, from_=0, to=10, increment=1, wrap=True)
        self.late_shift_spinner.set(self.late_shift_count)
        self.late_shift_spinner.grid(row=4, column=1, pady=10, padx=10, sticky="w")
        self.select_file_button.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        self.start_button = ttk.Button(self.root, text="シフト割り当て開始", command=self.start_shift_assignment)
        self.start_button.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.save_button = ttk.Button(self.root, text="結果を保存", command=self.save_results)
        self.save_button.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        self.exit_button = ttk.Button(self.root, text="終了", command=self.exit_application)
        self.exit_button.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.geometry('600x300')
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_path_label.config(text=filename)

    def start_shift_assignment(self):
        if self.selected_file_path is None:
            messagebox.showwarning("警告", "ファイルが選択されていません。")
            return
        early_shift_count = self.early_shift_spinner.get()
        late_shift_count = self.late_shift_spinner.get()
        if not self.is_valid_number(early_shift_count) or not self.is_valid_number(late_shift_count):
            messagebox.showerror("エラー", "早番または遅番の人数に無効な値が設定されています。")
            return
        early_shift_count = int(early_shift_count)
        late_shift_count = int(late_shift_count)
        try:
            preferences = self.scheduler.load_preferences(self.selected_file_path)
            self.scheduler.create_shift_schedule(preferences, early_shift_count, late_shift_count)
            messagebox.showinfo("完了", "シフト割り当てが完了しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました: {e}")

    def save_results(self):
        if self.scheduler.shift_schedule is None:
            messagebox.showwarning("警告", "まだシフト割り当てが行われていません。")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            self.scheduler.shift_schedule.to_csv(save_path, index=True)
            messagebox.showinfo("保存", "シフト表を保存しました。")

    def exit_application(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShiftSchedulerApp(root)
    root.mainloop()