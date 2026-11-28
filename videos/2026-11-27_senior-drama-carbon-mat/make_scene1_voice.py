"""시니어 드라마 B1(첫 장면) 대사 두 줄을 타입캐스트로 만든다.

영상 AI가 대사를 틀리게 만들 때 바꿔 넣거나, 입모양 맞추기 참고 음성으로 쓴다.
키는 저장소 규칙대로 환경 변수 TYPECAST_API_KEY → 맥 키체인 "typecast-api" 순서로 읽는다.

1) 목소리 후보 보기 (할머니 = 여성 elder, 사위 = 남성 young_adult·middle_age):
     python3 make_scene1_voice.py --list
2) 고른 목소리로 만들기:
     python3 make_scene1_voice.py --grandma tc_xxx --son tc_yyy
   → audio/B1_01_son.wav, audio/B1_02_grandma.wav
3) 요청 내용만 보기(키·크레딧 안 씀):
     python3 make_scene1_voice.py --grandma tc_xxx --son tc_yyy --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / ".claude" / "skills" / "reels" / "templates"))

from typecast_voice import (  # noqa: E402  저장소 공용 타입캐스트 코드를 그대로 쓴다
    USER_AGENT,
    NarrationError,
    TypecastSettings,
    _post,
    find_api_key,
    request_body,
)

VOICES_URL = "https://api.typecast.ai/v3/voices"

# (파일 이름, 역할, 대사) — scene1.md 대본과 글자 그대로 같아야 한다.
LINES = (
    ("B1_01_son", "son", "어머니, 보일러 좀 팍팍 트세요."),
    ("B1_02_grandma", "grandma", "그래, 니 맘대로 해라."),
)
CANDIDATE_FILTERS = (
    ("할머니 후보", {"gender": "female", "age": "elder"}),
    ("사위 후보(청년)", {"gender": "male", "age": "young_adult"}),
    ("사위 후보(중년)", {"gender": "male", "age": "middle_age"}),
)


def list_voices(api_key: str) -> None:
    for title, filters in CANDIDATE_FILTERS:
        query = urllib.parse.urlencode({"model": "ssfm-v31", **filters})
        request = urllib.request.Request(
            f"{VOICES_URL}?{query}", headers={"X-API-KEY": api_key, "User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            raise NarrationError(f"목소리 목록 요청 실패: 타입캐스트 {error.code}") from None
        voices = data if isinstance(data, list) else data.get("voices") or data.get("items") or []
        print(f"\n== {title} ({len(voices)}개)")
        for voice in voices:
            name = (voice.get("voice_name") or {}).get("kor", "?")
            uses = ", ".join(voice.get("use_cases") or [])
            print(f"{voice.get('voice_id')}  {name}  [{uses}]  {voice.get('preview_url') or ''}")


def make_lines(voices: dict[str, str], tempo: float, dry_run: bool) -> None:
    out_dir = HERE / "audio"
    texts = [text for _, _, text in LINES]
    api_key = "" if dry_run else find_api_key()
    for index, (stem, role, text) in enumerate(LINES):
        previous = texts[index - 1] if index > 0 else None
        following = texts[index + 1] if index + 1 < len(texts) else None
        body = request_body(text, TypecastSettings(voices[role], tempo), previous, following)
        if dry_run:
            print(json.dumps(body, ensure_ascii=False))
            continue
        wav = _post(body, api_key, urllib.request.urlopen, time.sleep)
        out_dir.mkdir(exist_ok=True)
        (out_dir / f"{stem}.wav").write_bytes(wav)
        print(f"만듦: audio/{stem}.wav  ({role}) {text}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="목소리 후보만 보여 준다")
    parser.add_argument("--grandma", help="할머니(장모님) 목소리 ID, tc_로 시작")
    parser.add_argument("--son", help="사위 목소리 ID, tc_로 시작")
    parser.add_argument("--tempo", type=float, default=1.0, help="말 빠르기 0.5~2.0")
    parser.add_argument("--dry-run", action="store_true", help="요청 내용만 출력")
    args = parser.parse_args()
    try:
        if args.list:
            list_voices(find_api_key())
            return 0
        if not (args.grandma and args.son):
            parser.error("--grandma 와 --son 목소리 ID를 함께 주세요. 먼저 --list 로 후보를 보세요.")
        make_lines({"grandma": args.grandma, "son": args.son}, args.tempo, args.dry_run)
    except (NarrationError, ValueError) as error:
        print(f"실패: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
