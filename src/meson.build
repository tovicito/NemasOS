pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'epola'

conf = configuration_data()
conf.set('PYTHON', py_installation.path())
conf.set('APP_ID', 'tte.nemas.Epola')
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'tte.nemas.Epola.in',
  output: 'tte.nemas.Epola',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

epola_sources = [
  'main.py',
  'window.py',
  'setup.py',
  'package_manager.py',
  'const.py',
  '__init__.py',
]

install_data(epola_sources, install_dir: moduledir)
