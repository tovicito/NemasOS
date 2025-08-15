class TPTError(Exception):
    """Excepción base para todos los errores controlados de TPT."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CriticalTPTError(TPTError):
    """Para errores que deben detener la ejecución inmediatamente."""
    pass

class SystemCommandError(TPTError):
    """Lanzada cuando un comando del sistema falla."""
    def __init__(self, command, stderr):
        self.command = " ".join(command)
        self.stderr = stderr
        message = f"El comando del sistema '{self.command}' falló:\n{self.stderr}"
        super().__init__(message)

class PackageNotFoundError(TPTError):
    """Lanzada cuando no se encuentra un paquete."""
    pass

class UnsupportedFormatError(TPTError):
    """Lanzada cuando un formato de paquete no es compatible."""
    pass

class VerificationError(TPTError):
    """Lanzada cuando falla una verificación, como un checksum."""
    pass

class DownloadError(TPTError):
    """Lanzada cuando falla una descarga."""
    pass

class MultipleSourcesFoundError(TPTError):
    """Lanzada cuando se encuentra el mismo paquete en múltiples fuentes (apt, tpt, flatpak)."""
    def __init__(self, package_name, choices):
        self.package_name = package_name
        self.choices = choices
        message = f"Se encontró '{package_name}' en múltiples fuentes. Por favor, elija una."
        super().__init__(message)

class ConfirmGitCloneError(TPTError):
    """Excepción especial para pedir confirmación al usuario antes de clonar un repo."""
    def __init__(self, package_name, repo_url):
        self.package_name = package_name
        self.repo_url = repo_url
        message = f"No se encontró '{package_name}'. ¿Probar a clonar el repositorio completo '{repo_url}'?"
        super().__init__(message)
