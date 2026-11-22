"""문장별 M1 음성 → 앞뒤 무음 제거 → 0.3/0.6/0.8초 간격으로 이음 → loudnorm → narration_timings.json"""
import sys,subprocess,re,json
FF,FP=sys.argv[1],sys.argv[2]
def dur(f): return float(subprocess.run([FP,'-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def bounds(f):
    d=dur(f)
    err=subprocess.run([FF,'-hide_banner','-i',f,'-af','silencedetect=noise=-35dB:d=0.05','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',err)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',err)]
    start=en[0] if st and st[0]<0.01 and en else 0.0
    end=d
    if st and st[-1]>start and (len(en)<len(st) or en[-1]>=d-0.02): end=st[-1]
    return max(0,start-0.08), min(d,end+0.08), d
segs=[]
for i in range(1,7):
    s,e,d=bounds(f'lines/s{i}_M1.wav'); segs.append((s,e)); print(i,round(s,3),round(e,3),round(d,3))
inputs=[]; filt=[]; t=0.3; secs=[]
for i,(s,e) in enumerate(segs,1):
    inputs+=['-i',f'lines/s{i}_M1.wav']
    filt.append(f'[{i-1}:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}]')
    L=e-s; secs.append({'id':f's{i}','start':round(t,3),'end':round(t+L,3)}); t+=L+(0.6 if i<6 else 0.8)
total=round(t,3)
filt.append('anullsrc=r=44100:cl=mono,atrim=0:0.3[lead]'); filt.append('anullsrc=r=44100:cl=mono,atrim=0:0.6,asplit=5[g1][g2][g3][g4][g5]'); filt.append('anullsrc=r=44100:cl=mono,atrim=0:0.8[tail]')
order='[lead]'+''.join(f'[a{i}]'+(f'[g{i}]' if i<6 else '') for i in range(1,7))+'[tail]'
filt.append(order+'concat=n=13:v=0:a=1[cat]')
subprocess.run([FF,'-y','-loglevel','error',*inputs,'-filter_complex',';'.join(filt),'-map','[cat]','-ar','44100','-ac','1','narration_edited.wav'],check=True)
subprocess.run([FF,'-y','-loglevel','error','-i','narration_edited.wav','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','44100','-ac','1','narration_norm.wav'],check=True)
print('edited',dur('narration_edited.wav'),'norm',dur('narration_norm.wav'),'calc',total)
json.dump({'total':total,'sections':secs,'note':'문장별 M1 음성(7790) 앞뒤 무음 제거(-35dB, 여유 0.08초) 뒤 앞 0.3초·문장 사이 0.6초·끝 0.8초로 이음, loudnorm I=-16:TP=-1.5:LRA=11'},open('narration_timings.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(secs))
