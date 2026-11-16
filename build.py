#!/usr/bin/env python3
"""data/*.yml 로 site/index.html 을 만든다.

    python3 build.py           # site/index.html 갱신
    python3 build.py --check   # 자료 검사 + site/index.html 이 최신인지 확인(다르면 종료 1)
"""
import html
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site" / "index.html"
TEMPLATE = ROOT / "site" / "template.html"

FIELDS = [  # (값, 분야 이름, 요약표 머리)
    ("pqc", "양자내성암호 (PQC)", "PQC"),
    ("zkp", "영지식 증명 (ZKP)", "ZKP"),
    ("fhe", "완전 동형암호 (FHE)", "FHE"),
    ("ntt", "PQC·FHE 공통 연산 (NTT)", "공통(NTT)"),
]
FIELD_KEYS = [f[0] for f in FIELDS]
DEVICES = {"gpu", "tpu", "npu"}
PARTS = [  # (kind, 앵커, 제목)
    ("conference", "conf", "학회"),
    ("journal", "jour", "저널"),
    ("preprint", "preprint", "예비 공개본"),
]
PREPRINT_LEAD = "학회·저널 게재를 확인하지 못한 IACR ePrint·arXiv 원고다."
VENUE_KEYS = {"id", "abbr", "name", "kind", "group", "bk21", "kiise"}
PAPER_KEYS = {"title", "authors", "year", "venue", "field", "device", "url", "gpu_partial", "note",
              "scheme", "ops", "sys_opt", "focus"}
VOCAB_OF = {"pqc": "pqc", "zkp": "zkp", "fhe": "fhe", "ntt": "pqc"}  # 분야 → 이름표(공통 NTT 편은 PQC 이름표)
GUIDE_TITLE = {"pqc": "PQC 방식과 부하 연산", "zkp": "ZKP 증명 체계 계열과 부하 연산", "fhe": "FHE 방식과 부하 연산"}


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


def load():
    venues = yaml.safe_load((ROOT / "data" / "venues.yml").read_text(encoding="utf-8"))
    papers = yaml.safe_load((ROOT / "data" / "papers.yml").read_text(encoding="utf-8"))
    tax = yaml.safe_load((ROOT / "data" / "taxonomy.yml").read_text(encoding="utf-8"))
    so_keys = [x["key"] for x in tax["sys_opts"]]
    errors = []
    ids = set()
    for v in venues:
        extra = set(v) - VENUE_KEYS
        if extra:
            errors.append(f"출판처 {v.get('id')}: 모르는 칸 {sorted(extra)}")
        for k in ("id", "abbr", "kind"):
            if not v.get(k):
                errors.append(f"출판처 {v}: {k} 가 비었다")
        if v.get("id") in ids:
            errors.append(f"출판처 id 중복: {v['id']}")
        ids.add(v.get("id"))
        if v.get("kind") not in {p[0] for p in PARTS}:
            errors.append(f"출판처 {v.get('id')}: kind 는 conference·journal·preprint 중 하나")
        if v.get("kind") != "preprint" and not v.get("group"):
            errors.append(f"출판처 {v.get('id')}: group 이 비었다")
        if v.get("kiise") not in (None, "최우수", "우수"):
            errors.append(f"출판처 {v.get('id')}: kiise 는 최우수·우수 중 하나")
        if v.get("bk21") not in (None, 1, 2, 3, 4):
            errors.append(f"출판처 {v.get('id')}: bk21 은 1~4")
    seen = {}
    for i, p in enumerate(papers):
        where = f"논문 {i + 1}번째({p.get('title', '?')[:40]})"
        extra = set(p) - PAPER_KEYS
        if extra:
            errors.append(f"{where}: 모르는 칸 {sorted(extra)}")
        for k in ("title", "authors", "year", "venue", "field", "device"):
            if not p.get(k):
                errors.append(f"{where}: {k} 가 비었다")
        if "url" not in p:
            errors.append(f"{where}: url 칸이 없다(없으면 null)")
        if p.get("venue") not in ids:
            errors.append(f"{where}: venue '{p.get('venue')}' 가 venues.yml 에 없다")
        if p.get("field") not in FIELD_KEYS:
            errors.append(f"{where}: field 는 {FIELD_KEYS} 중 하나")
        if p.get("device") not in DEVICES:
            errors.append(f"{where}: device 는 {sorted(DEVICES)} 중 하나")
        if not isinstance(p.get("year"), int):
            errors.append(f"{where}: year 는 정수")
        if not isinstance(p.get("authors"), list):
            errors.append(f"{where}: authors 는 목록([이름, 이름])")
        voc = tax["fields"].get(VOCAB_OF.get(p.get("field"), ""), {})
        for k, allowed in (("scheme", [x["key"] for x in voc.get("schemes", [])]),
                           ("ops", [x["key"] for x in voc.get("ops", [])])):
            vals = p.get(k)
            if not isinstance(vals, list) or not vals:
                errors.append(f"{where}: {k} 목록이 필요하다")
            elif set(vals) - set(allowed):
                errors.append(f"{where}: {k} 의 {sorted(set(vals) - set(allowed))} 가 data/taxonomy.yml 의 "
                              f"{VOCAB_OF.get(p.get('field'))} 이름표에 없다")
        if "sys_opt" in p:
            vals = p["sys_opt"]
            if not isinstance(vals, list) or not vals:
                errors.append(f"{where}: sys_opt 는 비어 있지 않은 목록(없으면 칸을 지운다)")
            elif set(vals) - set(so_keys):
                errors.append(f"{where}: sys_opt 의 {sorted(set(vals) - set(so_keys))} 가 data/taxonomy.yml 에 없다")
        if "focus" in p and not isinstance(p["focus"], str):
            errors.append(f"{where}: focus 는 한 줄 문자열")
        key = " ".join(str(p.get("title", "")).lower().split())
        if key in seen:
            errors.append(f"{where}: 제목이 {seen[key]}번째 논문과 같다")
        seen[key] = i + 1
    if errors:
        sys.exit("자료 오류:\n  " + "\n  ".join(errors))
    return venues, papers, tax


def labels_of(tax, field):
    voc = tax["fields"][VOCAB_OF[field]]
    return ({x["key"]: x["label"] for x in voc["schemes"]}, {x["key"]: x["label"] for x in voc["ops"]},
            {x["key"]: x["label"] for x in tax["sys_opts"]})


def paper_li(p, tax):
    q = p["title"].lower() + " " + ", ".join(a.lower() for a in p["authors"])
    sl, ol, so = labels_of(tax, p["field"])
    sys_opt = p.get("sys_opt", [])
    q += " " + " ".join([sl[k] for k in p["scheme"]] + [ol[k] for k in p["ops"]] + [so[k] for k in sys_opt]).lower()
    vf = VOCAB_OF[p["field"]]
    sattr = f' data-s="{" ".join(vf + ":" + k for k in p["scheme"])}"'
    extra = ('<span class="zk">' + "".join(f'<span class="sys s-{vf}">{esc(sl[k])}</span>' for k in p["scheme"])
             + "".join(f'<span class="op">{esc(ol[k])}</span>' for k in p["ops"])
             + "".join(f'<span class="so">{esc(so[k])}</span>' for k in sys_opt) + "</span>")
    if p.get("focus"):
        q += " " + p["focus"].lower()
        extra += f'<span class="fo">{esc(p["focus"])}</span>'

    au = p["authors"][0] + (" 외" if len(p["authors"]) > 1 else "")
    title = esc(p["title"])
    if p["url"]:
        title = f'<a href="{attr(p["url"])}" target="_blank" rel="noopener">{title}</a>'
    tags = ""
    if p.get("gpu_partial"):
        tags += '<span class="tag tag-part">GPU 평가 포함</span>'
    if p.get("note"):
        tags += f'<span class="tag">{esc(p["note"])}</span>'
    return (f'<li data-d="{p["field"]}"{sattr} data-q="{attr(q)}"><span class="yr">{p["year"]}</span>'
            f'<span class="ti">{title}<span class="au">{esc(au)}</span>{tags}{extra}</span></li>')


def venue_section(v, ps, tax):
    head = f'<h4>{esc(v["abbr"])}</h4>'
    if v.get("bk21"):
        head += (f'<span class="bk bk{v["bk21"]}" title="BK21플러스 IF (2018) {v["bk21"]}점">'
                 f'BK {v["bk21"]}</span>')
    if v.get("kiise"):
        cls = "ks ks1" if v["kiise"] == "최우수" else "ks"
        head += f'<span class="{cls}" title="한국정보과학회 (2024) {v["kiise"]}">정보과학회 {v["kiise"]}</span>'
    head += f'<span class="vn">{esc(v.get("name") or "")}</span><span class="vc">{len(ps)}편</span>'
    idattr = "" if v["kind"] == "preprint" else f' id="v-{v["id"]}"'
    body = ""
    for key, label, _ in FIELDS:
        fp = sorted((p for p in ps if p["field"] == key), key=lambda p: (-p["year"], p["title"].lower()))
        if not fp:
            continue
        body += (f'<div class="dom" data-d="{key}"><h5><span class="dot d-{key}"></span>{label} '
                 f'<span class="cnt">{len(fp)}</span></h5><ul>' + "".join(paper_li(p, tax) for p in fp) + "</ul></div>")
    return f'<section class="venue"{idattr}><header class="vh">{head}</header>{body}</section>'


def render(venues, papers, tax):
    papers = [p for p in papers if p["device"] == "gpu"]
    by_venue = {}
    for p in papers:
        by_venue.setdefault(p["venue"], []).append(p)
    parts_html = []
    rows = []  # (제목, 분야별 수)
    for kind, anchor, title in PARTS:
        vs = [v for v in venues if v["kind"] == kind and by_venue.get(v["id"])]
        if not vs:
            continue
        n = sum(len(by_venue[v["id"]]) for v in vs)
        s = f'  <section class="part" id="{anchor}"><h2>{title} <span class="cnt">{n}편</span></h2>'
        if kind == "preprint":
            rows.append((title, Counter(p["field"] for v in vs for p in by_venue[v["id"]])))
            s += f'<p class="lead">{PREPRINT_LEAD}</p><div class="venues">'
            s += "".join(venue_section(v, by_venue[v["id"]], tax) for v in vs) + "</div>"
        else:
            groups = []
            for v in vs:
                if v["group"] not in groups:
                    groups.append(v["group"])
            for g in groups:
                gv = [v for v in vs if v["group"] == g]
                rows.append((f"{title} · {g}", Counter(p["field"] for v in gv for p in by_venue[v["id"]])))
                s += f'<h3>{esc(g)}</h3><div class="venues">'
                s += "".join(venue_section(v, by_venue[v["id"]], tax) for v in gv) + "</div>"
        parts_html.append(s + "</section>")

    def cells(c):
        return "".join(f"<td>{c[k] or '·'}</td>" for k in FIELD_KEYS) + f'<td class="sum">{sum(c.values())}</td>'
    total = Counter(p["field"] for p in papers)
    table = ('<div class="tablewrap"><table class="mat"><thead><tr><th>구분</th>'
             + "".join(f"<th>{h}</th>" for _, _, h in FIELDS) + "<th>계</th></tr></thead><tbody>"
             + "".join(f'<tr class=""><th>{esc(t)}</th>{cells(c)}</tr>' for t, c in rows)
             + f'<tr class="total"><th>합계</th>{cells(total)}</tr></tbody></table></div>')
    kpis = f"      <span>전체 <b>{len(papers)}</b>편</span>\n" + "\n".join(
        f'      <span><i class="dot d-{k}"></i>{h} <b>{total[k]}</b></span>' for k, _, h in FIELDS[:3])
    guide = ('  <section class="guide" id="guide"><h2>방식·연산·최적화 표시</h2>'
             '<p class="lead">논문마다 구현·평가한 방식(색 테두리), 가속한 연산(회색 바탕), 시스템 관점 최적화(점선 테두리), '
             '핵심 아이디어(아래 줄)를 적었습니다. 여러 방식으로 평가한 논문은 방식을 여럿 적었습니다. '
             '아래 표의 부하 연산은 각 방식에서 시간을 많이 쓰는 연산과 그 근거입니다.</p>')
    options = ""
    for f in ("pqc", "zkp", "fhe"):
        fp = [p for p in papers if VOCAB_OF[p["field"]] == f]
        cnt = Counter(k for p in fp for k in p["scheme"])
        schemes = [x for x in tax["fields"][f]["schemes"] if cnt[x["key"]]]
        guide += (f'<h3><span class="dot d-{f}"></span>{GUIDE_TITLE[f]}</h3>'
                  '<div class="tablewrap"><table class="mat"><thead><tr><th>방식</th><th>부하 연산</th><th>편수</th></tr></thead><tbody>'
                  + "".join(f'<tr><th>{esc(x["label"])}</th><td>{esc(x["load"])}</td><td class="n">{cnt[x["key"]]}</td></tr>'
                            for x in schemes) + "</tbody></table></div>")
        options += (f'<optgroup label="{f.upper()}">'
                    + "".join(f'<option value="{f}:{x["key"]}">{esc(x["label"])} ({cnt[x["key"]]})</option>' for x in schemes)
                    + "</optgroup>")
    socnt = {f: Counter(k for p in papers if VOCAB_OF[p["field"]] == f for k in p.get("sys_opt", [])) for f in ("pqc", "zkp", "fhe")}
    guide += ('<h3>시스템 관점 최적화</h3><p class="lead">연산 알고리즘 자체가 아니라 실행 구조·자원 활용을 바꾼 최적화입니다.</p>'
              '<div class="tablewrap"><table class="mat"><thead><tr><th>항목</th><th>뜻</th><th>PQC</th><th>ZKP</th><th>FHE</th></tr></thead><tbody>'
              + "".join(f'<tr><th><span class="so">{esc(x["label"])}</span></th><td>{esc(x["desc"])}</td>'
                        + "".join(f'<td class="n">{socnt[f][x["key"]] or "·"}</td>' for f in ("pqc", "zkp", "fhe")) + "</tr>"
                        for x in tax["sys_opts"] if any(socnt[f][x["key"]] for f in socnt))
              + "</tbody></table></div></section>")
    select = ('    <select id="sys" aria-label="방식으로 거르기"><option value="all">방식 전체</option>' + options + "</select>")
    tpl = TEMPLATE.read_text(encoding="utf-8")
    return (tpl.replace("{{kpis}}", kpis).replace("{{table}}", table).replace("{{guide}}", guide)
            .replace("{{sysselect}}", select).replace("{{parts}}", "\n".join(parts_html)))


def main():
    venues, papers, tax = load()
    out = render(venues, papers, tax)
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != out:
            sys.exit("site/index.html 이 data/ 와 다르다 — python3 build.py 로 다시 만들어 함께 커밋한다")
        print(f"검사 통과: 논문 {len(papers)}편, 출판처 {len(venues)}곳")
        return
    OUT.write_text(out, encoding="utf-8")
    print(f"site/index.html 생성: 논문 {len(papers)}편")


if __name__ == "__main__":
    main()
