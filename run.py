# run.py
import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    # Hàm này giúp tìm file khi đã đóng gói vào file exe
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.getcwd(), path)

if __name__ == "__main__":
    # Đường dẫn đến file code chính của bạn bên trong file exe
    script_path = resolve_path("wiki_tool.py")
    
    # Giả lập lệnh chạy: streamlit run wiki_tool.py --global.developmentMode=false
    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
    ]
    
    sys.exit(stcli.main())