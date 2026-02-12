import time
import os
import getpass
from pywinauto.application import Application
from pywinauto import timings
import pyautogui

# ==========================================
# Configuration Section (Please Update These)
# ==========================================

# アプリケーションの実行可能ファイルへのパス
# 例: r"C:\Program Files\ClientApp\ClientApp.exe"
APP_PATH = r"C:\Path\To\ClientApplicationAccess.exe"

# ウィンドウのタイトル（部分一致でOK）
WINDOW_TITLE = "Client application access"

# UI要素の識別子 (Inspect.exe などを使って調べてください)
# 例: 'Button1', 'Edit1', 'Pane2', AutomationId="LoginButton" など
LOGIN_BUTTON_ID = "LoginButton"
USERNAME_FIELD_ID = "UsernameEdit"
PASSWORD_FIELD_ID = "PasswordEdit"
NOTES_PANEL_ID = "NotesPanel"  # ダブルクリックするパネル
DOWNLOAD_BUTTON_ID = "DownloadExcelButton"

# タイムアウト設定 (秒)
TIMEOUT = 10

def start_app():
    """アプリケーションを起動し、メインウィンドウに接続します。"""
    print(f"アプリケーションを起動しています: {APP_PATH}")
    try:
        app = Application(backend="uia").start(APP_PATH)
        # ウィンドウが表示されるのを待つ
        main_window = app.window(title_re=WINDOW_TITLE)
        main_window.wait('visible', timeout=TIMEOUT)
        print("アプリケーションが起動しました。")
        return app, main_window
    except Exception as e:
        print(f"アプリケーションの起動に失敗しました: {e}")
        return None, None

def login(window, username, password):
    """ログイン操作を実行します。"""
    print("ログインを試みています...")
    try:
        # ユーザー名とパスワードの入力フィールドを探す
        # 注: 'child_window' のパラメータ (auto_id, control_type) は Inspect.exe で確認してください

        # auto_id を使用した例
        user_field = window.child_window(auto_id=USERNAME_FIELD_ID, control_type="Edit")
        pass_field = window.child_window(auto_id=PASSWORD_FIELD_ID, control_type="Edit")
        login_btn = window.child_window(auto_id=LOGIN_BUTTON_ID, control_type="Button")

        # 認証情報を入力
        user_field.set_text(username)
        pass_field.set_text(password)

        # ログインボタンをクリック
        login_btn.click()

        # ログイン完了を待つ (必要に応じて時間を調整するか、次の画面の要素を待つように変更してください)
        time.sleep(5)
        print("ログイン操作が完了しました。")

    except Exception as e:
        print(f"ログイン中にエラーが発生しました: {e}")
        # pywinautoで要素が見つからない場合はPyAutoGUIにフォールバックする例
        print("座標ベースの操作 (PyAutoGUI) に切り替えます...")
        # ここで座標を指定するか、画像認識を使用する必要があります
        # pyautogui.click(x=100, y=200)
        # pyautogui.typewrite(username)
        # ...

def double_click_panel(window):
    """特定のパネルをダブルクリックします。"""
    print("パネルへ移動しています...")
    try:
        # control_type は "Pane", "Group", "Custom" などの可能性があります
        panel = window.child_window(auto_id=NOTES_PANEL_ID, control_type="Pane")
        panel.double_click_input()
        print("パネルをダブルクリックしました。")
        time.sleep(2)
    except Exception as e:
        print(f"パネルのクリック中にエラーが発生しました: {e}")

def download_excel(window):
    """Excelデータをダウンロードするボタンをクリックします。"""
    print("Excelダウンロードを開始します...")
    try:
        download_btn = window.child_window(auto_id=DOWNLOAD_BUTTON_ID, control_type="Button")
        download_btn.click()

        # 「名前を付けて保存」ダイアログが表示される場合の処理例
        # app = Application(backend="uia").connect(path=APP_PATH)
        # save_dialog = app.window(title="名前を付けて保存")
        # save_dialog.wait('visible', timeout=5)
        # save_dialog.Save.click()

        print("ダウンロードボタンをクリックしました。")
    except Exception as e:
        print(f"ダウンロードボタンのクリック中にエラーが発生しました: {e}")

def main():
    if not os.path.exists(APP_PATH):
        print(f"エラー: アプリケーションのパスが見つかりません: {APP_PATH}")
        print("スクリプト内の APP_PATH 変数を更新してください。")
        return

    # ユーザーに入力を求める (セキュリティのためスクリプトにハードコードしない)
    print("--- Client Application Access 自動化スクリプト ---")
    username = input("ユーザー名を入力してください: ")
    password = getpass.getpass("パスワードを入力してください (表示されません): ")

    app, main_window = start_app()

    if main_window:
        login(main_window, username, password)

        # ログイン後、ウィンドウの参照を更新する必要がある場合があります
        # main_window = app.window(title_re="メインダッシュボードのタイトル")

        double_click_panel(main_window)
        download_excel(main_window)

        print("自動化シーケンスが完了しました。")

if __name__ == "__main__":
    main()
