from whitebox import Plugin


class WhiteboxPluginGpsDisplayIcons(Plugin):
    """
    A plugin that displays a map using leaflet.js and updates the map with the GPS data received from the GPS plugin.

    Attributes:
        name: The name of the plugin.
        plugin_js: List of paths to the plugin's JS files.
        augments_plugin: The name of the plugin that this plugin augments.
    """

    name = "GPS Display Icons"

    plugin_js = [
        "/static/whitebox_plugin_gps_display_icons/whitebox_plugin_gps_display_icons.mjs",
    ]

    augments_plugin = "GPS Display"


plugin_class = WhiteboxPluginGpsDisplayIcons
