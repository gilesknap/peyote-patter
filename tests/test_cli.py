"""End-to-end CLI tests that actually invoke peyote.cli.main()."""

import json
import sys

import pytest
from PIL import Image

from peyote.cli import main
from peyote.font_ttf import available_fonts


needs_font = pytest.mark.skipif(
    not available_fonts(),
    reason="no system TTF fonts available",
)


def run_cli(monkeypatch, capsys, *argv):
    """Invoke main() with argv (without the program name)."""
    monkeypatch.setattr(sys, 'argv', ['peyote', *argv])
    main()
    return capsys.readouterr()


class TestCLIBasic:
    def test_no_args_errors(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['peyote'])
        with pytest.raises(SystemExit):
            main()

    @needs_font
    def test_text_to_png(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.png'
        result = run_cli(
            monkeypatch, capsys, 'HI', '--format', 'png',
            '--columns', '10', '--rows', '40',
            '--no-open', '-o', str(out),
        )
        assert out.exists()
        with Image.open(out) as img:
            assert img.format == 'PNG'
        assert 'Saved' in result.out

    @needs_font
    def test_text_to_svg(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.svg'
        run_cli(
            monkeypatch, capsys, 'HI', '--format', 'svg',
            '--columns', '10', '--rows', '40',
            '--no-open', '-o', str(out),
        )
        assert out.read_text().startswith('<svg')

    @needs_font
    def test_text_to_pdf(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.pdf'
        run_cli(
            monkeypatch, capsys, 'HI', '--format', 'pdf',
            '--columns', '10', '--rows', '40',
            '--no-open', '-o', str(out),
        )
        assert out.read_bytes()[:4] == b'%PDF'

    @needs_font
    def test_text_to_json(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, 'HI', '--format', 'json',
            '--columns', '10', '--rows', '40',
            '-o', str(out),
        )
        data = json.loads(out.read_text())
        assert 'fabric' in data
        assert data['title'] == 'HI'


class TestCLIPatterns:
    def test_pattern_only_renders(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        assert len(data['fabric']) == 20
        assert data['title'] == 'checker pattern'

    @needs_font
    def test_text_with_border(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, 'HI', '--border', 'checker',
            '--columns', '10', '--rows', '60',
            '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        # Borders should add accent-slot beads (>=2)
        flat = {v for row in data['fabric'] for v in row}
        assert any(v >= 2 for v in flat)

    @needs_font
    def test_text_with_wrap_border(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, 'HI', '--border', 'stripe-v',
            '--wrap-border', '--margin', '4', '--gap', '1',
            '--columns', '20', '--rows', '60',
            '--format', 'json', '-o', str(out),
        )
        assert out.exists()


class TestCLIPresets:
    def test_preset_ring(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker', '--preset', 'ring',
            '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        # ring preset is 10×72
        assert data['config']['columns'] == 10
        assert data['config']['rows'] == 72

    def test_preset_rows_override(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker', '--preset', 'ring',
            '--rows', '40', '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        assert data['config']['rows'] == 40


class TestCLIPalette:
    def test_named_palette_used(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20', '--palette', 'ocean',
            '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        assert data['palette']['colors']['0'] == '#E8F4F8'

    def test_explicit_colors(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--bg-color', '#123456', '--fg-color', '#abcdef',
            '--format', 'json', '-o', str(out),
        )
        data = json.loads(out.read_text())
        assert data['palette']['colors']['0'] == '#123456'
        assert data['palette']['colors']['1'] == '#abcdef'


class TestCLILoadFromJson:
    def test_load_fabric_from_json(self, tmp_path, monkeypatch, capsys):
        # First write a fabric to JSON, then load it back via CLI
        src = tmp_path / 'src.json'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--format', 'json', '-o', str(src),
        )
        out = tmp_path / 'out.json'
        run_cli(
            monkeypatch, capsys, '--fabric', str(src),
            '--format', 'json', '-o', str(out),
        )
        original = json.loads(src.read_text())['fabric']
        loaded = json.loads(out.read_text())['fabric']
        assert original == loaded


class TestCLIBeadCount:
    def test_bead_count_printed(self, tmp_path, monkeypatch, capsys):
        out = tmp_path / 'p.json'
        result = run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--format', 'json', '--bead-count', '-o', str(out),
        )
        assert 'Bead count' in result.out
        assert 'Total' in result.out


class TestCLIOutputDefaults:
    def test_default_output_filename(self, tmp_path, monkeypatch, capsys):
        # Run from tmp_path so the default file lands somewhere temporary
        monkeypatch.chdir(tmp_path)
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--format', 'json',
        )
        assert (tmp_path / 'peyote-pattern.json').exists()


class TestCLIOpenViewer:
    def test_xdg_open_invoked_for_png(self, tmp_path, monkeypatch, capsys):
        """When --no-open is not passed for png/pdf/svg, the viewer is launched.

        We capture the Popen call instead of actually opening a viewer.
        """
        from peyote import cli

        captured = {}

        def fake_popen(cmd, **kwargs):
            captured['cmd'] = cmd
            return None  # Popen normally returns a process; we don't use it

        monkeypatch.setattr(cli.subprocess, 'Popen', fake_popen)

        out = tmp_path / 'p.png'
        run_cli(
            monkeypatch, capsys, '--pattern', 'checker',
            '--columns', '10', '--rows', '20',
            '--format', 'png', '-o', str(out),
        )
        assert captured['cmd'] == ['xdg-open', str(out)]
