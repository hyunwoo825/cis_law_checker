# 러시아 노동법 Checker (cis_law_checker)

러시아 법인 근무 한국인 HR 담당자를 위한 러시아 노동법 변경사항 트래킹 대시보드.

## 대시보드 바로가기

**https://hyunwoo825.github.io/cis_law_checker/**

한국어/영어/러시아어 토글 지원. 위 링크로 바로 들어가서 보면 됨.

## 구성

- `data/labor-regulations.json` — 원본 데이터 (직접 수정 대상)
- `build.py` — `data/labor-regulations.json` → `index.html` 생성 스크립트
- `index.html` — 생성된 정적 페이지 (GitHub Pages가 이 파일을 렌더링, **직접 수정 금지**)
- `CLAUDE.md` — 데이터 갱신 규칙/스키마 명세 (Claude Code Routine이 참조)
- `.github/workflows/weekly-summary-email.yml` — `data/labor-regulations.json` 변경이 main에 push되면 변경 요약을 이메일로 발송
- `.github/scripts/build_email_summary.py` — 위 워크플로에서 쓰는 변경점 diff 스크립트

## 자동화 흐름

1. Claude Code Routine이 주 1회 러시아 노동법 관련 소스를 조사해 `data/labor-regulations.json`을 갱신하고 `build.py`로 `index.html`을 재생성한 뒤 main에 직접 push
2. push 이벤트를 GitHub Actions가 감지 → 이전 커밋과 diff해서 이번 주 변경점(신규/변경 항목)을 요약
3. Gmail SMTP로 담당자 메일로 발송, 위 대시보드 링크 첨부

## Pages 설정

Settings → Pages → Source: Deploy from a branch → `main` / `/(root)`
