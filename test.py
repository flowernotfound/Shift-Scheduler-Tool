import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class ShiftSchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('シフトスケジューラ')
        self.geometry('800x600')

        # UIの構築
        self.create_widgets()

        # シフトスケジュールデータ
        self.shift_schedule = None

    def create_widgets(self):
        # ファイル選択ボタン
        self.btn_load = tk.Button(self, text='ファイルを選択', command=self.load_file)
        self.btn_load.pack(pady=10)

        # シフト希望データのプレビュー表示
        self.preview_frame = ttk.Frame(self)
        self.preview_frame.pack(fill='both', expand=True)
        self.preview_tree = ttk.Treeview(self.preview_frame)
        self.preview_tree.pack(side='left', fill='both', expand=True)
        self.preview_scrollbar = ttk.Scrollbar(self.preview_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_scrollbar.pack(side='right', fill='y')
        self.preview_tree.configure(yscrollcommand=self.preview_scrollbar.set)

        # シフト割り当てボタン
        self.btn_assign = tk.Button(self, text='シフト割り当て開始', state='disabled', command=self.assign_shifts)
        self.btn_assign.pack(pady=10)

        # シフトスケジュール表示
        self.schedule_frame = ttk.Frame(self)
        self.schedule_frame.pack(fill='both', expand=True)
        self.schedule_tree = ttk.Treeview(self.schedule_frame)
        self.schedule_tree.pack(side='left', fill='both', expand=True)
        self.schedule_scrollbar = ttk.Scrollbar(self.schedule_frame, orient='vertical', command=self.schedule_tree.yview)
        self.schedule_scrollbar.pack(side='right', fill='y')
        self.schedule_tree.configure(yscrollcommand=self.schedule_scrollbar.set)

        # CSVとして保存ボタン
        self.btn_save = tk.Button(self, text='CSVとして保存', state='disabled', command=self.save_to_csv)
        self.btn_save.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('CSV Files', '*.csv')],
            title='シフト希望CSVファイルを選択してください'
        )
        if file_path:
            self.load_preview(file_path)

    def load_preview(self, file_path):
        try:
            # CSVファイルを読み込む
            df = pd.read_csv(file_path)

            # プレビューをクリア
            for i in self.preview_tree.get_children():
                self.preview_tree.delete(i)

            # プレビューツリーにカラムをセット
            self.preview_tree['columns'] = list(df.columns)
            self.preview_tree['show'] = 'headings'
            for column in df.columns:
                self.preview_tree.heading(column, text=column)

            # データをプレビューツリーに挿入
            for _, row in df.iterrows():
                self.preview_tree.insert('', 'end', values=list(row))

            # シフト割り当てボタンを有効化
            self.btn_assign['state'] = 'normal'

        except Exception as e:
            messagebox.showerror('エラー', f'ファイルを読み込めませんでした: {e}')

    def assign_shifts(self):
        # ここでシフト割り当てのロジックを実装する
        # 今はダミーデータを生成
        self.shift_schedule = pd.DataFrame({
            'Name': ['田中', '鈴木', '佐藤'],
            '1日': ['早番', '遅番', '休み'],
            '2日': ['遅番', '休み', '早番'],
            # ...他の日付も同様に...
        })
        self.show_schedule()

    def show_schedule(self):
        # シフトスケジュールを表示
        # スケジュールツリーをクリア
        for i in self.schedule_tree.get_children():
            self.schedule_tree.delete(i)

        # スケジュールツリーにカラムをセット
        self.schedule_tree['columns'] = list(self.shift_schedule.columns)
        self.schedule_tree['show'] = 'headings'
        for column in self.shift_schedule.columns:
            self.schedule_tree.heading(column, text=column)

        # データをスケジュールツリーに挿入
        for _, row in self.shift_schedule.iterrows():
            self.schedule_tree.insert('', 'end', values=list(row))

        # CSV保存ボタンを有効化
        self.btn_save['state'] = 'normal'

    def save_to_csv(self):
        # ファイル保存ダイアログを開く
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv')],
            title='保存するファイル名を選択してください'
        )
        if file_path:
            # データフレームをCSVとして保存
            self.shift_schedule.to_csv(file_path, index=False)
            messagebox.showinfo('成功', 'CSVファイルに保存しました！')

# アプリケーションの実行
app = ShiftSchedulerApp()
app.mainloop()