import re,sys,collections
f=sys.argv[1]; official=sys.argv[2]
off={}
for tok in official.split():
    off[int(tok[:2])]=tok[2]
txt=open(f).read()
print("### Q 개수:", len(re.findall(r"^### Q\d+", txt, flags=re.M)))
print("(정답) 개수:", txt.count("(정답)"))
missing=[i for i in range(1,71) if not re.search(rf"^### Q{i}( |$)", txt, flags=re.M)]
print("누락:", missing if missing else "없음")
blocks=re.split(r"^### Q(\d+).*$", txt, flags=re.M)
bad=[]; found={}
for i in range(1,len(blocks),2):
    qn=int(blocks[i]); body=blocks[i+1]
    m=re.search(r"\*\*([①②③④])[^\n]*?\(정답\)\*\*", body)
    if not m: bad.append((qn,"정답 마크 없음")); continue
    found[qn]=m.group(1)
    if off.get(qn)!=m.group(1): bad.append((qn,f"본문 {m.group(1)} vs 확정 {off.get(qn)}"))
print("본문 문항수:", len(found), "| 본문↔확정표 불일치:", bad if bad else "없음")
tbl=re.findall(r"(\d{2})([①②③④])\s", txt.split("## ✅ 정답표")[1])
tb={int(a):b for a,b in tbl}
diff=[(k,tb.get(k),off[k]) for k in off if tb.get(k)!=off[k]]
print("정답표 블록:", len(tb), "| 확정표 불일치:", diff if diff else "없음")
c=collections.Counter(tb.values())
print("분포:", {k:(c[k], f"{c[k]/70*100:.1f}%") for k in "①②③④"})
