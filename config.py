# config.py

# Cấu hình mặc định (Nên để trống để nhập trên UI cho bảo mật)
DEFAULT_API_KEY = ""
DEFAULT_SHEET_URL = ""
MODEL_TRANSLATE = "models/gemini-2.5-flash"

# CSS giao diện
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-title { font-size: 2.5rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #0f2027, #203a43, #2c5364); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; color: #555; margin-bottom: 30px; font-weight: 400; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); color: white; font-weight: 600; border: none; border-radius: 8px; padding: 12px 20px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .stButton>button:hover { background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); color: #fff; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e9ecef; }
    .stTextInput input { border-radius: 5px; border: 1px solid #ddd; padding: 10px; }
    .stTextInput input:focus { border-color: #1e3c72; box-shadow: 0 0 0 1px #1e3c72; }
    div[data-testid="stStatusWidget"] { border-radius: 8px; border: 1px solid #e0e0e0; background-color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
</style>
"""