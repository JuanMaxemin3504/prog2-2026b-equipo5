"""Gestión central de la red, contrato de operaciones y persistencia JSON."""

import json
import os
from modelo import Administrador, Dispositivo, Pagina, RegistroAcceso, Usuario


class Red:
    """Administra usuarios, dispositivos, páginas, bitácora y almacenamiento."""

    def __init__(self, archivo_bd: str | None = "datos_red.json", auto_guardar: bool = True) -> None:
        self._archivo_bd = archivo_bd
        self._auto_guardar = auto_guardar
        self._estado_encendida = False
        self._usuarios: list[Usuario] = []
        self._dispositivos: list[Dispositivo] = []
        self._paginas: list[Pagina] = []
        self._registros: list[RegistroAcceso] = []

    @property
    def esta_encendida(self) -> bool:
        return self._estado_encendida

    @property
    def usuarios(self) -> list[Usuario]:
        return list(self._usuarios)

    @property
    def dispositivos(self) -> list[Dispositivo]:
        return list(self._dispositivos)

    @property
    def paginas(self) -> list[Pagina]:
        return list(self._paginas)

    @property
    def registros(self) -> list[RegistroAcceso]:
        return list(self._registros)

    def registrar(self, objeto) -> None:
        """Da de alta un Usuario, Administrador, Dispositivo o Pagina en la red."""
        if isinstance(objeto, Usuario):
            if self.buscar_usuario(objeto.id) is not None:
                raise ValueError(f"El ID '{objeto.id}' ya está registrado.")
            self._usuarios.append(objeto)
        elif isinstance(objeto, Dispositivo):
            if self.buscar_dispositivo(objeto.ip) is not None:
                raise ValueError(f"La IP '{objeto.ip}' ya está registrada.")
            self._dispositivos.append(objeto)
        elif isinstance(objeto, Pagina):
            if self.buscar_pagina(objeto.url) is not None:
                raise ValueError(f"La página '{objeto.url}' ya está registrada.")
            self._paginas.append(objeto)
        else:
            raise TypeError("Objeto no soportado por la red.")
        self._persistir()

    def asignar(self, identificador: str, clave) -> None:
        """Asigna un dispositivo (IP) a un usuario (ID) o una página (URL) a un estado booleano."""
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValueError("El identificador no puede estar vacío.")
        id_limpio = identificador.strip()

        dispositivo = self.buscar_dispositivo(id_limpio)
        if dispositivo is not None:
            if not self._estado_encendida:
                raise ValueError("La red está apagada. No se pueden asignar dispositivos.")
            if not isinstance(clave, str) or not clave.strip():
                raise ValueError("Debe indicar el ID del usuario destino.")
            usuario = self.buscar_usuario(clave.strip())
            if usuario is None:
                raise ValueError(f"No existe el usuario con ID '{clave}'.")
            usuario.vincular_dispositivo(dispositivo)
            self._persistir()
            return

        pagina = self.buscar_pagina(id_limpio)
        if pagina is not None:
            if not isinstance(clave, bool):
                raise ValueError("La clave para una página debe ser booleana (True/False).")
            pagina.admitida = clave
            self._persistir()
            return

        raise ValueError(f"No existe ningún elemento registrado con identificador '{identificador}'.")

    def listar(self) -> list[str]:
        """Devuelve la descripción polimórfica de todos los elementos registrados."""
        elementos = [*self._usuarios, *self._dispositivos, *self._paginas]
        return [str(item) for item in elementos]

    def guardar(self, sistema=None, ruta: str | None = None) -> None:
        """Serializa el estado del sistema en el archivo JSON indicado."""
        obj = sistema if sistema is not None else self
        destino = ruta if ruta is not None else obj._archivo_bd
        if not destino:
            return
        datos = {
            "estado_encendida": obj._estado_encendida,
            "usuarios": [u.to_dict() for u in obj._usuarios],
            "dispositivos": [d.to_dict() for d in obj._dispositivos],
            "paginas": [p.to_dict() for p in obj._paginas],
            "registros": [r.to_dict() for r in obj._registros],
        }
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def cargar(self, sistema=None, ruta: str | None = None) -> "Red":
        """Reconstruye el estado del sistema desde un archivo JSON."""
        obj = sistema if sistema is not None else self
        origen = ruta if ruta is not None else obj._archivo_bd
        if not origen or not os.path.exists(origen):
            raise FileNotFoundError(f"No existe el archivo '{origen}'.")

        with open(origen, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        prev_auto = obj._auto_guardar
        obj._auto_guardar = False
        obj._usuarios.clear()
        obj._dispositivos.clear()
        obj._paginas.clear()
        obj._registros.clear()
        obj._estado_encendida = bool(datos.get("estado_encendida", False))

        mapa_u = {}
        for u in datos.get("usuarios", []):
            inst = (
                Administrador(u["id"], u["nombre"])
                if u.get("rol") == "Administrador"
                else Usuario(u["id"], u["nombre"])
            )
            obj._usuarios.append(inst)
            mapa_u[inst.id] = inst

        for d in datos.get("dispositivos", []):
            disp = Dispositivo(d["ip"])
            if d.get("usuario_id") in mapa_u:
                mapa_u[d["usuario_id"]].vincular_dispositivo(disp)
            obj._dispositivos.append(disp)

        mapa_p = {}
        for p in datos.get("paginas", []):
            pag = Pagina(p["url"], p.get("admitida", False))
            obj._paginas.append(pag)
            mapa_p[pag.url.lower()] = pag

        for r in datos.get("registros", []):
            usr = mapa_u.get(r["usuario_id"]) or Usuario(
                r["usuario_id"], r.get("usuario_nombre", "Eliminado")
            )
            pag = mapa_p.get(r["pagina_url"].lower(), Pagina(r["pagina_url"], r["permitido"]))
            obj._registros.append(RegistroAcceso(usr, pag, r["permitido"], r.get("fecha_hora")))

        obj._auto_guardar = prev_auto
        return obj

    def _persistir(self) -> None:
        if self._auto_guardar and self._archivo_bd:
            self.guardar(self, self._archivo_bd)

    def encender(self) -> None:
        self._estado_encendida = True
        self._persistir()

    def apagar(self) -> None:
        self._estado_encendida = False
        self._persistir()

    def registrar_acceso(self, registro: RegistroAcceso) -> None:
        self._registros.append(registro)
        self._persistir()

    def buscar_usuario(self, id_usuario: str) -> Usuario | None:
        return next((u for u in self._usuarios if u.id == id_usuario.strip()), None)

    def buscar_dispositivo(self, ip: str) -> Dispositivo | None:
        return next((d for d in self._dispositivos if d.ip == ip.strip()), None)

    def buscar_pagina(self, url: str) -> Pagina | None:
        return next((p for p in self._paginas if p.url.lower() == url.strip().lower()), None)