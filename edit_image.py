import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import base64
import os
from datetime import datetime
from pathlib import Path

def load_env():
    env = {}
    emv_path = Path(__file__).parent / ".emv"
    if emv_path.exists():
        with open(emv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def main():
    input_image_path = r"c:\Users\user\Desktop\argos\화면 캡처 2026-04-15 165531.png"
    model_id = "gemini-3.1-flash-image-preview"

    env = load_env()
    api_key = env.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError:
        print("ERROR: google-genai 또는 Pillow 패키지가 필요합니다.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # 원본 이미지 로드
    with open(input_image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "이 이미지의 하단 튤립 꽃들만 알록달록하게 바꿔줘. "
        "빨강, 주황, 노랑, 초록, 파랑, 보라, 분홍 등 다양한 색상으로 각 튤립을 다르게 색칠해줘. "
        "배경, 텍스트, 캐릭터, 롤러코스터 등 나머지 요소는 전혀 변경하지 말고 원본 그대로 유지해줘."
    )

    print(f"모델: {model_id}")
    print(f"입력 이미지: {input_image_path}")
    print(f"프롬프트: {prompt}")
    print()
    print("이미지 편집 중... (Gemini API 호출)")

    response = client.models.generate_content(
        model=model_id,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    output_dir = Path(__file__).parent / "OUTPUT"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []

    for i, part in enumerate(response.parts):
        if part.inline_data is not None:
            try:
                img = part.as_image()
                img_path = output_dir / f"edited_{timestamp}_{i+1}.png"
                img.save(str(img_path))
                saved_files.append(str(img_path))
                print(f"이미지 저장됨: {img_path}")
            except Exception:
                raw = part.inline_data.data
                if isinstance(raw, str):
                    raw = base64.b64decode(raw)
                img_path = output_dir / f"edited_{timestamp}_{i+1}.png"
                with open(img_path, "wb") as f:
                    f.write(raw)
                saved_files.append(str(img_path))
                print(f"이미지 저장됨 (raw): {img_path}")
        elif part.text:
            print(f"텍스트 응답: {part.text}")

    if saved_files:
        print()
        print("편집 완료!")
        print(f"저장 경로: {output_dir}")
        for p in saved_files:
            print(f"  - {p}")
        for p in saved_files:
            os.startfile(os.path.abspath(p))
    else:
        print("이미지가 생성되지 않았습니다.")
        print(f"응답 파트 수: {len(response.parts)}")

if __name__ == "__main__":
    main()
