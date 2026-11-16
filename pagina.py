class Pagina:
    def __init__(self, url: str, admitida: bool = False):
        if not url or not url.strip():
            raise ValueError("Error: La URL de la página es obligatoria.")
        self._url = url.strip()
        self._admitida = bool(admitida)

    def getUrl(self) -> str:
        return self._url

    def esAdmitida(self) -> bool:
        return self._admitida

    def setAdmitida(self, admitida: bool) -> None:
        self._admitida = bool(admitida)

    def __str__(self) -> str:
        estado = "Admitida" if self._admitida else "Restringida"
        return f"{self._url} [{estado}]"

    def to_dict(self) -> dict:
        return {
            "url": self._url,
            "admitida": self._admitida,
        }