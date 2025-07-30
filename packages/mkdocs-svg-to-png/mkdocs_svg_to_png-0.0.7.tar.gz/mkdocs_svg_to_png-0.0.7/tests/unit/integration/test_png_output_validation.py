"""
PNG output validation tests.
Tests that verify the actual PNG conversion results match expected outputs.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest

from mkdocs_svg_to_png.svg_converter import SvgToPngConverter


class TestPngOutputValidation:
    """Tests that validate actual PNG conversion outputs."""

    @pytest.fixture
    def fixtures_input_dir(self):
        """Path to fixtures input directory."""
        return Path(__file__).parent.parent.parent / "fixtures" / "input"

    @pytest.fixture
    def fixtures_expected_dir(self):
        """Path to fixtures expected directory."""
        return Path(__file__).parent.parent.parent / "fixtures" / "expected"

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def converter_config(self):
        """Converter configuration matching expected PNG generation."""
        return {
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": False,
        }

    @pytest.fixture
    def converter(self, converter_config):
        """SvgToPngConverter instance."""
        return SvgToPngConverter(converter_config)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _files_are_similar(
        self, file1: Path, file2: Path, tolerance: float = 0.1
    ) -> bool:
        """Check if two PNG files are similar in size (within tolerance)."""
        if not (file1.exists() and file2.exists()):
            return False

        size1 = file1.stat().st_size
        size2 = file2.stat().st_size

        if size1 == 0 or size2 == 0:
            return False

        # Calculate relative difference
        diff = abs(size1 - size2) / max(size1, size2)
        return diff <= tolerance

    @pytest.mark.parametrize(
        "svg_filename,expected_png_filename",
        [
            (
                "architecture_mermaid_0_07a67020.svg",
                "architecture_mermaid_0_07a67020.png",
            ),
            (
                "class-design_mermaid_0_86b4976d.svg",
                "class-design_mermaid_0_86b4976d.png",
            ),
            (
                "database-design_mermaid_0_3d6e6222.svg",
                "database-design_mermaid_0_3d6e6222.png",
            ),
            ("detailed-diagram.drawio.svg", "detailed-diagram.drawio.png"),
            ("index_mermaid_0_66026a20.svg", "index_mermaid_0_66026a20.png"),
            ("output_basic.svg", "output_basic.png"),
            ("output_sequence.svg", "output_sequence.png"),
            (
                "project-plan_mermaid_0_336420ee.svg",
                "project-plan_mermaid_0_336420ee.png",
            ),
            (
                "state-management_mermaid_0_5231eec1.svg",
                "state-management_mermaid_0_5231eec1.png",
            ),
            (
                "system-overview_mermaid_0_93d92671.svg",
                "system-overview_mermaid_0_93d92671.png",
            ),
            (
                "user-journey_mermaid_0_ccef6318.svg",
                "user-journey_mermaid_0_ccef6318.png",
            ),
        ],
    )
    def test_png_conversion_matches_expected(
        self,
        converter,
        fixtures_input_dir,
        fixtures_expected_dir,
        temp_output_dir,
        svg_filename,
        expected_png_filename,
    ):
        """Test that PNG conversion results match expected outputs."""
        svg_file = fixtures_input_dir / svg_filename
        expected_png = fixtures_expected_dir / expected_png_filename
        actual_png = temp_output_dir / f"actual_{expected_png_filename}"

        # Skip if files don't exist
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        if not expected_png.exists():
            pytest.skip(f"Expected PNG not found: {expected_png}")

        # Convert SVG to PNG
        result = converter.convert_svg_file(str(svg_file), str(actual_png))
        assert result is True, f"Conversion failed for {svg_filename}"
        assert actual_png.exists(), f"Output PNG not created: {actual_png}"

        # Check file sizes are similar (within 10% tolerance)
        assert self._files_are_similar(expected_png, actual_png, tolerance=0.1), (
            f"PNG file size differs significantly from expected. "
            f"Expected: {expected_png.stat().st_size:,} bytes, "
            f"Actual: {actual_png.stat().st_size:,} bytes"
        )

    def test_conversion_consistency(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test that repeated conversions produce consistent results."""
        svg_file = fixtures_input_dir / "architecture_mermaid_0_07a67020.svg"
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        # Convert the same SVG twice
        png1 = temp_output_dir / "consistency_test_1.png"
        png2 = temp_output_dir / "consistency_test_2.png"

        result1 = converter.convert_svg_file(str(svg_file), str(png1))
        result2 = converter.convert_svg_file(str(svg_file), str(png2))

        assert result1 is True
        assert result2 is True
        assert png1.exists()
        assert png2.exists()

        # Files should be very similar in size
        assert self._files_are_similar(png1, png2, tolerance=0.01), (
            f"Repeated conversions produced inconsistent results. "
            f"File 1: {png1.stat().st_size:,} bytes, "
            f"File 2: {png2.stat().st_size:,} bytes"
        )

    def test_basic_svg_files_conversion(
        self, converter, fixtures_input_dir, fixtures_expected_dir, temp_output_dir
    ):
        """Test conversion of basic SVG files (originally in fixtures)."""
        test_cases = [
            ("output_basic.svg", "output_basic.png"),
            ("output_sequence.svg", "output_sequence.png"),
        ]

        for svg_filename, expected_png_filename in test_cases:
            svg_file = fixtures_input_dir / svg_filename
            expected_png = fixtures_expected_dir / expected_png_filename
            actual_png = temp_output_dir / f"basic_{expected_png_filename}"

            if not (svg_file.exists() and expected_png.exists()):
                continue

            result = converter.convert_svg_file(str(svg_file), str(actual_png))
            assert result is True, f"Conversion failed for {svg_filename}"
            assert actual_png.exists(), f"Output PNG not created for {svg_filename}"

            # Basic validation - file should have reasonable size
            assert actual_png.stat().st_size > 1000, (
                f"Generated PNG too small for {svg_filename}: "
                f"{actual_png.stat().st_size} bytes"
            )

    def test_different_scale_output_sizes(
        self, converter_config, fixtures_input_dir, temp_output_dir
    ):
        """Test that different scales produce appropriately sized outputs."""
        svg_file = fixtures_input_dir / "detailed-diagram.drawio.svg"
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        scales = [0.5, 1.0, 2.0]
        png_files = []

        for scale in scales:
            converter_config["scale"] = scale
            converter = SvgToPngConverter(converter_config)

            png_file = temp_output_dir / f"scale_{scale}_test.png"
            result = converter.convert_svg_file(str(svg_file), str(png_file))

            assert result is True, f"Conversion failed at scale {scale}"
            assert png_file.exists(), f"PNG not created at scale {scale}"

            png_files.append((scale, png_file))

        # Verify that different scales produce different file sizes
        # (though this may not always be strictly proportional due to compression)
        sizes = [(scale, png.stat().st_size) for scale, png in png_files]

        # At minimum, scale 2.0 should generally be larger than scale 0.5
        scale_05_size = next(size for scale, size in sizes if scale == 0.5)
        scale_20_size = next(size for scale, size in sizes if scale == 2.0)

        assert scale_20_size > scale_05_size * 0.8, (
            f"Scale 2.0 ({scale_20_size:,} bytes) should be larger than "
            f"scale 0.5 ({scale_05_size:,} bytes)"
        )

    def test_expected_png_file_integrity(self, fixtures_expected_dir):
        """Test that all expected PNG files are valid and non-empty."""
        png_files = list(fixtures_expected_dir.glob("*.png"))
        assert (
            len(png_files) >= 11
        ), f"Expected at least 11 PNG files, found {len(png_files)}"

        for png_file in png_files:
            # Check file is not empty
            assert png_file.stat().st_size > 1000, (
                f"Expected PNG file too small: {png_file} "
                f"({png_file.stat().st_size} bytes)"
            )

            # Check file starts with PNG signature
            with png_file.open("rb") as f:
                signature = f.read(8)

            expected_signature = b"\x89PNG\r\n\x1a\n"
            assert (
                signature == expected_signature
            ), f"Invalid PNG signature in {png_file}: {signature.hex()}"

    def test_svg_to_png_file_associations(
        self, fixtures_input_dir, fixtures_expected_dir
    ):
        """Test that every generated PNG has a corresponding SVG input."""
        expected_pngs = list(fixtures_expected_dir.glob("*.png"))

        # Remove the original basic PNGs from the count
        basic_pngs = ["output_basic.png", "output_sequence.png"]
        generated_pngs = [png for png in expected_pngs if png.name not in basic_pngs]

        for png_file in generated_pngs:
            # Find corresponding SVG file
            svg_name = png_file.name.replace(".png", ".svg")
            svg_file = fixtures_input_dir / svg_name

            assert (
                svg_file.exists()
            ), f"No corresponding SVG file found for {png_file}: expected {svg_file}"
