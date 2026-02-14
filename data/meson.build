desktop_file = i18n.merge_file(
        input: 'tte.nemas.Epola.desktop.in',
       output: 'tte.nemas.Epola.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'tte.nemas.Epola.metainfo.xml.in',
       output: 'tte.nemas.Epola.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util, args: ['validate', appstream_file])
endif

install_data('tte.nemas.Epola.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas, args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

# Blueprint compilation
blueprint_compiler = find_program('blueprint-compiler')

# We'll compile Blueprints into .ui files and then bundle them in a gresource
blueprints = [
  'window.blp',
  'setup.blp',
  'app_widget.blp'
]

compiled_ui = []
foreach blp : blueprints
  compiled_ui += custom_target(blp.underscorify() + '_ui',
    input: blp,
    output: blp.replace('.blp', '.ui'),
    command: [blueprint_compiler, 'compile', '--output', '@OUTPUT@', '@INPUT@']
  )
endforeach

resources = gnome.compile_resources('tte.nemas.Epola',
  'tte.nemas.Epola.gresource.xml',
  dependencies: compiled_ui,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)
