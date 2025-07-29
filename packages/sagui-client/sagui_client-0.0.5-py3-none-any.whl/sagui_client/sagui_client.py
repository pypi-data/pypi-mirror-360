import traceback
import requests
import json
import sys
import os

def extract_trace_info(exc_type, exc_value, tb):
    trace_str = ''.join(traceback.format_exception(exc_type, exc_value, tb))

    while tb.tb_next:
        tb = tb.tb_next
    filename = tb.tb_frame.f_code.co_filename

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as read_error:
        source_code = f"Failed to read source file: {read_error}"

    return {
        "traceback": trace_str,
        "filename": filename,
        "source_code": source_code,
        "error_type": exc_type.__name__,
        "error_message": str(exc_value),
    }

def send_error_report(exc_type, exc_value, tb):
    sagui_host = os.environ.get("SAGUI_HOST") or "http://localhost:8000"
    payload = extract_trace_info(exc_type, exc_value, tb)

    headers = {"Content-Type": "application/json"}
    try:
        requests.post(f"{sagui_host}/error_reports", json=payload, headers=headers)
    except Exception as send_error:
        print(f"ErrorReporter failed to send report: {send_error}")

def install_global_handler():
    def custom_excepthook(exc_type, exc_value, tb):
        send_error_report(exc_type, exc_value, tb)
        # Let Python print the error as usual
        sys.__excepthook__(exc_type, exc_value, tb)

    sys.excepthook = custom_excepthook
