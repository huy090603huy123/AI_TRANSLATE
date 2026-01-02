# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

# --- 1. HÀM TÌM ĐƯỜNG DẪN THƯ VIỆN DOCX ---
# Chúng ta sẽ tìm xem folder 'docx' thật sự nằm ở đâu trong máy bạn
import docx
docx_path = os.path.dirname(docx.__file__)
print(f"!!! ĐÃ TÌM THẤY THƯ VIỆN DOCX TẠI: {docx_path}")

# --- KHỞI TẠO BIẾN ---
datas = []
binaries = []
hiddenimports = []

# --- 2. ÉP BUỘC COPY THƯ VIỆN DOCX VÀO TRONG EXE ---
# Cú pháp: (đường_dẫn_gốc, đường_dẫn_trong_exe)
datas += [(docx_path, 'docx')] 

# --- 3. GOM CÁC THƯ VIỆN KHÁC ---
libs_to_collect = [
    'streamlit',
    'cloudscraper',
    'trafilatura',
    'htmldate',
    'courlan',
    'google.generativeai',
    'gspread',
    # 'docx', -> KHÔNG gom tự động nữa, đã copy thủ công ở trên
    'lxml',
    'pandas',
    'numpy'
]

print("--- ĐANG GOM DỮ LIỆU CÁC THƯ VIỆN KHÁC ---")
for lib in libs_to_collect:
    try:
        # Lấy metadata (quan trọng cho google-ai và streamlit)
        datas += copy_metadata(lib)
        
        # Gom file và code
        tmp_ret = collect_all(lib)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
        print(f" > OK: {lib}")
    except Exception as e:
        print(f" ! Cảnh báo: {lib} - {e}")

# --- 4. NHÚNG CODE CHÍNH ---
datas += [('wiki_tool.py', '.')]

# --- 5. IMPORT ẨN (Bắt buộc phải khai báo tên 'docx') ---
hiddenimports += [
    'docx', 
    'docx.document',
    'docx.shared',
    'gzip',
    'encodings'
]

# --- 6. CẤU HÌNH BUILD ---
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Wiki_Tool_Final', # Đổi tên mới
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)