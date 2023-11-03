import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class ShiftSchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('シフトスケジューラ')
        self.geometry('800x600')
        self.create_widgets()
        self.shift_schedule = None

    def create_widgets(self):
        self.btn_load = tk.Button(self, text='ファイルを選択', command=self.load_file)
        self.btn_load.pack(pady=10)
        self.preview_frame = ttk.Frame(self)
        self.preview_frame.pack(fill='both', expand=True)
        self.preview_tree = ttk.Treeview(self.preview_frame)
        self.preview_tree.pack(side='left', fill='both', expand=True)
        self.preview_scrollbar = ttk.Scrollbar(self.preview_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_scrollbar.pack(side='right', fill='y')
        self.preview_tree.configure(yscrollcommand=self.preview_scrollbar.set)

        self.btn_assign = tk.Button(self, text='シフト割り当て開始', state='disabled', command=self.assign_shifts)
        self.btn_assign.pack(pady=10)

        self.schedule_frame = ttk.Frame(self)
        self.schedule_frame.pack(fill='both', expand=True)
        self.schedule_tree = ttk.Treeview(self.schedule_frame)
        self.schedule_tree.pack(side='left', fill='both', expand=True)
        self.schedule_scrollbar = ttk.Scrollbar(self.schedule_frame, orient='vertical', command=self.schedule_tree.yview)
        self.schedule_scrollbar.pack(side='right', fill='y')
        self.schedule_tree.configure(yscrollcommand=self.schedule_scrollbar.set)

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
            df = pd.read_csv(file_path)

            for i in self.preview_tree.get_children():
                self.preview_tree.delete(i)

            self.preview_tree['columns'] = list(df.columns)
            self.preview_tree['show'] = 'headings'
            for column in df.columns:
                self.preview_tree.heading(column, text=column)

            for _, row in df.iterrows():
                self.preview_tree.insert('', 'end', values=list(row))

            self.btn_assign['state'] = 'normal'

        except Exception as e:
            messagebox.showerror('エラー', f'ファイルを読み込めませんでした: {e}')

    def assign_shifts(self):
        try:
            columns = self.preview_tree['columns']
            data = []
            for item in self.preview_tree.get_children():
                data.append(self.preview_tree.item(item, 'values'))
            shift_preferences_df = pd.DataFrame(data, columns=columns)
            
            self.shift_schedule = self.calculate_shift_schedule(shift_preferences_df)
            
            if self.shift_schedule is not None:
                self.show_schedule()
        except Exception as e:
            messagebox.showerror('エラー', f'シフト割り当てに失敗しました: {e}')
    
    def calculate_shift_schedule(self, shift_preferences_df):
        shift_preferences_df = shift_preferences_df.applymap(str)

        applicants = shift_preferences_df['名前'].tolist()
        dates = shift_preferences_df.columns[2:]

        shift_schedule = {name: [] for name in applicants}
        
        for date in dates:
            daily_preferences = shift_preferences_df[['名前', date]].set_index('名前')
            
            early_count = (daily_preferences[date] == '早番').sum()
            late_count = (daily_preferences[date] == '遅番').sum()
            all_day_count = (daily_preferences[date] == '終日可能').sum()
            
            early_applicants = daily_preferences[daily_preferences[date] == '早番'].index.tolist()
            late_applicants = daily_preferences[daily_preferences[date] == '遅番'].index.tolist()
            all_day_applicants = daily_preferences[daily_preferences[date] == '終日可能'].index.tolist()
            
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
            
            for name in applicants:
                if len(shift_schedule[name]) < len(shift_schedule[applicants[0]]):
                    shift_schedule[name].append('休み')
        return pd.DataFrame.from_dict(shift_schedule, orient='index', columns=dates)

    def show_schedule(self):
        for i in self.schedule_tree.get_children():
            self.schedule_tree.delete(i)

        self.schedule_tree['columns'] = list(self.shift_schedule.columns)
        self.schedule_tree['show'] = 'headings'
        for column in self.shift_schedule.columns:
            self.schedule_tree.heading(column, text=column)

        for _, row in self.shift_schedule.iterrows():
            self.schedule_tree.insert('', 'end', values=list(row))
        self.btn_save['state'] = 'normal'

    def save_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv')],
            title='保存するファイル名を選択してください'
        )
        if file_path:
            self.shift_schedule.to_csv(file_path, index=False)
            messagebox.showinfo('成功', 'CSVファイルに保存しました！')

app = ShiftSchedulerApp()
app.mainloop()