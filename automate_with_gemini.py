import time
import os
import getpass
import json
import pyautogui
from PIL import Image
import google.generativeai as genai

# ==========================================
# Configuration Section
# ==========================================

# アプリケーションの実行可能ファイルへのパス
APP_PATH = r"C:\Path\To\ClientApplicationAccess.exe"

# Gemini APIキーの設定 (環境変数からの取得を推奨)
# export GEMINI_API_KEY="your_api_key_here"
API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not API_KEY:
    print("警告: 環境変数 'GEMINI_API_KEY' が設定されていません。")
    print("スクリプトを直接編集して API_KEY 変数にキーを設定するか、環境変数を設定してください。")
    # API_KEY = "ここにAPIキーを直接書くこともできますが非推奨です"

# ==========================================
# Gemini Vision Helper
# ==========================================

def get_element_coordinates(image_path, element_description):
    """
    スクリーンショットをGemini APIに送信し、指定された要素の座標（Bounding Box）を取得します。
    """
    if not API_KEY:
        raise ValueError("APIキーが設定されていません。")

    genai.configure(api_key=API_KEY)

    # 座標をJSON形式で返すようにシステムプロンプトを設定
    # AIに正確な座標を推論させるため、絶対的なピクセル数ではなく、0から1000の正規化された座標（パーセンテージ）で返すように指示します。
    system_instruction = """
    あなたは画面のスクリーンショットからUI要素の場所を特定するAIアシスタントです。
    ユーザーが探している要素を画像内で見つけ、その要素の中央の座標(x, y)を以下のJSON形式でのみ出力してください。

    【重要】座標は実際のピクセル数ではなく、画像の左上を(0, 0)、右下を(1000, 1000)とした正規化された座標で返してください。

    ```json
    {"x_norm": 500, "y_norm": 250, "found": true}
    ```

    もし見つからない場合は、"found": false を返してください。
    """

    # Gemini 1.5 Pro または Flash を使用
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=system_instruction
    )

    try:
        img = Image.open(image_path)
        img_width, img_height = img.size

        prompt = f"この画像の中で「{element_description}」という要素を探し、その中央の座標(0-1000のスケール)を教えてください。"

        response = model.generate_content([img, prompt])
        response_text = response.text

        # 応答からJSON部分を抽出 (簡易的な方法)
        import re
        match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Markdownブロックがない場合
            json_str = response_text

        data = json.loads(json_str)

        # 正規化された座標から実際の画面上のピクセル座標を計算する
        if data.get("found"):
            x_norm = data.get("x_norm", 0)
            y_norm = data.get("y_norm", 0)

            data["x"] = int(x_norm * (img_width / 1000))
            data["y"] = int(y_norm * (img_height / 1000))

        return data

    except Exception as e:
        print(f"Gemini APIの呼び出し中にエラーが発生しました: {e}")
        return {"found": False}

def click_element_with_gemini(element_description, wait_time=2):
    """
    画面のスクリーンショットを撮り、Geminiを使って要素を探し、クリックします。
    """
    print(f"「{element_description}」を探しています...")
    time.sleep(wait_time) # 画面が安定するのを待つ

    screenshot_path = "temp_screenshot.png"
    # ※注意: 機密情報が写っている場合はこの処理は避けるべきです
    pyautogui.screenshot(screenshot_path)

    try:
        result = get_element_coordinates(screenshot_path, element_description)

        if result.get("found"):
            x = result.get("x")
            y = result.get("y")
            print(f"要素が見つかりました: 座標(X:{x}, Y:{y})")

            # Geminiが推測した座標をクリック
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            return True
        else:
            print(f"エラー: 画像内に「{element_description}」が見つかりませんでした。")
            return False

    finally:
        # 一時的なスクリーンショットを削除
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

# ==========================================
# Automation Workflow
# ==========================================

def start_app():
    """アプリケーションを起動します。"""
    print(f"アプリケーションを起動しています: {APP_PATH}")
    try:
        os.startfile(APP_PATH)
        print("アプリケーションの起動をリクエストしました。画面が表示されるまで少し待ちます...")
        time.sleep(10) # 起動にかかる時間待機
    except Exception as e:
        print(f"起動エラー: {e}")

def main():
    print("=== Gemini APIを使用した自動化スクリプト ===")
    print("【警告】現在の画面全体のスクリーンショットがGemini APIに送信されます。")
    print("機密情報（特にパスワードなど）が画面に表示されていないことを確認してください。")

    if input("実行を続けますか？ (y/n): ").lower() != 'y':
        print("処理を中止しました。")
        return

    # 注意: ここではパスワード入力を自動化していません。
    # APIにパスワードを含む画面を送るリスクを避けるため、
    # 本番運用ではpywinautoで安全にテキスト入力する等との併用を推奨します。

    # 1. アプリを起動
    # start_app() # (実際の環境に合わせてコメントアウトを外してください)

    print("\n※このデモでは、すでにアプリが起動し、画面に表示されている前提で進みます。")

    # 2. ログインボタンをクリック
    if click_element_with_gemini("Login または サインイン ボタン"):
        time.sleep(5) # 画面遷移を待つ

        # 3. Notesパネルをダブルクリック (Geminiは位置特定のみで、操作はpyautoguiで行う)
        print("Notesパネルを探しています...")
        screenshot_path = "temp_screenshot.png"
        pyautogui.screenshot(screenshot_path)
        result = get_element_coordinates(screenshot_path, "Notes というテキストまたはアイコンのパネル")
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        if result.get("found"):
            x, y = result.get("x"), result.get("y")
            print(f"Notesパネルを見つけました。ダブルクリックします。(X:{x}, Y:{y})")
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.doubleClick()

            time.sleep(3) # 画面遷移を待つ

            # 4. ダウンロードボタンをクリック
            click_element_with_gemini("Download Excel または ダウンロード ボタン")

        else:
            print("Notesパネルが見つかりませんでした。")

    print("処理が完了しました。")

if __name__ == "__main__":
    main()
