#!/usr/bin/env python3
"""make_episode — ONE command for the validated v8 pipeline.

script.txt -> ElevenLabs voice(+timestamps) -> Higgsfield face -> HeyGen Avatar IV talking
-> coherent multicam edit (crop SAME render: wide/medium/close, ~2.8s cuts) -> word-pop captions
-> Higgsfield Sonilo music -> final 9:16 mp4. (See operations winning-formula-talking-human.)

This is the deterministic 'factory' the cheap agentic loop calls. No LLM cost here.
Usage: episode.py --script FILE --out DIR [--face-prompt "..."] [--reuse] [--no-upload]
Keys from operations/.secrets/.env. Requires: node CLIs (higgsfield, heygen) on PATH, /tmp/ffmpeg, uv.
"""
import json, os, subprocess, sys, base64, urllib.request, argparse, shlex

KEYCHAIN = os.environ.get("KEYCHAIN", "/config/workspace/operations/.secrets/.env")
FF = os.environ.get("FFMPEG", "/tmp/ffmpeg")
FONTS = os.environ.get("FONTS", "/tmp/fonts")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # ElevenLabs George (British storyteller)

def key(name):
    for ln in open(KEYCHAIN):
        if ln.startswith(name + "="):
            return ln.split("=", 1)[1].strip()
    raise SystemExit(f"missing key {name}")

def sh(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode:
        sys.stderr.write(f"\nCMD FAILED: {' '.join(map(str,cmd))[:200]}\n{p.stderr[-1500:]}\n")
        raise SystemExit(1)
    return p.stdout

def ff(args):  # ffmpeg helper
    sh([FF, "-y", *map(str, args)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--face-prompt", default="Photorealistic cinematic film still, distinguished sophisticated man in his late 50s, mature not elderly, salt-and-pepper hair and short beard, tailored charcoal three-piece suit, wood-paneled study, warm window light, looking at camera, 85mm, no text")
    ap.add_argument("--reuse", action="store_true", help="reuse voice/face/talking if present")
    ap.add_argument("--no-upload", action="store_true")
    a = ap.parse_args()
    O = a.out; os.makedirs(O, exist_ok=True)
    os.makedirs(FONTS, exist_ok=True)
    if not os.path.exists(f"{FONTS}/Anton-Regular.ttf"):
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf", f"{FONTS}/Anton-Regular.ttf")
    script = open(a.script).read().strip()

    # 1) VOICE + word timestamps (ElevenLabs)
    if not (a.reuse and os.path.exists(f"{O}/voice.mp3")):
        body = json.dumps({"text": script, "model_id": "eleven_multilingual_v2",
                           "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "use_speaker_boost": True}})
        out = sh(["curl","-s","-X","POST",
                  f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128",
                  "-H", f"xi-api-key: {key('ELEVENLABS_API_KEY')}", "-H","Content-Type: application/json","-d", body])
        d = json.loads(out)
        open(f"{O}/voice.mp3","wb").write(base64.b64decode(d["audio_base64"]))
        json.dump(d["alignment"], open(f"{O}/alignment.json","w"))
    al = json.load(open(f"{O}/alignment.json")); VO_END = al["character_end_times_seconds"][-1]

    # 2) FACE (Higgsfield Nano Banana Pro)
    if not (a.reuse and os.path.exists(f"{O}/face.png")):
        out = sh(["higgsfield","generate","create","nano_banana_2","--prompt",a.face_prompt,
                  "--aspect_ratio","9:16","--resolution","2k","--wait","--wait-timeout","5m","--wait-interval","4s","--json"])
        url = json.loads(out)[0]["result_url"]; urllib.request.urlretrieve(url, f"{O}/face.png")

    # 3) TALKING (HeyGen Avatar IV: image + our VO audio)
    env = {**os.environ, "HEYGEN_API_KEY": key("HEYGEN_API_KEY")}
    if not (a.reuse and os.path.exists(f"{O}/talking.mp4")):
        img_id = json.loads(sh(["heygen","asset","create","--file",f"{O}/face.png"], env=env))["data"]["asset_id"]
        aud_id = json.loads(sh(["heygen","asset","create","--file",f"{O}/voice.mp3"], env=env))["data"]["asset_id"]
        vbody = json.dumps({"type":"image","image":{"type":"asset_id","asset_id":img_id},
                            "audio_asset_id":aud_id,"aspect_ratio":"9:16","resolution":"720p","expressiveness":"high"})
        out = sh(["heygen","video","create","-d",vbody,"--wait","--timeout","20m"], env=env)
        import re
        m = re.findall(r'"video_url"\s*:\s*"([^"]+)"', out)
        if not m: raise SystemExit(f"no video_url in heygen output: {out[-400:]}")
        vurl = m[-1].replace("\\u0026", "&").replace("\\/", "/")
        urllib.request.urlretrieve(vurl, f"{O}/talking.mp4")

    # 4) COHERENT multicam edit (crop the SAME talking render; lip-sync preserved)
    FRZ = {"wide":1.0,"medium":1.18,"close":1.42}
    cyc = ["medium","wide","close","medium","close","wide","medium","close"]
    def vf(z):
        if z<=1.0: return "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setpts=PTS-STARTPTS"
        cw=int(720/z)//2*2; ch=int(1280/z)//2*2; x=(720-cw)//2; y=int((1280-ch)*0.30)//2*2
        return f"crop={cw}:{ch}:{x}:{y},scale=720:1280,fps=30,setpts=PTS-STARTPTS"
    bounds=[]; t=0.0
    while t < VO_END-0.4: bounds.append((round(t,3), round(min(t+2.8,VO_END),3))); t+=2.8
    with open(f"{O}/ce.txt","w") as lf:
        for i,(s,e) in enumerate(bounds):
            ff(["-ss",s,"-i",f"{O}/talking.mp4","-t",round(e-s,3),"-vf",vf(FRZ[cyc[i%len(cyc)]]),
                "-an","-c:v","libx264","-preset","medium","-pix_fmt","yuv420p",f"{O}/ce_{i}.mp4"])
            lf.write(f"file 'ce_{i}.mp4'\n")
    ff(["-f","concat","-safe","0","-i",f"{O}/ce.txt","-c","copy",f"{O}/ce_video.mp4"])

    # 5) WORD-POP captions (karaoke ASS)
    words=[]; cur=""; cs=None; ce=None
    for ch,s,e in zip(al["characters"],al["character_start_times_seconds"],al["character_end_times_seconds"]):
        if ch.isspace():
            if cur: words.append([cur,cs,ce]); cur=""; cs=None
        else:
            if cs is None: cs=s
            cur+=ch; ce=e
    if cur: words.append([cur,cs,ce])
    def tc(t): return f"{int(t//3600):01d}:{int(t%3600//60):02d}:{t%60:05.2f}"
    Y=r"{\c&H00FFFF&}"; W=r"{\c&HFFFFFF&}"
    lines=[words[i:i+3] for i in range(0,len(words),3)]
    hdr=("[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\nScaledBorderAndShadow: yes\n"
         "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
         "Style: Pop,Anton,60,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,5,2,2,60,60,250,1\n"
         "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    ev=[]
    for li,line in enumerate(lines):
        lend = lines[li+1][0][1] if li+1<len(lines) else line[-1][2]
        for wi,w in enumerate(line):
            b = line[wi+1][1] if wi+1<len(line) else lend
            if b<=w[1]: b=w[1]+0.05
            txt=" ".join((Y+x[0].upper()+W) if j==wi else x[0].upper() for j,x in enumerate(line))
            ev.append(f"Dialogue: 0,{tc(w[1])},{tc(b)},Pop,,0,0,0,,{txt}")
    open(f"{O}/captions.ass","w").write(hdr+"\n".join(ev)+"\n")

    # 6) MUSIC (Higgsfield Sonilo)
    if not (a.reuse and os.path.exists(f"{O}/music.mp3")):
        out = sh(["higgsfield","generate","create","sonilo_music","--prompt",
                  "Subtle elegant aspirational instrumental underscore, soft piano and warm strings, restrained, slow, no drums, background bed",
                  "--duration",str(int(VO_END)+1),"--wait","--wait-timeout","6m","--wait-interval","4s","--json"])
        urllib.request.urlretrieve(json.loads(out)[0]["result_url"], f"{O}/music.mp3")

    # 7) FINAL mux
    ff(["-i",f"{O}/ce_video.mp4","-i",f"{O}/talking.mp4","-i",f"{O}/music.mp3","-filter_complex",
        "[2:a]volume=0.10[bg];[1:a][bg]amix=inputs=2:normalize=0:duration=first[a];"
        f"[0:v]subtitles={O}/captions.ass:fontsdir={FONTS}[v]",
        "-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-shortest",f"{O}/episode.mp4"])
    print(f"[done] {O}/episode.mp4")

if __name__ == "__main__":
    main()
