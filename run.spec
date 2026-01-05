# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

# --- 1. TÌM THƯ VIỆN DOCX ---
import docx
docx_path = os.path.dirname(docx.__file__)

datas = []
binaries = []
hiddenimports = []

# --- 2. COPY DỮ LIỆU CẦN THIẾT ---
# Copy thư viện docx
datas += [(docx_path, 'docx')] 

# Nhúng file code và cấu hình
datas += [('main.py', '.'), ('config.py', '.')]

# Nhúng file credentials.json (nếu bạn muốn đóng gói luôn key)
# Nếu không muốn đóng gói key thì XÓA dòng dưới này đi
datas += [('credentials.json', '.')]

# Copy thư mục modules
datas += [('modules', 'modules')]

# --- 3. GOM CÁC THƯ VIỆN (Thêm tkinter vào đây nếu cần, nhưng quan trọng nhất là hiddenimports) ---
libs_to_collect = [
    'streamlit',
    'cloudscraper',
    'trafilatura',
    'htmldate',
    'courlan',
    'google.generativeai',
    'gspread',
    'lxml',
    'pandas',
    'numpy'
]

print("--- ĐANG GOM DỮ LIỆU THƯ VIỆN ---")
for lib in libs_to_collect:
    try:
        datas += copy_metadata(lib)
        tmp_ret = collect_all(lib)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f" ! Cảnh báo: {lib} - {e}")

# --- 4. IMPORT ẨN (QUAN TRỌNG: Đã thêm tkinter vào đây) ---
# PyInstaller không tự tìm thấy import trong main.py, nên phải khai báo ở đây
hiddenimports += [
    'docx', 
    'docx.document',
    'docx.shared',
    'gzip',
    'encodings',
    'tkinter',              # <--- MỚI THÊM
    'tkinter.filedialog'    # <--- MỚI THÊM
]

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Wiki_Engine_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Wiki_Engine_Pro',
)