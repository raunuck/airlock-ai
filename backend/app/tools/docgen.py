from pathlib import Path
from datetime import datetime
from docx import Document

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs"

def write_approval_note(findings: str, output_dir: Path | str | None = None) -> str:
    target_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    doc = Document()
    doc.add_heading("Approval Note", level=1)
    doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    doc.add_paragraph("Findings summary:")
    doc.add_paragraph(findings)
    doc.add_paragraph("Recommended action: ___________")

    filename = f"approval_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    file_path = target_dir / filename
    doc.save(str(file_path))
    return f"outputs/{filename}"