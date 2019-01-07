icon_themes = ['hicolor']
foreach theme : icon_themes
  scalable_dir = join_paths(theme, 'scalable/apps')
  scalable_icon = join_paths(scalable_dir, meson.project_name() + '.svg')
  dest = join_paths(get_option('prefix'), 'share/icons', scalable_dir)
  install_data(scalable_icon, install_dir: dest, rename: '@0@.svg'.format(application_id))

  symbolic_dir = join_paths(theme, 'symbolic/apps/')
  symbolic_icon = join_paths(symbolic_dir, meson.project_name() + '-symbolic.svg')
  dest_symbolic = join_paths(get_option('prefix'), 'share/icons', symbolic_dir)
  install_data(symbolic_icon,
              install_dir: dest_symbolic,
              rename: '@0@'.format(application_id) + '-symbolic.svg')
endforeach

