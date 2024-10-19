import pandas as pd
import csv
import re

# Đọc file CSV và chuẩn hóa số lượng cột
def normalize_csv(input_file, output_file):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    
    max_columns = max(len(row) for row in rows)
    normalized_rows = [row + [''] * (max_columns - len(row)) for row in rows]
    
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(normalized_rows)

# Đường dẫn tới file CSV gốc và file CSV đã chuẩn hóa
input_file = r'C:\Users\V220016\Downloads\DB\B20 prod DB.csv'  # Đường dẫn tới file CSV của bạn
normalized_file = r'C:\Users\V220016\Downloads\DB\normalized_csv_file.csv'

# Chuẩn hóa file CSV
normalize_csv(input_file, normalized_file)

# Đọc file CSV đã chuẩn hóa vào DataFrame
df = pd.read_csv(normalized_file, header=None)

# Định nghĩa hàm để phân loại các nhóm
def classify_category(value):
    if value.startswith('/GDpa') or value.startswith('/GMpa'):
        return 'pa'
    elif value.startswith('/tx'):
        return 'tx'
    elif value.startswith('/rx'):
        return 'rx'
    else:
        return 'other'

# Thêm một cột mới 'category' dựa trên giá trị của cột đầu tiên
df['category'] = df[0].apply(classify_category)

# Chia DataFrame thành các DataFrame con dựa trên giá trị của cột 'category'
df_pa = df[df['category'] == 'pa']
df_tx = df[df['category'] == 'tx']
df_rx = df[df['category'] == 'rx']
df_other = df[df['category'] == 'other']

# Loại bỏ cột 'category' nếu không cần thiết
df_pa = df_pa.drop(columns=['category'])
df_tx = df_tx.drop(columns=['category'])
df_rx = df_rx.drop(columns=['category'])
df_other = df_other.drop(columns=['category'])

# In kết quả để kiểm tra
print("DataFrame con chứa PA:")
print(df_pa)


df.to_csv('output.csv', index=False)
df_tx.to_csv('df_tx_hex.csv', index=False)

def matches_pattern(value):
    pattern = r"^/tx:\d+/\d+W/stepAtt/freqTab$"
    return re.match(pattern, value) is not None

# Lọc các hàng có cột đầu tiên khớp với mẫu
matching_rows = df_tx[df_tx[0].apply(matches_pattern)]

# Biến đổi giá trị hexa sang dạng số thập phân
def hex_to_dec(hex_value):
    return int(hex_value, 16)

# Duyệt qua các hàng khớp và biến đổi giá trị hexa
for index, row in matching_rows.iterrows():
    df_tx.loc[index] = [hex_to_dec(val) if isinstance(val, str) and val.startswith('0x') else val for val in row]

df_tx.to_csv('df_tx_dec.csv', index=False)
