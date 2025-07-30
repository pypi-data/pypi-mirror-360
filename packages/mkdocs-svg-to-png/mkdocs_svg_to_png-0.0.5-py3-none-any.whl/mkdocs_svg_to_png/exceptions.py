from __future__ import annotations

from typing import Any


class SvgPreprocessorError(Exception):
    def __init__(self, message: str, **context_params: Any) -> None:
        """Initialize the exception with a message and optional context parameters.

        Args:
            message: Human-readable error message
            **context_params: Arbitrary context parameters for error details
        """
        details = {k: v for k, v in context_params.items() if v is not None}

        # Truncate long SVG content for readability
        for key in ["svg_content", "svg_code"]:
            if (
                key in details
                and isinstance(details[key], str)
                and len(details[key]) > 200
            ):
                details[key] = details[key][:200] + "..."

        super().__init__(message)
        self.details = details


class SvgConfigError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: str | int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize configuration error with context.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the error
            config_value: The invalid configuration value
            suggestion: Suggested fix for the configuration error
        """
        super().__init__(
            message,
            config_key=config_key,
            config_value=config_value,
            suggestion=suggestion,
        )


class SvgConversionError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        svg_path: str | None = None,
        output_path: str | None = None,
        svg_content: str | None = None,
        cairo_error: str | None = None,
    ) -> None:
        """Initialize SVG conversion error with context.

        Args:
            message: Human-readable error message
            svg_path: Path to the SVG file being converted
            output_path: Target output path for PNG
            svg_content: SVG content that failed to convert
            cairo_error: CairoSVG specific error message
        """
        super().__init__(
            message,
            svg_path=svg_path,
            output_path=output_path,
            svg_content=svg_content,
            cairo_error=cairo_error,
        )


class SvgFileError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        operation: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize file operation error with context.

        Args:
            message: Human-readable error message
            file_path: Path to the file that caused the error
            operation: The file operation that failed (read, write, create, etc.)
            suggestion: Suggested fix for the file error
        """
        super().__init__(
            message, file_path=file_path, operation=operation, suggestion=suggestion
        )


class SvgParsingError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        source_file: str | None = None,
        line_number: int | None = None,
        svg_content: str | None = None,
    ) -> None:
        """Initialize parsing error with source context.

        Args:
            message: Human-readable error message
            source_file: The file where the parsing error occurred
            line_number: Line number where the error was found
            svg_content: The problematic SVG content
        """
        super().__init__(
            message,
            source_file=source_file,
            line_number=line_number,
            svg_content=svg_content,
        )


class SvgValidationError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        validation_type: str | None = None,
        invalid_value: str | None = None,
        expected_format: str | None = None,
    ) -> None:
        """Initialize validation error with context.

        Args:
            message: Human-readable error message
            validation_type: Type of validation that failed
            invalid_value: The value that failed validation
            expected_format: Expected format or pattern
        """
        super().__init__(
            message,
            validation_type=validation_type,
            invalid_value=invalid_value,
            expected_format=expected_format,
        )


class SvgImageError(SvgPreprocessorError):
    def __init__(
        self,
        message: str,
        image_format: str | None = None,
        image_path: str | None = None,
        svg_content: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize image generation error with context.

        Args:
            message: Human-readable error message
            image_format: Target image format (png, svg, etc.)
            image_path: Path where image should be generated
            svg_content: SVG diagram content that failed to render
            suggestion: Suggested fix for the image generation error
        """
        super().__init__(
            message,
            image_format=image_format,
            image_path=image_path,
            svg_content=svg_content,
            suggestion=suggestion,
        )
