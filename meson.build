project('AudioCutter', 'c',
  version: '0.1',
  meson_version: '>= 0.40',
  license: 'GPL-3.0',
  default_options: ['prefix=/usr']
)
project_id = 'org.gnome.AudioCutter'

i18n   = import('i18n')
python = import('python3')

message('Looking for dependencies')
python_bin = python.find_python()
if not python_bin.found()
    error('No valid python3 binary found')
endif
dependency('glib-2.0')
dependency('gobject-2.0')
dependency('gobject-introspection-1.0')
dependency('gtk+-3.0', version :'>=3.16')

BIN_DIR    = join_paths(get_option('prefix'), get_option('bindir'))
PYTHON_DIR = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
DATA_DIR   = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
LOCALE_DIR = join_paths(get_option('prefix'), get_option('datadir'), 'locale')

conf = configuration_data()
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', PYTHON_DIR)
conf.set('VERSION', meson.project_version())
conf.set('PROJECT_NAME', meson.project_name())
conf.set('LIBDIR', join_paths(get_option('prefix'), get_option('libdir')))
subdir('data')
subdir('po')



python_dep = dependency('python3', version : '>= 3.3')
gst_dep = dependency('gstreamer-1.0', version : '>= 1.12')
cairo_dep = dependency('cairo')
pycairo_dep = dependency('py3cairo')

shared_library('renderer',
    'AudioCutter/objects/renderer.c',
    dependencies: [gst_dep, python_dep, pycairo_dep, cairo_dep],
    name_prefix : '',
    install: true,
    install_dir: get_option('libdir') + '/AudioCutter/python')


install_subdir(
  meson.project_name(),
  install_dir: PYTHON_DIR
)

configure_file(
  input: 'audio-cutter.py.in',
  output: 'audio-cutter',
  configuration: conf,
  install_dir: BIN_DIR
)

meson.add_install_script('build/meson_post_install.py')
