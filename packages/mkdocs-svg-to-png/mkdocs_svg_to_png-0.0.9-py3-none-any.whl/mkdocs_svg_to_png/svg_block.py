import contextlib
from pathlib import Path
from typing import Any

from .utils import generate_image_filename


def _calculate_relative_path_prefix(page_file: str) -> str:
    """ページファイルパスから適切な相対パスプレフィックスを計算する

    Args:
        page_file: ページファイルのパス（例: "appendix/mkdocs-architecture.md"）

    Returns:
        相対パスプレフィックス（例: "../" or "../../../"）
    """
    if not page_file:
        return ""

    page_path = Path(page_file)
    # ディレクトリの深さを計算（ファイル名を除く）
    depth = len(page_path.parent.parts)

    # ルートレベル（深さ0）の場合は相対パス不要
    if depth == 0:
        return ""
    else:
        # 各階層に対して "../" を追加
        return "../" * depth


class SvgBlock:
    def __init__(
        self,
        code: str = "",
        file_path: str = "",
        start_pos: int = 0,
        end_pos: int = 0,
        attributes: dict[str, Any] | None = None,
    ):
        self.code = code.strip()
        self.file_path = file_path
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.attributes = attributes or {}

    def __repr__(self) -> str:
        if self.file_path:
            return (
                f"SvgBlock(file_path='{self.file_path}', "
                f"start={self.start_pos}, end={self.end_pos})"
            )
        else:
            return (
                f"SvgBlock(code='{self.code[:50]}...', "
                f"start={self.start_pos}, end={self.end_pos})"
            )

    def generate_png(
        self, output_path: str, svg_converter: Any, config: dict[str, Any]
    ) -> bool:
        """SVGからPNG画像を生成する"""
        if self.file_path:
            # SVGファイルから変換
            result = svg_converter.convert_svg_file(self.file_path, output_path)
        else:
            # インラインSVGコードから変換
            result = svg_converter.convert_svg_content(self.code, output_path)
        return bool(result)

    def get_image_markdown(
        self,
        image_path: str,
        page_file: str,
        preserve_original: bool = False,
        page_url: str = "",
    ) -> str:
        """画像のMarkdownを生成する"""
        image_path_obj = Path(image_path)

        # 相対パスプレフィックスを計算
        relative_prefix = _calculate_relative_path_prefix(page_file)

        # 相対パス付きで画像パスを構築
        relative_image_path = f"{relative_prefix}assets/images/{image_path_obj.name}"

        image_markdown = f"![SVG Diagram]({relative_image_path})"

        if preserve_original:
            if self.file_path:
                # ファイル参照の場合
                if self.attributes:
                    attr_str = ", ".join(
                        f"{k}: {v}" for k, v in self.attributes.items()
                    )
                    original_block = f"![SVG File]({self.file_path}) {{{attr_str}}}"
                else:
                    original_block = f"![SVG File]({self.file_path})"
            elif self.attributes:
                attr_str = ", ".join(f"{k}: {v}" for k, v in self.attributes.items())
                original_block = f"```svg {{{attr_str}}}\n{self.code}\n```"
            else:
                original_block = f"```svg\n{self.code}\n```"

            image_markdown = f"{image_markdown}\n\n{original_block}"

        return image_markdown

    def get_filename(self, page_file: str, index: int, image_format: str) -> str:
        """画像ファイル名を生成する"""
        content = self.file_path if self.file_path else self.code
        return generate_image_filename(page_file, index, content, image_format)


class MermaidBlock:
    def __init__(
        self,
        code: str,
        start_pos: int,
        end_pos: int,
        attributes: dict[str, Any] | None = None,
    ):
        self.code = code.strip()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.attributes = attributes or {}

    def __repr__(self) -> str:
        return (
            f"MermaidBlock(code='{self.code[:50]}...', "
            f"start={self.start_pos}, end={self.end_pos})"
        )

    def generate_image(
        self, output_path: str, image_generator: Any, config: dict[str, Any]
    ) -> bool:
        merged_config = config.copy()

        if "theme" in self.attributes:
            merged_config["theme"] = self.attributes["theme"]
        if "background" in self.attributes:
            merged_config["background_color"] = self.attributes["background"]
        if "width" in self.attributes:
            with contextlib.suppress(ValueError):
                merged_config["width"] = int(self.attributes["width"])
        if "height" in self.attributes:
            with contextlib.suppress(ValueError):
                merged_config["height"] = int(self.attributes["height"])

        result = image_generator.generate(self.code, output_path, merged_config)
        return bool(result)

    def get_image_markdown(
        self,
        image_path: str,
        page_file: str,
        preserve_original: bool = False,
        page_url: str = "",
    ) -> str:
        image_path_obj = Path(image_path)

        # 相対パスプレフィックスを計算
        relative_prefix = _calculate_relative_path_prefix(page_file)

        # 相対パス付きで画像パスを構築
        relative_image_path = f"{relative_prefix}assets/images/{image_path_obj.name}"

        image_markdown = f"![Mermaid Diagram]({relative_image_path})"

        if preserve_original:
            if self.attributes:
                attr_str = ", ".join(f"{k}: {v}" for k, v in self.attributes.items())
                original_block = f"```mermaid {{{attr_str}}}\n{self.code}\n```"
            else:
                original_block = f"```mermaid\n{self.code}\n```"

            image_markdown = f"{image_markdown}\n\n{original_block}"

        return image_markdown

    def get_filename(self, page_file: str, index: int, image_format: str) -> str:
        return generate_image_filename(page_file, index, self.code, image_format)
