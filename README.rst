=============
gedit-wraptor
=============

This is a plugin for gedit which allows wrapping lines in some languages even if text wrapping is disabled. This may be useful for languages such as Markdown or ReStructuredText where text wrapping may be useful, while it is mostly annoying for programming languages.

Installing
----------

Automatically:

Run::

    ./install.sh

Manually:

* Copy ``wraptor.plugin`` and ``wraptor.py`` to ``$XDG_DATA_HOME/gedit/plugins``. This defaults to ``~/.local/share/gedit/plugins``.
* The plugin can now be enabled in gedit by navigating to ``edit`` → ``Preferences`` → ``Plugins`` and checking ``Wraptor``
