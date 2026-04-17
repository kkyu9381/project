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
    input_image_path = r"c:\Users\user\Desktop\argos\1x\대지 1 사본.png"
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

    with open(input_image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "이 잠수함 인포그래픽 이미지의 하단에 있는 3개의 픽토그램 박스(작전지속능력, 기동성능, 은밀성 및 생존성)만 시각적으로 더 인상적이고 강조되게 개선해줘. "
        "다음 개선 사항을 적용해줘:\n"
        "1. 픽토그램 아이콘(시계, 프로펠러, 방패+눈)에 밝은 황금색(gold) 또는 밝은 청록색 발광 효과(glow) 추가\n"
        "2. 아이콘의 테두리와 내부 선을 더 밝고 선명하게 강조\n"
        "3. 픽토그램 박스 배경을 약간 더 밝게 하여 강조\n"
        "4. 전체적으로 '최고 성능', '무제한', '우월함'을 시각적으로 표현\n"
        "5. 텍스트(작전지속능력, 기동성능, 은밀성 및 생존성, 설명 텍스트)는 절대 변경하지 말 것\n"
        "6. 배경(바다, 잠수함, 상단 핵추진 흐름도)은 절대 변경하지 말 것\n"
        "7. 픽토그램 3개 박스만 더 밝고 인상적으로 변경"
    )

    print(f"모델: {model_id}")
    print(f"입력 이미지: {input_image_path}")
    print()
    print("핵추진 픽토그램 개선 중... (Gemini API 호출)")

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
                img_path = output_dir / f"nuclear_improved_{timestamp}_{i+1}.png"
                img.save(str(img_path))
                saved_files.append(str(img_path))
                print(f"이미지 저장됨: {img_path}")
            except Exception:
                raw = part.inline_data.data
                if isinstance(raw, str):
                    raw = base64.b64decode(raw)
                img_path = output_dir / f"nuclear_improved_{timestamp}_{i+1}.png"
                with open(img_path, "wb") as f:
                    f.write(raw)
                saved_files.append(str(img_path))
                print(f"이미지 저장됨 (raw): {img_path}")
        elif part.text:
            print(f"텍스트 응답: {part.text}")

    if saved_files:
        print()
        print("개선 완료!")
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
