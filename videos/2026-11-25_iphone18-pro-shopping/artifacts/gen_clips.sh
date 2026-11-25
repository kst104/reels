#!/bin/bash
# 힉스필드 Seedance 2.5, 720p, 1:1, 5초, 소리 없음. 실제 사진을 첫 화면으로 쓴다(6번만 글자 프롬프트).
KEEP="Keep the phone exactly as in the image: same shape, same cameras, same color. No text, no logos added, no new objects."
gen() { # id photo prompt
  if [ "$2" = "-" ]; then
    url=$(higgsfield generate create seedance_2_5 --mode t2v --prompt "$3" --duration 5 --resolution 720p --aspect_ratio 1:1 --generate_audio false --wait --wait-timeout 20m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  else
    url=$(higgsfield generate create seedance_2_5 --mode omni_reference --start-image "assets/images/src/$2" --prompt "$3 $KEEP" --duration 5 --resolution 720p --aspect_ratio 1:1 --generate_audio false --wait --wait-timeout 20m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  fi
  if [ -n "$url" ]; then curl -sSL -o "assets/video/$1.mp4" "$url" && echo "$1 ok $url"; else echo "$1 FAILED"; fi
}
gen s1 w01.jpg "Slow cinematic orbit around this silver smartphone on a table, soft light reflections sliding over the back." &
gen s2 w10.jpg "Gentle slow push-in on these two smartphones side by side, soft natural light." &
gen s3 w09.jpg "Subtle handheld camera drift, evening light, calm city atmosphere, the phone stays steady." &
gen s4 w06.jpg "Slow push-in on the phone screen top area, soft screen glow, very subtle motion." &
gen s6 - "Night city street with bright lamps and car headlights showing crisp starburst rays, slow smooth camera pan, photographed through a phone camera, realistic, no people's faces, no text." &
gen s7 w03.jpg "Slow smooth camera slide along this black smartphone, soft studio light sweeping across." &
gen s8 w02.jpg "Slow cinematic rotation around this smartphone, clean bright studio light." &
gen s9 w08.jpg "Slow push-in on this smartphone box on a table, warm soft light, calm unboxing mood." &
wait
