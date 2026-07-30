#!/usr/bin/env python3
"""
Russia Labor Law Checker — static site builder.

Reads data/labor-regulations.json (source of truth, maintained by the weekly
Claude Code run per CLAUDE.md) and regenerates index.html deterministically.

Usage:
    python build.py

Never hand-edit index.html — it is fully generated from data/labor-regulations.json.
"""
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "labor-regulations.json"
OUT_PATH = ROOT / "index.html"

CATS = {
 "급여·보상": {"ko": "급여·보상", "en": "Pay & Compensation", "ru": "Оплата труда"},
 "채용·해고": {"ko": "채용·해고", "en": "Hiring & Termination", "ru": "Приём и увольнение"},
 "문서·시스템": {"ko": "문서·시스템", "en": "Documents & Systems", "ru": "Документооборот и системы"},
 "외국인·주재원": {"ko": "외국인·주재원", "en": "Foreign Staff & Expats", "ru": "Иностранные сотрудники"},
 "병역·군동원": {"ko": "병역·군동원", "en": "Military Registration", "ru": "Воинский учёт"},
 "인사데이터": {"ko": "인사데이터", "en": "HR Data", "ru": "Кадровые данные"},
}
STATUS = {
 "시행중": {"ko": "시행중", "en": "In effect", "ru": "Действует"},
 "시행예정": {"ko": "시행예정", "en": "Upcoming", "ru": "Скоро вступит в силу"},
 "계류중": {"ko": "계류중", "en": "Pending in Duma", "ru": "На рассмотрении Госдумы"},
 "논의중": {"ko": "논의중", "en": "Under discussion", "ru": "Обсуждается"},
}
STATUS_DESC = {
 "시행중": {"ko": "이미 발효되어 지금 준수해야 하는 규정", "en": "Already in force and must be complied with now", "ru": "Уже вступил в силу и требует соблюдения сейчас"},
 "시행예정": {"ko": "법률 공포 완료, 발효일이 미래", "en": "Law has been promulgated; effective date is in the future", "ru": "Закон опубликован, дата вступления в силу — в будущем"},
 "계류중": {"ko": "국가두마(Госдума) 심의 중인 법안", "en": "Bill under review in the State Duma", "ru": "Законопроект рассматривается Государственной Думой"},
 "논의중": {"ko": "발의 예정 또는 초기 논의 단계", "en": "Expected to be introduced or in early discussion", "ru": "Ожидается внесение или находится на начальной стадии обсуждения"},
}

UI = {
 "ko": {
  "pageTitle": "러시아 노동법 Checker",
  "subLabel": "러시아 법인 인사총괄용 — 최근 시행·계류 중인 노동법 변화와 HR 준비사항",
  "updatedPrefix": "· 업데이트 ",
  "tlSection": "⏱ 타임라인",
  "impactLabel": "영향도",
  "pastDotNote": "● 흐린 점 = 이미 지난 시행일",
  "tbdTitle": "날짜 미확정 (계류·논의 단계)",
  "guideToggle": "러시아 노동법, 무엇이 한국과 다른가 — 핵심 개념 8가지",
  "guideSection": "📘 러시아 노동법 기초 (처음 보는 분을 위한 가이드)",
  "listSection": "📋 법안·규제 목록",
  "sortedNote": "영향도 높은 순 정렬",
  "filterAll": "전체",
  "sectionUpcoming": "🔜 시행 예정 · 계류 · 논의 중",
  "sectionActive": "✅ 이미 시행됨",
  "blkBackground": "왜 바뀌었나 (배경)",
  "blkWhatChanged": "무엇이 바뀌나",
  "blkChecklist": "HR 준비 체크리스트",
  "blkDocs": "개정·정비 대상 문서",
  "blkProcess": "진행 절차 (누구와 어떤 순서로)",
  "blkPenalty": "미준수 시",
  "blkGlossary": "용어",
  "blkSources": "출처",
  "emptyState": "조건에 맞는 항목이 없습니다",
  "footer": "정보 출처: КонсультантПлюс, Коммерсантъ, Контур, Главбух, МосЛигал 등 러시아 노동법·인사 전문 매체 및 공식 법령 공고 (항목별 출처는 각 카드 하단 참조) · 참고용 정보이며 법률 자문이 아닙니다. 실제 조치 전 현지 노무·법무 자문 확인 필요.",
  "todayLabel": "오늘 ",
  "tlCntTemplate": "{n}건 표시 · {m}건 날짜 미정",
 },
 "en": {
  "pageTitle": "Russia Labor Law Checker",
  "subLabel": "For HR leads at Russian entities — recent and pending labor law changes and HR readiness steps",
  "updatedPrefix": "· Updated ",
  "tlSection": "⏱ Timeline",
  "impactLabel": "Impact",
  "pastDotNote": "● faded dot = effective date already passed",
  "tbdTitle": "Date not yet fixed (pending / under discussion)",
  "guideToggle": "How Russian labor law differs from Korea's — 8 key concepts",
  "guideSection": "📘 Russian Labor Law Basics (for first-time readers)",
  "listSection": "📋 Regulations & Bills",
  "sortedNote": "sorted by impact, high to low",
  "filterAll": "All",
  "sectionUpcoming": "🔜 Upcoming · Pending · Under Discussion",
  "sectionActive": "✅ Already in Effect",
  "blkBackground": "Why it changed (background)",
  "blkWhatChanged": "What changed",
  "blkChecklist": "HR readiness checklist",
  "blkDocs": "Documents to update",
  "blkProcess": "Process (who, in what order)",
  "blkPenalty": "If not complied with",
  "blkGlossary": "Glossary",
  "blkSources": "Sources",
  "emptyState": "No items match the current filter",
  "footer": "Sources: КонсультантПлюс (ConsultantPlus), Kommersant, Kontur, Glavbukh, MosLegal and other Russian labor-law/HR publications and official legal notices (see each card's Sources section for item-level links) · For reference only, not legal advice. Confirm with local labor/legal counsel before taking action.",
  "todayLabel": "Today ",
  "tlCntTemplate": "{n} shown · {m} date TBD",
 },
 "ru": {
  "pageTitle": "Чекер трудового законодательства России",
  "subLabel": "Для HR-руководителей российских юрлиц — актуальные и готовящиеся изменения трудового законодательства и шаги по подготовке",
  "updatedPrefix": "· Обновлено ",
  "tlSection": "⏱ Хронология",
  "impactLabel": "Влияние",
  "pastDotNote": "● бледная точка = дата вступления в силу уже прошла",
  "tbdTitle": "Дата ещё не определена (на рассмотрении / обсуждается)",
  "guideToggle": "Чем трудовое право России отличается от корейского — 8 ключевых понятий",
  "guideSection": "📘 Основы трудового права России (для тех, кто впервые знакомится)",
  "listSection": "📋 Список законов и законопроектов",
  "sortedNote": "отсортировано по влиянию, от высокого к низкому",
  "filterAll": "Все",
  "sectionUpcoming": "🔜 Скоро вступит в силу · На рассмотрении · Обсуждается",
  "sectionActive": "✅ Уже действует",
  "blkBackground": "Почему изменилось (предыстория)",
  "blkWhatChanged": "Что изменилось",
  "blkChecklist": "Чек-лист готовности HR",
  "blkDocs": "Документы для пересмотра",
  "blkProcess": "Процедура (с кем и в каком порядке)",
  "blkPenalty": "При несоблюдении",
  "blkGlossary": "Термины",
  "blkSources": "Источники",
  "emptyState": "Нет элементов, соответствующих фильтру",
  "footer": "Источники: КонсультантПлюс, Коммерсантъ, Контур, Главбух, МосЛигал и другие профильные издания по трудовому праву и HR, а также официальные публикации нормативных актов (ссылки по каждому пункту — в разделе «Источники» карточки) · Только для справки, не является юридической консультацией. Перед принятием мер проконсультируйтесь с местным юристом по трудовому праву.",
  "todayLabel": "Сегодня ",
  "tlCntTemplate": "{n} показано · {m} дата не определена",
 },
}

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>러시아 노동법 Checker</title>
<style>
:root { color-scheme: light; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Malgun Gothic", Roboto, sans-serif;
  background: #f6f7f9; color: #1a1d21; line-height: 1.55; padding: 20px;
}
.wrap { max-width: 1040px; margin: 0 auto; }
header { margin-bottom: 18px; position: relative; }
.langbar { position:absolute; top:0; right:0; display:flex; gap:4px; background:#fff; border:1px solid #e2e6ea; border-radius:99px; padding:3px; }
.langbtn { border:none; background:transparent; border-radius:99px; padding:6px 14px; font-size:12.5px; font-weight:700; cursor:pointer; color:#6b7280; }
.langbtn.on { background:#0f766e; color:#fff; }
h1 { font-size: 22px; font-weight: 700; padding-right:150px; }
.sub { color: #6b7280; font-size: 13px; margin-top: 4px; }
.section-title { font-size: 14px; font-weight: 700; color:#374151; margin: 24px 0 10px; text-transform: uppercase; letter-spacing: .04em; display:flex; align-items:center; gap:8px; }
.section-title .cnt { background:#eef2f5; color:#475569; font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; text-transform:none; letter-spacing:normal; }

.sumrow { display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
.sumchip { background:#fff; border:1px solid #e6e8eb; border-radius:10px; padding:10px 16px; flex:1; min-width:110px; }
.sumchip .n { font-size:20px; font-weight:800; }
.sumchip .l { font-size:12px; color:#6b7280; margin-top:2px; }

.tl-wrap { background:#fff; border:1px solid #e6e8eb; border-radius:12px; padding:44px 28px 46px; position:relative; overflow-x:auto; }
.tl-inner { position:relative; min-width:760px; height:150px; }
.tl-axis { position:absolute; left:0; right:0; top:75px; height:2px; background:#e2e6ea; }
.tl-tick { position:absolute; top:69px; width:1px; height:13px; background:#d1d5db; }
.tl-tick-label { position:absolute; top:88px; transform:translateX(-50%); font-size:10.5px; color:#9aa3ad; white-space:nowrap; }
.tl-today { position:absolute; top:8px; bottom:8px; width:2px; background:#e5484d; z-index:5; }
.tl-today-label { position:absolute; top:-8px; transform:translateX(-50%); background:#e5484d; color:#fff; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:99px; white-space:nowrap; }
.tl-ev { position:absolute; top:75px; cursor:pointer; }
.tl-dot { position:absolute; left:50%; transform:translate(-50%,-50%); width:13px; height:13px; border-radius:50%; border:2.5px solid #fff; box-shadow:0 0 0 1px rgba(0,0,0,.08); z-index:3; }
.tl-dot.High { background:#e5484d; } .tl-dot.Medium { background:#f59e0b; } .tl-dot.Low { background:#94a3b8; }
.tl-dot.past { opacity:.42; }
.tl-ev:hover .tl-dot { transform:translate(-50%,-50%) scale(1.45); box-shadow:0 0 0 4px rgba(15,118,110,.15); }
.tl-dlabel { position:absolute; left:50%; transform:translateX(-50%); font-size:9.5px; font-weight:700; white-space:nowrap; }
.tl-dlabel.future { color:#0f766e; }
.tl-dlabel.pastl { color:#9aa3ad; }
.tl-legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:8px; font-size:11.5px; color:#6b7280; }
.tl-legend span { display:inline-flex; align-items:center; gap:5px; }
.tl-legend i { width:9px; height:9px; border-radius:50%; display:inline-block; }
.tbd-row { margin-top:14px; padding-top:12px; border-top:1px dashed #e5e7eb; }
.tbd-title { font-size:11.5px; color:#9aa3ad; margin-bottom:7px; }
.tbd-chips { display:flex; flex-wrap:wrap; gap:7px; }
.tbd-chip { font-size:12px; background:#f8fafc; border:1px solid #eef0f2; border-radius:99px; padding:5px 12px; cursor:pointer; color:#374151; }
.tbd-chip:hover { background:#f1f5f9; }
.tbd-chip b { color:#0f766e; }

.guide { background:#fff; border:1px solid #e6e8eb; border-radius:12px; overflow:hidden; }
.guide-head { padding:14px 16px; cursor:pointer; display:flex; align-items:center; gap:8px; font-weight:700; font-size:14px; }
.guide-head:hover { background:#fafafa; }
.guide-body { display:none; padding:0 16px 16px; }
.guide.open .guide-body { display:block; }
.guide-intro { font-size:13.5px; color:#374151; background:#f8fafc; border-radius:8px; padding:12px 14px; margin-bottom:12px; }
.kp { display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); gap:10px; }
.kp-item { border:1px solid #eef0f2; border-radius:8px; padding:10px 12px; }
.kp-item b { font-size:13px; color:#0f766e; }
.kp-item p { font-size:12.5px; color:#4b5563; margin-top:4px; }
.chev { transition:transform .15s; font-size:12px; color:#9ca3af; margin-left:auto; }
.open > .guide-head .chev, .card.open .chev { transform:rotate(90deg); }

.filters { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
.fbtn { border:1px solid #d1d5db; background:#fff; border-radius:99px; padding:5px 13px; font-size:12.5px; cursor:pointer; color:#374151; }
.fbtn.on { background:#0f766e; border-color:#0f766e; color:#fff; }

.card { background:#fff; border:1px solid #e6e8eb; border-radius:12px; margin-bottom:12px; overflow:hidden; }
.card.imp-High { border-left:4px solid #e5484d; }
.card.imp-Medium { border-left:4px solid #f59e0b; }
.card.imp-Low { border-left:4px solid #cbd5e1; }
.card-head { padding:14px 16px; cursor:pointer; }
.card-head:hover { background:#fafafa; }
.chrow { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.badge { font-size:11px; font-weight:700; padding:2.5px 8px; border-radius:99px; white-space:nowrap; }
.b-cat { background:#eef2ff; color:#3730a3; }
.b-st-active { background:#dcfce7; color:#166534; }
.b-st-planned { background:#fef3c7; color:#92400e; }
.b-st-pending { background:#e0e7ff; color:#3730a3; }
.b-st-disc { background:#f3f4f6; color:#4b5563; }
.b-imp-High { background:#fde7e7; color:#c11; }
.b-imp-Medium { background:#fff3e0; color:#b45309; }
.b-imp-Low { background:#eef2f5; color:#475569; }
.b-dday { background:#111827; color:#fff; }
.ct { font-size:15px; font-weight:700; margin-top:7px; }
.cru { font-size:12px; color:#6b7280; margin-top:2px; }
.cdate { font-size:12px; color:#0f766e; font-weight:600; margin-top:4px; }
.card-body { display:none; padding:0 16px 16px; border-top:1px solid #f3f4f6; }
.card.open .card-body { display:block; }
.blk { margin-top:14px; }
.blk-t { font-size:12px; font-weight:800; color:#0f766e; text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; }
.blk p { font-size:13.5px; color:#374151; }
.blk ul { margin:0; padding-left:0; list-style:none; }
.blk ul li { font-size:13.5px; color:#374151; padding:5px 0 5px 26px; position:relative; }
.blk ul.checks li::before { content:"☐"; position:absolute; left:4px; color:#0f766e; font-weight:700; }
.blk ul.docs li::before { content:"📄"; position:absolute; left:0; font-size:12px; }
.proc { background:#f8fafc; border-radius:8px; padding:10px 12px; font-size:13px; color:#374151; }
.pen { background:#fff5f5; border-left:3px solid #e5484d; border-radius:6px; padding:9px 12px; font-size:13px; color:#7f1d1d; }
.gl { display:flex; flex-wrap:wrap; gap:6px; }
.gl span { font-size:12px; background:#f3f4f6; border-radius:6px; padding:4px 9px; color:#4b5563; }
.gl b { color:#111827; }
.srcs a { font-size:12px; color:#2563eb; text-decoration:none; display:block; padding:2px 0; word-break:break-all; }
.srcs a:hover { text-decoration:underline; }
footer { margin-top:26px; font-size:11.5px; color:#9ca3af; text-align:center; }
.empty { text-align:center; color:#9ca3af; font-size:13px; padding:30px 0; }
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="langbar" id="langbar"></div>
  <h1 id="h1Title"></h1>
  <div class="sub" id="subLabel"></div>
  <div class="sumrow" id="sumrow"></div>
</header>

<div class="section-title" id="tlSectionTitle"></div>
<div class="tl-wrap">
  <div class="tl-inner" id="tlInner"></div>
  <div class="tl-legend" id="tlLegend"></div>
  <div class="tbd-row">
    <div class="tbd-title" id="tbdTitle"></div>
    <div class="tbd-chips" id="tbdChips"></div>
  </div>
</div>

<div class="section-title" id="guideSectionTitle"></div>
<div class="guide" id="guide">
  <div class="guide-head" onclick="this.parentElement.classList.toggle('open')">
    <span id="guideToggleLabel"></span>
    <span class="chev">▶</span>
  </div>
  <div class="guide-body">
    <div class="guide-intro" id="guideIntro"></div>
    <div class="kp" id="guideKp"></div>
  </div>
</div>

<div class="section-title" id="listSectionTitle"></div>
<div class="filters" id="catFilters"></div>
<div class="filters" id="stFilters"></div>

<div class="section-title" style="margin-top:20px" id="sectionUpcomingTitle"></div>
<div id="upcomingCards"></div>

<div class="section-title" id="sectionActiveTitle"></div>
<div id="activeCards"></div>

<div class="empty" id="empty" style="display:none"></div>

<footer id="footerText"></footer>
</div>

<script>
const DATA = __DATA__;
const CATS = __CATS__;
const STATUS = __STATUS__;
const STATUS_DESC = __STATUS_DESC__;
const UI = __UI__;
const TODAY_STR = "__TODAY__";

let lang = (function(){ try { return localStorage.getItem('laborLangPref') || 'ko'; } catch(e){ return 'ko'; } })();
const impRank = {"High":3,"Medium":2,"Low":1};
let fCat = "전체", fSt = "전체";

function parseDate(s){
  const m = s && s.match(/(\d{4})-(\d{2})-(\d{2})/);
  return m ? new Date(+m[1], +m[2]-1, +m[3]) : null;
}
const today = parseDate(TODAY_STR) || new Date();
today.setHours(0,0,0,0);
DATA.regulations.forEach(r => { r._date = parseDate(r.effectiveDate); });

function T(){ return UI[lang]; }
function title(r){ return lang==='ko' ? r.titleKo : (lang==='en' ? r.titleEn : r.titleRu); }
function field(r, key){ return lang==='ko' ? r[key] : r.i18n[lang][key]; }
function effDateDisplay(r){ if (lang==='ko' || !r.effectiveDateI18n) return r.effectiveDate; return r.effectiveDateI18n[lang] || r.effectiveDate; }
function catLabel(cat){ return (CATS[cat] && CATS[cat][lang]) || cat; }
function stLabel(st){ return (STATUS[st] && STATUS[st][lang]) || st; }

function setLangBar(){
  const opts = [["ko","한국어"],["en","EN"],["ru","RU"]];
  document.getElementById('langbar').innerHTML = opts.map(([code,label]) =>
    `<button class="langbtn ${lang===code?'on':''}" onclick="setLang('${code}')">${label}</button>`).join('');
}
function setLang(code){
  lang = code;
  try { localStorage.setItem('laborLangPref', code); } catch(e){}
  renderAll();
}

function renderAll(){
  setLangBar();
  document.documentElement.lang = lang;
  const t = T();
  document.getElementById('h1Title').textContent = t.pageTitle;
  document.getElementById('subLabel').innerHTML = t.subLabel + ' <span>' + t.updatedPrefix + DATA.meta.lastUpdated + '</span>';
  document.getElementById('tlSectionTitle').innerHTML = t.tlSection + ' <span class="cnt" id="tlCnt"></span>';
  document.getElementById('guideSectionTitle').textContent = t.guideSection;
  document.getElementById('guideToggleLabel').textContent = t.guideToggle;
  document.getElementById('listSectionTitle').innerHTML = t.listSection + ' <span class="cnt">' + t.sortedNote + '</span>';
  document.getElementById('sectionUpcomingTitle').innerHTML = t.sectionUpcoming + ' <span class="cnt" id="upcomingCnt"></span>';
  document.getElementById('sectionActiveTitle').innerHTML = t.sectionActive + ' <span class="cnt" id="activeCnt"></span>';
  document.getElementById('tbdTitle').textContent = t.tbdTitle;
  document.getElementById('empty').textContent = t.emptyState;
  document.getElementById('footerText').textContent = t.footer;
  document.getElementById('tlLegend').innerHTML =
    '<span><i style="background:#e5484d"></i>' + t.impactLabel + ' High</span>' +
    '<span><i style="background:#f59e0b"></i>' + t.impactLabel + ' Medium</span>' +
    '<span><i style="background:#94a3b8"></i>' + t.impactLabel + ' Low</span>' +
    '<span style="opacity:.55">' + t.pastDotNote + '</span>';

  renderSummary();
  renderTimeline();
  renderGuide();
  renderFilters();
  renderCards();
}

function renderSummary(){
  const stCounts = {};
  DATA.regulations.forEach(r => stCounts[r.status] = (stCounts[r.status]||0)+1);
  document.getElementById('sumrow').innerHTML =
    ['시행중','시행예정','계류중','논의중'].map(s =>
      `<div class="sumchip"><div class="n">${stCounts[s]||0}</div><div class="l">${stLabel(s)}</div></div>`).join('');
}

function renderTimeline(){
  const dated = DATA.regulations.filter(r => r._date);
  const tbd = DATA.regulations.filter(r => !r._date);
  document.getElementById('tlCnt').textContent = T().tlCntTemplate.replace('{n}', dated.length).replace('{m}', tbd.length);

  let minD, maxD;
  if (dated.length){
    minD = new Date(Math.min(today, ...dated.map(r=>r._date.getTime())));
    maxD = new Date(Math.max(today, ...dated.map(r=>r._date.getTime())));
  } else { minD = new Date(today); maxD = new Date(today); }
  minD = new Date(minD.getFullYear(), minD.getMonth()-1, 1);
  maxD = new Date(maxD.getFullYear(), maxD.getMonth()+2, 1);
  const span = maxD - minD;
  function xPos(d){ return ((d - minD) / span) * 100; }

  const ticks = [];
  let cur = new Date(minD.getFullYear(), Math.floor(minD.getMonth()/3)*3, 1);
  while (cur <= maxD){ ticks.push(new Date(cur)); cur = new Date(cur.getFullYear(), cur.getMonth()+3, 1); }

  const byDate = {};
  dated.forEach(r => { const k = r._date.toISOString().slice(0,10); (byDate[k] = byDate[k] || []).push(r); });

  let tl = '';
  tl += `<div class="tl-axis"></div>`;
  ticks.forEach(t => {
    const x = xPos(t);
    tl += `<div class="tl-tick" style="left:${x}%"></div>`;
    tl += `<div class="tl-tick-label" style="left:${x}%">${t.getFullYear()}.${String(t.getMonth()+1).padStart(2,'0')}</div>`;
  });
  const todayX = xPos(today);
  tl += `<div class="tl-today" style="left:${todayX}%"></div>`;
  tl += `<div class="tl-today-label" style="left:${todayX}%">${T().todayLabel}${today.getFullYear()}.${String(today.getMonth()+1).padStart(2,'0')}.${String(today.getDate()).padStart(2,'0')}</div>`;

  Object.keys(byDate).forEach(k => {
    const group = byDate[k].sort((a,b)=>impRank[b.impact]-impRank[a.impact]);
    const d = group[0]._date;
    const x = xPos(d);
    const isPast = d < today;
    group.forEach((r, i) => {
      const dy = i * 17;
      tl += `<div class="tl-ev" style="left:${x}%; top:${dy}px" onclick="openCard('${r.id}')" title="${title(r)} (${stLabel(r.status)}, ${T().impactLabel} ${r.impact}, ${r.effectiveDate})">
        <div class="tl-dot ${r.impact} ${isPast?'past':''}"></div>
      </div>`;
    });
    const labelY = 20 + (group.length-1)*17;
    tl += `<div class="tl-dlabel ${isPast?'pastl':'future'}" style="left:${x}%; top:${labelY}px">${d.getMonth()+1}/${d.getDate()}${!isPast ? ' · D-'+Math.round((d-today)/86400000) : ''}</div>`;
  });

  document.getElementById('tlInner').innerHTML = tl;
  document.getElementById('tlInner').style.height = (100 + Math.max(...Object.values(byDate).map(g=>g.length),1)*17) + 'px';

  document.getElementById('tbdChips').innerHTML = tbd.length ? tbd.map(r =>
    `<div class="tbd-chip" onclick="openCard('${r.id}')"><b>${stLabel(r.status)}</b> · ${title(r)} <span style="color:#9aa3ad">(${effDateDisplay(r)})</span></div>`
  ).join('') : '';
}

function renderGuide(){
  const g = lang==='ko' ? DATA.basicsGuide : DATA.basicsGuide.i18n[lang];
  document.getElementById('guideIntro').textContent = g.intro;
  document.getElementById('guideKp').innerHTML = g.keyPoints.map(k =>
    `<div class="kp-item"><b>${k.title}</b><p>${k.desc}</p></div>`).join('');
}

function renderFilters(){
  const cats = ["전체", ...new Set(DATA.regulations.map(r => r.category))];
  const sts = ["전체","시행중","시행예정","계류중","논의중"];
  document.getElementById('catFilters').innerHTML = cats.map(c =>
    `<button class="fbtn ${fCat===c?'on':''}" onclick="fCat='${c}';renderFilters();renderCards()">${c==="전체"?T().filterAll:catLabel(c)}</button>`).join('');
  document.getElementById('stFilters').innerHTML = sts.map(s =>
    `<button class="fbtn ${fSt===s?'on':''}" onclick="fSt='${s}';renderFilters();renderCards()">${s==="전체"?T().filterAll:stLabel(s)}</button>`).join('');
}

function blk(t, inner){ return inner ? `<div class="blk"><div class="blk-t">${t}</div>${inner}</div>` : ''; }

function cardHtml(r){
  const t = T();
  const bg = field(r,'background'), wc = field(r,'whatChanged'), pen = field(r,'penalty'),
        proc = field(r,'process'), checks = field(r,'hrChecklist'), docs = field(r,'internalDocs');
  const showGlossary = lang !== 'ru' && r.glossary && r.glossary.length;
  const glossHtml = showGlossary ? r.glossary.map(g => {
    if (lang === 'en') return `<span><b>${g.term}</b>${g.en ? ' — '+g.en : ''}</span>`;
    return `<span><b>${g.term}</b>${g.en ? ` (${g.en})` : ''} — ${g.ko}</span>`;
  }).join('') : '';
  return `
  <div class="card imp-${r.impact}" id="card-${r.id}">
    <div class="card-head" onclick="this.parentElement.classList.toggle('open')">
      <div class="chrow">
        <span class="badge b-cat">${catLabel(r.category)}</span>
        <span class="badge ${({"시행중":"b-st-active","시행예정":"b-st-planned","계류중":"b-st-pending","논의중":"b-st-disc"})[r.status]||'b-st-disc'}">${stLabel(r.status)}</span>
        <span class="badge b-imp-${r.impact}">${t.impactLabel} ${r.impact}</span>
        ${r._date && r._date >= today ? `<span class="badge b-dday">D-${Math.round((r._date-today)/86400000)}</span>` : ''}
        <span class="chev">▶</span>
      </div>
      <div class="ct">${title(r)}</div>
      <div class="cru">${lang==='ko' ? (r.titleRu + (r.titleEn?` · <span style="color:#0f766e">${r.titleEn}</span>`:'')) : (lang==='en' ? r.titleRu : r.titleEn)}</div>
      <div class="cdate">${lang==='ko'?'시행':(lang==='en'?'Effective':'Вступление в силу')}: ${effDateDisplay(r)}</div>
    </div>
    <div class="card-body">
      ${blk(t.blkBackground, `<p>${bg}</p>`)}
      ${blk(t.blkWhatChanged, `<p>${wc}</p>`)}
      ${blk(t.blkChecklist, `<ul class="checks">${checks.map(c=>`<li>${c}</li>`).join('')}</ul>`)}
      ${blk(t.blkDocs, `<ul class="docs">${docs.map(d=>`<li>${d}</li>`).join('')}</ul>`)}
      ${blk(t.blkProcess, `<div class="proc">${proc}</div>`)}
      ${blk(t.blkPenalty, `<div class="pen">${pen}</div>`)}
      ${showGlossary ? blk(t.blkGlossary, `<div class="gl">${glossHtml}</div>`) : ''}
      ${blk(t.blkSources, `<div class="srcs">${r.sources.map(s=>`<a href="${s}" target="_blank">${s}</a>`).join('')}</div>`)}
    </div>
  </div>`;
}

function renderCards(){
  const filtered = DATA.regulations.filter(r =>
    (fCat==="전체"||r.category===fCat) && (fSt==="전체"||r.status===fSt));

  const active = filtered.filter(r => r.status === "시행중")
    .sort((a,b) => impRank[b.impact]-impRank[a.impact] || (b._date?b._date.getTime():-Infinity) - (a._date?a._date.getTime():-Infinity));

  const upcoming = filtered.filter(r => r.status !== "시행중")
    .sort((a,b) => impRank[b.impact]-impRank[a.impact] || (a._date?a._date.getTime():Infinity) - (b._date?b._date.getTime():Infinity));

  document.getElementById('activeCnt').textContent = active.length + (lang==='ko' ? '건' : '');
  document.getElementById('upcomingCnt').textContent = upcoming.length + (lang==='ko' ? '건' : '');
  document.getElementById('activeCards').innerHTML = active.map(cardHtml).join('');
  document.getElementById('upcomingCards').innerHTML = upcoming.map(cardHtml).join('');
  document.getElementById('empty').style.display = (active.length + upcoming.length) ? 'none' : 'block';
}

function openCard(id){
  fCat = "전체"; fSt = "전체"; renderFilters(); renderCards();
  const el = document.getElementById('card-'+id);
  if (el){ el.classList.add('open'); el.scrollIntoView({behavior:'smooth', block:'start'}); }
}

renderAll();
</script>
</body>
</html>"""


def build():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    # Use current UTC date as "today" for the timeline marker. Data's meta.lastUpdated
    # should be set by the update process to the date content was last researched.
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    html = HTML_TEMPLATE
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__CATS__", json.dumps(CATS, ensure_ascii=False))
    html = html.replace("__STATUS__", json.dumps(STATUS, ensure_ascii=False))
    html = html.replace("__STATUS_DESC__", json.dumps(STATUS_DESC, ensure_ascii=False))
    html = html.replace("__UI__", json.dumps(UI, ensure_ascii=False))
    html = html.replace("__TODAY__", today_str)

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Built {OUT_PATH} ({len(html)} bytes) from {len(data['regulations'])} regulations, today={today_str}")


if __name__ == "__main__":
    build()
