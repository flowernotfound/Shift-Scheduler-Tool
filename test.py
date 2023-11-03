import tkinter as tk
import tkinter.messagebox

root = tk.Tk()
root.title("シフトスケジュール生成器")

# ファイル選択ボタン
file_button = tk.Button(root, text="CSVファイルを選択")
file_button.pack()

# 選択したファイルのラベル
file_label = tk.Label(root, text="ファイルが選択されていません")
file_label.pack()

# シフト生成ボタン（初期状態は無効）
generate_button = tk.Button(root, text="シフトスケジュールを生成", state='disabled')
generate_button.pack()

# 結果表示エリア
result_text = tk.Text(root, height=45, width=150)
result_text.pack()

# エクスポートボタン（初期状態は無効）
export_button = tk.Button(root, text="シフトスケジュールをエクスポート", state='disabled')
export_button.pack()

# メインループ
root.mainloop()