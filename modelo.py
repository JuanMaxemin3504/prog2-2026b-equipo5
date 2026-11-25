"""Entidades del dominio: Pagina, Dispositivo, RegistroAcceso, Usuario y Administrador."""

from datetime import datetime


class Pagina:
    """Representa una página web y su estado de admisión."""

    def __init__(self, url: str, admitida: bool = False) -> None:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("La URL de la página es obligatoria.")
        self._url = url.strip()
        self._admitida = bool(admitida)

    @property
    def url(self) -> str:
        return self._url

    @property
    def admitida(self) -> bool:
        return self._admitida

    @admitida.setter
    def admitida(self, valor: bool) -> None:
        self._admitida = bool(valor)

    def to_dict(self) -> dict:
        return {"url": self._url, "admitida": self._admitida}

    def __str__(self) -> str:
        return f"[Pagina] {self._url} [{'Admitida' if self._admitida else 'Restringida'}]"


class Dispositivo:
    """Representa un equipo de red identificado por una dirección IPv4."""

    def __init__(self, ip: str, usuario=None) -> None:
        if not self.validar_ip(ip):
            raise ValueError(f"La IP '{ip}' no tiene un formato IPv4 válido.")
        self._ip = ip.strip()
        self._usuario = usuario

    @staticmethod
    def validar_ip(ip: str) -> bool:
        if not isinstance(ip, str):
            return False
        partes = ip.strip().split(".")
        if len(partes) != 4:
            return False
        return all(
            p.isdigit() and (len(p) == 1 or not p.startswith("0")) and 0 <= int(p) <= 255
            for p in partes
        )

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, valor) -> None:
        self._usuario = valor

    def to_dict(self) -> dict:
        return {"ip": self._ip, "usuario_id": self._usuario.id if self._usuario else None}

    def __str__(self) -> str:
        dueno = f"{self._usuario.nombre} ({self._usuario.id})" if self._usuario else "Sin asignar"
        return f"[Dispositivo] IP: {self._ip} | Propietario: {dueno}"


class RegistroAcceso:
    """Registra un intento de navegación en la bitácora del sistema."""

    def __init__(self, usuario, pagina: Pagina, permitido: bool, fecha_hora: str | None = None) -> None:
        self._usuario = usuario
        self._pagina = pagina
        self._permitido = bool(permitido)
        self._fecha_hora = fecha_hora or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def fecha_hora(self) -> str:
        return self._fecha_hora

    @property
    def permitido(self) -> bool:
        return self._permitido

    def to_dict(self) -> dict:
        return {
            "usuario_id": self._usuario.id,
            "usuario_nombre": self._usuario.nombre,
            "pagina_url": self._pagina.url,
            "permitido": self._permitido,
            "fecha_hora": self._fecha_hora,
        }

    def __str__(self) -> str:
        estado = "PERMITIDO" if self._permitido else "DENEGADO"
        return f"[{self._fecha_hora}] {self._usuario.nombre} ({self._usuario.id}) -> {self._pagina.url} | {estado}"


class Usuario:
    """Representa un usuario estándar con límite de 2 dispositivos conectados."""

    MAX_DISPOSITIVOS = 2

    def __init__(self, id_usuario: str, nombre: str) -> None:
        if not isinstance(id_usuario, str) or not id_usuario.strip():
            raise ValueError("El ID del usuario es obligatorio.")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del usuario es obligatorio.")
        self._id = id_usuario.strip()
        self._nombre = nombre.strip()
        self._dispositivos: list[Dispositivo] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def dispositivos(self) -> list[Dispositivo]:
        return list(self._dispositivos)

    @property
    def rol(self) -> str:
        return "Usuario"

    def vincular_dispositivo(self, dispositivo: Dispositivo) -> None:
        if dispositivo in self._dispositivos:
            raise ValueError(f"El dispositivo '{dispositivo.ip}' ya está asignado a este usuario.")
        if len(self._dispositivos) >= self.MAX_DISPOSITIVOS:
            raise ValueError(f"El usuario '{self._nombre}' ya alcanzó el límite de {self.MAX_DISPOSITIVOS} dispositivos.")
        if dispositivo.usuario is not None and dispositivo.usuario is not self:
            raise ValueError(f"El dispositivo '{dispositivo.ip}' ya pertenece a otro usuario.")
        dispositivo.usuario = self
        self._dispositivos.append(dispositivo)

    def desvincular_dispositivo(self, dispositivo: Dispositivo) -> None:
        if dispositivo in self._dispositivos:
            self._dispositivos.remove(dispositivo)

    def conectarse(self, dispositivo: Dispositivo, red) -> bool:
        if not red.esta_encendida:
            raise ValueError("La red está apagada. No se puede conectar el dispositivo.")
        if red.buscar_usuario(self._id) is None:
            raise ValueError(f"El usuario '{self._id}' no está registrado en la red.")
        if red.buscar_dispositivo(dispositivo.ip) is None:
            red.registrar(dispositivo)
        red.asignar(dispositivo.ip, self._id)
        return True

    def visitar_pagina(self, pagina: Pagina, red) -> bool:
        if not red.esta_encendida:
            raise ValueError("La red está apagada. No se puede navegar.")
        if not self._dispositivos:
            raise ValueError("Debes conectar al menos un dispositivo para navegar.")
        red.registrar_acceso(RegistroAcceso(self, pagina, pagina.admitida))
        if not pagina.admitida:
            raise PermissionError(f"Acceso denegado: '{pagina.url}' no está permitida.")
        return True

    def _formatear_datos(self, target: "Usuario") -> str:
        ips = ", ".join(d.ip for d in target.dispositivos) if target.dispositivos else "Ninguno"
        return f"ID: {target.id} | Nombre: {target.nombre} | Dispositivos ({len(target.dispositivos)}/2): {ips}"

    def consultar_datos(self, objetivo: "Usuario | None" = None) -> str:
        target = self if objetivo is None else objetivo
        if target.id != self._id:
            raise PermissionError("No tienes permisos para consultar datos de otros usuarios.")
        return self._formatear_datos(target)

    def encender_red(self, red) -> None:
        raise PermissionError("Solo el administrador puede encender la red.")

    def apagar_red(self, red) -> None:
        raise PermissionError("Solo el administrador puede apagar la red.")

    def admitir_pagina(self, pagina: Pagina, red) -> None:
        raise PermissionError("Solo el administrador puede admitir páginas.")

    def restringir_pagina(self, pagina: Pagina, red) -> None:
        raise PermissionError("Solo el administrador puede restringir páginas.")

    def revisar_historial(self, red) -> list[str]:
        raise PermissionError("Solo el administrador puede revisar el historial.")

    def to_dict(self) -> dict:
        return {"id": self._id, "nombre": self._nombre, "rol": self.rol}

    def __str__(self) -> str:
        return f"[{self.rol}] ID: {self._id} | Nombre: {self._nombre}"


class Administrador(Usuario):
    """Representa un administrador con control total sobre la red."""

    def __init__(self, id_usuario: str, nombre: str) -> None:
        super().__init__(id_usuario, nombre)

    @property
    def rol(self) -> str:
        return "Administrador"

    def consultar_datos(self, objetivo: Usuario | None = None) -> str:
        target = self if objetivo is None else objetivo
        return f"{super()._formatear_datos(target)} | Rol: {self.rol}"

    def encender_red(self, red) -> None:
        red.encender()

    def apagar_red(self, red) -> None:
        red.apagar()

    def admitir_pagina(self, pagina: Pagina, red) -> None:
        if red.buscar_pagina(pagina.url) is None:
            red.registrar(pagina)
        red.asignar(pagina.url, True)

    def restringir_pagina(self, pagina: Pagina, red) -> None:
        if red.buscar_pagina(pagina.url) is None:
            red.registrar(pagina)
        red.asignar(pagina.url, False)

    def revisar_historial(self, red) -> list[str]:
        return [str(r) for r in red.registros]

    def __str__(self) -> str:
        return f"{super().__str__()} (Privilegios Totales)"