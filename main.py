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
    st.error("Chưa cài thư viện gspread! Chạy: pip install gspread google-auth")

# ======================================================
# CẤU HÌNH GIAO DIỆN WEB
# ======================================================
st.set_page_config(
    page_title="Wiki Intelligence Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ======================================================
# HÀM WORKER (ĐỂ TẠI MAIN ĐỂ DỄ GỌI STREAMLIT LOG)
# ======================================================
def process_url_worker(row_idx, row_data, group_folder_path, group_name_str, api_key, model_name, safety_settings, count_label):
    try:
        link = str(row_data['URL']).strip()
        if not link or link == 'nan':
            return False, "Link rỗng", row_idx, None

        # 1. Cào dữ liệu
        content, msg = extract_article_content(link)
        if not content:
            return False, f"Lỗi cào dữ liệu: {msg}", row_idx, None

        # 2. Dịch & Chuẩn hóa
        genai.configure(api_key=api_key)
        model_clean = genai.GenerativeModel(model_name)
        
        translated_text = translate_simple(content, api_key)
        clean_text = re.sub(r'\[\w+\]', '', translated_text)
        
        # 3. Phân tích Header
        header_segment = clean_text[:5000]
        analysis_result = analyze_header(model_clean, header_segment, safety_settings)
        
        detected_name = analysis_result.get("name", group_name_str)
        if not detected_name: detected_name = group_name_str
        intro_short = analysis_result.get("intro", "")
        infobox_raw = analysis_result.get("infobox", "")
        
        # 4. Format Body
        chunks = split_text(clean_text, max_length=6000)
        formatted_body_parts = []
        
        for i, chunk in enumerate(chunks):
            is_first = (i == 0)
            processed_chunk = format_body_chunk(model_clean, chunk, safety_settings, is_first_chunk=is_first)
            formatted_body_parts.append(processed_chunk)
        
        full_body_text = "\n".join(formatted_body_parts)

        # 5. Lưu File
        safe_filename = sanitize_filename(f"{count_label}. {detected_name}") + ".docx"
        filepath = os.path.join(group_folder_path, safe_filename)
        
        create_final_docx(filepath, detected_name, intro_short, infobox_raw, full_body_text, link)
        
        return True, "Thành công", row_idx, safe_filename

    except Exception as e:
        return False, f"Exception: {str(e)}", row_idx, None

# ======================================================
# MAIN UI
# ======================================================
def main():
    st.markdown('<p class="main-title">TOOL WIKI (Modular Ver)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Hệ thống Xử lý & Chuẩn hóa Dữ liệu Đa tầng</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ CONTROL PANEL")
        st.markdown("---")
        
        with st.expander("🔑 Cấu hình Kết nối", expanded=True):
            api_key = st.text_input("Gemini API Key", value=DEFAULT_API_KEY, type="password")
            sheet_url = st.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL)
        
        with st.expander("🧠 Cấu hình Xử lý", expanded=True):
            model_name = st.text_input("Model Chuẩn hóa", value="gemini-2.5-flash")
            current_dir = os.getcwd()
            save_dir = st.text_input("Thư mục lưu trữ (Local)", value=current_dir)
            max_workers = st.slider("Số luồng (Threads)", 1, 10, 4)
        
        st.markdown("---")
        start_btn = st.button("KHỞI CHẠY HỆ THỐNG")

    if start_btn:
        if not api_key:
            st.error("⚠️ Thiếu API Key!")
            return
        
        cred_path = "credentials.json"
        if not os.path.exists(cred_path):
            st.error("❌ Lỗi: Không tìm thấy file 'credentials.json'.")
            return

        st.markdown("### 📡 TRẠNG THÁI HOẠT ĐỘNG")
        status_container = st.status("Đang khởi tạo kết nối...", expanded=True)
        progress_bar = st.progress(0)
        
        def log(msg):
            timestamp = datetime.now().strftime('%H:%M:%S')
            status_container.markdown(f"⏱️ `{timestamp}` | {msg}")
            print(f"[{timestamp}] {msg}")

        try:
            # Connect Sheet
            log("☁️ Đang kết nối Google API...")
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(cred_path, scopes=scope)
            client = gspread.authorize(creds)
            
            try:
                sheet = client.open_by_url(sheet_url)
                worksheet = sheet.get_worksheet(0)
                log(f"✅ Kết nối Sheet: **{sheet.title}**")
            except Exception as e:
                status_container.update(label="❌ Lỗi kết nối Sheet!", state="error")
                st.error(f"Chi tiết: {e}")
                return

            data = worksheet.get_all_records()
            df = pd.DataFrame(data)

            # Create Folder
            timestamp_folder = f"Wiki_Final_{datetime.now().strftime('%Y%m%d_%H%M')}"
            save_folder = os.path.join(save_dir, timestamp_folder)
            os.makedirs(save_folder, exist_ok=True)
            log(f"📂 Thư mục lưu: `{timestamp_folder}`")

            status_cell = worksheet.find("Trạng thái")
            status_col_idx = status_cell.col

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
                    progress_bar.progress(processed_groups / total_groups)
                    continue 

                status_container.update(label=f"▶️ Xử lý: **{group_name_str}** ({len(pending_data)} links)", state="running")
                log(f"🔹 Nhóm: `{group_name_str}`")
                
                group_folder_path = os.path.join(save_folder, sanitize_filename(group_name_str))
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
                            log(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ Xong: {fname}")
                            batch_cells_update.append(Cell(row=row_idx + 2, col=status_col_idx, value="DONE"))
                        else:
                            log(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ Lỗi ({url}): {msg}")

                if batch_cells_update:
                    worksheet.update_cells(batch_cells_update)
                    log(f"&nbsp;&nbsp;&nbsp;&nbsp;🔄 Đã cập nhật Sheet ({len(batch_cells_update)} dòng).")

                processed_groups += 1
                progress_bar.progress(processed_groups / total_groups)
            
            status_container.update(label="✅ HOÀN TẤT!", state="complete", expanded=False)
            st.success("Xử lý xong toàn bộ.")
            st.balloons()

        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    main()