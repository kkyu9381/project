import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
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

UPSCALE_MODEL = "imagen-3.0-upscale-001"

def resolve_model(model_str):
    return UPSCALE_MODEL

def main():
    parser = argparse.ArgumentParser(description="Gemini 이미지 업스케일링")
    parser.add_argument("--input", required=True, help="원본 이미지 경로")
    parser.add_argument("--model", default="나노바나나 2", help="모델 선택")
    parser.add_argument("--quality", default="2K", help="화질 (2K, 4K)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: 입력 이미지를 찾을 수 없습니다: {input_path}")
        sys.exit(1)

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
        print("ERROR: 필수 패키지 설치 필요: pip install google-genai Pillow")
        sys.exit(1)

    # 원본 이미지 로드 및 정보 확인
    orig_img = Image.open(str(input_path))
    orig_w, orig_h = orig_img.size
    print(f"원본 이미지: {input_path.name}")
    print(f"원본 크기: {orig_w} x {orig_h}")
    print(f"모델: {resolve_model(args.model)}")
    print(f"목표 화질: {args.quality}")
    print()

    client = genai.Client(api_key=api_key)

    # 이미지를 bytes로 읽기
    img_bytes = input_path.read_bytes()
    suffix = input_path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    mime_type = mime_map.get(suffix, "image/jpeg")

    # 화질 → 목표 너비 매핑
    target_widths = {"2K": 2560, "4K": 3840, "1K": 1280}
    target_w = target_widths.get(args.quality.upper(), 2560)
    scale = target_w / orig_w
    target_h = int(orig_h * scale)

    print(f"목표 크기: {target_w} x {target_h} (배율: {scale:.1f}x)")
    print()

    # Gemini image editing: 이미지 + 프롬프트 → 고화질 이미지 출력
    gemini_model = "gemini-2.0-flash-exp"
    upscale_prompt = (
        f"Upscale this image to {target_w}x{target_h} pixels. "
        "Maximize sharpness and detail. Preserve all original content, text, colors, and layout exactly. "
        "Output only the upscaled image with no changes to composition."
    )

    print(f"Gemini 이미지 편집 시도 중... (모델: {gemini_model})")

    gemini_success = False
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type=mime_type),
                upscale_prompt,
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        gemini_parts_with_image = [p for p in response.parts if p.inline_data is not None]
        if gemini_parts_with_image:
            gemini_success = True
    except Exception as e:
        print(f"Gemini 편집 실패: {e}")
        print("고화질 PIL 업스케일링으로 전환합니다...")

    # OUTPUT 폴더에 저장
    output_dir = Path(__file__).parent / "OUTPUT"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = input_path.stem
    saved_files = []

    if gemini_success:
        for i, part in enumerate(response.parts):
            if part.inline_data is not None:
                try:
                    img = part.as_image()
                    out_path = output_dir / f"{stem}_upscaled_{args.quality}_{timestamp}.png"
                    img.save(str(out_path))
                    saved_files.append(str(out_path))
                    new_w, new_h = img.size
                    print(f"업스케일 완료 (Gemini): {new_w} x {new_h}")
                    print(f"저장됨: {out_path}")
                except Exception:
                    raw = part.inline_data.data
                    if isinstance(raw, str):
                        raw = base64.b64decode(raw)
                    out_path = output_dir / f"{stem}_upscaled_{args.quality}_{timestamp}.png"
                    with open(out_path, "wb") as f:
                        f.write(raw)
                    saved_files.append(str(out_path))
                    print(f"저장됨 (raw): {out_path}")
    else:
        # PIL 고화질 업스케일링 (LANCZOS + 샤프닝)
        from PIL import ImageFilter, ImageEnhance
        print(f"PIL LANCZOS 업스케일링 중... ({orig_w}x{orig_h} → {target_w}x{target_h})")
        upscaled = orig_img.resize((target_w, target_h), Image.LANCZOS)
        # 선명도 강화
        upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))
        upscaled = ImageEnhance.Sharpness(upscaled).enhance(1.3)
        out_path = output_dir / f"{stem}_upscaled_{args.quality}_{timestamp}.png"
        upscaled.save(str(out_path), "PNG", optimize=True)
        saved_files.append(str(out_path))
        new_w, new_h = upscaled.size
        print(f"업스케일 완료 (PIL LANCZOS): {new_w} x {new_h}")
        print(f"저장됨: {out_path}")

    if saved_files:
        print()
        print("업스케일링 완료!")
        for p in saved_files:
            os.startfile(os.path.abspath(p))
    else:
        print("이미지가 생성되지 않았습니다.")
        print(f"응답 파트 수: {len(response.parts)}")

if __name__ == "__main__":
    main()
