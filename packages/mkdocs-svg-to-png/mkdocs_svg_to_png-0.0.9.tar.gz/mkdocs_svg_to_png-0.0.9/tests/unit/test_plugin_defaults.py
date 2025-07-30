"""Test plugin default configuration behavior."""

from mkdocs_svg_to_png.plugin import SvgToPngPlugin


class TestPluginDefaults:
    """Test plugin default configuration values."""

    def test_デフォルト設定でプラグインを初期化できる(self):
        """プラグインが最小構成で初期化できることを確認。"""
        plugin = SvgToPngPlugin()

        # MkDocsプラグインのconfig_schemeが存在することを確認
        assert hasattr(plugin, "config_scheme")
        assert plugin.config_scheme is not None

        # 設定スキーマがタプル形式であることを確認
        assert isinstance(plugin.config_scheme, tuple)
        assert len(plugin.config_scheme) > 0

    def test_enabled_のデフォルト値がTrueである(self):
        """enabled オプションのデフォルト値が True であることを確認。"""
        plugin = SvgToPngPlugin()

        # config_schemeから enabled の設定を検索
        enabled_config = None
        for config_item in plugin.config_scheme:
            if config_item[0] == "enabled":
                enabled_config = config_item[1]
                break

        assert enabled_config is not None
        assert enabled_config.default is True

    def test_すべてのオプションがデフォルト値を持つ(self):
        """全てのオプションが適切なデフォルト値を持つことを確認。"""
        plugin = SvgToPngPlugin()

        # 必須でないオプション（デフォルト値が必要）のリスト
        expected_defaults = {
            "enabled": True,
            "output_dir": "assets/images",
            "dpi": 300,
            "output_format": "png",
            "quality": 95,
            "background_color": "transparent",
            "cache_enabled": True,
            "cache_dir": ".svg_cache",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "cleanup_generated_images": False,
        }

        # config_schemeの各設定項目を検証
        for config_item in plugin.config_scheme:
            config_name = config_item[0]
            config_option = config_item[1]

            if config_name in expected_defaults:
                expected_default = expected_defaults[config_name]
                assert hasattr(
                    config_option, "default"
                ), f"{config_name} should have a default value"
                assert config_option.default == expected_default, (
                    f"{config_name} default should be "
                    f"{expected_default}, got {config_option.default}"
                )

    def test_オプショナル設定がNoneをデフォルトとする(self):
        """オプショナルな設定項目が適切にNoneをデフォルトとすることを確認。"""
        plugin = SvgToPngPlugin()

        # オプショナルな設定項目（Noneまたは空文字がデフォルト）
        optional_configs = [
            "enabled_if_env",
            "temp_dir",
        ]

        for config_item in plugin.config_scheme:
            config_name = config_item[0]

            if config_name in optional_configs:
                config_option = config_item[1]
                # Optional設定またはデフォルトがNone/空文字であることを確認
                if hasattr(config_option, "default"):
                    assert config_option.default in [
                        None,
                        "",
                    ], f"{config_name} should default to None or empty string"
