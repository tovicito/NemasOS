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
