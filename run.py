# run.py
import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    # Hàm này giúp tìm file khi đã đóng gói vào file exe (folder tạm _MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.getcwd(), path)

if __name__ == "__main__":
    # SỬA LẠI TÊN FILE CHÍNH CHO ĐÚNG VỚI DỰ ÁN CỦA BẠN
    script_path = resolve_path("main.py")
    
    # Giả lập lệnh chạy: streamlit run main.py --global.developmentMode=false
    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
    ]
    
    sys.exit(stcli.main())