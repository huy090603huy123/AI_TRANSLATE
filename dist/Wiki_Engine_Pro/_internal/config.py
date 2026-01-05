# config.py

# Cấu hình mặc định
DEFAULT_API_KEY = ""
DEFAULT_SHEET_URL = ""
MODEL_TRANSLATE = "models/gemini-2.5-flash"

# CSS giao diện chuẩn "ImageEngine PRO" (Dark Theme & Seamless Header)
CUSTOM_CSS = """
<style>
    /* 1. Import Fonts: Inter (UI) & JetBrains Mono (Terminal) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* 2. Global Dark Theme Override */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0; 
        background-color: #03050a; /* Nền đen xanh deep */
    }
    
    .stApp {
        background-color: #03050a;
    }

    /* --- PHẦN QUAN TRỌNG: FIX LỖI TRẮNG Ở ĐẦU TRANG --- */
    
    /* 2.1. Ẩn thanh trang trí 7 màu mặc định của Streamlit */
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0px;
        display: none;
    }

    /* 2.2. Làm trong suốt thanh Header (Nơi chứa nút Deploy/Menu) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        backdrop-filter: blur(1px); /* Hiệu ứng mờ nhẹ nếu cần */
    }

    /* 2.3. (Tùy chọn) Ẩn nút Deploy và Toolbar để giống Native App hơn */
    .stDeployButton {
        display: none;
    }
    
    /* Chỉnh màu icon menu 3 chấm sang trắng */
    div[data-testid="stToolbar"] button {
        color: #64748b !important;
    }
    div[data-testid="stToolbar"] button:hover {
        color: #ffffff !important;
    }

    /* --------------------------------------------------- */

    /* 3. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b101a;
        border-right: 1px solid #1e293b;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2); /* Thêm bóng đổ cho sidebar tách biệt */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .logo-text {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c7d2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        padding-top: 10px;
    }

    /* 4. Input Fields (Dark Input) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #161b26 !important;
        border: 1px solid #2d3648 !important;
        color: #f8fafc !important;
        border-radius: 8px;
        padding: 10px 12px;
    }
    
    .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    .stMarkdown label, .stTextInput label {
        color: #94a3b8 !important;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 5. Buttons (Gradient Purple) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #5b4eff 0%, #7c3aed 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 14px 20px;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 14px rgba(91, 78, 255, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(91, 78, 255, 0.5);
        color: #fff;
    }

    /* 6. Terminal/Output Area Styling */
    div[data-testid="stStatusWidget"] {
        background-color: #0b101a !important;
        border: 1px solid #1e293b;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .terminal-box {
        background-color: #0b101a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 20px;
        font-family: 'JetBrains Mono', monospace;
        color: #cbd5e1;
        margin-top: 20px;
        min-height: 400px; /* Tăng chiều cao mặc định */
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5); /* Hiệu ứng lõm vào trong */
    }
    
    .terminal-header {
        border-bottom: 1px solid #1e293b;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-size: 12px;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .dot {
        height: 10px; width: 10px; 
        background-color: #334155; 
        border-radius: 50%; 
        display: inline-block;
    }

    .success-text { color: #10b981; }
    .error-text { color: #ef4444; }
    .info-text { color: #3b82f6; }

    /* Ẩn footer 'Made with Streamlit' */
    footer {visibility: hidden;}
    
</style>
"""