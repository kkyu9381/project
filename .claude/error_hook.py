"""
Claude Code PostToolUse 훅 스크립트
Bash 도구 실행 결과에서 오류를 감지하여 메모리에 자동 기록합니다.
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path.home() / ".claude" / "projects" / "D--project" / "memory"
ERROR_LOG = MEMORY_DIR / "error_log.md"
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"

ERROR_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r"Error:",
    r"Exception:",
    r"ModuleNotFoundError",
    r"FileNotFoundError",
    r"PermissionError",
    r"ConnectionError",
    r"TimeoutError",
    r"ValueError",
    r"KeyError",
    r"AttributeError",
    r"ImportError",
    r"❌",
    r"FAILED",
    r"exit code [1-9]",
]


def detect_error(output: str) -> str | None:
    """출력에서 오류 메시지를 감지하고 요약을 반환합니다."""
    for pattern in ERROR_PATTERNS:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            # 오류가 발생한 줄 전후 컨텍스트 추출
            lines = output.splitlines()
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    start = max(0, i - 1)
                    end = min(len(lines), i + 3)
                    return "\n".join(lines[start:end]).strip()
    return None


def append_error_to_log(error_summary: str, command: str):
    """error_log.md에 새 오류 항목을 추가합니다."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n### [{timestamp}] 미해결\n"
        f"**메시지:** {error_summary[:200]}\n"
        f"**컨텍스트:** `{command[:100]}` 실행 중 발생\n"
        f"**해결 방법:** (미기록)\n"
    )

    # 이미 동일한 오류가 기록되어 있는지 확인 (중복 방지)
    if ERROR_LOG.exists():
        existing = ERROR_LOG.read_text(encoding="utf-8")
        # 오류 메시지 첫 50자로 중복 확인
        key = error_summary[:50]
        if key in existing:
            return  # 이미 기록된 오류

    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        if not ERROR_LOG.exists() or ERROR_LOG.stat().st_size == 0:
            f.write("---\nname: 오류 기록 로그\ndescription: 프로젝트 진행 중 발생한 오류와 해결 방법을 추적하는 로그\ntype: project\n---\n# 오류 기록\n")
        f.write(entry)

    ensure_memory_index()


def ensure_memory_index():
    """MEMORY.md에 error_log.md 항목이 있는지 확인하고 없으면 추가합니다."""
    if not MEMORY_INDEX.exists():
        return

    content = MEMORY_INDEX.read_text(encoding="utf-8")
    if "error_log.md" not in content:
        with open(MEMORY_INDEX, "a", encoding="utf-8") as f:
            f.write("- [오류 기록](error_log.md) — 발생한 오류와 해결 방법 추적 로그\n")


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
        tool_output = data.get("output", "") or data.get("result", "") or ""
        command = data.get("input", {}).get("command", "") if isinstance(data.get("input"), dict) else ""

        if not tool_output:
            return

        error_summary = detect_error(str(tool_output))
        if error_summary:
            append_error_to_log(error_summary, str(command))

    except (json.JSONDecodeError, KeyError, TypeError):
        # 훅 스크립트 자체 오류는 조용히 무시
        pass


if __name__ == "__main__":
    main()
