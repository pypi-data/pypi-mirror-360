# Claude PyHooks

Claude Codeのhook実装のためのライブラリ

## 概要

Claude Codeのhook機能を活用するためのフレームワーク。以下のhookタイプに対応：

- **PreToolUse**: ツール実行前の制御（危険コマンドブロック、確認など）
- **PostToolUse**: ツール実行後の処理（ログ、バックアップ、音声通知など）
- **Notification**: Claude Codeからの通知処理
- **Stop**: セッション終了時の処理
- **SubagentStop**: サブエージェント終了時の処理

## インストール

```bash
pip install claude-pyhooks
uv add claude-pyhooks # uv 使用の場合
```

開発版 (uvの使用を推奨):
```bash
git clone <this-repository>
cd claude-pyhooks
uv sync
uv pip install -e .
```

## 基本的な使い方

### PreToolUse（危険なコマンドをブロック）

```python
#!/usr/bin/env python3
from claude_pyhooks import PreToolUseInput, block

def main():
    hook_input = PreToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        command = hook_input.tool_input.command
        if command is None:
            return
        command = command.strip()

        if "rm -rf /" in command:
            PreToolUseOutput.block(
                f"Dangerous command blocked: {dangerous}"
            ).execute()
            return

if __name__ == "__main__":
    main()
```

### PostToolUse（実行結果をログ）

```python
#!/usr/bin/env python3
from pathlib import Path

from claude_pyhooks import BashInput, BashResponse, PostToolUseInput

current_dir = Path(__file__).parent.resolve()


def main():
    hook_input = PostToolUseInput.from_stdin()

    if hook_input.tool_name == "Bash":
        assert isinstance(hook_input.tool_input, BashInput)
        assert isinstance(hook_input.tool_response, BashResponse)
        command = hook_input.tool_input.command
        success = not hook_input.tool_response.stderr

        status = "success" if success else "failure"
        with open(current_dir / "bash_command_log.txt", "a") as log_file:
            log_file.write(f"{status}: {command}\n")

if __name__ == "__main__":
    main()
```

### Notification（音声通知）

```python
#!/usr/bin/env python3
from claude_pyhooks import NotificationInput, SUCCESS_BEEP, ERROR_BEEP

def main():
    hook_input = NotificationInput.from_stdin()
    is_error = hook_input.message and "error" in hook_input.message.lower()

    beep = ERROR_BEEP if is_error else DEFAULT_BEEP
    beep.execute()

if __name__ == "__main__":
    main()
```

## Claude Code設定

`~/.claude/settings.json`などにhookを追加:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "uv run /path/to/pre_hook.py"
          }
        ]
      }
    ]
  }
}
```


## 実装

### 入力クラス
- 主要なクラス
  - `PreToolUseInput`
  - `PostToolUseInput` 
  - `NotificationInput`
  - `StopInput`
  - `SubagentStopInput`
- メンバ変数に入力を保管する
- `tool_input`(`PreToolUseInput`, `PostToolUseInput`内)は自動で判定されて型変換される
  - `BashInput`などに変換される
- `tool_response`(`PostToolUseInput`内)は自動で判定されて型変換される
  - `BashRequest`などに変換される

### コマンド
- `execute()`により実行する
- `CommandQueue`によりキューでの実行が可能

#### 出力クラス
- 主要なクラス
  - `PreToolUseOutput`
  - `PostToolUseOutput`
  - `StopOutput`
  - `SubagentStopOutput`
- クラス関数に`block()` (`PreToolUseOutput`は`approve()`も)定義されており、簡単な用途ではこちらが便利。
- blockするような出力で`execute()`すると自動でexit code 2で終了する。

#### 音声コマンド
- 主要なクラス
  - `BeepCommand`
  - `BeepSequence`
- デフォルト定義(`BeepCommand`のインスタンス)
  - `DEFAULT_BEEP`
  - `SUCCESS_BEEP`
  - `ERROR_BEEP`
  - `WARNING_BEEP`

## サンプルコード

`examples/`ディレクトリに実用的なサンプル:

- `pre_bash.py`: 危険なBashコマンドをブロック
- `post_bash.py`: Bashコマンドの実行結果をログ
- `notification_beep.py`: 音声通知

詳細: [examples/README.md](examples/README.md)

## ライセンス

MIT License
