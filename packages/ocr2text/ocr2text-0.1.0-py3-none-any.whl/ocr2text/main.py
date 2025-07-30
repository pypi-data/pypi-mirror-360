import requests
import hashlib
import time
import os
import json
import re
import urllib.parse
import websocket

def convert_pdf_to_text_with_ocr(pdf_path: str, lang: str = "eng"):
    """
    Converts a scanned/image-based PDF to a selectable, searchable text file using PDFCandy OCR.
    
    Args:
        pdf_path (str): Path to the input PDF file.
        output_txt_path (str): Path where the output text file will be saved.
        lang (str): OCR language (default is English).
    
    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    # === Extract Config ===
    print("🔧 Extracting session config...")
    def extract_pdfcandy_config():
        html = requests.get("https://pdfcandy.com/pdf-ocr.html").text
        return {
            "session_id": re.search(r"sessionId:\s*'([a-z0-9]+)'", html).group(1),
            "auth_token": re.search(r"token:\s*'([a-z0-9]+)'", html).group(1),
            "api_host": re.search(r"endpoint:\s*'https://(s\d+\.api\.pdfcandy\.com)/v2'", html).group(1),
            "upload_key": re.search(r"upload_endpoint_key:\s*'([a-z0-9]+)'", html).group(1)
        }

    config = extract_pdfcandy_config()
    timestamp = int(time.time() * 1000)
    filename = os.path.basename(pdf_path)

    # === Upload PDF ===
    upload_url = f"https://{config['api_host']}/uploadcbc/{timestamp}-{filename}"
    with open(pdf_path, "rb") as f:
        file_data = f.read()

    print("🔼 Uploading PDF...")
    upload_resp = requests.post(
        upload_url,
        data=file_data,
        headers={
            "authorization": config['upload_key'],
            "x-chunk": "000000",
            "origin": "https://pdfcandy.com",
            "referer": "https://pdfcandy.com/",
            "user-agent": "Mozilla/5.0"
        }
    )
    if not upload_resp.ok:
        print("❌ Upload failed:", upload_resp.status_code)
        return False
    print("✅ Upload successful.")

    # === Get Metadata ===
    meta_url = f"https://{config['api_host']}/v2/getvideometa/{config['session_id']}/{timestamp}-{filename}/"
    headers = {
        "authorization": config['auth_token'],
        "origin": "https://pdfcandy.com",
        "referer": "https://pdfcandy.com/",
        "user-agent": "Mozilla/5.0",
        "content-type": "application/json"
    }

    response = requests.post(meta_url, headers=headers, json={})
    if not response.ok:
        print("❌ Metadata fetch failed.")
        return False

    file_md5 = response.json().get("md5")

    # === Trigger OCR ===
    payload = {
        "files": [{
            "md5": file_md5,
            "file": filename,
            "job": "pdf-ocr"
        }],
        "options": {"lang": lang},
        "autoprogress": True,
        "session_id": config['session_id'],
        "job": "pdf-ocr"
    }

    ocr_url = f"https://{config['api_host']}/v2"
    print("🧠 Triggering OCR...")
    ocr_resp = requests.post(
        ocr_url,
        data=f"payload={urllib.parse.quote(json.dumps(payload))}",
        headers={
            "authorization": config['auth_token'],
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://pdfcandy.com",
            "referer": "https://pdfcandy.com/",
            "user-agent": "Mozilla/5.0"
        }
    )
    if not ocr_resp.ok:
        print("❌ OCR trigger failed.")
        return False

    # === Wait for WebSocket Completion ===
    finish = False
    def on_message(ws, message):
        nonlocal finish
        print("📩", message)
        if "finished" in message:
            print("✅ OCR Completed!")
            finish = True
            ws.close()

    def on_error(ws, error):
        print("❌ WebSocket error:", error)

    def on_close(ws, *args):
        print("🔌 WebSocket closed")

    def on_open(ws): 
        print("🔗 Listening for OCR complete signal...")

    ws_url = f"wss://{config['api_host']}/ws/{config['session_id']}"
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header={"Origin": "https://pdfcandy.com"}
    )

    ws.run_forever()

    if finish:
        # === Download Text File ===
        txt_filename = filename.replace(".pdf", ".txt")
        output_txt_path = os.path.join(os.path.dirname(pdf_path), txt_filename)
        download_url = f"https://{config['api_host']}/{config['session_id']}/{txt_filename}?dl"
        print("⬇️ Downloading OCR result...")

        response = requests.get(download_url, headers={
            "referer": "https://pdfcandy.com/",
            "user-agent": "Mozilla/5.0"
        })

        if response.ok:
            with open(output_txt_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved OCR text to {output_txt_path}")
            return True
        else:
            print("❌ Download failed.")
            return False

    print("⚠️ OCR process did not complete.")
    return False
