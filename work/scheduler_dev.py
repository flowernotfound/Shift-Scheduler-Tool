import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
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

    def assign_shifts_for_day(self, preferences, day):
        early_shift_candidates = preferences[preferences[day] == '早番']['名前'].tolist()
        late_shift_candidates = preferences[preferences[day] == '遅番']['名前'].tolist()
        all_day_candidates = preferences[preferences[day] == '終日可能']['名前'].tolist()
        assigned_early_shift = random.sample(early_shift_candidates, min(2, len(early_shift_candidates)))
        assigned_late_shift = random.sample(late_shift_candidates, min(2, len(late_shift_candidates)))
        while len(assigned_early_shift) < 2:
            if all_day_candidates:
                candidate = random.choice(all_day_candidates)
                assigned_early_shift.append(candidate)
                all_day_candidates.remove(candidate)
            else:
                break
        while len(assigned_late_shift) < 2:
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

    def create_shift_schedule(self, preferences):
        shift_schedule = pd.DataFrame(index=preferences['名前'].unique())
        for day in [f'希望日 [{i}日]' for i in range(1, 32) if f'希望日 [{i}日]' in preferences.columns]:
            daily_shifts = self.assign_shifts_for_day(preferences, day)
            for shift_type, names in daily_shifts.items():
                for name in names:
                    shift_schedule.loc[name, day] = shift_type
            shift_schedule[day] = shift_schedule[day].fillna('休み')
        self.shift_schedule = shift_schedule

class ShiftSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.scheduler = ShiftScheduler()
        self.selected_file_path = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("シフトスケジュール作成ツール")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 800
        height = 600
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        self.file_path_label = tk.Label(self.root, text="ファイルが選択されていません")
        self.file_path_label.pack()

        self.select_file_button = tk.Button(self.root, text="ファイルを選択", command=self.select_file)
        self.select_file_button.pack()

        self.start_button = tk.Button(self.root, text="シフト割り当て開始", command=self.start_shift_assignment)
        self.start_button.pack()

        self.save_button = tk.Button(self.root, text="結果を保存", command=self.save_results)
        self.save_button.pack()

        self.exit_button = tk.Button(self.root, text="終了", command=self.exit_application)
        self.exit_button.pack()

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
        try:
            preferences = self.scheduler.load_preferences(self.selected_file_path)
            self.scheduler.create_shift_schedule(preferences)
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