# NemasOS
Un repositorio de github en el que se guarda las ISO más recientes (y antiguas) de NemásOS, aquí, no esperes una distro de LINUX super detallada, esta distro fue, es y será creada como un proyecto que se nos ocurrió en el recreo de el colegio, no esperes una interfaz que te enamores

**SOBRE NEMÁS OS**
La distro nunca tendrá versión de pago, ya que queremos que **TÚ** no pierdas dinero por un sistema que puede que al final ni uses, como nuestro lema dice (**UBUNTU WITHOUT UBUNTU**) prometemos una experiencia fácil y lista de usar, pero sin las basuras de ubuntu (spyware, cosas de pago, actualizaciones lentas...)

**TU PRIVACIDAD, LO PRIMERO**
Aquí, en Nemás, no nos interesa cuantas horas ves videos de gatitos adorables, aquí, lo que nos importa es tu privacidad, por eso 

**TPT**
TPT (Total Package Tool) es una herramienta escrita en python hecha para que CUALQUIER PAQUETE (si, desde un .deb hasta un .exe) funcione fácilmente sin necesidad de hacer nada, TODAVÍA EN BETA


**VERSIONES DE BRANCH Y FUNCIONAMIENTO DE TPT**
tpt crea un archivo actual-branch.txt que contiene el texto "regular", eso hace que los repos de sources guardados en tpt-sources.list (tpt lo genera solo en el primer arranque con algunos repos) apliquen esta estructura, por ejemplo, al tener el repo oficial (github.com/tovicito/NemásOS/) pues se junta con la rama (la que tenga en tpt-sources.list) y el nombre del paquete y extensión (la ext. mira todas hasta encontrar una valida en una url valida), p.ej. si tenemos el repo oficial + tpt + branch regular + descargar el paquete "ejemplo" + que la extensión es .py: ejecutaremos "sudo tpt --install ejemplo", luego, tpt generará urls como "https://raw.githubusercontent.com/tovicito/NemasOS/regular/ejemplo.sh" y irá por todas las url y extensiones hasta encontrar uno que responda y entonces, lo descargará

Esperamos que tengas una experiencia satisfactoria con Nemás OS, atentamente, Equipo de desarrollo de NemásOS (EDNO)
