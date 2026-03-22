from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pdf2md.cli import main


class TestCliBasic:
    def test_stdout_output(self, cli_runner: CliRunner, simple_text_pdf: str):
        result = cli_runner.invoke(main, [simple_text_pdf])
        assert result.exit_code == 0
        assert "Main Title" in result.output

    def test_file_output(self, cli_runner: CliRunner, simple_text_pdf: str, tmp_path):
        output_file = str(tmp_path / "output.md")
        result = cli_runner.invoke(main, [simple_text_pdf, "-o", output_file])
        assert result.exit_code == 0
        content = Path(output_file).read_text()
        assert "Main Title" in content

    def test_version(self, cli_runner: CliRunner):
        result = cli_runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.1" in result.output

    def test_help(self, cli_runner: CliRunner):
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Convert a PDF document" in result.output


class TestCliErrors:
    def test_nonexistent_file(self, cli_runner: CliRunner):
        result = cli_runner.invoke(main, ["/nonexistent/file.pdf"])
        assert result.exit_code != 0

    def test_images_and_embed_exclusive(
        self, cli_runner: CliRunner, simple_text_pdf: str
    ):
        result = cli_runner.invoke(
            main, [simple_text_pdf, "--images", "--embed-images"]
        )
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output


class TestCliOptions:
    def test_page_range(self, cli_runner: CliRunner, multi_page_pdf: str):
        result = cli_runner.invoke(main, [multi_page_pdf, "-p", "1"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_page_breaks(self, cli_runner: CliRunner, multi_page_pdf: str):
        result = cli_runner.invoke(main, [multi_page_pdf, "--page-breaks"])
        assert result.exit_code == 0
        assert "---" in result.output

    def test_max_header_level(self, cli_runner: CliRunner, simple_text_pdf: str):
        result = cli_runner.invoke(main, [simple_text_pdf, "--max-header-level", "1"])
        assert result.exit_code == 0
        # All headers should be clamped to h1
        for line in result.output.splitlines():
            if line.startswith("#"):
                assert line.startswith("# ")
                assert not line.startswith("## ")

    def test_verbose(self, cli_runner: CliRunner, simple_text_pdf: str):
        result = cli_runner.invoke(main, [simple_text_pdf, "-v"])
        assert result.exit_code == 0

    def test_keep_headers_footers(self, cli_runner: CliRunner, simple_text_pdf: str):
        result = cli_runner.invoke(main, [simple_text_pdf, "--keep-headers-footers"])
        assert result.exit_code == 0

    def test_image_dir_with_spaces(
        self, cli_runner: CliRunner, with_image_pdf: str, tmp_path
    ):
        """Regression: --image-dir with spaces should not fail (GH-1)."""
        image_dir = str(tmp_path / "path with spaces" / "imgs")
        output_file = str(tmp_path / "out.md")
        result = cli_runner.invoke(
            main,
            [with_image_pdf, "--images", "--image-dir", image_dir, "-o", output_file],
        )
        assert result.exit_code == 0, result.output
        written = list(Path(image_dir).glob("*.png"))
        assert len(written) > 0
