"""Módulo que define la entidad Dispositivo y la validación de direcciones IPv4."""


class Dispositivo:
    """Representa un equipo de red identificado mediante una dirección IPv4."""

    def __init__(self, ip: str, usuario=None) -> None:
        """Inicializa un dispositivo validando el formato de su dirección IP.

        Args:
            ip: Dirección IPv4 en formato 'X.X.X.X'.
            usuario: Propietario opcional del dispositivo.

        Raises:
            ValueError: Si la dirección IP no tiene un formato IPv4 válido.
        """
        if not Dispositivo.validar_ip(ip):
            raise ValueError(f"La IP '{ip}' no tiene un formato IPv4 válido.")
        self._ip: str = ip.strip()
        self._usuario = usuario

    @staticmethod
    def validar_ip(ip: str) -> bool:
        """Verifica que una cadena corresponda a una dirección IPv4 válida."""
        if not isinstance(ip, str):
            return False
        partes = ip.strip().split(".")
        if len(partes) != 4:
            return False
        for parte in partes:
            if not parte.isdigit():
                return False
            if len(parte) > 1 and parte.startswith("0"):
                return False
            numero = int(parte)
            if numero < 0 or numero > 255:
                return False
        return True

    @property
    def ip(self) -> str:
        """Devuelve la dirección IP del dispositivo."""
        return self._ip

    @property
    def usuario(self):
        """Devuelve el usuario propietario del dispositivo o None si no está asignado."""
        return self._usuario

    @usuario.setter
    def usuario(self, valor) -> None:
        """Asigna el usuario propietario del dispositivo."""
        self._usuario = valor

    def to_dict(self) -> dict:
        """Serializa el dispositivo a un diccionario compatible con JSON."""
        return {
            "ip": self._ip,
            "usuario_id": self._usuario.id if self._usuario else None,
        }

    def __str__(self) -> str:
        """Devuelve una representación legible del dispositivo y su propietario."""
        propietario = (
            f"{self._usuario.nombre} (ID: {self._usuario.id})"
            if self._usuario
            else "Sin asignar"
        )
        return f"IP: {self._ip} | Propietario: {propietario}"