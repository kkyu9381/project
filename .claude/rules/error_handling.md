---
description: 오류 발생 시 자동으로 메모리에 기록하고 해결 후 업데이트하는 규칙
---

# 오류 처리 및 메모리 저장 규칙

## 오류 감지 즉시 수행할 작업

Bash, Python 스크립트, API 호출 등 어떤 도구 실행에서든 오류가 발생하면 **즉시** 다음 절차를 따른다.

### 1단계: 오류 메모리에 기록

`C:/Users/user/.claude/projects/D--project/memory/error_log.md` 파일에 아래 형식으로 추가한다:

```markdown
### [YYYY-MM-DD HH:MM] 미해결
**메시지:** (오류 원문 또는 요약)
**컨텍스트:** (어떤 작업 중 발생했는지)
**해결 방법:** (미기록)
```

### 2단계: MEMORY.md 인덱스 확인

`C:/Users/user/.claude/projects/D--project/memory/MEMORY.md`에 `error_log.md` 항목이 없으면 추가한다:

```markdown
- [오류 기록](error_log.md) — 발생한 오류와 해결 방법 추적 로그
```

### 3단계: 오류 해결 후 즉시 업데이트

오류를 해결하면 **절대 생략하지 말고** `error_log.md`를 Edit 도구로 수정한다:
- `미해결` → `해결됨`
- `**해결 방법:** (미기록)` → 실제 해결 방법으로 교체

---

## 기록 대상 오류 유형

- Python 스크립트 실행 오류 (traceback, exit code ≠ 0)
- API 호출 실패 (HTTP 오류, 인증 실패, 모델 오류)
- 파일 I/O 오류 (파일 없음, 권한 오류)
- 패키지/의존성 오류 (import 실패, 설치 필요)
- 환경 변수 누락 오류

## 기록 제외 대상

- 사용자가 직접 수정하여 즉시 해결된 오타/문법 오류
- 테스트 목적의 의도적 오류

---

## 저장 형식 예시

```markdown
### [2026-04-13 03:00] 해결됨
**메시지:** ModuleNotFoundError: No module named 'google.generativeai'
**컨텍스트:** image_gen.py 실행 중 발생
**해결 방법:** `pip install google-generativeai` 실행으로 해결
```

---

## 중요 원칙

- 오류 발생 → 기록은 **선택이 아닌 필수**
- 해결 후 업데이트 **생략 금지**
- 같은 오류가 반복되면 기존 항목에 "재발" 메모 추가
- `error_log.md`가 길어지면 해결된 오류는 `resolved_errors.md`로 이동
