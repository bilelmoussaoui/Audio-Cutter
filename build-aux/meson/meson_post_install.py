#!/usr/bin/env python3

from os import environ, path
from subprocess import call

destdir = environ.get('DESTDIR', '')

if not destdir:
    prefix = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
    icons_dir = path.join(prefix, 'share/icons/hicolor')
    schema_dir = path.join(prefix, 'share/glib-2.0/schemas')
    desktop_dir = path.join(prefix, 'share/applications')

    print('Updating icon cache...')
    call(['gtk-update-icon-cache', '-qtf', icons_dir])
    print("Installing new Schemas")
    call(['glib-compile-schemas', schema_dir])
    print("Updating desktop database")
    call(["update-desktop-database", desktop_dir])
