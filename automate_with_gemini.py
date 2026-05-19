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
    """1. アプリケーション(Notes)を起動します。"""
    print(f"Notesアプリケーションを起動しています: {APP_PATH}")
    try:
        os.startfile(APP_PATH)
        print("アプリケーションの起動をリクエストしました。ログイン画面が表示されるまで待ちます...")
        time.sleep(10) # アプリ起動にかかる時間（環境に合わせて調整）
        return True
    except Exception as e:
        print(f"起動エラー: {e}")
        return False

def double_click_element_with_gemini(element_description, wait_time=2):
    """
    画面のスクリーンショットを撮り、Geminiを使って要素を探し、ダブルクリックします。
    """
    print(f"「{element_description}」を探してダブルクリックします...")
    time.sleep(wait_time)

    screenshot_path = "temp_screenshot.png"
    pyautogui.screenshot(screenshot_path)

    try:
        result = get_element_coordinates(screenshot_path, element_description)

        if result.get("found"):
            x, y = result.get("x"), result.get("y")
            print(f"要素が見つかりました: 座標(X:{x}, Y:{y})")
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.doubleClick()
            return True
        else:
            print(f"エラー: 画像内に「{element_description}」が見つかりませんでした。")
            return False
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

def type_text(text):
    """キーボード入力をシミュレートします。"""
    # パスワードなどを入力する際に使用します
    pyautogui.write(text, interval=0.05)
    time.sleep(1)

def main():
    print("=== Gemini APIを使用した Notes 自動化スクリプト ===")
    print("【警告】現在の画面全体のスクリーンショットがGemini APIに送信されます。")
    print("機密情報が画面に表示されていないことを確認してください。")

    # ユーザー名とパスワードをコンソールから安全に入力
    print("\n--- 認証情報の設定 ---")
    username = input("Notesのユーザー名を入力してください: ")
    password = getpass.getpass("Notesのパスワードを入力してください (画面には表示されません): ")

    if input("\n実行を開始しますか？ (y/n): ").lower() != 'y':
        print("処理を中止しました。")
        return

    # 1. Notesアプリを立ち上げる
    print("\n[ステップ 1: Notesアプリの起動]")
    # 実際の環境では以下のコメントアウトを外して実行パスを使用してください
    # start_app()
    print("(デモ: 既にNotesが起動していると仮定して進みます)")
    time.sleep(2)

    # 2. ログイン
    print("\n[ステップ 2: ログイン]")
    # ユーザー名フィールドをクリックして入力
    if click_element_with_gemini("ユーザー名の入力フィールド (テキストボックス)"):
        type_text(username)

    # パスワードフィールドをクリックして入力
    # （※入力したパスワードは「***」で隠れるため、次のスクショを撮っても安全という前提です）
    if click_element_with_gemini("パスワードの入力フィールド (テキストボックス)"):
        type_text(password)

    # ログインボタンをクリック
    if click_element_with_gemini("ログイン (Login) ボタン または OK ボタン"):
        print("ログイン処理の完了を待っています...")
        time.sleep(10) # ログインしてNotesのメイン画面が開くまで待つ

        # 3. 文書DBをダブルクリック
        print("\n[ステップ 3: 文書DBを開く]")
        if double_click_element_with_gemini("「文書DB」という名前のアイコン、データベース、またはタブ"):
            print("文書DBが開くのを待っています...")
            time.sleep(5)

            # 4. 文書DBを閉じる
            print("\n[ステップ 4: 文書DBを閉じる]")
            # ウィンドウを閉じる「×」ボタンや、閉じるアイコンを探す
            click_element_with_gemini("文書DBのタブを閉じるための「×」ボタン、または「閉じる」ボタン")
            time.sleep(3)

        else:
            print("「文書DB」が見つからなかったため、以降の処理をスキップします。")

        # 5. Notesを閉じる
        print("\n[ステップ 5: Notesアプリを閉じる]")
        # アプリケーション自体の終了
        click_element_with_gemini("Notesアプリ全体のウィンドウを閉じるための右上の「×」ボタン、または「終了」メニュー")

    print("\n自動化シーケンスが完了しました。")

if __name__ == "__main__":
    main()
