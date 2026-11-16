class Dispositivo:
    def __init__(self, ip: str, usuario=None):
        if not Dispositivo.validarIp(ip):
            raise ValueError(f"Error: La IP '{ip}' no tiene un formato válido.")
        self._ip = ip.strip()
        self._usuario = usuario

    @staticmethod
    def validarIp(ip: str) -> bool:
        if not isinstance(ip, str):
            return False
        partes = ip.strip().split(".")
        if len(partes) != 4:
            return False
        for parte in partes:
            if not parte.isdigit():
                return False
            # Evita ceros a la izquierda inválidos como "01" o "001"
            if len(parte) > 1 and parte.startswith("0"):
                return False
            numero = int(parte)
            if numero < 0 or numero > 255:
                return False
        return True

    def getIp(self) -> str:
        return self._ip

    def getUsuario(self):
        return self._usuario

    def setUsuario(self, usuario) -> None:
        self._usuario = usuario

    def __str__(self) -> str:
        propietario = (
            f"{self._usuario.getNombre()} (ID: {self._usuario.getId()})"
            if self._usuario
            else "Sin asignar"
        )
        return f"IP: {self._ip} | Propietario: {propietario}"

    def to_dict(self) -> dict:
            return {
                "ip": self._ip,
                "usuario_id": self._usuario.getId() if self._usuario else None,
            }
    