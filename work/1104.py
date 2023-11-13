import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import os
import random

selected_file_path = None
assigned_shifts = None

# 特定の日に対してシフト希望を抽出し、早番と遅番を割り当てる関数
def assign_shifts_for_day(preferences, day):
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

def create_shift_schedule(preferences):
    shift_schedule = pd.DataFrame(index=preferences['名前'].unique())
    for day in [f'希望日 [{i}日]' for i in range(1, 32) if f'希望日 [{i}日]' in preferences.columns]:
        daily_shifts = assign_shifts_for_day(preferences, day)
        for shift_type, names in daily_shifts.items():
            for name in names:
                shift_schedule.loc[name, day] = shift_type
        shift_schedule[day] = shift_schedule[day].fillna('休み')
    return shift_schedule

# メインウィンドウの作成
root = tk.Tk()
root.title("シフトスケジュール作成ツール")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = 800
height = 600
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

file_path_label = tk.Label(root, text="ファイルが選択されていません")
file_path_label.pack()

def select_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        selected_file_path = file_path
        filename = os.path.basename(file_path)
        file_path_label.config(text=filename)

def start_shift_assignment():
    global assigned_shifts, selected_file_path
    if selected_file_path is None:
        messagebox.showwarning("警告", "ファイルが選択されていません。")
        return
    try:
        data = pd.read_csv(selected_file_path)
        assigned_shifts = create_shift_schedule(data)
        messagebox.showinfo("完了", "シフト割り当てが完了しました。")
    except Exception as e:
        messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました: {e}")

def save_results():
    global assigned_shifts
    if assigned_shifts is None:
        messagebox.showwarning("警告", "まだシフト割り当てが行われていません。")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        assigned_shifts.to_csv(save_path, index=True)
        messagebox.showinfo("保存", "シフト表を保存しました。")

def exit_application():
    root.destroy()

select_file_button = tk.Button(root, text="ファイルを選択", command=select_file)
select_file_button.pack()
start_button = tk.Button(root, text="シフト割り当て開始", command=start_shift_assignment)
start_button.pack()
save_button = tk.Button(root, text="結果を保存", command=save_results)
save_button.pack()
exit_button = tk.Button(root, text="終了", command=exit_application)
exit_button.pack()

root.mainloop()