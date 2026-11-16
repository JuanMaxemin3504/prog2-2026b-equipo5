from datetime import datetime


class RegistroAcceso:
    def __init__(self, usuario, pagina, permitido: bool, fechaHora: str = None):
        self._usuario = usuario
        self._pagina = pagina
        self._permitido = bool(permitido)
        self._fechaHora = (
            fechaHora if fechaHora else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def registrarIntento(self) -> str:
        estado = "PERMITIDO" if self._permitido else "DENEGADO"
        return (
            f"[{self._fechaHora}] Usuario: {self._usuario.getNombre()} "
            f"(ID: {self._usuario.getId()}) -> {self._pagina.getUrl()} | {estado}"
        )

    def getFechaHora(self) -> str:
        return self._fechaHora

    def esPermitido(self) -> bool:
        return self._permitido

    def getUsuario(self):
        return self._usuario

    def getPagina(self):
        return self._pagina

    def to_dict(self) -> dict:
        return {
            "usuario_id": self._usuario.getId(),
            "usuario_nombre": self._usuario.getNombre(),
            "pagina_url": self._pagina.getUrl(),
            "permitido": self._permitido,
            "fechaHora": self._fechaHora,
        }

    def __str__(self) -> str:
        return self.registrarIntento()