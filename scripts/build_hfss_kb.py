"""
Build HFSS modeling knowledge base from ANSYS product PDF docs.

Usage:
    python scripts/build_hfss_kb.py --doc-root "E:/download/ANSYS2026R1/ANSYS2026R1_ProductDocPDF/v261"

Output:
    hfss_modeling_knowledge_base.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from pypdf import PdfReader
except Exception as exc:
    raise SystemExit(
        "Missing dependency 'pypdf'. Install with: pip install pypdf"
    ) from exc


HFSS_CORE_KEYWORDS = [
    "hfss",
    "electronics desktop",
    "aedt",
    "3d layout",
    "maxwell",
    "q3d",
    "siwave",
]

HFSS_MODELING_KEYWORDS = [
    "wave port",
    "lumped port",
    "radiation boundary",
    "pml",
    "airbox",
    "open region",
    "solution setup",
    "adaptive",
    "mesh",
    "s parameter",
    "driven modal",
    "driven terminal",
    "eigenmode",
    "coax",
    "microstrip",
    "substrate",
    "excitation",
    "frequency sweep",
    "de-embed",
    "boundary condition",
]

TOPIC_RULES: List[Tuple[str, List[str], str]] = [
    (
        "端口激励设置",
        ["wave port", "lumped port", "excitation", "de-embed"],
        "自动建模时先识别馈电截面并匹配端口类型；波导/同轴优先 wave port，集总馈电优先 lumped port，必要时设置 de-embed。",
    ),
    (
        "辐射边界与计算域",
        ["radiation boundary", "pml", "airbox", "open region"],
        "自动建模时先创建包络空气域，再对外表面赋予 Radiation 或 PML，避免直接在金属体外表面误设开放边界。",
    ),
    (
        "求解类型与设置",
        ["driven modal", "driven terminal", "eigenmode", "solution setup", "adaptive"],
        "根据结构和目标选择求解类型；端口网络问题优先 Driven 模式，并在 setup 中配置自适应与频率点。",
    ),
    (
        "网格与收敛",
        ["mesh", "adaptive", "convergence", "delta s"],
        "自动建模时优先依赖自适应网格；关键缝隙、馈点、薄介质附近应增加局部网格关注。",
    ),
    (
        "参数化与扫描",
        ["parameter", "sweep", "optimization", "design variable"],
        "把关键几何和材料参数变量化，再配置频率扫和参数扫，保证自动建模后可直接用于优化。",
    ),
]


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_candidate_pdf(name: str) -> bool:
    lower = name.lower()
    if lower.startswith("._"):
        return False

    # Only keep docs most likely to have HFSS/AEDT content
    keep_keywords = [
        "electronics_desktop",
        "spaceclaim",
        "cad",
        "workbench",
        "sherlock",
        "icepak",
        "act",
        "scripting",
        "release_notes",
        "known_issues",
        "installation",
        "mechanical",
        "aedt",
    ]
    return any(token in lower for token in keep_keywords)


def score_text_for_hfss(text: str) -> int:
    lower = text.lower()
    
    # Must contain at least one HFSS core keyword
    has_core = any(kw in lower for kw in HFSS_CORE_KEYWORDS)
    if not has_core:
        return 0
    
    # Score by modeling-related keywords (bonus points for building content)
    score = 0
    for kw in HFSS_MODELING_KEYWORDS:
        if kw in lower:
            score += 1
    
    return max(0, score)  # Only keep if at least one modeling keyword found


def extract_relevant_chunks(pdf_path: Path, max_pages: int = 60) -> List[Dict]:
    chunks: List[Dict] = []
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return chunks

    total_pages = min(len(reader.pages), max_pages)

    for i in range(total_pages):
        try:
            raw = reader.pages[i].extract_text() or ""
        except Exception:
            continue

        text = normalize_text(raw)
        if len(text) < 120:
            continue

        score = score_text_for_hfss(text)
        if score <= 0:
            continue

        excerpt = text[:900]
        tags = []
        lower_excerpt = excerpt.lower()
        for topic, keys, _rec in TOPIC_RULES:
            if any(k in lower_excerpt for k in keys):
                tags.append(topic)

        if not tags:
            tags = ["通用HFSS建模"]

        chunks.append(
            {
                "source": pdf_path.name,
                "page": i + 1,
                "score": score,
                "raw_excerpt": excerpt,
                "tags": tags,
            }
        )

    return chunks


def convert_chunk_to_entry(chunk: Dict) -> Dict:
    title = f"{chunk['source']} - p{chunk['page']}"
    primary_tag = chunk["tags"][0] if chunk.get("tags") else "通用HFSS建模"

    recommendation = "在自动建模前先查询该主题规则，并将对应边界/端口/setup策略映射到当前几何。"
    for topic, _keys, rec in TOPIC_RULES:
        if topic == primary_tag:
            recommendation = rec
            break

    summary = f"该页包含与{primary_tag}相关的HFSS/AEDT关键词，可用于自动建模决策。"

    return {
        "title": title,
        "source": chunk["source"],
        "page": chunk["page"],
        "tags": chunk.get("tags", []),
        "summary": summary,
        "recommendation": recommendation,
        "raw_excerpt": chunk.get("raw_excerpt", ""),
        "score": chunk.get("score", 0),
    }


def build_kb(doc_root: Path, output_file: Path, max_files: int = 80) -> Dict:
    all_pdfs = sorted([p for p in doc_root.glob("*.pdf") if is_candidate_pdf(p.name)])
    selected = all_pdfs[:max_files]

    raw_chunks: List[Dict] = []
    for pdf in selected:
        raw_chunks.extend(extract_relevant_chunks(pdf))

    raw_chunks.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_chunks = raw_chunks[:min(250, len(raw_chunks))]
    
    # Filter to keep only high-confidence HFSS modeling entries (score >= 2)
    top_chunks = [c for c in top_chunks if c.get("score", 0) >= 2]
    
    entries = [convert_chunk_to_entry(c) for c in top_chunks]

    kb = {
        "metadata": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source_root": str(doc_root),
            "scanned_files": len(selected),
            "matched_chunks": len(raw_chunks),
            "entry_count": len(entries),
            "note": "Automatically extracted from local ANSYS PDFs; verify critical settings against official docs.",
        },
        "entries": entries,
    }

    output_file.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")
    return kb


def main() -> None:
    parser = argparse.ArgumentParser(description="Build HFSS modeling knowledge base from ANSYS PDF docs")
    parser.add_argument("--doc-root", required=True, help="Path to ANSYS ProductDocPDF/v261 directory")
    parser.add_argument("--output", default="hfss_modeling_knowledge_base.json", help="Output JSON file path")
    parser.add_argument("--max-files", type=int, default=80, help="Maximum candidate PDFs to scan")
    args = parser.parse_args()

    doc_root = Path(args.doc_root)
    if not doc_root.exists() or not doc_root.is_dir():
        raise SystemExit(f"Invalid doc root: {doc_root}")

    output = Path(args.output)
    kb = build_kb(doc_root=doc_root, output_file=output, max_files=args.max_files)

    print("KB build complete")
    print(f"Output: {output.resolve()}")
    print(f"Entries: {kb['metadata']['entry_count']}")
    print(f"Scanned files: {kb['metadata']['scanned_files']}")
    print(f"Matched chunks: {kb['metadata']['matched_chunks']}")


if __name__ == "__main__":
    main()
