from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python render_pdf_pages.py <input.pdf> <output_dir>")
        return 1

    try:
        import fitz  # type: ignore
    except ModuleNotFoundError:
        print("PyMuPDF is required. Install with: python -m pip install pymupdf --target <dir>")
        return 2

    pdf_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    for index, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pix.save(output_dir / f"page-{index + 1}.png")
    doc.close()
    print(f"Rendered {len(list(output_dir.glob('page-*.png')))} pages to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
