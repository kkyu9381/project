# 🎨 Gemini 이미지 생성 프로젝트

이 프로젝트는 Claude Code 스킬과 Gemini API를 통합하여 고품질 이미지를 자동으로 생성하는 시스템입니다.

## 📋 프로젝트 개요

- **목표:** Claude Code 스킬 호출 시마다 Gemini API를 사용하여 이미지 자동 생성
- **모델:** Gemini 3.1 Flash 또는 3.0 Pro
- **결과:** JSON 형식의 메타데이터와 함께 `generated_images/` 폴더에 저장

## 🚀 구현된 3가지 방법

### 방법 1️⃣: 스킬 프롬프트 통합 (권장)
**파일:** `SKILL.MD`

사용자가 스킬을 호출하면:
1. 4가지 정보 수집 (주제, 비율, 모델, 화질)
2. `generate_image.py` 자동 실행
3. 결과 표시

```bash
# 자동 실행 명령어
python3 generate_image.py --prompt "$PROMPT" --ratio "$RATIO" --model "$MODEL" --quality "$QUALITY" --num_images 1
```

**장점:** 간단하고 직관적, 사용자 친화적

---

### 방법 2️⃣: 설정 파일 훅 (자동화)
**파일:** `.vscode/settings.json`

Claude Code의 설정 파일에 훅을 등록:
- `onSkillInvoke`: 스킬 호출 시 자동 실행
- `claudeCode.imageGeneration`: 이미지 생성 설정
- `claudeCode.environment`: 환경 변수 자동 로드

**장점:** 가장 자동화된 방식, 깔끔한 구조

---

### 방법 3️⃣: Python 래퍼 스크립트 (유연함)
**파일:** `image_wrapper.py` + `generate_image.py`

두 스크립트의 조합:
- `image_wrapper.py`: JSON 입력을 받아 `generate_image.py` 호출
- `generate_image.py`: 실제 Gemini API 호출 및 실행

```python
# JSON 입력 예시
{
    "prompt": "노을 지는 바다",
    "ratio": "16:9",
    "model": "gemini-3.1-flash-image-preview",
    "quality": "2K"
}
```

**장점:** 가장 유연하고 확장 가능, 프로그래매틱 호출 가능

---

## 📁 파일 구조

```
D:/project/
├── .emv                      # 환경 변수 (GEMINI_API_KEY)
├── .vscode/
│   └── settings.json         # Claude Code 설정 (방법 2)
├── CLAUDE.md                 # 이 파일
├── SKILL.MD                  # 스킬 프롬프트 (방법 1)
├── GEMINI IMAGE.PY           # 레거시 스크립트
├── generate_image.py         # 메인 Python 스크립트 (방법 1, 3)
├── image_wrapper.py          # 래퍼 스크립트 (방법 3)
└── generated_images/         # 생성된 이미지 저장 폴더 (자동 생성)
    └── image_20260413_*.json # 생성 결과
```

## 🔧 사용 방법

### 방법 1: Claude Code 스킬 호출
```
사용자: "멋진 풍경 사진 만들어줘"
→ SKILL.MD의 프롬프트가 실행
→ 4가지 정보 수집
→ generate_image.py 자동 실행
→ 결과 표시
```

### 방법 2: 자동 훅 실행 (설정 파일)
```
스킬 호출 시:
→ .vscode/settings.json의 훅 자동 실행
→ generate_image.py 호출
→ 환경 변수 자동 로드
```

### 방법 3: Python 스크립트 직접 호출
```bash
# 커맨드라인에서
python3 generate_image.py \
  --prompt "노을 지는 바다" \
  --ratio "16:9" \
  --model "gemini-3.1-flash-image-preview" \
  --quality "2K"

# 또는 래퍼를 통해
python3 image_wrapper.py '{"prompt": "...", "model": "..."}'
```

## 🔐 환경 변수 설정

**.emv 파일에 다음 내용이 필수:**
```
GEMINI_API_KEY=your_api_key_here
```

## 📊 모델 매핑

| 한글명 | 영문명 | 모델명 |
|--------|--------|--------|
| 나노바나나 2 | Flash | `gemini-3.1-flash-image-preview` |
| 나노바나나 프로 | Pro | `gemini-3.0-pro` |

## 🎯 화질 및 비율

**화질:**
- `2K`: 고해상도 2K
- `4K`: 초고해상도 4K

**비율:**
- `1:1`: 정사각형
- `16:9`: 와이드 화면
- `4:3`: 표준

## 📦 설치 및 준비

### 1. Python 패키지 설치
```bash
pip install google-generativeai
```

### 2. API 키 설정
`.emv` 파일에서 `GEMINI_API_KEY` 확인

### 3. 각 방법 선택
- **방법 1:** `/이미지생성` 스킬 호출 (권장)
- **방법 2:** 자동 훅 (설정 완료됨)
- **방법 3:** 커맨드라인 또는 Python에서 직접 호출

## 🔍 트러블슈팅

### API 키 오류
```
❌ GEMINI_API_KEY가 설정되지 않았습니다
```
→ `.emv` 파일에서 API 키 확인

### Python 패키지 오류
```
❌ google-generativeai 패키지 설치 필요
```
→ `pip install google-generativeai` 실행

### 스크립트 실행 오류
```bash
# generate_image.py 직접 테스트
python3 generate_image.py --prompt "test" --model "gemini-3.1-flash-image-preview"
```

## 💡 팁

1. **프롬프트 최적화:** 구체적이고 자세한 설명일수록 좋음
2. **비율 선택:** 목적에 맞게 선택 (포스터: 16:9, 프로필: 1:1)
3. **모델 선택:** 빠른 생성은 Flash, 품질은 Pro
4. **결과 확인:** `generated_images/` 폴더에서 JSON 메타데이터 확인

## 📂 OUTPUT 폴더 규칙

**모든 생성 결과물은 반드시 `D:/project/OUTPUT/` 폴더에 저장해야 합니다.**

- 이미지, JSON 메타데이터, 스크립트 실행 결과물 등 모든 산출물 포함
- 스크립트가 다른 경로에 저장하도록 되어 있다면 `OUTPUT/`으로 수정할 것
- Claude가 직접 파일을 생성할 때도 `OUTPUT/` 폴더 사용
- `OUTPUT/` 폴더는 없으면 자동 생성됨 (`Path("OUTPUT").mkdir(exist_ok=True)`)

---

## 🧠 메모리 규칙 (Claude Code 공식 메모리 시스템)

메모리 디렉토리: `C:/Users/user/.claude/projects/D--project/memory/`

> 상세 오류 처리 규칙: `.claude/rules/error_handling.md` 참고
> 자동 훅: `.claude/settings.json` (PostToolUse → `error_hook.py`)

**언제 메모리에 저장해야 하는가:**

1. **오류/에러 발생 시** — 도구 실행 오류 즉시 기록 (훅이 자동 감지, Claude도 직접 기록)
2. **오류 해결 시** — 해결 즉시 해결 방법 업데이트 (절대 생략 금지)
3. **중요한 프로젝트 결정** — 모델 변경, 파일 구조 변경, API 방식 변경 등
4. **사용자 피드백** — 선호하는 작업 방식, 하지 말아야 할 것 등

**오류 기록 형식 (error_log.md):**

```markdown
### [YYYY-MM-DD HH:MM] 미해결
**메시지:** (오류 원문 요약)
**컨텍스트:** (어떤 작업 중 발생했는지)
**해결 방법:** (미기록)
```

**오류 해결 후 업데이트:**
- `C:/Users/user/.claude/projects/D--project/memory/error_log.md` → Edit 도구로 수정
- `미해결` → `해결됨`, `(미기록)` → 실제 해결 방법

**MEMORY.md 인덱스 유지:**
- 새 토픽 파일 생성 시 `MEMORY.md`에 한 줄 항목 추가
- 형식: `- [제목](파일명.md) — 한 줄 설명`

---

## 📝 예시

```
사용자: "멋진 풍경 사진 만들어줘"

Claude: "네, 멋진 풍경 이미지를 제작해 드릴게요!
1. 상세 주제: 어떤 풍경인가요?
2. 비율: 원하시는 비율?
3. 모델: 나노바나나 2(빠름) 또는 프로(정교함)?
4. 화질: 2K 또는 4K?"

사용자: "노을 지는 바다 / 16:9 / 나노바나나 2 / 2K"

Claude: "🎨 이미지 생성 중...
[python3 generate_image.py 자동 실행]
✅ 생성 완료!
📁 저장 경로: generated_images/image_20260413_123456.json"
```

---

**최종 업데이트:** 2026-04-13
