import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import base64
import os
import subprocess
from datetime import datetime
from pathlib import Path

# .emv 파일에서 API 키 로드
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

MODEL_MAP = {
    "나노바나나 2": "gemini-3.1-flash-image-preview",
    "나노바나나2": "gemini-3.1-flash-image-preview",
    "flash": "gemini-3.1-flash-image-preview",
    "나노바나나 프로": "gemini-3-pro-image-preview",
    "나노바나나프로": "gemini-3-pro-image-preview",
    "pro": "gemini-3-pro-image-preview",
}

def resolve_model(model_str):
    return MODEL_MAP.get(model_str, model_str)

def main():
    parser = argparse.ArgumentParser(description="Gemini 이미지 생성")
    parser.add_argument("--prompt", required=True, help="이미지 프롬프트")
    parser.add_argument("--model", default="나노바나나 2", help="모델 선택")
    parser.add_argument("--ratio", default="16:9", help="이미지 비율 (1:1, 16:9, 4:3, 9:16)")
    parser.add_argument("--quality", default="2K", help="화질 (512, 1K, 2K, 4K)")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    model_id = resolve_model(args.model)
    print(f"모델: {model_id}")
    print(f"비율: {args.ratio}")
    print(f"화질: {args.quality}")
    print(f"프롬프트: {args.prompt[:80]}...")
    print()

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: google-genai 패키지가 필요합니다. 설치: pip install google-genai Pillow")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print("이미지 생성 중... (Gemini API 호출)")
    response = client.models.generate_content(
        model=model_id,
        contents=[args.prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=args.ratio,
                image_size=args.quality,
            ),
        ),
    )

    # OUTPUT 폴더 확인
    output_dir = Path(__file__).parent / "OUTPUT"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []

    for i, part in enumerate(response.parts):
        if part.inline_data is not None:
            try:
                img = part.as_image()
                img_path = output_dir / f"image_{timestamp}_{i+1}.png"
                img.save(str(img_path))
                saved_files.append(str(img_path))
                print(f"이미지 저장됨: {img_path}")
            except Exception:
                # as_image() 실패 시 raw bytes로 저장
                raw = part.inline_data.data
                if isinstance(raw, str):
                    raw = base64.b64decode(raw)
                img_path = output_dir / f"image_{timestamp}_{i+1}.png"
                with open(img_path, "wb") as f:
                    f.write(raw)
                saved_files.append(str(img_path))
                print(f"이미지 저장됨 (raw): {img_path}")
        elif part.text:
            print(f"텍스트 응답: {part.text}")

    if saved_files:
        print()
        print("생성 완료!")
        print(f"저장 경로: {output_dir}")
        for p in saved_files:
            print(f"  - {p}")
        # 생성된 이미지 자동으로 열기
        for p in saved_files:
            os.startfile(os.path.abspath(p))
    else:
        print("이미지가 생성되지 않았습니다. 응답 내용 확인 필요.")
        print(f"응답 파트 수: {len(response.parts)}")

if __name__ == "__main__":
    main()
