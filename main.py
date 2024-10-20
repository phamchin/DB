import csv
import os
import re

# Directory
input_folder = r"./DB files"
temp_folder = r"./Temp"
output_folder = r"./Output"
normalized_csv_folder = r"./Normalized_csv_files"


# Xử lý txt to csv

# Hàm dọn dẹp file txt
def process_txt_file(input_file_path, output_file_path, separator=','):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        current_line = ""

        for line in infile:
            # Loại bỏ ký tự NULL
            line = line.replace('\x00', '')
            # Kiểm tra nếu dòng bắt đầu bằng ký tự '/'
            if line.startswith('/'):
                # Nếu có một dòng hiện tại, lưu nó trước khi bắt đầu một dòng mới
                if current_line:
                    # Loại bỏ khoảng trắng thừa xung quanh dấu phẩy
                    current_line = re.sub(r'\s*,\s*', ',', current_line.strip())
                    # Thay thế các khoảng trắng liên tiếp bằng dấu phẩy hoặc dấu cách
                    cleaned_line = re.sub(r'\s+', separator, current_line)
                    outfile.write(cleaned_line + '\n')
                # Bắt đầu một dòng mới
                current_line = line.strip()
            else:
                # Nếu không, nối dòng hiện tại với dòng trước đó
                current_line += " " + line.strip()

        # Đừng quên lưu dòng cuối cùng
        if current_line:
            # Loại bỏ khoảng trắng thừa xung quanh dấu phẩy
            current_line = re.sub(r'\s*,\s*', ',', current_line.strip())
            # Thay thế các khoảng trắng liên tiếp bằng dấu phẩy hoặc dấu cách
            cleaned_line = re.sub(r'\s+', separator, current_line)
            outfile.write(cleaned_line + '\n')

# Hàm lọc toàn bộ các file txt trong thư mục
# Hàm gọi hàm dọn dẹp và ghi lại vào thư mục temp
def process_temp_directory(input_directory, output_directory, separator=','):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):  # Chỉ xử lý các tệp .txt
            input_file_path = os.path.join(input_directory, filename)
            output_file_name = os.path.splitext(filename)[0] + '.csv'
            output_file_path = os.path.join(output_directory, output_file_name)
            process_txt_file(input_file_path, output_file_path, separator)

# Convert txt to CSV and save to Temp
process_temp_directory(input_folder, temp_folder)

# ======================== Chạy ổn tại đây ========================


# Hàm chuẩn hoá chuẩn hóa số lượng cột file csv
def normalize_csv(input_file, output_file_path):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    
    max_columns = max(len(row) for row in rows)
    normalized_rows = [row + [''] * (max_columns - len(row)) for row in rows]

    with open(output_file_path, 'w', newline='') as outfile:  # Sử dụng output_file_path
        writer = csv.writer(outfile)
        writer.writerows(normalized_rows)

# Hàm Đọc các file csv chưa chuẩn hoá, rồi lưu vào thư mục chuẩn hoá
def normalizing_csv_files(input_csv_folder, output_normalized_csv_folder):
    # Kiểm tra nếu chưa tồn tại thư mục chứa output các file csv được chuẩn hoá thì tạo nó.
    if not os.path.exists(output_normalized_csv_folder):
        os.makedirs(output_normalized_csv_folder)

    if not os.path.exists(input_csv_folder):
        print("There is no csv file found in Temp")

    for filename in os.listdir(input_csv_folder):
        if filename.endswith('.csv'):
            input_file_path = os.path.join(input_csv_folder, filename)
            output_file_name = os.path.splitext(filename)[0] + '_normalized.csv'
            output_file_path = os.path.join(output_normalized_csv_folder, output_file_name)
            normalize_csv(input_file_path, output_file_path)

normalizing_csv_files(temp_folder, normalized_csv_folder)


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

#
# df.to_csv('output.csv', index=False)
# df_tx.to_csv('df_tx_hex.csv', index=False)
#
# def matches_pattern(value):
#     pattern = r"^/tx:\d+/\d+W/stepAtt/freqTab$"
#     return re.match(pattern, value) is not None
#
# # Lọc các hàng có cột đầu tiên khớp với mẫu
# matching_rows = df_tx[df_tx[0].apply(matches_pattern)]
#
# # Biến đổi giá trị hexa sang dạng số thập phân
# def hex_to_dec(hex_value):
#     return int(hex_value, 16)
#
# # Duyệt qua các hàng khớp và biến đổi giá trị hexa
# for index, row in matching_rows.iterrows():
#     df_tx.loc[index] = [hex_to_dec(val) if isinstance(val, str) and val.startswith('0x') else val for val in row]
#
# df_tx.to_csv('df_tx_dec.csv', index=False)
