project('tte.nemas.Epola', 'c',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

python = import('python')
py_installation = python.find_installation('python3')

conf = configuration_data()
conf.set('APP_ID', 'tte.nemas.Epola')
conf.set('VERSION', meson.project_version())
conf.set('PYTHON', py_installation.path())
conf.set('pkgdatadir', join_paths(get_option('prefix'), get_option('datadir'), meson.project_name()))

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
