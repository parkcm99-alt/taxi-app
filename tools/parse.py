#!/usr/bin/env python3
"""docs/*.md → questions.json  (파서 규격: id, subject, q, choices, answer, exp)"""
import re, json, glob, os, sys

DOCS = "/Users/parkyoungsun/Desktop/taxi-app/docs"
MARKS = "①②③④"

# 텍스트 기출 과목 경계 (문항 번호 기준)
#   Q1  ~ Q99  : 1 법규
#   Q100~ Q???  : 2 안전운행요령
#   Q???~ Q240 : 3 운송서비스   ← TEXT_SVC_START 는 Codex 판정 후 확정
TEXT_SAFE_START = 100
TEXT_SVC_START  = 173         # Q173부터 운송서비스

FILES = [
    ("택시_기출_텍스트_Q001-Q070_승인본.md", "t-", "text"),
    ("택시_기출_텍스트_Q071-Q160.md", "t-", "text"),   # Codex 작업물 (없으면 자동 skip)
    ("택시_기출_텍스트_Q161-Q240.md", "t-", "text"),   # Codex 작업물 (없으면 자동 skip)
    ("택시_CBT_제1회_70문항.md", "c1-", "cbt"),
    ("택시_CBT_제2회_70문항.md", "c2-", "cbt"),
    ("택시_CBT_제3회_70문항.md", "c3-", "cbt"),
    ("택시_CBT_제4회_70문항.md", "c4-", "cbt"),
    ("택시_CBT_제5회_70문항.md", "c5-", "cbt"),
    ("택시_CBT_제6회_70문항.md", "c6-", "cbt"),
    ("택시_CBT_제7회_70문항.md", "c7-", "cbt"),
]

def subject_for(kind, qn):
    if kind == "text":
        if TEXT_SVC_START and qn >= TEXT_SVC_START: return 3
        if qn >= TEXT_SAFE_START: return 2
        return 1
    if qn <= 20:  return 1
    if qn <= 40:  return 2
    if qn <= 60:  return 3
    return 4

def clean(s):
    s = s.replace("**", "")
    s = s.replace(" (정답)", "").replace("(정답)", "")
    return s.strip()

def parse_file(path, prefix, kind):
    raw = open(path, encoding="utf-8").read()
    body = raw.split("## ✅ 정답표")[0]
    out, errs = [], []
    blocks = re.split(r"^### Q(\d+)([^\n]*)$", body, flags=re.M)
    for i in range(1, len(blocks), 3):
        qn = int(blocks[i]); flags = blocks[i + 1]; seg = blocks[i + 2]
        lines = [l for l in seg.split("\n") if l.strip()]
        qtext, extra, choiceline, exp = None, [], None, []
        for l in lines:
            ls = l.strip()
            if ls.startswith(">"):
                exp.append(ls.lstrip("> ").strip()); continue
            if choiceline is None and re.match(r"^\*?\*?[①②③④]", ls):
                choiceline = ls; continue
            if choiceline is None:
                if qtext is None and ls.startswith("**"):
                    qtext = clean(ls)
                else:
                    extra.append(ls)
        if qtext is None or choiceline is None:
            errs.append((prefix, qn, "문제/선택지 파싱 실패")); continue
        if extra:
            qtext = qtext + "\n" + " ".join(extra)
        parts = choiceline.split(" · ")
        if len(parts) != 4:
            errs.append((prefix, qn, f"선택지 {len(parts)}개")); continue
        choices, answer = [], None
        for idx, p in enumerate(parts):
            p = p.strip()
            if "(정답)" in p:
                if answer is not None:
                    errs.append((prefix, qn, "정답 2개 이상"))
                answer = idx
            c = clean(p)
            if not c or c[0] not in MARKS:
                errs.append((prefix, qn, f"선택지 기호 이상: {c[:12]}")); break
            choices.append(c[1:].strip())
        else:
            if answer is None:
                errs.append((prefix, qn, "정답 없음")); continue
            out.append({
                "id": f"{prefix}{qn:02d}",
                "subject": subject_for(kind, qn),
                "q": qtext,
                "choices": choices,
                "answer": answer,
                "exp": " ".join(exp),
                "img": f"{prefix}{qn:02d}" if "🖼" in flags else None,
            })
    return out, errs

def main():
    allq, allerr = [], []
    for fn, prefix, kind in FILES:
        p = os.path.join(DOCS, fn)
        if not os.path.exists(p):
            print(f"{fn:45s}   -   (미작성 · skip)"); continue
        q, e = parse_file(p, prefix, kind)
        allq += q; allerr += e
        print(f"{fn:45s} {len(q):3d}문항  오류 {len(e)}")
    print(f"\n총 {len(allq)}문항")
    from collections import Counter
    print("과목별:", dict(sorted(Counter(x['subject'] for x in allq).items())))
    print("그림 문항:", [x['id'] for x in allq if x['img']])
    ids = [x['id'] for x in allq]
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup: print("!! 중복 ID:", dup)
    if allerr:
        print("\n!! 오류:")
        for e in allerr: print("  ", e)
    json.dump(allq, open(sys.argv[1], "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

main()
