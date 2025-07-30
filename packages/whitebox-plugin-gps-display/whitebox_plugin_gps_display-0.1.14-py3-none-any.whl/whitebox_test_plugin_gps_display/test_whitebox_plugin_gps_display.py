from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginGpsDisplay(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.plugins
                if x.__class__.__name__ == "WhiteboxPluginGpsDisplay"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "GPS Display")

    def test_provides_capabilities(self):
        self.assertEqual(self.plugin.provides_capabilities, ["map"])
