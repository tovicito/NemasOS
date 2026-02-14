# Epola

Epola es la tienda de aplicaciones moderna para NemasOS, diseñada con GTK4 y Libadwaita.

## Requisitos del Sistema

Para compilar y ejecutar Epola desde el código fuente, necesitarás:

- Python 3
- Meson
- Ninja
- Blueprint Compiler
- Libadwaita (desarrollo)
- GObject Introspection para Python (`python3-gi`)
- PackageKit, Flatpak y/o Snap (para la gestión de paquetes)

## Compilación e Instalación

### Usando GNOME Builder (Recomendado)

1. Abre GNOME Builder.
2. Selecciona "Abrir un proyecto" y elige la carpeta de Epola.
3. Builder detectará automáticamente el archivo `tte.nemas.Epola.json` y configurará el entorno Flatpak.
4. Haz clic en el botón de "Reproducir" (Ejecutar) para compilar y lanzar la aplicación.

### Manualmente (Meson)

```bash
# Configurar el directorio de construcción
meson setup builddir

# Compilar
meson compile -C builddir

# Instalar (requiere privilegios de root)
sudo meson install -C builddir
```

## Estructura del Proyecto

- `src/`: Lógica de la aplicación en Python.
- `data/`: Interfaces (Blueprint), esquemas de configuración y metadatos.
- `po/`: Archivos de traducción.
- `tte.nemas.Epola.json`: Manifiesto Flatpak.

## Características

- Interfaz moderna y adaptativa.
- Soporte para Flatpak, Snap y paquetes nativos (PackageKit).
- Asistente de configuración inicial (Setup Wizard).
- Grillas de aplicaciones con widgets elegantes.
- Animaciones fluidas.
```
