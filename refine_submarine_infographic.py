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

def load_image_bytes(path, mime_type):
    with open(path, "rb") as f:
        return f.read(), mime_type

def generate_refined_infographic(client, types, submarine_path, base_infographic_path, sub_mime, base_mime, label, output_dir):
    sub_bytes, sub_mime_type = load_image_bytes(submarine_path, sub_mime)
    base_bytes, base_mime_type = load_image_bytes(base_infographic_path, base_mime)

    prompt = (
        "You are a world-class military defense infographic designer. "
        "I'm providing two reference images:\n"
        "1. A high-quality 3D rendered black submarine (side view on white background)\n"
        "2. A submarine technical infographic with Korean text — use it as content/structure reference\n\n"
        "Create a HIGHLY POLISHED, SOPHISTICATED defense industry infographic. "
        "This should look like it belongs in a premium Korean defense publication or official navy briefing material.\n\n"

        "=== LAYOUT (16:9 widescreen) ===\n"
        "- Rich dark navy background with subtle technical grid overlay and faint radar/sonar circle motifs\n"
        "- Title bar at top with a thin accent line separator\n"
        "- LEFT COLUMN (25% width): vertical pictogram flow chain\n"
        "  * 5 circular icon cards stacked vertically with connecting arrows\n"
        "  * Each card: dark panel with glowing blue border, white line-art icon inside, Korean label below\n"
        "  * Icons represent the propulsion chain (fuel → engine/reactor → generator → motor → propeller)\n"
        "  * Connecting arrows with subtle glow effect between cards\n"
        "- CENTER+RIGHT (75% width): submarine operational scene\n"
        "  * Draw a horizontal water surface line across the middle with realistic ocean shading above/below\n"
        "  * Place 3–4 submarine renderings (from image 1) horizontally in a row, each at different depths\n"
        "  * Each submarine slightly smaller as it goes deeper, creating depth perspective\n"
        "  * Dashed depth-indicator lines dropping down from water surface to each submarine\n"
        "  * Korean state labels (수상항해, 스노클 심도, 잠항, 심심도 작전) above each submarine\n"
        "  * Curved arrows connecting each submarine showing the operational flow\n"
        "  * Annotate key submarine parts with thin callout lines (잠망경, 함교, 스크루 등)\n\n"

        "=== BOTTOM PANEL ===\n"
        "- Semi-transparent dark panel across the bottom\n"
        "- 3 stat blocks side by side, each with a small icon + bold Korean label + description text\n"
        "  (작전지속능력, 기동성능, 은밀성 및 생존성)\n\n"

        "=== VISUAL STYLE ===\n"
        "- Color palette: deep navy #0d1b2a, electric blue #1e90ff accents, steel gray #4a6fa5, white text\n"
        "- Subtle lens flare / glow effects on key elements\n"
        "- Typography: bold Korean title, medium weight labels, thin description text\n"
        "- All text in Korean (clean, properly spaced)\n"
        "- Professional, refined — NOT cartoony, NOT overcrowded\n"
        "- NO photo inserts of real engine parts\n\n"

        "Follow the content topic from image 2 (the reference infographic)."
    )

    print(f"\n[{label}] 인포그래픽 생성 중...")
    print(f"  잠수함: {submarine_path}")
    print(f"  베이스: {base_infographic_path}")

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[
            types.Part.from_bytes(data=sub_bytes, mime_type=sub_mime_type),
            types.Part.from_bytes(data=base_bytes, mime_type=base_mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []

    for i, part in enumerate(response.parts):
        if part.inline_data is not None:
            try:
                img = part.as_image()
                img_path = output_dir / f"submarine_infographic_{label}_{timestamp}.png"
                img.save(str(img_path))
                saved_files.append(str(img_path))
                print(f"  저장됨: {img_path}")
            except Exception:
                raw = part.inline_data.data
                if isinstance(raw, str):
                    raw = base64.b64decode(raw)
                img_path = output_dir / f"submarine_infographic_{label}_{timestamp}.png"
                with open(img_path, "wb") as f:
                    f.write(raw)
                saved_files.append(str(img_path))
                print(f"  저장됨 (raw): {img_path}")
        elif part.text:
            print(f"  텍스트 응답: {part.text}")

    return saved_files

def main():
    env = load_env()
    api_key = env.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: google-genai 패키지가 필요합니다. 설치: pip install google-genai Pillow")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    output_dir = Path(__file__).parent / "OUTPUT"
    output_dir.mkdir(exist_ok=True)

    all_saved = []

    # 이미지 1: imageB_0004 + IMG_8450 베이스
    files1 = generate_refined_infographic(
        client, types,
        submarine_path=r"c:\Users\user\Desktop\argos\imageB_0004.png",
        base_infographic_path=r"c:\Users\user\Downloads\IMG_8450.jpeg",
        sub_mime="image/png",
        base_mime="image/jpeg",
        label="01",
        output_dir=output_dir,
    )
    all_saved.extend(files1)

    # 이미지 2: imageB_0005 + IMG_8449 베이스
    files2 = generate_refined_infographic(
        client, types,
        submarine_path=r"c:\Users\user\Desktop\argos\imageB_0005.png",
        base_infographic_path=r"c:\Users\user\Downloads\IMG_8449.jpeg",
        sub_mime="image/png",
        base_mime="image/jpeg",
        label="02",
        output_dir=output_dir,
    )
    all_saved.extend(files2)

    print("\n=============================")
    print("모든 이미지 생성 완료!")
    print(f"저장 경로: {output_dir}")
    for p in all_saved:
        print(f"  - {p}")

    # 자동으로 이미지 열기
    for p in all_saved:
        os.startfile(os.path.abspath(p))

if __name__ == "__main__":
    main()
