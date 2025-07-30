import requests
import mimetypes
import time
import random
from pathlib import Path
from .img_util import get_img_content_type


def get_file_content_type(file_path: str) -> str:
    """根據檔案類型取得對應的 MIME type
    如果是圖片檔案，會使用 get_img_content_type 來檢測實際的圖片格式
    如果是其他檔案，則使用副檔名來判斷

    Args:
        file_path: 檔案路徑

    Returns:
        str: MIME type，如果無法判斷則返回 application/octet-stream
    """
    # 先用副檔名判斷是否為圖片
    content_type, _ = mimetypes.guess_type(file_path)

    # 如果副檔名顯示是圖片，使用 get_img_content_type 進行實際檢測
    if content_type and content_type.startswith("image/"):
        try:
            return get_img_content_type(file_path)
        except (ValueError, FileNotFoundError):
            # 如果圖片檢測失敗，回傳原本用副檔名判斷的結果
            return content_type

    # 非圖片檔案或無法判斷類型，回傳原本的結果
    return content_type or "application/octet-stream"


def upload_and_get_tmp_public_url(
    file_path: str, botrun_flow_lang_url: str = "", user_id: str = ""
) -> str:
    """上傳檔案到 GCS，並取得公開存取的 URL
    如果是圖片檔案，會根據實際的圖片格式來調整檔案副檔名

    Args:
        file_path: 本地檔案路徑
        botrun_flow_lang_url: botrun flow lang API 的 URL，預設為空字串
        user_id: 使用者 ID

    Returns:
        str: 上傳後的公開存取 URL
    """
    # 外層 try-except: 處理第一次嘗試與重試邏輯
    try:
        return _perform_upload(file_path, botrun_flow_lang_url, user_id)
    except Exception as e:
        import traceback

        # 第一次嘗試失敗，記錄錯誤但不立即返回
        print(f"First attempt failed: {str(e)}")
        traceback.print_exc()

        # 隨機等待 7-15 秒
        retry_delay = random.randint(7, 20)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)

        # 第二次嘗試
        try:
            print("Retry attempt...")
            return _perform_upload(file_path, botrun_flow_lang_url, user_id)
        except Exception as retry_e:
            # 第二次嘗試也失敗，記錄錯誤並返回錯誤訊息
            print(f"Retry attempt failed: {str(retry_e)}")
            traceback.print_exc()
            return "Error uploading file"


def _perform_upload(
    file_path: str, botrun_flow_lang_url: str = "", user_id: str = ""
) -> str:
    """執行實際的上傳操作

    Args:
        file_path: 本地檔案路徑
        botrun_flow_lang_url: botrun flow lang API 的 URL
        user_id: 使用者 ID

    Returns:
        str: 上傳後的公開存取 URL
    """
    try:
        # 如果沒有提供 API URL，使用預設值
        if not botrun_flow_lang_url or not user_id:
            raise ValueError("botrun_flow_lang_url and user_id are required")

        # 取得檔案的 MIME type
        content_type = get_file_content_type(file_path)

        # 從檔案路徑取得檔案名稱
        file_name = Path(file_path).name

        # 如果是圖片檔案，根據實際的 content type 調整副檔名
        if content_type.startswith("image/"):
            # 取得檔案名稱（不含副檔名）
            name_without_ext = Path(file_name).stem
            # 根據 content type 決定新的副檔名
            ext_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "image/webp": ".webp",
            }
            new_ext = ext_map.get(content_type, Path(file_name).suffix)
            file_name = f"{name_without_ext}{new_ext}"

        # 準備 API endpoint
        url = f"{botrun_flow_lang_url}/api/tmp-files/{user_id}"

        # 準備檔案
        files = {
            "file": (file_name, open(file_path, "rb"), content_type),
            "file_name": (None, file_name),
            "content_type": (None, content_type),
        }

        # 發送請求
        response = requests.post(url, files=files)
        response.raise_for_status()  # 如果請求失敗會拋出異常

        # 從回應中取得 URL
        result = response.json()
        return result.get("url", "")

    except Exception as e:
        # 這裡把異常往上拋，讓外層的重試邏輯處理
        raise e


def upload_html_and_get_public_url(
    file_path: str, botrun_flow_lang_url: str = "", user_id: str = ""
) -> str:
    """上傳 HTML 檔案到 GCS，並取得公開存取的 URL
    此函數僅接受 .html 檔案

    Args:
        file_path: 本地 HTML 檔案路徑
        botrun_flow_lang_url: botrun flow lang API 的 URL，預設為空字串
        user_id: 使用者 ID

    Returns:
        str: 上傳後的公開存取 URL
    """
    # 檢查檔案是否為 HTML 檔案
    if not file_path.lower().endswith(".html"):
        raise ValueError("Only HTML files are allowed")

    # 外層 try-except: 處理第一次嘗試與重試邏輯
    try:
        return _perform_html_upload(file_path, botrun_flow_lang_url, user_id)
    except Exception as e:
        import traceback

        # 第一次嘗試失敗，記錄錯誤但不立即返回
        print(f"First attempt failed: {str(e)}")
        traceback.print_exc()

        # 隨機等待 7-15 秒
        retry_delay = random.randint(7, 20)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)

        # 第二次嘗試
        try:
            print("Retry attempt...")
            return _perform_html_upload(file_path, botrun_flow_lang_url, user_id)
        except Exception as retry_e:
            # 第二次嘗試也失敗，記錄錯誤並返回錯誤訊息
            print(f"Retry attempt failed: {str(retry_e)}")
            traceback.print_exc()
            return "Error uploading HTML file"


def _perform_html_upload(
    file_path: str, botrun_flow_lang_url: str = "", user_id: str = ""
) -> str:
    """執行 HTML 檔案的上傳操作

    Args:
        file_path: 本地 HTML 檔案路徑
        botrun_flow_lang_url: botrun flow lang API 的 URL
        user_id: 使用者 ID

    Returns:
        str: 上傳後的公開存取 URL
    """
    try:
        # 如果沒有提供 API URL，使用預設值
        if not botrun_flow_lang_url or not user_id:
            raise ValueError("botrun_flow_lang_url and user_id are required")

        # 檢查檔案是否為 HTML 檔案
        if not file_path.lower().endswith(".html"):
            raise ValueError("Only HTML files are allowed")

        # 取得檔案的 MIME type
        content_type = "text/html"

        # 從檔案路徑取得檔案名稱
        file_name = Path(file_path).name

        # 準備 API endpoint
        url = f"{botrun_flow_lang_url}/api/html-files/{user_id}"

        # 準備檔案
        files = {
            "file": (file_name, open(file_path, "rb"), content_type),
            "file_name": (None, file_name),
            "content_type": (None, content_type),
        }

        # 發送請求
        response = requests.post(url, files=files)
        response.raise_for_status()  # 如果請求失敗會拋出異常

        # 從回應中取得 URL
        result = response.json()
        return result.get("url", "")

    except Exception as e:
        # 這裡把異常往上拋，讓外層的重試邏輯處理
        raise e
