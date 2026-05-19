# Client Application Access 自動化スクリプト

このスクリプトは、「Client application access」というデスクトップアプリを操作し、ログイン、特定のパネルへの移動、Excelデータのダウンロードを自動化するためのテンプレートです。

## 前提条件

1.  **Python**: システムに Python 3.x がインストールされている必要があります。
2.  **ライブラリ**: 以下のコマンドで必要なライブラリをインストールしてください。

    ```bash
    pip install pywinauto pyautogui
    ```

    *   `pywinauto`: Windowsの標準的なコントロール（ボタン、入力欄など）を操作するために使用します。
    *   `pyautogui`: 画面上の座標指定や画像認識で操作する場合のフォールバックとして使用します。

## 設定方法

スクリプト (`automate_notes_app.py`) を実行する前に、お使いの環境に合わせて設定を変更する必要があります。テキストエディタでスクリプトを開き、以下の変数を更新してください。

1.  **APP_PATH**: アプリケーションの実行ファイル（`.exe`）へのフルパス。
    *   例: `r"C:\Program Files\ClientApp\ClientApp.exe"`
2.  **WINDOW_TITLE**: タスクバーやタイトルバーに表示されるウィンドウのタイトル。
    *   例: `"Client application access - Dashboard"`
3.  **UI要素の識別子 (ID)**: 操作したいボタンや入力フィールドの識別子（Automation IDなど）を特定し、以下の変数に設定してください。
    *   `LOGIN_BUTTON_ID`
    *   `USERNAME_FIELD_ID`
    *   `PASSWORD_FIELD_ID`
    *   `NOTES_PANEL_ID`
    *   `DOWNLOAD_BUTTON_ID`

### UI要素の識別子を見つける方法

アプリケーション内の要素（ボタンや入力欄）の正しい識別子（AutomationIdやControlTypeなど）を見つけるには、Microsoftが提供しているツールを使用するのが便利です。

*   **Inspect.exe** (Windows SDKに含まれています)
*   **Accessibility Insights for Windows**

また、スクリプト内でウィンドウ構造全体を出力させることで確認することも可能です。

```python
# main() 関数内のウィンドウ接続後に以下を追加
main_window.print_control_identifiers()
```

これを実行すると、コンソールにウィンドウ内のすべてのコントロールとそのプロパティが表示されます。そこから対象のボタンやフィールドの `auto_id` や `title` を探してコピーしてください。

## 実行方法

設定が完了したら、コマンドプロンプトやターミナルで以下のコマンドを実行します。

```bash
python automate_notes_app.py
```

実行すると、ユーザー名とパスワードの入力が求められます（パスワードは画面に表示されません）。

## トラブルシューティング

*   **アプリが起動しない**: `APP_PATH` が正しいか確認してください。
*   **要素が見つからない**: アプリの起動や画面遷移に時間がかかっている可能性があります。`TIMEOUT` の値を増やすか、`time.sleep()` で待機時間を追加してください。
*   **ログインできない**: 入力されたユーザー名・パスワードが正しいか、またスクリプトが正しいフィールドに入力しているか確認してください。
*   **"Element not found" エラー**: ウィンドウの構造が動的に変化している可能性があります。エラーが発生した時点での状態を `print_control_identifiers()` で確認してください。

## 補足

*   このスクリプトは `pywinauto` の `uia` バックエンドを使用しています。これは最近のWindowsアプリ（WPF, UWPなど）に適しています。もし対象のアプリが古い形式（Win32, MFCなど）の場合は、`backend="uia"` を `backend="win32"` に変更する必要があるかもしれません。

---

## 【新機能】Gemini API (Vision) を使った自動化について

従来の `pywinauto` では、UI要素のIDや座標を事前に手動で調べる必要がありました。これを解決するため、**AIの画像認識を活用して画面から自動でボタンを探してクリックするサンプルスクリプト (`automate_with_gemini.py`)** を追加しました。

このスクリプトは、画面のスクリーンショットを Gemini API に送信し、「Downloadボタンの座標を教えて」とAIに尋ねることで、面倒なID調査を不要にします。

### 必要な追加ライブラリ

Gemini APIを利用するため、追加で以下のライブラリをインストールしてください。

```bash
pip install google-generativeai pillow
```

### 実行準備

Gemini APIを使用するには、Google AI Studio で無料のAPIキーを取得し、環境変数に設定する必要があります。

**Windowsの場合:**
```cmd
set GEMINI_API_KEY="あなたのAPIキー"
```
または、PowerShellの場合:
```powershell
$env:GEMINI_API_KEY="あなたのAPIキー"
```

### セキュリティに関する重要事項（必ずお読みください）

`automate_with_gemini.py` は、**実行中の画面全体のスクリーンショットを Google の API サーバーに送信します。**

*   **無料枠の利用について**: Google AI Studio の無料枠（Free Tier）を利用する場合、送信された画像データはGoogleによってAIモデルの学習やサービス改善に利用される可能性があります。
*   **機密情報の保護**: そのため、**パスワード入力画面、個人情報、顧客データ、機密扱いの社内システム画面などが写っている状態でこのスクリプトを実行しないでください。**
*   **安全な利用方法**: 業務で利用する場合や、機密情報を取り扱う場合は、データが学習に利用されない Google Cloud Vertex AI の有料枠（エンタープライズ版）経由で Gemini API を利用するか、機密部分（パスワード入力など）は従来の `pywinauto` を使い、影響のない画面でのみAI画像認識を使用するようスクリプトを改修してください。

現在のサンプルスクリプトでは、パスワード入力をAIに任せず、ログイン後の安全な画面での利用を想定したデモとなっています。
