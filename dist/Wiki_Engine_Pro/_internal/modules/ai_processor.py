# modules/ai_processor.py
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import time
from config import MODEL_TRANSLATE

def translate_simple(content_input, api_key):
    """Hàm dịch đơn giản có cơ chế Retry khi hết quota"""
    genai.configure(api_key=api_key)
    
    system_instruction = """
    Bạn là một dịch giả chuyên nghiệp.
    NHIỆM VỤ: Dịch đoạn văn bản sau sang tiếng Việt.
    
    YÊU CẦU CẤU TRÚC (BẮT BUỘC):
    1. Dịch sát nghĩa, KHÔNG TÓM TẮT.
    2. Giữ nguyên định dạng Markdown (#, **, -).
    3. XỬ LÝ TIÊU ĐỀ: 
       - Nếu gặp một dòng văn bản ngắn, đứng riêng biệt (ví dụ: "Background", "Biography", "Season 1"), HÃY BIẾN NÓ THÀNH HEADING (Thêm dấu ## hoặc ### vào trước).
       - Ví dụ: "Background" -> "### Bối cảnh".
       - TUYỆT ĐỐI KHÔNG để in đậm (**Text**), phải dùng Heading (### Text).
    """
    
    config = GenerationConfig(temperature=0.0) 
    model = genai.GenerativeModel(model_name=MODEL_TRANSLATE, system_instruction=system_instruction)

    max_chunk_size = 10000
    chunks = []
    current_chunk = ""
    
    paragraphs = content_input.split('\n')
    for para in paragraphs:
        para = para.strip()
        if not para: continue
        
        if len(current_chunk) + len(para) > max_chunk_size:
            chunks.append(current_chunk)
            current_chunk = para + "\n"
        else:
            current_chunk += para + "\n"
    if current_chunk: chunks.append(current_chunk)

    full_translated_text = ""
    
    for i, chunk in enumerate(chunks):
        for attempt in range(5):
            try:
                prompt = f"Dịch đoạn này:\n\n{chunk}"
                response = model.generate_content(prompt, generation_config=config)
                full_translated_text += response.text + "\n\n"
                time.sleep(1) 
                break 
            except Exception as e:
                # Xử lý lỗi Quota (Logic từ Code 2)
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg:
                    time.sleep(10)
                else:
                    time.sleep(2)
    
    return full_translated_text

def analyze_header(model, text, safety):
    """Phân tích Header Wiki"""
    prompt = """
    Phân tích văn bản và trích xuất dữ liệu theo phong cách Wikipedia.
    
    YÊU CẦU ĐẶC BIỆT:
    1. VIẾT HOA CHỮ CÁI ĐẦU TIÊN cho tất cả Danh Từ Riêng (Tên người, Địa danh, Tên Gia tộc...).
    2. GIỮ NGUYÊN tên gốc tiếng Anh (không dịch nghĩa địa danh nếu đó là tên riêng).
    3. LOẠI BỎ hoàn toàn các số trong ngoặc vuông như [1], [2].
    
    OUTPUT FORMAT (Bắt buộc):
    [NAME_START]
    ...Tên chuẩn (Viết hoa)...
    [NAME_END]
    
    [INTRO_START]
    ...Đoạn giới thiệu ngắn gọn (Viết hoa đúng tên riêng)...
    [INTRO_END]
    
    [INFO_START]
    Tên đầy đủ|...
    Sinh|...
    ...
    [INFO_END]
    """
    try:
        response = model.generate_content(f"{prompt}\n\nNguồn:\n{text}", safety_settings=safety)
        content = response.text
        
        result = {"name": "", "intro": "", "infobox": ""}
        if "[NAME_START]" in content:
            result["name"] = content.split("[NAME_START]")[1].split("[NAME_END]")[0].strip()
        if "[INTRO_START]" in content:
            result["intro"] = content.split("[INTRO_START]")[1].split("[INTRO_END]")[0].strip()
        if "[INFO_START]" in content:
            result["infobox"] = content.split("[INFO_START]")[1].split("[INFO_END]")[0].strip()
        return result
    except: 
        return {"name": "", "intro": "", "infobox": ""}

def format_body_chunk(model, text, safety, is_first_chunk=False):
    """
    Format lại thân bài.
    Sửa đổi: Thêm tham số is_first_chunk để ra lệnh riêng cho đoạn đầu.
    """
    
    # Chỉ dẫn đặc biệt cho đoạn đầu tiên để tránh mất nội dung
    special_instruction = ""
    if is_first_chunk:
        special_instruction = """
        [CỰC KỲ QUAN TRỌNG - CHÚ Ý]:
        - Đây là phần bắt đầu của bài viết. Nó chứa: Giới thiệu (Intro), Tổng quan (Overview), Mô tả nhân vật, và các phần đầu (như Season 1).
        - NHIỆM VỤ: Giữ lại TOÀN BỘ các phần này. KHÔNG ĐƯỢC CẮT BỎ hay TÓM TẮT bất kỳ dòng nào.
        - Nếu thấy tiêu đề "Overview", "Character description", "Season 1"... HÃY ĐỊNH DẠNG NÓ THÀNH HEADING (## hoặc ###).
        - TUYỆT ĐỐI KHÔNG nhảy cóc sang Season 2. Phải dịch từ chữ đầu tiên.
        """

    prompt = f"""
    Bạn là biên tập viên Wikipedia chuyên nghiệp. Nhiệm vụ của bạn là chuẩn hóa định dạng văn bản sau đây.
    
    {special_instruction}
    QUY TẮC BẮT BUỘC:
    1. VIẾT HOA CHỮ CÁI ĐẦU TIÊN cho các Danh Từ Tên Riêng (Tên nhân vật, Địa danh, Sự kiện). 
       - Ví dụ: "vịnh nô lệ" -> "Vịnh Nô Lệ", "cuộc nổi dậy của robert" -> "Cuộc Nổi Dậy của Robert".
    2. GIỮ NGUYÊN trật tự từ và tên gốc của địa danh/tên người (Ví dụ: "King's Landing" giữ nguyên, không dịch là Bến Vua).
    3. LOẠI BỎ SỐ TRONG NGOẶC VUÔNG (Ví dụ xóa [1], [10], [a]).
    4. KHÔNG tự ý tạo Heading nếu văn bản gốc không phải là tiêu đề.
    5. KHÔNG dùng shortcode [amp_spoiler].
    6. In đậm (Bold) các Tên Riêng quan trọng lần đầu xuất hiện hoặc trọng tâm câu.
    7. [QUAN TRỌNG] TUYỆT ĐỐI GIỮ NGUYÊN CẤP ĐỘ HEADING (số lượng dấu #). 
       - Nếu input là "## Tiêu đề" thì Output BẮT BUỘC là "## Tiêu đề" (KHÔNG được đổi thành ###).
       - AI không được tự ý thay đổi cấu trúc cây thư mục của bài viết.
    8. KHÔNG ĐƯỢC chép lại phần "QUY TẮC BẮT BUỘC" này vào kết quả. Chỉ trả về nội dung đã sửa.
    QUY TẮC ĐỊNH DẠNG (BẮT BUỘC):
    1. GIỮ NGUYÊN NỘI DUNG: Không thêm bớt, không tóm tắt. Input có gì, Output phải có đó.
    2. VIẾT HOA TÊN RIÊNG: Các danh từ riêng (Tên người, Địa danh, Sự kiện) phải viết hoa chữ cái đầu.
       - Ví dụ: "king's landing" -> "King's Landing", "stark" -> "Stark".
    3. ĐỊNH DẠNG HEADING:
       - Các dòng tiêu đề (ví dụ: "Overview", "Biography", "Season 1") phải chuyển thành Markdown Heading (thêm dấu ## hoặc ### phía trước).
       - KHÔNG để tiêu đề ở dạng in đậm (**Text**).
    4. SỐ THAM CHIẾU: Loại bỏ sạch các số trong ngoặc vuông (ví dụ [1], [2], [a]).
    5. CẤU TRÚC: Giữ nguyên thứ tự đoạn văn.
    6. [QUAN TRỌNG] TUYỆT ĐỐI GIỮ NGUYÊN CẤP ĐỘ HEADING (số lượng dấu #).

    Văn bản cần xử lý:
    """
    
    for i in range(3):
        try:
            full_prompt = f"{prompt}\n\n{text}"
            response = model.generate_content(full_prompt, safety_settings=safety)
            return response.text
        except Exception:
            time.sleep(2)
    return text 