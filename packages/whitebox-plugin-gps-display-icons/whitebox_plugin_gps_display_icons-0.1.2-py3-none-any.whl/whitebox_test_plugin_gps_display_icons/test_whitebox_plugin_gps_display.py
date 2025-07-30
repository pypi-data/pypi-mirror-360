from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginGpsDisplay(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.plugins
                if x.__class__.__name__ == "WhiteboxPluginGpsDisplayIcons"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "GPS Display Icons")

    def test_plugin_template(self):
        self.assertIsNone(self.plugin.plugin_template)

    def test_plugin_css(self):
        self.assertEqual(self.plugin.plugin_css, [])

    def test_plugin_js(self):
        expected_js = [
            "/static/whitebox_plugin_gps_display_icons/whitebox_plugin_gps_display_icons.mjs"
        ]
        self.assertEqual(self.plugin.plugin_js, expected_js)

    def test_plugin_augments(self):
        self.assertEqual(self.plugin.augments_plugin, "GPS Display")
