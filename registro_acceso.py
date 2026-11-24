"""Módulo que define la bitácora de intentos de acceso a páginas web."""

from datetime import datetime
from pagina import Pagina


class RegistroAcceso:
    """Representa un evento de intento de acceso web realizado por un usuario."""

    def __init__(
        self,
        usuario,
        pagina: Pagina,
        permitido: bool,
        fecha_hora: str | None = None,
    ) -> None:
        """Crea un registro de acceso con marca de tiempo."""
        self._usuario = usuario
        self._pagina: Pagina = pagina
        self._permitido: bool = bool(permitido)
        self._fecha_hora: str = (
            fecha_hora if fecha_hora else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    @property
    def fecha_hora(self) -> str:
        """Devuelve la fecha y hora del intento de acceso."""
        return self._fecha_hora

    @property
    def permitido(self) -> bool:
        """Indica si el intento de acceso fue permitido."""
        return self._permitido

    @property
    def usuario(self):
        """Devuelve el usuario asociado al registro."""
        return self._usuario

    @property
    def pagina(self) -> Pagina:
        """Devuelve la página asociada al registro."""
        return self._pagina

    def registrar_intento(self) -> str:
        """Formatea el detalle del intento de acceso para su consulta."""
        estado = "PERMITIDO" if self._permitido else "DENEGADO"
        return (
            f"[{self._fecha_hora}] Usuario: {self._usuario.nombre} "
            f"(ID: {self._usuario.id}) -> {self._pagina.url} | {estado}"
        )

    def to_dict(self) -> dict:
        """Serializa el registro a un diccionario compatible con JSON."""
        return {
            "usuario_id": self._usuario.id,
            "usuario_nombre": self._usuario.nombre,
            "pagina_url": self._pagina.url,
            "permitido": self._permitido,
            "fecha_hora": self._fecha_hora,
        }

    def __str__(self) -> str:
        """Devuelve la representación textual del registro."""
        return self.registrar_intento()