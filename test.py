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
        # プレビューからデータを取得
        try:
            # ツリービューの内容をDataFrameに変換
            columns = self.preview_tree['columns']
            data = []
            for item in self.preview_tree.get_children():
                data.append(self.preview_tree.item(item, 'values'))
            shift_preferences_df = pd.DataFrame(data, columns=columns)
            
            # シフトスケジュールを計算
            self.shift_schedule = self.calculate_shift_schedule(shift_preferences_df)
            
            # シフトスケジュールを表示
            if self.shift_schedule is not None:
                self.show_schedule()
        except Exception as e:
            messagebox.showerror('エラー', f'シフト割り当てに失敗しました: {e}')
    
    def calculate_shift_schedule(self, shift_preferences_df):
        # CSVから読み込んだデータは文字列として扱われるので、適切な形式に変換する
        shift_preferences_df = shift_preferences_df.applymap(str)

        # 応募者名と日付カラムを取得
        applicants = shift_preferences_df['名前'].tolist()
        dates = shift_preferences_df.columns[2:]  # 最初の2カラムはタイムスタンプと名前

        # 初期化
        shift_schedule = {name: [] for name in applicants}
        
        # 各日付ごとにシフトを割り当てる
        for date in dates:
            # その日の希望を取得
            daily_preferences = shift_preferences_df[['名前', date]].set_index('名前')
            
            # 早番、遅番、終日可能、休みの数をカウント
            early_count = (daily_preferences[date] == '早番').sum()
            late_count = (daily_preferences[date] == '遅番').sum()
            all_day_count = (daily_preferences[date] == '終日可能').sum()
            
            # 希望者リストを作成
            early_applicants = daily_preferences[daily_preferences[date] == '早番'].index.tolist()
            late_applicants = daily_preferences[daily_preferences[date] == '遅番'].index.tolist()
            all_day_applicants = daily_preferences[daily_preferences[date] == '終日可能'].index.tolist()
            
            # 早番と遅番を割り当てる
            for _ in range(2):
                if early_applicants:
                    chosen_one = early_applicants.pop(0)
                    shift_schedule[chosen_one].append('早番')
                elif all_day_applicants:
                    chosen_one = all_day_applicants.pop(0)
                    shift_schedule[chosen_one].append('早番')
                
                if late_applicants:
                    chosen_one = late_applicants.pop(0)
                    shift_schedule[chosen_one].append('遅番')
                elif all_day_applicants:
                    chosen_one = all_day_applicants.pop(0)
                    shift_schedule[chosen_one].append('遅番')
            
            # 未割り当ての人に休みを割り当てる
            for name in applicants:
                if len(shift_schedule[name]) < len(shift_schedule[applicants[0]]):
                    shift_schedule[name].append('休み')

        # データフレームに変換して返す
        return pd.DataFrame.from_dict(shift_schedule, orient='index', columns=dates)



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