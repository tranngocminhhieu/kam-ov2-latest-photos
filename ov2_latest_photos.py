import os
import shutil
import glob
import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore')
from tqdm.contrib import tzip
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from pyfiglet import figlet_format
import zipfile

def unzip_file(zip_file_path):
    try:
        # Lấy đường dẫn của thư mục chứa tệp ZIP
        destination_folder = os.path.dirname(zip_file_path)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Giải nén tất cả các tệp trong ZIP vào thư mục chứa nó
            zip_ref.extractall(destination_folder)

        # print(f"Đã giải nén tệp '{os.path.basename(zip_file_path)}' thành công vào '{destination_folder}'.")
    except Exception as e:
        print(f"Error: {e}")

def copy_file(source_path, destination_folder, rename=None):
    try:
        # Lấy tên tệp từ đường dẫn nguồn
        file_name = os.path.basename(source_path)

        # Nếu có tham số rename, sử dụng tên mới
        if rename:
            file_name, file_extension = os.path.splitext(file_name)
            file_name = f"{rename}{file_extension}"

        # Tạo đường dẫn đến thư mục đích
        destination_path = os.path.join(destination_folder, file_name)

        # Copy tệp từ nguồn đến đích
        shutil.copy2(source_path, destination_path)

        # print(f"Tệp '{file_name}' đã được sao chép thành công vào '{destination_folder}'.")
    except Exception as e:
        print(f"Error: {e}")

print(figlet_format("OV2 Latest Photo", width=110))
print('From KAM Analyst\n')

# Support for ask file and folder
root = tk.Tk()
root.withdraw()

input('You need to provide the folder path containing the images, press Enter to start browsing the folder [Enter]:')

original_folder = filedialog.askdirectory()
results_folder = os.path.join(original_folder, 'results')

image_formats = ['*.png', '*.jpeg', '*.jpg']
image_files = []
for image_format in image_formats:
    image_files.extend(glob.glob(os.path.join(original_folder, image_format)))

zip_files = glob.glob(os.path.join(original_folder, '*.zip'))

print(f'Found {len(image_files)} image files and {len(zip_files)} zip files')

if len(zip_files):
    is_unzip = input(f'Do you want to extract zip files? [Y/N]:')
    if is_unzip.lower() in ['y', 'yes', '']:
        for file in tqdm(zip_files):
            unzip_file(file)
        image_files = []
        for image_format in image_formats:
            image_files.extend(glob.glob(os.path.join(original_folder, image_format)))
        print(f'Extraction completed, we have {len(image_files)} image files.')

tracking_ids = []
scan_datetimes = []
numbers = []
for file in image_files:
    matches = re.match(r'.*?\/?(\w+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\d+)\.jpeg$', file)
    tracking_id = matches[1]
    scan_datetime = f'{matches[2].split("_")[0]} {matches[2].split("_")[-1].replace("-", ":")}'
    number = matches[3]
    tracking_ids.append(tracking_id)
    scan_datetimes.append(scan_datetime)
    numbers.append(number)

data = {
    'file':image_files,
    'tracking_id': tracking_ids,
    'scan_datetime': scan_datetimes,
    'number': numbers
}

df = pd.DataFrame(data)
df.scan_datetime = pd.to_datetime(df.scan_datetime)
df.sort_values(by='scan_datetime', ascending=False, inplace=True)
df.drop_duplicates(subset='tracking_id', inplace=True, keep='first')

print(f'Found {df.shape[0]} unique tracking_ids')

# Kiểm tra xem thư mục đích có tồn tại không
if os.path.exists(results_folder):
    shutil.rmtree(results_folder)
os.makedirs(results_folder)

is_rename = input('Do you want to rename the file to tracking_id? [Y/N]:')

for file, tracking_id in tzip(df.file, df.tracking_id):
    if is_rename.lower() in ['y', 'yes', '']:
        name = tracking_id
    else:
        name = None
    copy_file(source_path=file, destination_folder=results_folder, rename=name)

print(f'Done, check the results at ABC {results_folder}')
input('Enter to Exit [Enter]:')

#macOS: pyinstaller --clean --collect-all pyfiglet --onefile ov2_latest_photos.py
#Windows: pyinstaller --clean --collect-all pyfiglet --onefile ov2_latest_photos.py
