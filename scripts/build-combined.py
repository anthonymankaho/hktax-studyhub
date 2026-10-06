#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build "HK Tax Study Hub - Combined.html" as a single self-contained file.

Frame follows HKICPA_Study_Platform.html: sticky topbar, a MAIN card index,
one tab-panel per page, jump-search and a dark-mode toggle. Each panel keeps
the page's own two-column shell (sidebar TOC + content).

Everything is read from the clean sources under pages/ and assets/, so the
em-dash corruption in earlier hand-built combined files cannot come back.
Run from the project root:  python scripts/build-combined.py
"""

import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "HK Tax Study Hub - Combined.html")
OUT_WEB = os.path.join(ROOT, "combined.html")
# The published site's landing page IS this app. The old hand-written
# multi-file hub used to live here; its card blurbs now live in PAGES[*]["en"],
# so there is one landing page instead of two that drift apart.
OUT_INDEX = os.path.join(ROOT, "index.html")

BUILD_DATE = "6 October 2026"
IRD_READ_DATE = "6 October 2026"

# One entry per tab panel. `en` is the card blurb on the MAIN index; `zh` is the
# Chinese summary shown both on the card and at the head of the panel.
PAGES = [
    dict(id="ird-updates", src="ird-updates.html", group="Start here",
         label="IRD What's New", label_zh="稅務局最新消息",
         en="Everything on IRD's What's New page, read against this Hub and marked enacted, bill or proposed — with the exact page each item changed. Last read 6 October 2026 (1 Jun – 30 Sep 2026).",
         zh="整理稅務局「最新消息」所載事項，標明哪些已成為法例、哪些仍屬草案或政策建議，以及本平台已據此更新的頁面。",
         kw="ird what's new news policy address updates bills"),
    dict(id="acca-tx-hkg", src="acca-tx-hkg.html", group="Start here",
         label="ACCA TX-HKG", label_zh="ACCA TX-HKG 考試",
         en="Syllabus mapped to this Hub, what the examining team reports as weak, and original practice questions in the exam's own format — 15 MCQs plus three Section B questions, worked on the current basis with the exam-year figure alongside. Verified links to ACCA's own papers.",
         zh="考試大綱對應本平台頁面、考官報告所指的弱項，以及依考試格式原創的練習題（15 條 MCQ 及三條 Section B），以現行年度計算並並列考試年度數字。附已驗證的 ACCA 官方連結。",
         kw="acca tx-hkg f6 exam syllabus mcq section a b examiner report past paper practice"),
    dict(id="question-bank", src="question-bank.html", group="Start here",
         label="Question Bank A", label_zh="題庫 A",
         en="ACCA TX-HKG Section A — a filterable practice bank of 282 original multiple-choice questions across all five syllabus areas. Select an answer and check it for a Correct/Incorrect verdict and a live score. Every computational answer and distractor is generated from the Hub's own tax-computation module, so the arithmetic cannot drift from the explanation. Filter by area, topic or difficulty, search by keyword or section, or pull a shuffled Random 15.",
         zh="ACCA TX-HKG 題庫 Section A：282 條原創選擇題，涵蓋五個考試範疇，可按範疇、主題或難度篩選。選好答案後按核對即會顯示對錯並即時計分。所有涉及計算的題目及其錯誤選項均由本平台的稅務計算模組產生，確保數字與解釋一致，亦支援關鍵字搜尋及隨機抽15題練習。",
         kw="question bank practice questions mcq acca tx-hkg section a random quiz filter score"),
    dict(id="question-bank-b", src="question-bank-b.html", group="Start here",
         label="Question Bank B", label_zh="題庫 B",
         en="ACCA TX-HKG Section B — 3 original OT case scenarios (15 linked questions, 30 marks), matching the exam's own case-question format: one set of facts, five questions against it, spanning more than one syllabus area at once. Same select-and-check scoring as Section A.",
         zh="ACCA TX-HKG 題庫 Section B：3 個原創個案情境（合共15條相連題目，30分），仿照考試的個案題格式——同一組資料，五條相關問題，橫跨多於一個考試範疇。計分方式與 Section A 相同。",
         kw="question bank section b ot case questions mixed partnership scenario"),
    dict(id="question-bank-c", src="question-bank-c.html", group="Start here",
         label="Question Bank C", label_zh="題庫 C",
         en="ACCA TX-HKG Section C — 2 original constructed-response questions (15 marks + 25 marks), matching the exam's own format: full scenario, a graded model answer laid out as a real computation, marks allocated line by line.",
         zh="ACCA TX-HKG 題庫 Section C：2 條原創長題目（15分及25分），仿照考試格式——完整情境、附詳細評分準則的計算過程模範答案。",
         kw="question bank section c constructed response long question model answer"),
    dict(id="computation-formats", src="computation-formats.html", group="Start here",
         label="Computation Formats", label_zh="計算格式",
         en="The pro-forma layout for each tax in one place — property, salaries, profits, depreciation allowances and personal assessment — with what belongs on each line and a worked example apiece. Textbook layouts, re-checked against IRD.",
         zh="五種稅的標準計算格式集於一頁：物業稅、薪俸稅、利得稅、摺舊免稅額及個人入息課稅，逐行說明並各配一條例題。格式取自教科書，並已對照稅務局核新。",
         kw="computation format pro-forma layout template proforma exam"),
    dict(id="tax-reconciliation", src="tax-reconciliation.html", group="Start here",
         label="Tax Reconciliation", label_zh="稅務調節",
         en="The exam's favourite question: a wrong profits tax or personal assessment computation, ten notes, produce the revised one. Two full illustrations with note-by-note working, the revised computation and a reconciliation that closes exactly.",
         zh="考試最常見的題型：給一份錯誤的利得稅或個人入息課稅計算表及十項附註，要求重新編製。兩條完整例題，逐項分析、修正後計算表及完全吐合的調節表。",
         kw="reconciliation reconcile wrong computation revised adjustment exam notes bookkeeper"),
    dict(id="transaction-checker", src="transaction-checker.html", group="Start here",
         label="Transaction Checker", label_zh="交易稅務檢查器",
         en="Search any transaction by keyword to confirm Taxable / Non-taxable / Deductible / Non-deductible / Dutiable, with the exact section and a link to the full explanation — the working tool for tax computation analysis.",
         zh="按交易或會計項目快速查看可能屬於應課稅、非應課稅、可扣稅、不可扣稅或須繳印花稅，並連回相關章節。",
         kw="transaction checker taxable deductible dutiable search"),
    dict(id="dipn-index", src="dipn-index.html", group="Start here",
         label="DIPN Index", label_zh="DIPN 索引",
         en="All 73 currently-in-force DIPN/SOIPN/EDOIPN documents, searchable by number, topic or keyword, with a summary and worked-example flag — each row linking to IRD's own PDF.",
         zh="列出 IRD DIPN、SOIPN 及 EDOIPN 文件，方便按編號、主題或關鍵字搜尋，每行並連結至稅務局官方 PDF。",
         kw="dipn soipn edoipn index practice notes"),

    dict(id="profits-tax", src="profits-tax.html", group="Tax types",
         label="Profits Tax", label_zh="利得稅",
         en="Territorial source principle, two-tiered rates, taxable/non-taxable receipts, deductible/non-deductible expenses, FSIE, Patent Box, computation template.",
         zh="涵蓋香港來源原則、兩級制稅率、應課稅收入、扣稅開支、虧損、FSIE、Patent Box 及基本計算格式。",
         kw="profits tax source two-tiered fsie patent box"),
    dict(id="profits-tax-entities", src="profits-tax-entities.html", group="Tax types",
         label="Profits Tax by Entity", label_zh="利得稅：三種實體",
         en="One charge under s.14, three different computations: sole proprietorship, partnership and corporation. Covers s.17(2) payments to owners and their spouses, partnership allocation and reallocation, corporate partners and the apportioned two-tier band, and which owners can carry their share into personal assessment.",
         zh="同一條段，三種不同計算：獨資、合夥及法團。涵蓋 s.17(2) 對業主及其配偶的支付、合夥利潤分配與重新分配、法團合夥人與兩級制稅階的攝分，以及哪類業主可將分潤納入個人入息課稅。",
         kw="sole proprietor partnership corporation entity allocation corporate partner s17(2) s16AA bir51 bir52"),
    dict(id="salaries-tax", src="salaries-tax.html", group="Tax types",
         label="Salaries Tax", label_zh="薪俸稅",
         en="Progressive rates vs. standard rate cap, personal allowances, deduction ceilings, territorial source and the 60-day rule, personal assessment election.",
         zh="涵蓋香港受僱工作、入息、福利、可扣除支出、個人免稅額、標準稅率上限及個人入息課稅銜接。",
         kw="salaries tax employment allowances personal assessment"),
    dict(id="property-tax", src="property-tax.html", group="Tax types",
         label="Property Tax", label_zh="物業稅",
         en="Chargeable persons, net assessable value, the 20% statutory repair allowance, and the interaction with profits tax (corporate set-off / exemption).",
         zh="說明物業稅的納稅人、租金收入、差餉、20% 法定修葺免稅額、不可收回租金及公司業主與利得稅的互動。",
         kw="property tax net assessable value rates repairs"),
    dict(id="personal-assessment", src="personal-assessment.html", group="Tax types",
         label="Personal Assessment", label_zh="個人入息課稅",
         en="Not a tax but an election: aggregates property, business and employment income into one computation at progressive rates after allowances. Eligibility, the 2018/19 separate-election change, time limits, the standard-rate cap, and when electing actually costs money.",
         zh="並非稅種，而是一項選擇：把物業、業務及受僱入息合併計算，按累進稅率並扣除免稅額。涵蓋資格、2018/19 年起可分開選擇的改動、時限、標準稅率上限，以及甚麼情況下選擇反而更貴。",
         kw="personal assessment election s41 aggregate progressive allowances ir76c"),
    dict(id="stamp-duty", src="stamp-duty.html", group="Tax types",
         label="Stamp Duty", label_zh="印花稅",
         en="Share transfers, property (AVD/BSD/SSD), leases and partnership admission — including the 2026 amendment ordinances.",
         zh="說明印花稅以文書為課稅對象，涵蓋物業、股票、租約、BSD/SSD、關聯公司寬免及上訴程序。",
         kw="stamp duty avd bsd ssd shares lease"),
    dict(id="depreciation-allowances", src="depreciation-allowances.html", group="Tax types",
         label="Depreciation & Allowances", label_zh="折舊及免稅額",
         en="Industrial and commercial buildings allowances, plant and machinery pools, initial/annual/balancing allowances and charges.",
         zh="整理工業/商業建築物免稅額、機械及設備、初期/每年免稅額、結餘課稅/免稅額及特定資產即時扣除。",
         kw="depreciation allowances buildings plant machinery pooling"),
    dict(id="ird-administration", src="ird-administration.html", group="Tax types",
         label="IRD Administration", label_zh="稅務局行政",
         en="Returns and filing, assessment and estimated assessment, objections and appeals, penalties, holdover of provisional tax, plus AEOI and crypto-asset reporting.",
         zh="涵蓋報稅、評稅、估計評稅、反對、上訴、暫繳稅緩繳、罰則、稅務調查，以及自動交換財務帳戶資料與加密資產申報。",
         kw="ird administration returns assessment objection penalties aeoi carf"),

    dict(id="profits-tax-return-guide", src="profits-tax-return-guide.html", group="Returns",
         label="Profits Tax Return Guide", label_zh="利得稅報稅表指南",
         en="Box-by-box walkthrough of BIR51 (corporations), plus how BIR52 (persons other than corporations) and BIR54 (non-residents) differ — tied back to the Profits Tax and Depreciation pages.",
         zh="把 BIR51/52/54 的欄位與稅務計算邏輯連接，說明哪些資料要填在報稅表，哪些屬於另附稅務計算。",
         kw="profits tax return guide bir51 bir52 bir54"),
    dict(id="profits-tax-return-finder", src="profits-tax-return-finder.html", group="Returns",
         label="Profits Tax Return Box Finder", label_zh="利得稅報稅表欄位搜尋",
         en="Keyword search over every box on BIR51, BIR52 and BIR54, including the supplementary forms — for when you know the figure but not which box it belongs in.",
         zh="用關鍵字尋找 BIR51、BIR52、BIR54 欄位，適合在準備報稅表或溫習 supplementary forms 時使用。",
         kw="bir box finder supplementary forms"),

    dict(id="profits-tax-illustrations", src="profits-tax-illustrations.html", group="Worked illustrations",
         label="Profits Tax — Illustrations", label_zh="利得稅例題",
         en="Source, capital vs revenue, bad debts, IP, losses and two-tiered computations — DIPN examples paraphrased and textbook figures recomputed against current law.",
         zh="以改寫例題展示來源地、資本/收益性質、壞帳、知識產權、虧損及兩級制計算等常見考點。",
         kw="profits tax worked illustrations examples"),
    dict(id="salaries-tax-illustrations", src="salaries-tax-illustrations.html", group="Worked illustrations",
         label="Salaries Tax — Illustrations", label_zh="薪俸稅例題",
         en="The 60-day rule, housing benefit valuation, share options, termination gratuities, a full computation, and three personal assessment election scenarios.",
         zh="以服務地點、僱傭關係、福利、股份獎勵及個人入息課稅情境強化考試判斷。",
         kw="salaries tax worked illustrations examples"),
    dict(id="property-tax-illustrations", src="property-tax-illustrations.html", group="Worked illustrations",
         label="Property Tax — Illustrations", label_zh="物業稅例題",
         en="NAV computations built from rent, rates, tenant-paid outgoings, irrecoverable rent, and corporate-owned property scenarios.",
         zh="用租金、差餉、租客代付開支、不可收回租金及公司持有物業情境練習 NAV 計算。",
         kw="property tax worked illustrations examples"),
    dict(id="stamp-duty-illustrations", src="stamp-duty-illustrations.html", group="Worked illustrations",
         label="Stamp Duty — Illustrations", label_zh="印花稅例題",
         en="Property purchases, corporate buyers, Hong Kong share transfers and intra-group reorganisations — every figure recomputed against post-2026 law.",
         zh="以物業買賣、公司買樓、香港股票轉讓及關聯公司重組練習印花稅分析。",
         kw="stamp duty worked illustrations examples"),
    dict(id="depreciation-allowances-illustrations", src="depreciation-allowances-illustrations.html",
         group="Worked illustrations",
         label="Depreciation & Allowances — Illustrations", label_zh="折舊及免稅額例題",
         en="Pooling, asset disposals, commercial buildings, refurbishment and prescribed fixed assets worked end to end.",
         zh="透過池制、出售資產、商業建築物、翻新及指定固定資產練習折舊免稅額。",
         kw="depreciation allowances worked illustrations examples"),
    dict(id="module9-extra-practice", src="module9-extra-practice.html", group="Worked illustrations",
         label="Module 9 Extra Practice Q&A", label_zh="Module 9 額外練習問答",
         en="An extra question bank, grouped by profits tax, salaries tax, property tax, personal assessment, stamp duty and cross-border withholding.",
         zh="改寫練習庫，按利得稅、薪俸稅、物業稅、個人入息課稅、印花稅及跨境預扣稅分類。",
         kw="module 9 extra practice questions answers"),
]

# Sister platforms - separate sites, linked out rather than embedded.
RELATED = [
    dict(url="https://anthonymanhk.github.io/hkfrs-as-study-platform/",
         label="HKFRS / HKAS Study Platform",
         label_zh="財務報告準則學習平台",
         short="HKFRS / HKAS",
         en="The companion platform for financial reporting — every active HKFRS and HKAS, bilingual, with a question bank. Where this Hub covers the tax, that one covers the accounts the tax computation starts from.",
         zh="財務報告的姊妹平台：涵蓋所有現行 HKFRS 及 HKAS，中英雙語並附題庫。本平台講稅務，那邊講稅務計算所依據的帳目。"),
]

GROUP_ORDER = ["Start here", "Tax types", "Returns", "Worked illustrations"]

GROUP_ZH = {
    "Start here": "由此開始",
    "Tax types": "各稅種",
    "Returns": "報稅表",
    "Worked illustrations": "例題",
}

GROUP_BLURB = {
    "Start here": "The three tools you open first — what IRD changed recently, then the searchable transaction and DIPN indexes.",
    "Tax types": "One page per head of charge, each stating the current law with its statutory references.",
    "Returns": "Mapping the computation onto the actual BIR forms.",
    "Worked illustrations": "Paraphrased DIPN and Module 9 examples, recomputed against current rates.",
}

PAGE_IDS = {p["id"] for p in PAGES}


# Personal allowances, per IRD pam61e. IRD publishes 2024/25 and 2025/26 as a
# single column, so one set of exam-year figures covers ACCA TX-HKG from the
# June 2025 sitting through December 2026.
CURRENT_YA = "2026/27"
EXAM_YA = "2025/26"           # what D26 examines
ALLOWANCES = {
    "basic":            {"2026/27": "145,000", "2025/26": "132,000"},
    "married":          {"2026/27": "290,000", "2025/26": "264,000"},
    "child":            {"2026/27": "140,000", "2025/26": "130,000"},
    "single parent":    {"2026/27": "145,000", "2025/26": "132,000"},
    "dep parent 60+":   {"2026/27": "55,000",  "2025/26": "50,000"},
    "dep parent 55-59": {"2026/27": "27,500",  "2025/26": "25,000"},
}
# Figures that look like allowances but are not, so the check must ignore them.
NOT_AN_ALLOWANCE = (
    "160,000",   # the proposed 2026/27 child allowance, still only proposed
    "120,000",   # historical textbook figures, flagged as stale in situ
    "100,000",
    "46,000",
)


def check_allowances(html):
    """Fail the build if an allowance line states a figure from neither year.

    The Hub is written on the current YA with the exam YA alongside. A figure
    matching neither is almost always a stale allowance left behind by a rate
    change, which is silent and costly in a tax reference.

    A line may legitimately name several allowances at once ("a basic
    allowance where the married person's allowance of $290,000 applies"), so
    the accepted set is the union over every allowance mentioned on the line.
    """
    known = {v for years in ALLOWANCES.values() for v in years.values()}
    figure = re.compile(r"(?<![\d,])\d{2,3},\d{3}(?![\d,])")
    problems = []

    for n, line in enumerate(html.split(chr(10)), 1):
        low = line.lower()
        if "allowance" not in low:
            continue
        if any(w in low for w in ("dual", "stale", "original book", "proposed")):
            continue                      # dual-stated, historical, or not yet law

        named = [k for k in ALLOWANCES if k.split()[0] in low]
        if not named:
            continue
        ok = {ALLOWANCES[k][y] for k in named for y in (CURRENT_YA, EXAM_YA)}

        stray = [f for f in figure.findall(line)
                 if f in known and f not in ok and f not in NOT_AN_ALLOWANCE]
        if stray:
            problems.append("line %d: %s states %s; expected one of %s"
                            % (n, "/".join(named), ", ".join(sorted(set(stray))),
                               ", ".join(sorted(ok))))

    if problems:
        sys.exit("!! allowance figures from neither %s nor %s:" % (CURRENT_YA, EXAM_YA)
                 + chr(10) + chr(10).join("   " + x for x in problems[:12]))
    return len(ALLOWANCES)

def read(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def extract(html, tag, attrs):
    """Return inner HTML of the first <tag ...attrs...> element, matching nesting."""
    m = re.search(r"<%s[^>]*%s[^>]*>" % (tag, re.escape(attrs)), html)
    if not m:
        return None
    start = m.end()
    depth = 1
    pos = start
    token = re.compile(r"</?%s\b" % tag)
    while depth:
        n = token.search(html, pos)
        if not n:
            return None
        depth += -1 if n.group(0).startswith("</") else 1
        pos = n.end()
    return html[start:html.rfind("<", start, pos)]


def localise(fragment, pid):
    """Namespace a page fragment so 17 pages can share one document."""
    # own anchors
    fragment = re.sub(r'\bid="([A-Za-z][\w-]*)"', lambda m: 'id="%s__%s"' % (pid, m.group(1)), fragment)
    fragment = re.sub(r'\bhref="#([\w-]+)"', lambda m: 'href="#%s__%s"' % (pid, m.group(1)), fragment)

    # cross-page links -> tab anchors
    def page_link(m):
        target, anchor = m.group(1), m.group(2)
        if target not in PAGE_IDS:
            return m.group(0)
        return 'href="#%s"' % (target + "__" + anchor if anchor else target)

    fragment = re.sub(r'href="(?:\.\./pages/|pages/)?([a-z0-9-]+)\.html(?:#([\w-]+))?"', page_link, fragment)
    fragment = re.sub(r'href="(?:\.\./)?index\.html(?:#[\w-]+)?"', 'href="#MAIN"', fragment)

    # Repo-root files: pages/ reaches them via ../, the combined file sits at
    # the root already, so the ../ has to go or the link escapes the site.
    fragment = re.sub(r'href="\.\./(LICENSE|README\.md)"', r'href="\1"', fragment)

    # freshness placeholders were driven by a script that no longer applies here
    fragment = re.sub(r'<div id="[\w-]*freshness-banner"[^>]*>\s*</div>', "", fragment)
    fragment = re.sub(r'<ul id="[\w-]*freshness-sources"[^>]*>\s*</ul>', "", fragment)
    return fragment


def page_style(html, pid):
    """Pull a page's own <style> block and namespace it to that panel.

    The builder only lifts <main class="content">, so without this a page's
    local CSS silently vanishes from the combined edition while its class
    names are still used in the markup. Each selector is prefixed with the
    panel id so two pages defining the same class cannot collide.
    """
    head = html.split("</head>", 1)[0]
    m = re.search(r"<style>(.*?)</style>", head, re.S)
    if not m:
        return ""
    css = m.group(1).strip()
    if not css:
        return ""
    if "@" in css:
        sys.exit("!! %s has an at-rule in its <style>; namespacing not implemented" % pid)

    out = []
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selectors, body = rule.group(1).strip(), rule.group(2).strip()
        if selectors.startswith("/*"):
            selectors = re.sub(r"/\*.*?\*/", "", selectors, flags=re.S).strip()
        if not selectors:
            continue
        scoped = ", ".join(
            "#%s %s" % (pid, sel.strip()) for sel in selectors.split(",") if sel.strip()
        )
        out.append("%s{%s}" % (scoped, body))
    return "\n/* ---- %s ---- */\n%s\n" % (pid, "\n".join(out)) if out else ""


def zh_note(label_zh, summary_zh):
    """Traditional Chinese orientation note shown at the head of every panel."""
    return (
        '<div class="zh-translation"><strong>%s</strong>%s</div>'
        % (label_zh, summary_zh)
    )


def inject_zh(content, note):
    """Place the Chinese note straight after the page title block."""
    marker = "</div>\n\n    <"
    idx = content.find('class="page-title"')
    if idx < 0:
        return note + content
    close = content.find("</div>", content.find("</div>", idx) + 6)
    if close < 0:
        return note + content
    close += len("</div>")
    return content[:close] + "\n" + note + content[close:]


def build_panel(pid, label, src, label_zh, summary_zh):
    html = read(os.path.join(ROOT, "pages", src))
    content = extract(html, "main", 'class="content"')
    if content is None:
        sys.exit("!! could not find <main class=\"content\"> in %s" % src)
    toc = extract(html, "aside", 'class="toc"')

    content = localise(content, pid)
    content = inject_zh(content, zh_note(label_zh, summary_zh))
    toc = localise(toc, pid) if toc else ""

    shell_style = "" if toc else ' style="grid-template-columns:1fr"'
    aside = '<aside class="toc">%s</aside>' % toc if toc else ""
    panel = (
        '<section class="tab-panel" id="%s" data-label="%s">\n'
        '  <div class="shell"%s>%s<main class="content">%s</main></div>\n'
        "</section>\n" % (pid, label, shell_style, aside, content)
    )
    return panel, page_style(html, pid)



def build_revision_notice():
    """Markup for the 'what changed' notice, from data/revision.json.

    Returns "" when the file is absent, so the build never depends on it.
    """
    # assets/, not data/ - this filesystem is case-insensitive, so a lowercase
    # data/ folder resolves into the gitignored Data/ archive and the file
    # would never be committed.
    path = os.path.join(ROOT, "assets", "revision.json")
    if not os.path.exists(path):
        return ""
    with io.open(path, encoding="utf-8") as fh:
        d = json.load(fh)

    def item(x, body_key):
        link = x.get("link")
        name = ('<a href="%s">%s</a>' % (link, x["name"])) if link else x["name"]
        date = ' <span class="rev-date">%s</span>' % x["date"] if x.get("date") else ""
        return "<li><strong>%s</strong>%s<br>%s</li>" % (name, date, x[body_key])

    revised = "".join(item(x, "note") for x in d.get("sections_revised", []))
    gaps = "".join(item(x, "reason") for x in d.get("sections_need_increase", []))

    return """
  <div class="rev-notice-wrap">
    <details class="rev-notice">
      <summary>
        <strong>What has changed in this Hub</strong>
        <span class="rev-meta">%d revised &middot; %d still missing &middot; updated %s</span>
      </summary>
      <div class="rev-body">
        <p class="rev-summary">%s</p>
        <h3 class="rev-h">Revised</h3>
        <ul class="rev-list">%s</ul>
        <h3 class="rev-h rev-h-gap">Still missing, and why</h3>
        <ul class="rev-list rev-list-gap">%s</ul>
        <p class="rev-foot">%s</p>
      </div>
    </details>
  </div>
""" % (len(d.get("sections_revised", [])), len(d.get("sections_need_increase", [])),
       d.get("last_updated", "unknown"), d.get("summary", ""), revised, gaps,
       d.get("notes", ""))


def build_cards():
    out = []
    for group in GROUP_ORDER:
        out.append('<h2 class="family-heading">%s · %s</h2>' % (group, GROUP_ZH[group]))
        out.append('<p class="group-blurb">%s</p>' % GROUP_BLURB[group])
        out.append('<div class="card-grid">')
        for pg in PAGES:
            if pg["group"] != group:
                continue
            haystack = " ".join(
                (pg["kw"], pg["label"], pg["label_zh"], pg["en"], pg["zh"])
            ).lower().replace('"', "")
            out.append(
                '<button class="std-card" data-target="%s" data-search="%s">'
                '<div class="card-code">%s</div>'
                '<div class="card-title-zh">%s</div>'
                '<div class="card-desc">%s</div>'
                '<div class="card-desc card-desc-zh">%s</div>'
                "</button>"
                % (pg["id"], haystack, pg["label"], pg["label_zh"], pg["en"], pg["zh"])
            )
        out.append("</div>")

    if RELATED:
        out.append('<h2 class="family-heading">Related platforms \u00b7 \u76f8\u95dc\u5e73\u53f0</h2>')
        out.append('<p class="group-blurb">A separate site. Opens in a new tab.</p>')
        out.append('<div class="card-grid">')
        for r in RELATED:
            hay = " ".join((r["label"], r["label_zh"], r["en"], r["zh"])).lower().replace('"', "")
            out.append(
                '<a class="std-card" href="%s" target="_blank" rel="noopener" data-search="%s">'
                '<div class="card-code">%s &rarr;</div>'
                '<div class="card-title-zh">%s</div>'
                '<div class="card-desc">%s</div>'
                '<div class="card-desc card-desc-zh">%s</div>'
                "</a>" % (r["url"], hay, r["label"], r["label_zh"], r["en"], r["zh"])
            )
        out.append("</div>")
    return "\n".join(out)


def build_nav():
    items = [
        '<button class="navlink" data-target="%s">%s</button>' % (pg["id"], pg["label"])
        for pg in PAGES
        if pg["group"] == "Start here"
    ]
    items += [
        '<a class="navlink" href="%s" target="_blank" rel="noopener">%s &rarr;</a>'
        % (r["url"], r["short"])
        for r in RELATED
    ]
    return "\n".join(items)


FRAME_CSS = """
/* ---------- topbar palette ----------
   Kept independent of --brand: in dark mode --brand lightens to a pink that
   cannot carry white text, so the bar needs its own dark tokens. */
:root{
  --topbar-bg:#8b2635; --topbar-bg2:#6e1e2a;
  --topbar-text:#ffffff; --topbar-dim:#fdeceb; --topbar-accent:#f5d9a8;
}
@media (prefers-color-scheme: dark){
  :root{
    --topbar-bg:#5c1a23; --topbar-bg2:#3d1017;
    --topbar-text:#fbeaec; --topbar-dim:#e7bcc1; --topbar-accent:#e0b978;
  }
}
:root[data-theme="dark"]{
  --topbar-bg:#5c1a23; --topbar-bg2:#3d1017;
  --topbar-text:#fbeaec; --topbar-dim:#e7bcc1; --topbar-accent:#e0b978;
}
:root[data-theme="light"]{
  --topbar-bg:#8b2635; --topbar-bg2:#6e1e2a;
  --topbar-text:#ffffff; --topbar-dim:#fdeceb; --topbar-accent:#f5d9a8;
}

/* ---------- explicit theme overrides (must follow main.css) ---------- */
:root[data-theme="dark"]{
  --bg:#14171c; --surface:#1b1f26; --surface-alt:#20242c; --border:#2c313a;
  --text:#e6e9ee; --text-muted:#9aa3af; --brand:#d97b86; --brand-dark:#e79ba3; --link:#6bb3e0;
  --ok-bg:#123420; --ok-text:#7fd99a; --ok-border:#1f5c34;
  --warn-bg:#3a2e0f; --warn-text:#e8c46b; --warn-border:#63501c;
  --bad-bg:#3a1717; --bad-text:#f0a0a3; --bad-border:#5c2323;
  --tax-bg:#182b3d; --tax-text:#7fc0ef;
  --deduct-bg:#132a19; --deduct-text:#86d69c;
  --nondeduct-bg:#2e1616; --nondeduct-text:#f0a0a3;
  --code-bg:#20242c; --shadow:0 1px 3px rgba(0,0,0,.4);
}
:root[data-theme="light"]{
  --bg:#f5f6f8; --surface:#ffffff; --surface-alt:#eef1f5; --border:#dde1e7;
  --text:#1b2430; --text-muted:#5b6472; --brand:#8b2635; --brand-dark:#6e1e2a; --link:#1a5d8f;
  --ok-bg:#e6f4ea; --ok-text:#1e7a34; --ok-border:#b7e0c3;
  --warn-bg:#fdf3e0; --warn-text:#946200; --warn-border:#f1d79a;
  --bad-bg:#fbe9e9; --bad-text:#a3282c; --bad-border:#f0c4c4;
  --tax-bg:#e9f0f9; --tax-text:#1a5d8f;
  --deduct-bg:#eef6ee; --deduct-text:#2c7a3d;
  --nondeduct-bg:#f6eeee; --nondeduct-text:#a3282c;
  --code-bg:#f1f2f4; --shadow:0 1px 3px rgba(20,24,30,.08), 0 1px 2px rgba(20,24,30,.06);
}

/* ---------- topbar ---------- */
.topbar{
  background:linear-gradient(180deg, var(--topbar-bg), var(--topbar-bg2));
  color:var(--topbar-text); display:flex; align-items:center; flex-wrap:wrap;
  padding:0 12px; gap:4px; position:sticky; top:0; z-index:100;
  box-shadow:var(--shadow);
}
.topbar .brand{font-weight:700;padding:10px 14px 10px 6px;white-space:nowrap;letter-spacing:.2px;font-size:15px;color:var(--topbar-text)}
.topbar .brand small{display:block;font-weight:400;font-size:11px;opacity:.85}
.navlink,.toolbtn{
  background:transparent;border:none;color:var(--topbar-dim);font-family:inherit;
  padding:12px 13px;cursor:pointer;font-size:13.5px;font-weight:600;
  border-bottom:3px solid transparent;
}
.navlink:hover,.toolbtn:hover{background:rgba(255,255,255,.14);color:var(--topbar-text)}
.navlink.active{background:rgba(255,255,255,.18);border-bottom-color:var(--topbar-accent);color:var(--topbar-text)}
.topbar .spacer{flex:1 1 auto}
.topbar .searchwrap{margin:7px 6px}
.topbar input[type="search"]{
  padding:7px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);
  background:rgba(255,255,255,.12);color:var(--topbar-text);width:230px;font-size:13.5px;font-family:inherit;
}
.topbar input[type="search"]::placeholder{color:var(--topbar-dim);opacity:.7}

/* ---------- tab panels ---------- */
.tab-panel{display:none}
.tab-panel.active{display:block}
.tab-panel .shell{padding-top:20px}
.tab-panel .toc{top:66px}
.crumb{max-width:1280px;margin:0 auto;padding:12px 20px 0;font-size:12.5px;color:var(--text-muted)}
.crumb a{cursor:pointer}

/* ---------- MAIN index ---------- */
#MAIN .hero{max-width:1280px;margin:0 auto;padding:30px 20px 4px}
#MAIN .hero h1{font-size:29px;margin:0 0 6px}
#MAIN .hero p{color:var(--text-muted);max-width:820px;font-size:14.5px}
#MAIN .hero-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
#MAIN .hero-actions button{border:1px solid var(--brand);border-radius:6px;padding:8px 13px;
  font:inherit;font-size:13px;cursor:pointer}
#MAIN .intro-open{background:var(--brand);color:#fff}
#MAIN .intro-open:hover{background:var(--brand-dark)}
.intro-dialog{width:min(680px,calc(100% - 28px));max-width:680px;max-height:86vh;
  padding:0;border:1px solid var(--border);border-radius:12px;background:var(--surface);
  color:var(--text);box-shadow:0 12px 44px rgba(0,0,0,.32)}
.intro-dialog::backdrop{background:rgba(10,14,20,.62)}
.intro-body{padding:22px 24px 18px;display:flex;flex-direction:column;
  max-height:86vh;overflow:hidden}
.intro-dialog h2{margin:0;color:var(--brand);font-size:21px}
.intro-subtitle{margin:4px 0 16px;color:var(--text-muted);font-size:13px}
.intro-list{flex:1 1 auto;min-height:0;overflow-y:auto;margin:0;padding:0 8px 0 22px;font-size:13.5px}
.intro-list li{margin:0 0 11px;line-height:1.55}
.intro-list strong{color:var(--brand)}
.intro-zh{display:block;color:var(--text-muted);margin-top:2px}
.intro-note{margin:14px 0;padding:10px 12px;border-left:3px solid var(--warn-border);
  background:var(--warn-bg);color:var(--warn-text);font-size:12.5px}
.intro-footer{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.intro-footer label{display:flex;align-items:center;gap:7px;font-size:12.5px;cursor:pointer}
.intro-close{background:var(--brand);color:#fff}
.intro-close:hover{background:var(--brand-dark)}
#MAIN .index-wrap{max-width:1280px;margin:0 auto;padding:0 20px 50px}
.family-heading{margin:30px 0 2px;font-size:17px;color:var(--brand);border-bottom:2px solid var(--border);padding-bottom:6px}
.group-blurb{color:var(--text-muted);font-size:13px;margin:6px 0 0}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:12px}
.std-card{
  text-align:left;background:var(--surface);border:1px solid var(--border);border-radius:10px;
  padding:14px 16px;cursor:pointer;box-shadow:var(--shadow);color:var(--text);
  font-family:inherit;transition:transform .12s ease,border-color .12s ease;
}
.std-card:hover{transform:translateY(-2px);border-color:var(--brand)}
.std-card .card-code{font-weight:700;font-size:14.5px;color:var(--brand)}
.std-card .card-title-zh{font-size:13px;color:var(--text);margin-top:3px}
.std-card .card-desc{font-size:12px;color:var(--text-muted);margin-top:6px;line-height:1.5}
.std-card .card-desc-zh{margin-top:4px;padding-top:4px;border-top:1px dotted var(--border)}
.no-match{color:var(--text-muted);font-size:13.5px;padding:14px 0;display:none}

/* ---------- bilingual notes carried from the previous edition ---------- */
.zh-translation{
  background:var(--surface-alt);border-left:3px solid var(--brand);
  padding:8px 10px;margin:6px 0 16px;color:var(--text);font-size:14px;
}
.zh-translation strong{color:var(--brand);display:block;margin-bottom:3px}

/* ---------- freshness banner ---------- */
.hub-freshness{max-width:1280px;margin:16px auto 0;padding:0 20px}
.hub-freshness .freshness{margin:0}


/* ---------- revision notice ----------
   Uses --warn-* from main.css so it follows the manual data-theme toggle,
   not just the OS preference. */
.rev-notice-wrap{max-width:1280px;margin:14px auto 0;padding:0 20px}
.rev-notice{background:var(--warn-bg);border:1px solid var(--warn-border);
  border-radius:var(--radius);color:var(--warn-text);font-size:13.5px}
.rev-notice > summary{cursor:pointer;padding:11px 14px;list-style:none;
  display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.rev-notice > summary::-webkit-details-marker{display:none}
.rev-notice > summary::before{content:"\25b8";display:inline-block;transition:transform .15s}
.rev-notice[open] > summary::before{transform:rotate(90deg)}
.rev-meta{font-size:12px;opacity:.85;margin-left:auto}
.rev-body{padding:0 14px 14px;border-top:1px solid var(--warn-border)}
.rev-summary{margin:10px 0 0}
.rev-h{font-size:12px;text-transform:uppercase;letter-spacing:.06em;margin:14px 0 4px}
.rev-h-gap{color:var(--bad-text)}
.rev-list{margin:0;padding-left:20px}
.rev-list li{margin:7px 0;line-height:1.5}
.rev-list-gap li{color:var(--text)}
.rev-date{font-size:11.5px;opacity:.75;font-variant-numeric:tabular-nums}
.rev-foot{margin:12px 0 0;font-size:12.5px;opacity:.85}
@media (max-width:760px){.rev-notice-wrap{padding:0 14px}.rev-meta{margin-left:0;width:100%}}

footer.appfoot{text-align:center;color:var(--text-muted);font-size:12.5px;padding:22px 20px 40px;border-top:1px solid var(--border);max-width:1280px;margin:0 auto}

@media (max-width:760px){
  .topbar{position:static}
  .tab-panel .toc{position:static;max-height:none}
  .topbar input[type="search"]{width:170px}
}
"""

FRAME_JS = r"""
(function(){
  var root = document.documentElement;

  /* ---------- first-visit guide ---------- */
  var guide = document.getElementById('welcomeGuide');
  var guideOpen = document.getElementById('guideOpen');
  var guideClose = document.getElementById('guideClose');
  var guideSkip = document.getElementById('guideDontShow');
  var guideKey = 'hktax_intro_dismissed';
  function showGuide(){
    if(guide && !guide.open) guide.showModal();
  }
  if(guide && guideOpen && guideClose && guideSkip){
    guideOpen.addEventListener('click', showGuide);
    guideClose.addEventListener('click', function(){ guide.close(); });
    guide.addEventListener('close', function(){
      if(guideSkip.checked){
        try{ localStorage.setItem(guideKey, 'true'); }catch(e){}
      }
    });
    var guideDismissed = false;
    try{ guideDismissed = localStorage.getItem(guideKey) === 'true'; }catch(e){}
    if(!guideDismissed) showGuide();
  }

  /* ---------- tabs ---------- */
  function activate(id){
    if(!document.getElementById(id)) id = 'MAIN';
    document.querySelectorAll('.tab-panel').forEach(function(p){ p.classList.toggle('active', p.id === id); });
    document.querySelectorAll('.navlink').forEach(function(b){ b.classList.toggle('active', b.dataset.target === id); });
    try{ history.replaceState(null, '', '#' + id); }catch(e){}
    window.scrollTo(0, 0);
  }
  window.hubActivate = activate;

  document.addEventListener('click', function(ev){
    var tabBtn = ev.target.closest('[data-target]');
    if(tabBtn){ activate(tabBtn.dataset.target); return; }

    var a = ev.target.closest('a[href^="#"]');
    if(!a) return;
    var raw = a.getAttribute('href').slice(1);
    if(!raw) return;
    var panel = document.getElementById(raw);
    if(panel && panel.classList.contains('tab-panel')){ ev.preventDefault(); activate(raw); return; }
    var el = document.getElementById(raw);
    if(!el) return;
    var owner = el.closest('.tab-panel');
    ev.preventDefault();
    if(owner && !owner.classList.contains('active')) activate(owner.id);
    el.scrollIntoView({behavior:'smooth', block:'start'});
  });

  /* ---------- MAIN card search ---------- */
  var search = document.getElementById('jumpSearch');
  var noMatch = document.getElementById('noMatch');
  function filterCards(){
    var q = (search.value || '').trim().toLowerCase();
    var shown = 0;
    document.querySelectorAll('.std-card').forEach(function(card){
      var hit = !q || card.dataset.search.indexOf(q) !== -1
                   || card.textContent.toLowerCase().indexOf(q) !== -1;
      card.hidden = !hit;
      if(hit) shown++;
    });
    document.querySelectorAll('#MAIN .family-heading, #MAIN .group-blurb, #MAIN .card-grid').forEach(function(el){
      var grid = el.classList.contains('card-grid') ? el : el.nextElementSibling;
      while(grid && !grid.classList.contains('card-grid')) grid = grid.nextElementSibling;
      var any = grid && Array.prototype.some.call(grid.querySelectorAll('.std-card'), function(c){ return !c.hidden; });
      el.hidden = !any;
    });
    noMatch.style.display = shown ? 'none' : 'block';
  }
  search.addEventListener('input', function(){ if(!document.getElementById('MAIN').classList.contains('active')) activate('MAIN'); filterCards(); });
  search.addEventListener('keydown', function(ev){
    if(ev.key !== 'Enter') return;
    var first = Array.prototype.find.call(document.querySelectorAll('.std-card'), function(c){ return !c.hidden; });
    if(first){ search.value = ''; filterCards(); activate(first.dataset.target); }
  });

  /* ---------- dark mode ---------- */
  function applyTheme(t){
    if(t === 'dark' || t === 'light') root.setAttribute('data-theme', t);
    else root.removeAttribute('data-theme');
  }
  var saved = null;
  try{ saved = localStorage.getItem('hktax_theme'); }catch(e){}
  if(saved) applyTheme(saved);
  document.getElementById('themeBtn').addEventListener('click', function(){
    var cur = root.getAttribute('data-theme');
    var isDark = cur === 'dark' || (!cur && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var next = isDark ? 'light' : 'dark';
    applyTheme(next);
    try{ localStorage.setItem('hktax_theme', next); }catch(e){}
  });

  /* ---------- searchable data tables ---------- */
  function linkToTab(href){
    if(!href) return '';
    var m = /^([a-z0-9-]+)\.html(?:#([\w-]+))?$/.exec(href);
    if(!m) return href;
    return '#' + (m[2] ? m[1] + '__' + m[2] : m[1]);
  }
  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }
  // Official IRD source URL, derived from the document number.
  // Pattern verified against ird.gov.hk 2026-09-24: zero-padded 2 digits,
  // lowercase suffix, e.g. DIPN 1 -> dipn01.pdf, DIPN 13A -> dipn13a.pdf.
  function officialUrl(no){
    var m = /^(DIPN|SOIPN|EDOIPN) (\d+)([A-Za-z]?)$/.exec(no || '');
    if(!m) return null;
    var n = m[2].length < 2 ? '0' + m[2] : m[2];
    return 'https://www.ird.gov.hk/eng/pdf/' + m[1].toLowerCase() + n + m[3].toLowerCase() + '.pdf';
  }
  function mountTable(prefix, cfg){
    var q = document.getElementById(prefix + '__q');
    var tbody = document.getElementById(prefix + '__results-body');
    if(!q || !tbody) return;
    var countEl = document.getElementById(prefix + '__checker-count');
    var emptyEl = document.getElementById(prefix + '__checker-empty');
    var data = cfg.data() || [];

    (cfg.filters || []).forEach(function(f){
      var sel = document.getElementById(prefix + '__' + f.id);
      if(!sel || !f.populate) return;
      Array.from(new Set(data.map(function(r){ return r[f.key]; }))).forEach(function(v){
        var o = document.createElement('option');
        o.value = v; o.textContent = v;
        sel.appendChild(o);
      });
    });

    function render(){
      var term = (q.value || '').trim().toLowerCase();
      var rows = data.filter(function(row){
        for(var i = 0; i < (cfg.filters || []).length; i++){
          var f = cfg.filters[i];
          var sel = document.getElementById(prefix + '__' + f.id);
          if(sel && sel.value && row[f.key] !== sel.value) return false;
        }
        return !term || cfg.haystack(row).toLowerCase().indexOf(term) !== -1;
      });
      if(countEl) countEl.textContent = rows.length + ' of ' + data.length + ' ' + cfg.label + ' shown';
      if(emptyEl) emptyEl.style.display = rows.length ? 'none' : 'block';
      tbody.innerHTML = rows.map(cfg.row).join('');
    }
    q.addEventListener('input', render);
    (cfg.filters || []).forEach(function(f){
      var sel = document.getElementById(prefix + '__' + f.id);
      if(sel) sel.addEventListener('change', render);
    });
    render();
  }

  var STATUS_LABEL = {
    taxable:'Taxable', nontaxable:'Non-taxable', deductible:'Deductible',
    nondeductible:'Non-deductible', dutiable:'Dutiable', dutyfree:'Duty-free (0%)',
    allowance:'Allowance available'
  };

  mountTable('transaction-checker', {
    data: function(){ return window.TRANSACTIONS; },
    label: 'transactions',
    filters: [{id:'filter-tax', key:'tax', populate:true}, {id:'filter-status', key:'status'}],
    haystack: function(r){ return r.item + ' ' + r.note + ' ' + r.tax + ' ' + r.section; },
    row: function(r){
      return '<tr>'
        + '<td><span class="tag tag-' + r.status + '">' + esc(STATUS_LABEL[r.status] || r.status) + '</span></td>'
        + '<td>' + esc(r.tax) + '</td>'
        + '<td class="item">' + esc(r.item) + '</td>'
        + '<td>' + esc(r.section) + '</td>'
        + '<td class="note">' + esc(r.note) + '</td>'
        + '<td class="goto"><a href="' + linkToTab(r.page) + '">View section &rarr;</a></td>'
        + '</tr>';
    }
  });

  mountTable('dipn-index', {
    data: function(){ return window.DIPN_INDEX; },
    label: 'documents',
    filters: [{id:'filter-group', key:'group', populate:true}, {id:'filter-status', key:'status'}],
    haystack: function(r){ return r.no + ' ' + r.title + ' ' + r.summary + ' ' + r.group; },
    row: function(r){
      var badge = r.status === 'core'
        ? '<a href="' + linkToTab(r.link) + '" class="tag tag-deductible">Core &rarr;</a>'
        : '<span class="tag tag-nontaxable">Reference only</span>';
      return '<tr>'
        + '<td>' + esc(r.no) + '</td>'
        + '<td>' + esc(r.title) + (r.example ? ' <span class="tag tag-taxable" style="margin-left:4px">example</span>' : '') + '</td>'
        + '<td>' + esc(r.group) + '</td>'
        + '<td>' + esc(r.date) + '</td>'
        + '<td class="note">' + esc(r.summary) + '</td>'
        + '<td><a href="' + officialUrl(r.no) + '" target="_blank" rel="noopener">IRD PDF &rarr;</a></td>'
        + '<td>' + badge + '</td>'
        + '</tr>';
    }
  });

  mountTable('profits-tax-return-finder', {
    data: function(){ return window.BIR_BOXES; },
    label: 'boxes',
    filters: [{id:'filter-form', key:'form'}],
    haystack: function(r){ return r.form + ' ' + r.part + ' ' + r.box + ' ' + r.label + ' ' + (r.note || ''); },
    row: function(r){
      return '<tr>'
        + '<td><span class="tag tag-dutiable">' + esc(r.form) + '</span></td>'
        + '<td>' + esc(r.box) + '</td>'
        + '<td>' + esc(r.part) + '</td>'
        + '<td class="item">' + esc(r.label) + '</td>'
        + '<td class="note">' + esc(r.note) + '</td>'
        + '<td class="goto">' + (r.link ? '<a href="' + linkToTab(r.link) + '">View section &rarr;</a>' : '') + '</td>'
        + '</tr>';
    }
  });

  /* ---------- open the requested tab ---------- */
  activate((location.hash || '#MAIN').slice(1));
})();
"""


def main():
    base_css = read(os.path.join(ROOT, "assets", "css", "main.css")) + FRAME_CSS

    data_js = "\n".join(
        read(os.path.join(ROOT, "assets", "js", f))
        for f in ("transactions-data.js", "dipn-index-data.js", "bir-finder-data.js")
    )

    panels, page_css = [], []
    for pg in PAGES:
        panel, css_ = build_panel(
            pg["id"], pg["label"], pg["src"], pg["label_zh"], pg["zh"]
        )
        panels.append(panel)
        if css_:
            page_css.append(css_)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="A study aid for Hong Kong tax - profits, property and salaries tax, stamp duty, depreciation allowances and personal assessment - built from IRD guidance and the Inland Revenue Ordinance. Not professional advice.">
<title>HK Tax Study Hub</title>
<style>
%(css)s
</style>
</head>
<body>

<div class="topbar">
  <div class="brand">HK Tax Study Hub<small>Combined single-file edition</small></div>
  <button class="navlink active" data-target="MAIN">MAIN 主頁</button>
%(nav)s
  <div class="spacer"></div>
  <div class="searchwrap">
    <input type="search" id="jumpSearch" placeholder="Jump to a page... 跳至頁面" />
  </div>
  <button class="toolbtn ai-prompt-btn" title="Copy a hardened HK-tax prompt to paste into your browser AI">AI Prompts</button>
  <button class="toolbtn" id="themeBtn">&#9789; Dark Mode</button>
</div>

<dialog class="intro-dialog" id="welcomeGuide" aria-labelledby="welcomeTitle">
  <div class="intro-body">
    <h2 id="welcomeTitle">Welcome to the HK Tax Study Hub · 歡迎使用香港稅務學習平台</h2>
    <p class="intro-subtitle">A quick guide to what the Hub does and how to use it · 平台功能及使用方法簡介</p>
    <ul class="intro-list">
      <li><strong>Find a tool or topic · 尋找工具或稅務主題</strong> — Choose a card on the home page, use the top navigation, or type into “Jump to a page”. The search narrows the cards; press Enter to open the first match.<span class="intro-zh">可在主頁選擇功能卡、使用上方導覽，或輸入「Jump to a page」搜尋；按 Enter 開啟首個符合項目。</span></li>
      <li><strong>Check a transaction · 查核交易稅務處理</strong> — Open Transaction Checker, search by an account name or transaction keyword, and use the tax/status filters. Follow “View section” to read the rule and its context.<span class="intro-zh">開啟「交易檢查器」，搜尋會計科目或交易關鍵字，再按稅種／處理方式篩選；點選「View section」閱讀相關規則及說明。</span></li>
      <li><strong>Learn a tax topic · 學習稅務主題</strong> — Start with a tax page for the rules, rates and computation format; use its links to open worked illustrations, return guidance, or related topics.<span class="intro-zh">先閱讀各稅項頁面的規則、稅率及計算格式，再透過頁面連結查看例題、報稅表指引或相關主題。</span></li>
      <li><strong>Practise ACCA TX-HKG · 練習 ACCA TX-HKG</strong> — Section A offers searchable/filterable MCQs and Random 15; Section B gives linked case questions; Section C has constructed-response questions and model answers. Select an answer and choose “Show answer” to check it and update your score where scoring is provided.<span class="intro-zh">A 部分提供可搜尋／篩選的選擇題及隨機 15 題；B 部分是相連個案題；C 部分提供長題目及模範答案。選擇答案後按「Show answer」核對；設有計分的部分會同步更新分數。</span></li>
      <li><strong>Check updates and sources · 查閱更新及資料來源</strong> — IRD What’s New records announced changes and whether they are enacted, bills or proposals. The DIPN Index searches practice notes. Use the cited ordinance and current IRD guidance to verify a point.<span class="intro-zh">「稅務局最新消息」記錄政策變動及其已生效、草案或建議狀態；DIPN 索引可搜尋實務指引。重要事項請核對所引法例及稅務局最新指引。</span></li>
      <li><strong>Personalise your view · 自訂閱讀方式</strong> — Use “Dark Mode” to switch themes. “AI Prompts” copies a cautious Hong Kong tax prompt for you to paste into an AI chat; it does not connect to or verify an AI’s answer.<span class="intro-zh">使用「Dark Mode」切換顯示主題。「AI Prompts」只會複製審慎的香港稅務提示詞，供你貼到 AI 對話中；平台不會連接 AI 或核實其答案。</span></li>
    </ul>
    <p class="intro-note"><strong>Study material only · 僅供學習參考。</strong> This Hub is not professional tax advice. Check the current law and IRD guidance before relying on a figure or section reference. · 本平台並非專業稅務意見；依賴任何數字或條文前，請核對現行法例及稅務局指引。</p>
    <div class="intro-footer">
      <label><input type="checkbox" id="guideDontShow"> Don’t show this again · 下次不再顯示</label>
      <button type="button" class="intro-close" id="guideClose">Get started · 開始使用</button>
    </div>
  </div>
</dialog>

<section class="tab-panel active" id="MAIN">
  <div class="hero">
    <h1>Hong Kong Tax Study Hub</h1>
    <p>Consolidated internal reference for HK profits, property and salaries tax, stamp duty, and depreciation allowances — built for (1) tax computation and taxable/deductible analysis on Hong Kong incorporated companies' financial statements, and (2) team study with worked illustrations drawn from IRD's Departmental Interpretation &amp; Practice Notes (DIPNs).</p>
    <p>雙語參考資料，涵蓋香港利得稅、物業稅、薪俸稅、印花稅及折舊免稅額，供稅務計算分析及團隊溫習之用。本平台僅供學習參考，不能取代《稅務條例》（第112章）及稅務局現行指引。</p>
    <div class="callout watch" style="max-width:860px">
      <span class="lbl">Study material — not professional advice · 學習材料，非專業意見</span>
      Nothing here is tax advice, and reading it creates no adviser–client relationship. This is written to one finance team's internal working standard and published openly because the underlying material is public — not because it has been reviewed for anyone else's use. It contains mistakes and goes out of date as the law changes. <strong>Verify against the Inland Revenue Ordinance (Cap. 112), the Stamp Duty Ordinance (Cap. 117) and current IRD guidance before relying on any figure for a filing position.</strong>
      <div style="margin-top:6px">本平台所載內容並非稅務意見，閱讀不構成顧問關係。內容按某財務團隊的內部工作標準撰寫，因所依據的資料屬公開而公開發布，並未經審核供他人使用；內容或有錯誤，亦會隨法例變動而過時。<strong>在依賴任何數字作報稅立場前，請核對《稅務條例》（第112章）、《印花稅條例》（第117章）及稅務局現行指引。</strong></div>
    </div>
    <div class="hero-actions">
      <button type="button" class="intro-open" id="guideOpen">How to use this Hub · 使用指南</button>
    </div>
  </div>
  <div class="hub-freshness">
    <div class="freshness ok">
      <span class="dot"></span>
      <span class="msg">IRD <a href="https://www.ird.gov.hk/eng/new/index.htm" target="_blank" rel="noopener">What's New</a> read on <strong>%(ird_date)s</strong> — items from 1 Jun to 30 Sep 2026 reviewed. The Stamp Duty (Amendment) (No. 3) Bill 2026 is carried as a <strong>bill</strong>, and two 2026 Policy Address measures as <strong>proposed</strong> — none of the three is law yet. · 稅務局最新消息已於 %(ird_date)s 覆核。</span>
      <button data-target="ird-updates">Open IRD What's New &rarr;</button>
    </div>
  </div>
%(revision_notice)s
  <div class="index-wrap">
%(cards)s
    <p class="no-match" id="noMatch">No page matches that search. · 沒有符合的頁面。</p>
  </div>
</section>

%(panels)s

<footer class="appfoot">HK Tax Study Hub — combined single-file snapshot, built %(build_date)s. Internal working document: verify against the Inland Revenue Ordinance (Cap. 112) and current IRD guidance before relying on any figure for a filing position. · 內部工作文件，引用前請核對《稅務條例》及稅務局現行指引。</footer>

<script>
%(data)s
</script>
<script>
%(frame)s
</script>
<script>
%(ai_prompt)s
</script>
</body>
</html>
""" % {
        "css": base_css + "".join(page_css),
        "nav": build_nav(),
        "cards": build_cards(),
        "panels": "\n".join(panels),
        "data": data_js,
        "frame": FRAME_JS,
        "ai_prompt": read(os.path.join(ROOT, "assets", "js", "ai-prompt.js")),
        "revision_notice": build_revision_notice(),
        "build_date": BUILD_DATE,
        "ird_date": IRD_READ_DATE,
    }

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    # Clean-URL twin for the published site: the spaced filename is what people
    # recognise as an email attachment, but it URL-encodes badly in a link.
    for extra in (OUT_WEB, OUT_INDEX):
        with io.open(extra, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)

    print("wrote %s (%.1f KB)" % (os.path.basename(OUT), len(html.encode("utf-8")) / 1024.0))
    print("wrote combined.html and index.html (same content)")
    print("panels: %d + MAIN | page CSS blocks inlined: %d" % (len(panels), len(page_css)))
    print("allowance guard: %d allowance types checked against %s and %s"
          % (check_allowances(html), CURRENT_YA, EXAM_YA))
    for bad in ("??", "禮"):
        n = html.count(bad)
        print("corruption check %r: %d" % (bad, n))


if __name__ == "__main__":
    main()
