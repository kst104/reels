# 시니어 드라마 「보일러는 니 맘대로」: 첫 장면(B1)만

- 홍보 상품: 한일의료기 탄소매트 1인용 (상점 표 `docs/shop-sync.md` 2절 7번 후보)
- 장르: 참교육 / 길이: 30초(2장면 중 B1, 15초) / 만드는 방법: 대사까지 나오는 영상 AI
- 사용자 요청(2026-11-27): "이미지를 먼저 보여주고, 첫장면만 먼저 뽑아줘. 다 만들지말고"
- 그래서 **B2 대본·영상 프롬프트·업로드 문구는 아직 쓰지 않았다.** B1을 보고 정한 뒤에 쓴다.

## 전체 줄거리 (한 줄, 방향만)

처가에 온 사위가 반팔 차림으로 장모님 집 보일러를 마음대로 올린다. 장모님은 "그래, 니 맘대로 해라" 하고는 밤에 보일러를 끈다. (B2 예정) 새벽, 사위는 이불을 말고 덜덜 떨고, 장모님만 탄소매트 위에서 귤을 까먹는다. 사위가 "그거 뭐예요?" 하면 장모님이 "니 거는 니가 사라." 하고, 다음 날 사위 이름으로 매트 상자가 줄줄이 도착한다.

- 「맞아 맞아」 포인트: 남의 집 보일러 온도를 마음대로 올리는 사람, 난방비 걱정하는 부모님
- 참교육 대상은 사위의 "남의 집 난방비 생각 안 하는 뻔뻔함" 하나만. 사위를 외모·직업으로 깎아내리지 않는다.

## 인물·장소 (이미지 완성)

| 이름 | 파일 | 설명 |
|---|---|---|
| C1 장모님 | `images/C1_grandma.png` | 75세 안팎, 은회색 짧은 파마머리, 은테 안경, 분홍 누빔 조끼 + 잔꽃무늬 블라우스, 회색 고무줄 바지, 베이지 양말. 경상도 말투, 무표정 속 살짝 웃는 얼굴 |
| C2 사위 | `images/C2_son-in-law.png` | 35세 안팎, 통통한 몸, 짧은 검은 머리, 흰 반팔 티, 회색 조거 바지, 맨발. 넉살 좋고 뻔뻔한 말투 |
| L1 장모님 집 거실 | `images/L1_living-room.png` | 오래된 아파트 거실, 밤, 노란 장판, 귤 바구니 놓인 접이식 나무 상, 짙은 나무 장식장, 벽시계, **문 옆 벽의 흰 보일러 조절기** |
| P1 상품 | 없음 (아래 "상품 사진" 참고) | B2에서 쓴다 |

- 이미지 생성: 허깅페이스 Z-Image-Turbo, 시드 C1 877041 / C2 432975 / L1 651050
- L1 오른쪽 칸(반대편)에는 프롬프트에 없던 흰 스탠드 에어컨이 생겼다. B1은 보일러 조절기 쪽만 찍으므로 그대로 둔다.

## 장면 B1 대본

```
장면 B1 (15초) · 장소: L1 · 등장: C1, C2
화면: 보일러 조절기 버튼을 누르는 손가락 클로즈업 → 반팔 차림 사위가 웃으며 돌아본다
      → 거실 문간에 팔짱 낀 장모님, 얼굴로 천천히 다가가는 카메라
      → 사위가 상 쪽으로 가자, 장모님이 조절기 앞으로 와서 전원을 "딸깍" 끈다
대사:
  사위: "어머니, 보일러 좀 팍팍 트세요."
  장모님: "그래, 니 맘대로 해라."
마지막 3초: 장모님 손가락이 전원 버튼을 누르고 조절기 불이 꺼진다. 장모님이 카메라를 슬쩍 보며 입꼬리만 올린다.
```

대사 점검: 2줄(3줄 이하), 받침이 꼬이는 말 없음, 상품 이름은 대사에 넣지 않음.

## 장면 B1 영상 프롬프트 (그대로 붙여 넣기)

생성 화면에서도 **길이 15초, 비율 9:16**으로 맞춘다. 참고 이미지는 `C1_grandma.png`, `C2_son-in-law.png`, `L1_living-room.png` 세 장을 붙인다.

```
15-second vertical 9:16 cinematic shot. Use reference images exactly as given: C1 grandmother sheet (C1_grandma.png), C2 son-in-law sheet (C2_son-in-law.png), L1 living room sheet (L1_living-room.png).
Keep faces, clothes, room layout exactly as in the references. Do not shorten or change this prompt.

Tone: deadpan Korean family comedy with a quiet thriller feel. Night, warm tungsten lamp light, slightly dim corners, slow deliberate camera moves.

0–3s: Close-up of the small white digital boiler thermostat on the wall beside the doorway. A man's finger presses the up button again and again with soft beeps. The display glows; numbers are not readable.
3–7s: Pull back to a medium shot. C2, the son-in-law in a white short-sleeve t-shirt and grey joggers, barefoot, turns toward the doorway with a cheeky grin.
C2 son-in-law (Korean, casual, cheerful): "어머니, 보일러 좀 팍팍 트세요."
7–11s: Cut to C1, the grandmother in the pink quilted vest, standing in the doorway with arms crossed. Slow push-in on her calm face behind silver-rimmed glasses.
C1 grandmother (Korean, Gyeongsang dialect, calm and low): "그래, 니 맘대로 해라."
11–15s: The son-in-law walks away toward the low table with the tangerine basket. The grandmother steps to the thermostat and presses the power button with one finger, a clear click. The display goes dark. She glances at the camera and gives a tiny one-sided smile. End on her face.

Rules: Korean dialogue exactly as written, lip-sync to the speaker. Only these two lines of dialogue.
No subtitles, no on-screen text, no background music.
```

## 만드는 순서 (크레딧 아끼기)

1. 위 이미지 세 장의 얼굴·옷·거실이 마음에 드는지 먼저 본다. 바꿀 곳이 있으면 말해 주면 그 이미지만 다시 만든다.
2. B1만 **낮은 화질(480p 등)**로 한 번 만들어 본다. B2는 아직 만들지 않는다.
3. 다 나오면 아래 표로 점검한다. 어긋난 곳만 고쳐 다시 만든다.

| 점검 | 볼 것 |
|---|---|
| 얼굴 | 장모님 안경·파마머리, 사위 통통한 얼굴이 이미지와 같은가 |
| 옷 | 분홍 누빔 조끼 / 흰 반팔 티·회색 바지·맨발 |
| 장소 | 문 옆 흰 보일러 조절기, 노란 장판, 귤 바구니 상 |
| 대사 | 두 줄이 글자 그대로 나오는가, 입모양이 말하는 사람과 맞는가 |
| 반전 | 마지막에 조절기 불이 꺼지고 장모님이 카메라를 보는가 |

- 쓰는 영상 도구가 15초를 못 만들면 알려 달라. 10초판으로 줄여 다시 쓴다.
- 이 세션에서는 영상을 직접 만들 수 없다. 연결된 힉스필드 커넥터는 작업 목록·크레딧 확인만 되고 생성은 안 된다.

## 대사 음성 (타입캐스트, 선택)

영상 AI가 대사를 틀리게 만들 때 바꿔 넣을 음성을 `make_scene1_voice.py`로 만든다. 키가 있는 맥미니에서 돌린다.

```bash
python3 make_scene1_voice.py --list
python3 make_scene1_voice.py --grandma tc_할머니ID --son tc_사위ID
```

- `--list`는 할머니(여성 elder)·사위(남성 young_adult, middle_age) 후보의 ID, 이름, 미리듣기 주소를 보여 준다. 사투리를 낼 수 있는지는 API 정보로 알 수 없어서 미리듣기로 골라야 한다.
- 결과: `audio/B1_01_son.wav`, `audio/B1_02_grandma.wav`

## 상품 사진(P1): B2 전에 필요한 것

- 상품의 실제 색·무늬·온도조절기·상자 모양을 **확인하지 못했다.** 스마트스토어 상품 페이지가 로그인 화면으로 넘어가서 열리지 않았다.
- 블로그 후기 두 편은 서로 다른 판매 페이지를 가리켜, 그 글의 "베이지색", "다이얼 조절기" 설명이 이 상품 것이라고 단정할 수 없다.
- 그래서 P1은 AI로 지어내지 않는다. 광고 영상이라 실제와 다른 생김새를 보여 주면 안 되기 때문이다. **상점(브랜드 커넥트)에 등록한 그 상품의 대표 사진을 받아서** P1로 쓴다.
- 대사·자막에 "전자파 없는" 같은 효능 문구는 넣지 않는다. 블로그 후기에 그런 말이 있지만 근거(인증 이름·시험 결과)를 확인하지 못했다.
- 쇼핑 커넥트 등록 여부: 한 블로그의 상품 링크(naver.me/Gnt9RIKh)가 브랜드 커넥트 제휴 주소(channelProductNo=12554272168)로 이어진다. 쇼핑 커넥트 상품일 가능성은 있지만, 우리 상점에서 링크를 발급할 수 있는지는 사용자가 브랜드 커넥트에서 확인해야 한다.
