# Russia Labor Law Checker — project instructions

## Purpose & audience

This repo publishes a trilingual (KO/EN/RU) static dashboard tracking Russian
labor-law changes relevant to a Korean-owned company's HR function in Russia.

Audience: a Korean HR lead running a Russian legal entity (Moscow subsidiary),
with **no prior background in Russian law**. Every item must be written so
that person can act on it without outside help beyond a labor lawyer for
final sign-off. This is not a legal brief — it's an operational HR readiness
briefing. Do not write for Russian lawyers; write for a Korean HR generalist.

Coverage scope (do not expand beyond this without being asked):
- Russian employee labor management (employment contracts, dismissal, working
  time, leave, pay/bonuses)
- Foreign national (expatriate) employment — work permits, HQS/VKS status,
  migration law as it affects hiring/managing foreign staff
- Military registration / mobilization-related employer obligations
  (воинский учёт)
- Personal data / HR data compliance (152-FZ and related)

## Repository layout

```
data/labor-regulations.json   ← single source of truth. Edit this.
build.py                      ← generates index.html from the JSON. Run after every edit.
index.html                    ← FULLY GENERATED. Never hand-edit. Always regenerate via `python build.py`.
CLAUDE.md                     ← this file
.github/workflows/weekly-summary-email.yml   ← fires on push to `main` that touches
                                                data/labor-regulations.json or index.html.
                                                Two ordered jobs: `deploy` (publishes
                                                index.html to GitHub Pages) runs first;
                                                `notify` (needs: deploy) only sends the diff
                                                summary email after deploy succeeds. Requires
                                                repo Settings → Pages → Source = "GitHub
                                                Actions" (not "Deploy from a branch") — the
                                                workflow's `deploy` job has no effect on the
                                                live site otherwise. Email recipients come
                                                from the `NOTIFY_EMAILS` repo variable
                                                (Settings → Secrets and variables → Actions →
                                                Variables), comma-separated — not hardcoded.
```

**Golden rule: `data/labor-regulations.json` is the only file a human or
Claude should edit by hand. `index.html` is a build artifact.** If you ever
find yourself editing `index.html` directly, stop — edit the JSON and run
`python build.py` instead.

## Weekly update procedure

Each run (whether scheduled or manually triggered):

1. **Research.** Search Russian-language sources for developments in the four
   coverage areas above since the last `meta.lastUpdated` date. Good source
   types: kontur.ru, glavbukh.ru, consultant.ru (КонсультантПлюс),
   pravovest-audit.ru, pro-ability.ru, mos.legal, easydocs.ru,
   kommersant.ru, official sources (publication.pravo.gov.ru,
   sozd.duma.gov.ru — bill tracker). Prefer primary/official sources for
   law numbers and dates; secondary HR/legal-media sources are fine for
   plain-language explanation.
2. **Decide new vs. update.** Match against existing `regulations[].id` by
   underlying law/bill (check `titleRu`, law number in `background`/
   `whatChanged`). If a bill's status changed (e.g. 계류중 → 시행중), **update
   the existing entry in place** — do not duplicate. Only add a new entry
   for a genuinely new law/bill/development.
3. **Never delete existing entries.** If something is repealed or superseded,
   update its `status`/`whatChanged` to say so rather than removing it.
4. **Write the Korean fields first** (see schema below), matching the
   existing tone: concise, checklist-driven, always naming the concrete
   internal document to update and the concrete next step — never just
   "review the law."
5. **Immediately fill in `i18n.en` and `i18n.ru`.** This is not optional and
   not a "nice to have" — leaving these blank makes Korean text leak into
   the EN/RU views (this happened once already; see "known pitfalls"
   below). Every regulation must have complete `i18n.en` and `i18n.ru`
   blocks before the run ends.
6. **Assign `impact`:** `High` = direct, material financial/legal exposure or
   affects a large share of staff (e.g. MROT changes, large fines, expat
   status). `Medium` = real but narrower/procedural exposure. `Low` =
   administrative housekeeping with limited direct HR action.
7. **Assign `status`:** `시행중` (already in force) / `시행예정` (promulgated,
   future effective date) / `계류중` (bill pending in the Duma) / `논의중`
   (expected or early-stage discussion). This exact Korean string is the
   data key — do not translate it in the JSON itself; translations live in
   `build.py`'s `STATUS` dict (see below).
8. Update `meta.lastUpdated` to the run date (build.py also does this
   automatically at build time, but set it explicitly if you know the
   research date).
9. **Run `python build.py`.** Fix anything it errors on before proceeding.
10. **Commit and push directly to `main`** — both `data/labor-regulations.json`
    and the regenerated `index.html`, together, in one commit. This routine
    does **not** use a feature branch or PR: pushing straight to `main` is the
    intended, approved workflow for this repo (it's also what triggers
    `.github/workflows/weekly-summary-email.yml`, which emails a summary of
    the update). Commit message: `Weekly update YYYY-MM-DD: <n> added, <m>
    updated` (state which IDs).

## `data/labor-regulations.json` schema

Top level: `{ meta, basicsGuide, regulations: [...] }`.

### `meta`
- `title`, `audience`, `lastUpdated` (YYYY-MM-DD), `note`, `statusLegend`
  (Korean status descriptions — leave structure as-is, this is legacy and
  superseded by `build.py`'s STATUS_DESC map, kept for data completeness).

### `basicsGuide`
- `intro` (Korean), `keyPoints[]` (`{title, desc}` in Korean) — the "8 key
  concepts" primer explaining Russian HR/legal jargon to a first-time
  Korean reader (ЛНА, ГИТ, приказ, КЭДО, МРОТ, воинский учёт, ВКС,
  consultation sequence).
- `i18n.en` / `i18n.ru` — same shape (`intro`, `keyPoints[]`), full English
  and Russian translations. Only extend this if you add a genuinely new
  concept to the primer (rare) — do not add per-regulation content here.

### `regulations[]` — each item:

| Field | Type | Notes |
|---|---|---|
| `id` | string | `LAB-NNN`, next sequential number, never reuse/renumber existing IDs |
| `category` | string (Korean, enum) | One of: `급여·보상`, `채용·해고`, `문서·시스템`, `외국인·주재원`, `병역·군동원`, `인사데이터`. If a genuinely new category is needed, add it here **and** to `CATS` in `build.py` with en/ru labels — otherwise the filter chip and card badge will show the raw Korean key untranslated in EN/RU views. |
| `titleKo` | string | Korean title, plain description of the change |
| `titleRu` | string | Original Russian title/law citation (as commonly referenced in Russian sources) |
| `titleEn` | string | English title (parallel to titleRu, not a translation of titleKo) |
| `status` | string (Korean, enum) | `시행중` / `시행예정` / `계류중` / `논의중` — must match a key in `STATUS` in build.py |
| `impact` | string enum | `High` / `Medium` / `Low` (kept as English tokens across all languages — do not translate) |
| `effectiveDate` | string | ISO `YYYY-MM-DD` where possible. If the actual date is not a clean ISO date (e.g. "2026년 내 채택 전망", "미정 (2026년 발의)"), still try to embed a `YYYY-MM-DD` substring if any date is known (the timeline parser extracts dates via regex `\d{4}-\d{2}-\d{2}`); if truly no date exists, leave it as free Korean text — the build script will bucket it into the "date TBD" list. **If this field contains free-form Korean prose (not a clean date), you must also add `effectiveDateI18n: {en, ru}`** — see known pitfalls. |
| `background` | string (Korean) | Why this changed — 1-3 sentences of context |
| `whatChanged` | string (Korean) | The concrete change, numbered ① ② ③ if multi-part |
| `penalty` | string (Korean) | Concrete consequence of non-compliance, with fine amounts/article numbers where known |
| `hrChecklist` | string[] (Korean) | 3-5 concrete, checkable actions — not vague advice |
| `internalDocs` | string[] (Korean) | Concrete internal document names to review/amend |
| `process` | string (Korean) | Who to involve, in what order, using `→` arrows |
| `glossary` | `{term, ko, en}[]` | Russian jargon terms used in this item's text, with Korean explanation and English gloss. Omit if the item doesn't introduce new jargon beyond what's in `basicsGuide`. |
| `sources` | string[] | Real URLs. At least one, prefer 2 for anything with legal/financial consequences. |
| `i18n` | `{en: {...}, ru: {...}}` | **Required.** Each of `en`/`ru` must contain: `background`, `whatChanged`, `penalty`, `process`, `hrChecklist` (array), `internalDocs` (array) — full independent translations, not machine-literal; write them the way an HR consultant would write for that audience. Do NOT include `titleKo`/`titleRu`/`titleEn` here (those already exist at top level) and do NOT duplicate `glossary` here (EN glossary reuses `glossary[].en`; RU view hides the glossary block entirely since the terms are native to that reader — see below). |
| `effectiveDateI18n` | `{en, ru}` (optional) | Only present when `effectiveDate` is free-form Korean prose instead of a clean date. Translate that prose, e.g. `"시행중 (통제 강화 지속)"` → `en: "Ongoing (enforcement continuing to tighten)"`, `ru: "Действует (контроль продолжает ужесточаться)"`. |

## Known pitfalls (read before editing)

1. **Korean leaking into EN/RU views.** Any regulation missing its `i18n`
   block, or with an `effectiveDate` that's free-form Korean text but no
   `effectiveDateI18n`, will show raw Korean in the English/Russian toggle
   views. This is a real bug that shipped once already — always grep the
   built `index.html` for Korean characters while in EN/RU mode before
   considering a run done (see verification step below).
2. **New `category` not added to `build.py`'s `CATS` dict** → filter chips
   and card badges show the untranslated Korean key in EN/RU views. Same
   failure mode for a new `status` value not added to `STATUS`/`STATUS_DESC`.
3. **Glossary in RU view.** The build script deliberately hides the glossary
   block when `lang === 'ru'` (a Russian-speaking reader doesn't need
   Russian jargon explained in Russian). Don't try to "fix" this — it's
   intentional, matches earlier explicit product direction.
4. **`impact` and `status` are literal enum tokens, not free text.** Don't
   invent new impact levels; don't translate `High`/`Medium`/`Low`.
5. **Sorting/sectioning is automatic**, driven by `status` (`시행중` → "Already
   in Effect" section; everything else → "Upcoming/Pending/Discussion"
   section) and `impact` (High→Low within each section, then by date). You
   do not need to manually order `regulations[]` — but for readability keep
   related/sequential law numbers near each other if convenient.
6. **Do not add a "lens"/persona badge to the UI.** This was explicitly
   removed at the user's request — the page is a plain overview for local
   staff, not framed around a particular reader's perspective.
7. **Footer must credit real information sources**, not the internal data
   file path. If you change the mix of sources materially, update the
   footer text in `build.py`'s `UI[lang].footer` for all three languages.

## Verification before finishing a run

Run this after `python build.py` to catch the Korean-leak class of bug
before committing (adjust paths if needed):

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('index.html','utf8');
const script = html.split('<script>')[1].split('</script>')[0];
const store = {};
function elStub(id){ if(!store[id]) store[id] = {_html:'',_text:'',style:{},classList:{toggle(){},add(){}},
  set innerHTML(v){this._html=v;}, get innerHTML(){return this._html;},
  set textContent(v){this._text=v;}, get textContent(){return this._text;}, scrollIntoView(){} }; return store[id]; }
global.document = { getElementById: elStub, documentElement:{lang:''} };
const ls={}; global.localStorage={getItem:k=>ls[k]||null, setItem:(k,v)=>{ls[k]=v;}};
eval(script);
['en','ru'].forEach(l => {
  eval('setLang(\"'+l+'\")');
  const all = store['activeCards']._html + store['upcomingCards']._html;
  const leaks = (all.match(/[가-힣]+/g)||[]);
  console.log(l, 'korean leaks:', leaks.length, leaks.slice(0,5));
});
"
```

Both `en` and `ru` must report `korean leaks: 0`. If not, find the
regulation missing its i18n/effectiveDateI18n and fix it before committing.

## Style conventions

- Korean is the base language throughout `data/labor-regulations.json`
  top-level fields; `i18n.en`/`i18n.ru` carry full parallel translations.
- Russian legal/technical terms mentioned in Korean prose should be
  annotated inline as `Русский термин/EnglishGloss` on first use within a
  field (matches existing entries) — but only in the **Korean** fields;
  the `i18n.en`/`i18n.ru` translations should read as clean single-language
  prose with no slash-annotations.
- Write `hrChecklist` and `internalDocs` items as concrete nouns/actions a
  Korean HR generalist can act on directly, not abstract legal summaries.
- Currency: rubles as `₽` with Korean numeral grouping conventions in Korean
  text (e.g. `27,093루블`), plain `RUB` in English, `₽` in Russian.
