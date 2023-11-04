import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import os   

# メインウィンドウの作成
root = tk.Tk()
root.title("シフトスケジュール作成ツール")

# ファイルパスラベル（先にこれを定義します）
file_path_label = tk.Label(root, text="ファイルが選択されていません")
file_path_label.pack()

def select_file():
    # ファイル選択ダイアログを表示
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        # 選択したファイルの名前を抽出し、ラベルに表示
        filename = os.path.basename(file_path)
        file_path_label.config(text=filename)

def start_shift_assignment():
    # シフト割り当てを開始する
    # ここにシフト割り当てのコードを実装する

def save_results():
    # 結果をCSVとして保存する
    # ここに保存機能のコードを実装する

def exit_application():
    # アプリケーションを終了する
    root.destroy()


# ファイル選択ボタン
select_file_button = tk.Button(root, text="ファイルを選択", command=select_file)
select_file_button.pack()

# シフト割り当て開始ボタン
start_button = tk.Button(root, text="シフト割り当て開始", command=start_shift_assignment)
start_button.pack()

# 結果を保存ボタン
save_button = tk.Button(root, text="結果を保存", command=save_results)
save_button.pack()

# 終了ボタン
exit_button = tk.Button(root, text="終了", command=exit_application)
exit_button.pack()

# イベントループ
root.mainloop()
