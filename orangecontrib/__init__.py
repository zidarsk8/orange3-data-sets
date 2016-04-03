"""Default package name for orange plugins.

orangecontrib is a namespace modules shared by multiple Orange add-on so it
needs to declare namespace.
"""

__import__("pkg_resources").declare_namespace(__name__)
