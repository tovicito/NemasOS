project('tte.nemas.Epola', 'c',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

python = import('python')
py_installation = python.find_installation('python3')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

conf = configuration_data()
conf.set('APP_ID', 'tte.nemas.Epola')
conf.set('VERSION', meson.project_version())
conf.set('PYTHON', py_installation.full_path())
conf.set('pkgdatadir', pkgdatadir)

subdir('data')
subdir('src')
subdir('po')

python3 = find_program('python3')
meson.add_install_script(
  python3,
  files('build-aux/post_install.py'),
  get_option('prefix'),
  get_option('datadir'),
)
