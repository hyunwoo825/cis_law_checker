#!/usr/bin/env python3
"""
data/labor-regulations.json 의 이전 커밋(HEAD^) 대비 변경점을 사람이 읽을 수 있는
한국어 텍스트로 요약해서 summary.txt 로 출력한다.
GitHub Actions에서: git show HEAD^:data/labor-regulations.json 을 stdin으로 넘기거나
old.json / new.json 두 파일 경로를 인자로 받는다.

Usage:
    python3 build_email_summary.py <old_json_path_or_-> <new_json_path> <output_path>

<old_json_path_or_-> 가 파일이 없거나 "-" 인 경우(최초 커밋 등) "이번이 첫 데이터"로 처리.
"""
import json
import sys
import os

FIELDS_TO_CHECK = [
    ("status", "상태"),
    ("impact", "영향도"),
    ("effectiveDate", "시행일"),
    ("background", "배경"),
    ("whatChanged", "변경내용"),
    ("penalty", "벌금/제재"),
    ("process", "절차"),
    ("hrChecklist", "HR 체크리스트"),
    ("internalDocs", "개정 대상 문서"),
]


def load_json(path):
    if not path or path == "-" or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_by_id(data):
    if not data:
        return {}
    return {r["id"]: r for r in data.get("regulations", [])}


def main():
    old_path, new_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    old_data = load_json(old_path)
    new_data = load_json(new_path)

    lines = []
    meta = new_data.get("meta", {}) if new_data else {}
    last_updated = meta.get("lastUpdated", "")

    if old_data is None:
        lines.append(f"최초 데이터 커밋입니다. 총 {len(new_data.get('regulations', []))}건이 등록되어 있습니다.")
        out = "\n".join(lines)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
        return

    old_map = index_by_id(old_data)
    new_map = index_by_id(new_data)

    added = [rid for rid in new_map if rid not in old_map]
    removed = [rid for rid in old_map if rid not in new_map]
    changed = []

    for rid in new_map:
        if rid in old_map:
            old_r, new_r = old_map[rid], new_map[rid]
            diff_fields = []
            for key, label in FIELDS_TO_CHECK:
                if old_r.get(key) != new_r.get(key):
                    diff_fields.append(label)
            if diff_fields:
                changed.append((rid, new_r, diff_fields))

    if not added and not removed and not changed:
        lines.append("데이터 내용에 실질적인 변경이 없습니다 (메타 정보만 갱신되었을 수 있음).")
    else:
        lines.append(f"이번 주 업데이트 요약 (기준일: {last_updated})")
        lines.append("=" * 50)

        if added:
            lines.append("")
            lines.append(f"[신규 추가 {len(added)}건]")
            for rid in added:
                r = new_map[rid]
                lines.append(f"- {rid} | {r.get('titleKo','')} ({r.get('titleEn','')})")
                lines.append(f"    분류: {r.get('category','')} / 상태: {r.get('status','')} / 영향도: {r.get('impact','')}")
                lines.append(f"    시행일: {r.get('effectiveDate','')}")

        if changed:
            lines.append("")
            lines.append(f"[내용 변경 {len(changed)}건]")
            for rid, r, diff_fields in changed:
                lines.append(f"- {rid} | {r.get('titleKo','')} ({r.get('titleEn','')})")
                lines.append(f"    변경된 항목: {', '.join(diff_fields)}")

        if removed:
            lines.append("")
            lines.append(f"[비정상: 삭제 감지 {len(removed)}건] (원칙적으로 삭제되면 안 됨, 확인 필요)")
            for rid in removed:
                lines.append(f"- {rid}")

    lines.append("")
    lines.append("-" * 50)
    lines.append("대시보드: https://hyunwoo825.github.io/cis_law_checker/")
    lines.append("리포: https://github.com/hyunwoo825/cis_law_checker")

    out = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(out)


if __name__ == "__main__":
    main()
