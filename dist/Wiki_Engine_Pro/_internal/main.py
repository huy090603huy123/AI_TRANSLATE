# main.py
import streamlit as st
import os
import re
import pandas as pd
import concurrent.futures
import google.generativeai as genai
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from gspread.cell import Cell

# Import thư viện giao diện Windows (Chỉ dùng để chọn Folder Output)
import tkinter as tk
from tkinter import filedialog

# Import Modules
from config import DEFAULT_API_KEY, DEFAULT_SHEET_URL, CUSTOM_CSS
from modules.scraper import extract_article_content
from modules.ai_processor import translate_simple, analyze_header, format_body_chunk
from modules.document_gen import create_final_docx
from modules.utils import sanitize_filename, split_text

# --- Thư viện Google Sheet ---
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.error("Chưa cài thư viện gspread!")

# ======================================================
# CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ======================================================
# Lấy đường dẫn thư mục hiện tại chứa file main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Mặc định file credentials.json PHẢI nằm ở đây
CRED_FILE_PATH = os.path.join(BASE_DIR, "credentials.json")

# ======================================================
# HÀM HỖ TRỢ CHỌN THƯ MỤC (OUTPUT)
# ======================================================
def select_folder():
    """Mở cửa sổ chọn thư mục lưu trữ"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(master=root)
        root.destroy()
        return folder_path
    except: return None

# ======================================================
# CẤU HÌNH GIAO DIỆN STREAMLIT
# ======================================================
st.set_page_config(
    page_title="Wiki Processing Unit",
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State ---
# Lưu đường dẫn Output (nếu chưa có thì lấy thư mục hiện tại)
if 'output_path' not in st.session_state:
    st.session_state.output_path = BASE_DIR

# ======================================================
# HÀM WORKER
# ======================================================
def process_url_worker(row_idx, row_data, group_folder_path, group_name_str, api_key, model_name, safety_settings, count_label):
    try:
        link = str(row_data['URL']).strip()
        if not link or link == 'nan':
            return False, "Link rỗng", row_idx, None

        # 1. Cào
        content, msg = extract_article_content(link)
        if not content:
            return False, f"Lỗi cào: {msg}", row_idx, None

        # 2. Dịch
        genai.configure(api_key=api_key)
        model_clean = genai.GenerativeModel(model_name)
        translated_text = translate_simple(content, api_key)
        clean_text = re.sub(r'\[\w+\]', '', translated_text)
        
        # 3. Header
        header_segment = clean_text[:5000]
        analysis_result = analyze_header(model_clean, header_segment, safety_settings)
        detected_name = analysis_result.get("name", group_name_str) or group_name_str
        intro_short = analysis_result.get("intro", "")
        infobox_raw = analysis_result.get("infobox", "")
        
        # 4. Body
        chunks = split_text(clean_text, max_length=6000)
        formatted_body_parts = []
        for i, chunk in enumerate(chunks):
            is_first = (i == 0)
            processed_chunk = format_body_chunk(model_clean, chunk, safety_settings, is_first_chunk=is_first)
            formatted_body_parts.append(processed_chunk)
        
        full_body_text = "\n".join(formatted_body_parts)

        # 5. Save
        safe_filename = sanitize_filename(f"{count_label}. {detected_name}") + ".docx"
        filepath = os.path.join(group_folder_path, safe_filename)
        create_final_docx(filepath, detected_name, intro_short, infobox_raw, full_body_text, link)
        
        return True, "Complete", row_idx, safe_filename

    except Exception as e:
        return False, f"Error: {str(e)}", row_idx, None

# ======================================================
# MAIN UI
# ======================================================
def main():
    # --- Sidebar ---
    with st.sidebar:
        st.markdown('<div class="logo-text">⚡ WIKI ENGINE PRO</div>', unsafe_allow_html=True)
        
        st.markdown("### ⚙️ KẾT NỐI")
        
        # 1. API Key
        api_key = st.text_input("API KEY", value=DEFAULT_API_KEY, type="password")
        
        # 2. Sheet URL
        sheet_url = st.text_input("SHEET URL", value=DEFAULT_SHEET_URL)
        
        st.markdown("### 🧠 CẤU HÌNH")
        model_name = st.text_input("MODEL SLUG", value="gemini-2.5-flash")
        
        # 3. Output Folder Picker (Vẫn giữ nút chọn Folder)
        st.markdown('<label style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 0.5px;">OUTPUT DIRECTORY</label>', unsafe_allow_html=True)
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            save_dir = st.text_input("path_display", value=st.session_state.output_path, label_visibility="collapsed")
            if save_dir != st.session_state.output_path:
                st.session_state.output_path = save_dir
        with col2:
            if st.button("📂", key="btn_out", help="Chọn thư mục lưu"):
                selected_folder = select_folder()
                if selected_folder:
                    st.session_state.output_path = selected_folder
                    st.rerun()

        # Hiển thị trạng thái file credentials (Chỉ báo, không cho sửa)
        cred_exists = os.path.exists(CRED_FILE_PATH)
        if cred_exists:
            st.success("🔑 Credentials: Đã tìm thấy")
        else:
            st.error("❌ Credentials: Không tìm thấy file")

        max_workers = st.slider("THREADS", 1, 10, 4)
        
        st.markdown("---")
        start_btn = st.button("BẮT ĐẦU XỬ LÝ")
        st.caption("SERVER STATUS: 🟢 Online")

    # --- Main Area ---
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="margin:0;">TERMINAL OUTPUT</h2>
            <span style="color: #64748b; font-family: 'JetBrains Mono'; font-size: 12px;">v2.7.0 release</span>
        </div>
    """, unsafe_allow_html=True)

    terminal_placeholder = st.empty()

    if not start_btn:
        # Màn hình chờ
        cred_msg = f"<span class='success-text'>DETECTED ({os.path.basename(CRED_FILE_PATH)})</span>" if cred_exists else "<span class='error-text'>MISSING (Please add credentials.json)</span>"
        
        terminal_placeholder.markdown(f"""
            <div class="terminal-box">
                <div class="terminal-header">
                    <span class="dot" style="background:#ef4444"></span>
                    <span class="dot" style="background:#f59e0b"></span>
                    <span class="dot" style="background:#10b981"></span>
                    <span style="margin-left: 10px;">bash --login</span>
                </div>
                <div style="opacity: 0.8;">
                    <span class="success-text">➜</span> <span class="info-text">~</span> System initialized.<br>
                    <span class="success-text">➜</span> <span class="info-text">~</span> Auto-Auth: {cred_msg}<br>
                    <span class="success-text">➜</span> <span class="info-text">~</span> Save Path: <span style="color: #f59e0b;">{st.session_state.output_path}</span><br>
                    <br>
                    <span style="color: #475569;">// Sẵn sàng. Nhấn BẮT ĐẦU XỬ LÝ để chạy.</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- LOGIC CHẠY ---
        log_lines = [f"<span class='success-text'>➜</span> Starting Engine..."]
        
        def render_terminal(logs):
            log_content = "<br>".join(logs[-18:]) 
            terminal_placeholder.markdown(f"""
                <div class="terminal-box">
                    <div class="terminal-header">
                        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                        <span style="margin-left: 10px;">running...</span>
                    </div>
                    {log_content}
                    <br><span class="success-text">➜</span> <span class="info-text">processing</span><span class="blink">_</span>
                </div>
                <style>.blink {{animation: blinker 1s linear infinite;}} @keyframes blinker {{50% {{opacity: 0;}}}}</style>
            """, unsafe_allow_html=True)
            print(logs[-1]) 

        render_terminal(log_lines)
        progress_bar = st.progress(0)

        # 1. Validation
        if not api_key:
            log_lines.append("<span class='error-text'>[ERROR] API Key is missing.</span>")
            render_terminal(log_lines)
            return

        if not os.path.exists(CRED_FILE_PATH):
            log_lines.append(f"<span class='error-text'>[FATAL ERROR] Cannot find 'credentials.json'.</span>")
            log_lines.append(f"<span class='info-text'>➤ Please copy your JSON key to: {BASE_DIR}</span>")
            render_terminal(log_lines)
            return

        try:
            # 2. Connect Google
            log_lines.append(f"<span class='info-text'>ℹ</span> Authenticating using local file...")
            render_terminal(log_lines)
            
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(CRED_FILE_PATH, scopes=scope)
            client = gspread.authorize(creds)
            
            sheet = client.open_by_url(sheet_url)
            worksheet = sheet.get_worksheet(0)
            log_lines.append(f"<span class='success-text'>✔</span> Connected: <b>{sheet.title}</b>")
            render_terminal(log_lines)

            # 3. Setup Folder Output (Lấy từ Input người dùng chọn)
            timestamp_folder = f"Wiki_Build_{datetime.now().strftime('%Y%m%d_%H%M')}"
            final_save_path = os.path.join(st.session_state.output_path, timestamp_folder)
            os.makedirs(final_save_path, exist_ok=True)
            log_lines.append(f"<span class='info-text'>[DIR]</span> Creating output at: {final_save_path}")

            # 4. Processing
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            try:
                status_cell = worksheet.find("Trạng thái")
                status_col_idx = status_cell.col
            except:
                log_lines.append("<span class='error-text'>[ERROR] Column 'Trạng thái' not found in Sheet.</span>")
                render_terminal(log_lines)
                return

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            grouped = df.groupby('Tên File')
            total_groups = len(grouped)
            processed_groups = 0

            for group_name, group_data in grouped:
                group_name_str = str(group_name).strip()
                if not group_name_str: continue

                pending_data = group_data[group_data['Trạng thái'].str.strip().str.upper() != 'DONE']
                if pending_data.empty:
                    processed_groups += 1
                    continue 

                log_lines.append(f"<span class='info-text'>➤</span> Group: <b>{group_name_str}</b>")
                render_terminal(log_lines)
                
                group_folder_path = os.path.join(final_save_path, sanitize_filename(group_name_str))
                os.makedirs(group_folder_path, exist_ok=True)
                
                batch_cells_update = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures_map = {}
                    count_link = 0
                    for idx, row in pending_data.iterrows():
                        count_link += 1
                        future = executor.submit(
                            process_url_worker, 
                            idx, row, group_folder_path, group_name_str, 
                            api_key, model_name, safety_settings, count_link
                        )
                        futures_map[future] = row['URL']
                    
                    for future in concurrent.futures.as_completed(futures_map):
                        url = futures_map[future]
                        success, msg, row_idx, fname = future.result()
                        
                        if success:
                            log_lines.append(f"&nbsp;&nbsp;<span class='success-text'>+</span> Saved: {fname}")
                            batch_cells_update.append(Cell(row=row_idx + 2, col=status_col_idx, value="DONE"))
                        else:
                            log_lines.append(f"&nbsp;&nbsp;<span class='error-text'>x</span> Fail: {msg}")
                        render_terminal(log_lines)

                if batch_cells_update:
                    worksheet.update_cells(batch_cells_update)
                
                processed_groups += 1
                progress_bar.progress(processed_groups / total_groups)
            
            log_lines.append(f"<br><span class='success-text'>✔ DONE.</span>")
            render_terminal(log_lines)
            st.balloons()

        except Exception as e:
            log_lines.append(f"<span class='error-text'>[FATAL]</span> {str(e)}")
            render_terminal(log_lines)

if __name__ == "__main__":
    main()