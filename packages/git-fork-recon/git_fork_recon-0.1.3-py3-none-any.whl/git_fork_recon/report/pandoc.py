from pathlib import Path
import subprocess
import logging
from typing import List, Set

logger = logging.getLogger(__name__)


class PandocConverter:
    """Handles document format conversion using pandoc."""

    def __init__(self):
        self._pandoc_available = self._check_pandoc_installed()

    def _check_pandoc_installed(self) -> bool:
        """Check if pandoc is installed and available on PATH."""
        try:
            subprocess.run(
                ["pandoc", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _check_latex_installed(self) -> bool:
        """Check if pdflatex and required packages are installed."""
        try:
            subprocess.run(
                ["pdflatex", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def convert(self, input_path: Path, formats: List[str]) -> None:
        """Convert input file to specified formats using pandoc.

        Args:
            input_path: Path to input file (typically markdown)
            formats: List of output formats to generate (e.g. ["html", "pdf"])
        """
        if not self._pandoc_available:
            logger.warning("Pandoc not installed, not generating html or pdf")
            return

        valid_formats: Set[str] = {"html", "pdf"}
        requested_formats = {f.strip().lower() for f in formats}
        formats_to_generate = requested_formats & valid_formats

        for fmt in formats_to_generate:
            output_path = input_path.with_suffix(f".{fmt}")

            # Check for PDF dependencies
            if fmt == "pdf" and not self._check_latex_installed():
                logger.error(
                    "PDF generation requires LaTeX to be installed. "
                    "On Ubuntu/Debian, run: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra"
                )
                continue

            try:
                result = subprocess.run(
                    [
                        "pandoc",
                        "--from=markdown",
                        f"--to={fmt}",
                        str(input_path),
                        "-o",
                        str(output_path),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.info(f"Generated {fmt} report: {output_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to generate {fmt} report: {e}")
                if e.stderr:
                    if fmt == "pdf" and "xcolor.sty" in e.stderr:
                        logger.error(
                            "Missing LaTeX packages required for PDF generation. "
                            "On Ubuntu/Debian, run: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra"
                        )
                    else:
                        logger.error(f"Pandoc error output: {e.stderr}")
