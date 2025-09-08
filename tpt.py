#!/usr/bin/env python3
import sys
import os
import subprocess
import time

paquetes_compatibles = [".py", ".sh", ".deb"]

def iniciando():
    print("Bienvenido a tpt")
    paqueteextension = input("Diga la extensión de su paquete por favor (ej: .deb, .sh, .py): ").strip()
    return paqueteextension

def comprobacion(paqueteextension):
    if paqueteextension not in paquetes_compatibles:
        print("❌ Ese paquete no es compatible actualmente, cerrando herramienta.")
        sys.exit()
    else:
        print("✅ Ese paquete está disponible en nuestra herramienta.")
        return preguntar_paquete()

def preguntar_paquete():
    direccion_paquete = input("Díganos la ruta exacta del paquete (por ejemplo, /home/usuario/paquete.deb): ").strip()
    if not os.path.exists(direccion_paquete):
        print("❌ Esa ruta no existe, cerrando herramienta.")
        sys.exit()
    return direccion_paquete

def preguntar_nombre(extension):
    nombre_paquete = input("Elija un nombre para el paquete SIN ESPACIOS (será el nombre del ejecutable): ").strip()
    ruta_objetivo = "/usr/local/bin"
    ruta_destino = os.path.join(ruta_objetivo, nombre_paquete + extension)

    # Verificar si ya existe un archivo con ese nombre
    if os.path.exists(ruta_destino):
        print(f"⚠️ Ya existe un ejecutable llamado {nombre_paquete + extension} en {ruta_objetivo}.")
        opcion = input("¿Desea sobrescribirlo? (s/n): ").strip().lower()
        if opcion != "s":
            print("Cancelando instalación.")
            sys.exit()

    return nombre_paquete, ruta_objetivo, ruta_destino

def instalar_paquete(extension, ruta, nombre, ruta_objetivo, ruta_destino):
    if extension == ".deb":
        try:
            subprocess.run(["sudo", "dpkg", "-i", ruta], check=True)
            subprocess.run(["sudo", "apt", "install", "-f"], check=True)
            print("✅ Paquete .deb instalado correctamente.")
        except subprocess.CalledProcessError:
            print("❌ Error al instalar el paquete .deb.")
    elif extension in [".sh", ".py"]:
        print(f"📦 El paquete se moverá a: {ruta_destino}")
        time.sleep(2)
        subprocess.run(["chmod", "+x", ruta])
        try:
            subprocess.run(["sudo", "mv", ruta, ruta_destino], check=True)
            print(f"✅ Paquete {extension} instalado como ejecutable: {nombre}")
        except subprocess.CalledProcessError:
            print("❌ Error al mover el archivo al destino.")
    else:
        print("❌ Tipo de paquete no manejado.")

if __name__ == "__main__":
    extension = iniciando()
    ruta_paquete = comprobacion(extension)

    if extension in [".py", ".sh"]:
        nombre, ruta_objetivo, ruta_destino = preguntar_nombre(extension)
        instalar_paquete(extension, ruta_paquete, nombre, ruta_objetivo, ruta_destino)
    else:
        instalar_paquete(extension, ruta_paquete, None, None, None)
