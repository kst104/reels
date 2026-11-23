#!/bin/bash
D="$HOME/Library/Application Support/open-generative-ai/local-ai"
OUT="$(cd "$(dirname "$0")" && pwd)/assets/images"
gen() { # id seed prompt
  [ -s "$OUT/$1.png" ] && return
  T=$(date +%s)
  DYLD_LIBRARY_PATH="$D/bin" "$D/bin/sd-cli" --diffusion-model "$D/models/z_image_turbo-Q4_K.gguf" \
    --llm "$D/models/Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf" --vae "$D/models/ae.safetensors" \
    -p "$3" -o "$OUT/$1.png" --steps 8 -H 1280 -W 720 --cfg-scale 1.0 --seed "$2" \
    --sampling-method euler --scheduler simple > "$OUT/$1.log" 2>&1
  echo "$1 exit $? $(( $(date +%s)-T ))s"
}
gen c1 101 "Realistic photograph, a hand holding a clear plastic water bottle about to pour water into the open water tank of a white home humidifier, cozy winter living room, soft daylight, vertical composition, no text, no logos"
gen c2 102 "Realistic photograph, kitchen counter with two clear glasses of water side by side, one being filled from a kitchen faucet and one from a countertop water purifier spout, bright clean kitchen, vertical composition, no text, no logos"
gen c3 103 "Realistic photograph, several plain clear gallon jugs of water with blank white labels on a shelf next to a small white humidifier, soft light, vertical composition, no text, no logos"
gen c4 104 "Realistic close-up photograph, cool white mist streaming from the nozzle of an ultrasonic humidifier, backlit against a dark background showing fine floating droplets and particles, vertical composition, no text, no logos"
gen c5 105 "Realistic photograph, hands emptying old water from a humidifier water tank into a kitchen sink, water splashing, morning light, vertical composition, no text, no logos"
gen c6 106 "Realistic photograph, hands in rubber gloves washing a humidifier water tank with a soft sponge and soapy water in a sink, rinsing water running, clean bright bathroom, vertical composition, no text, no logos"
gen c7 107 "Realistic photograph, a small white humidifier releasing gentle mist on a bedside table in a cozy warm bedroom at night, soft lamp light, an analog hygrometer dial nearby with no readable numbers, vertical composition, no text, no logos"
echo ALL DONE
