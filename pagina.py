"""Módulo que define la entidad Pagina para el control de acceso web."""


class Pagina:
    """Representa una página web y su estado de admisión dentro de la red."""

    def __init__(self, url: str, admitida: bool = False) -> None:
        """Inicializa una página validando que su URL no esté vacía."""
        if not isinstance(url, str) or not url.strip():
            raise ValueError("La URL de la página es obligatoria.")
        self._url: str = url.strip()
        self._admitida: bool = bool(admitida)

    @property
    def url(self) -> str:
        """Devuelve la dirección URL de la página."""
        return self._url

    @property
    def admitida(self) -> bool:
        """Indica si la página está admitida en la red."""
        return self._admitida

    @admitida.setter
    def admitida(self, valor: bool) -> None:
        """Actualiza el estado de admisión de la página."""
        self._admitida = bool(valor)

    def to_dict(self) -> dict:
        """Serializa la página a un diccionario compatible con JSON."""
        return {
            "url": self._url,
            "admitida": self._admitida,
        }

    def __str__(self) -> str:
        """Devuelve una representación legible de la página."""
        estado = "Admitida" if self._admitida else "Restringida"
        return f"{self._url} [{estado}]"