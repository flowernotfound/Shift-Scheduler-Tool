import pandas as pd
import random
import os

# CSVファイルのパス
file_path = './input/test.csv'

# CSVファイルの読み込み
try:
    # Attempt to read the CSV with default encoding
    shift_preferences = pd.read_csv(file_path)
except UnicodeDecodeError:
    # If there's an encoding error, try a common alternative encoding
    shift_preferences = pd.read_csv(file_path, encoding='utf-8-sig')

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

# シフトスケジュールを作成
shift_schedule = create_shift_schedule(shift_preferences)

# CSVファイルとしてシフトスケジュールを保存する
output_path = './output/shift_schedule.csv'
shift_schedule.to_csv(output_path)

# 結果を確認
shift_schedule.head()