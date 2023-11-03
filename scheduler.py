import pandas as pd
import random
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# CSVファイルのパス
file_path = ''

# # CSVファイルの読み込み
# try:
#     # Attempt to read the CSV with default encoding
#     shift_preferences = pd.read_csv(file_path)
# except UnicodeDecodeError:
#     # If there's an encoding error, try a common alternative encoding
#     shift_preferences = pd.read_csv(file_path, encoding='utf-8-sig')

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

# 全日にわたってシフトを割り当て、シフトスケジュールを作成する関数
def create_shift_schedule(preferences):
    shift_schedule = pd.DataFrame(index=preferences['名前'].unique())
    
    for day in [f'希望日 [{i}日]' for i in range(1, 32) if f'希望日 [{i}日]' in preferences.columns]:
        daily_shifts = assign_shifts_for_day(preferences, day)
        
        for shift_type, names in daily_shifts.items():
            for name in names:
                shift_schedule.loc[name, day] = shift_type
                
        shift_schedule[day] = shift_schedule[day].fillna('休み')
    return shift_schedule

# GUI用
def select_file():
    # ファイル選択ダイアログを開いてファイルパスを取得する関数
    global file_path, generate_button
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_label.config(text=file_path)
        generate_button.config(state='normal')
    else:
        file_label.config(text="ファイルが選択されていません")
        generate_button.config(state='disabled')

def display_shift_schedule():
    # グローバル変数を宣言
    global file_path, shift_schedule
    try:
        shift_preferences = pd.read_csv(file_path)
        shift_schedule = create_shift_schedule(shift_preferences)  # この変数をグローバルに設定
        # 結果をテキストエリアに表示
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, shift_schedule.to_string())
        export_button.config(state='normal')
    except Exception as e:
        messagebox.showerror("エラー", str(e))
        export_button.config(state='disabled')


def export_shift_schedule():
    # グローバル変数を宣言
    global file_path, shift_schedule
    # exportの処理はここで完結するようにします
    if shift_schedule is not None:
        output_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_path:
            try:
                shift_schedule.to_csv(output_path, index=False)
                messagebox.showinfo("成功", "シフトスケジュールがエクスポートされました。")
            except Exception as e:
                messagebox.showerror("エラー", str(e))

# ここからGUIの起動コード
root = tk.Tk()
root.title("シフトスケジュール生成器")

# ファイル選択ボタン
file_button = tk.Button(root, text="CSVファイルを選択", command=select_file)
file_button.pack()

# 選択したファイルのラベル
file_label = tk.Label(root, text="ファイルが選択されていません")
file_label.pack()

# シフト生成ボタン（初期状態は無効）
generate_button = tk.Button(root, text="シフトスケジュールを生成", command=display_shift_schedule, state='disabled')
generate_button.pack()

# 結果表示エリア
result_text = tk.Text(root, height=45, width=150)
result_text.pack()

# エクスポートボタン（初期状態は無効）
export_button = tk.Button(root, text="シフトスケジュールをエクスポート", command=export_shift_schedule, state='disabled')
export_button.pack()

# メインループ
root.mainloop()

# # シフトスケジュールを作成
# shift_schedule = create_shift_schedule(shift_preferences)

# # CSVファイルとしてシフトスケジュールを保存する
# output_path = './output/shift_schedule.csv'
# shift_schedule.to_csv(output_path)

# # 結果を確認
# shift_schedule.head()
