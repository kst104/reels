#!/bin/bash
# 2번 프레임 검증·렌더 (Chrome이 필요해 샌드박스 밖에서 실행)
set -u
. ~/Downloads/reels/.tools/env.sh
cd ~/Downloads/reels/OpenMontage/projects/jujube-tea-sugar-shorts/hyperframes
LOG=../render_log.txt; : > $LOG
for c in validate inspect; do echo "=== $c" >> $LOG; npx --yes hyperframes $c --json > ../hf_$c.json 2>>$LOG; echo "exit $?" >> $LOG; done
echo "=== snapshot" >> $LOG
npx --yes hyperframes snapshot --at 1.79,5.68,10.18,14.65,17.83,22.53,28.18,31.35,33.36,37.43 >> $LOG 2>&1; echo "exit $?" >> $LOG
echo "=== render" >> $LOG; S=$(date +%s)
npx --yes hyperframes render --output ../renders/final.mp4 --fps 30 --quality high --strict >> $LOG 2>&1; echo "exit $? seconds $(( $(date +%s)-S ))" >> $LOG
echo DONE >> $LOG
