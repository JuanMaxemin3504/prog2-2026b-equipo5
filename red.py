import json
import os
from dispositivo import Dispositivo
from pagina import Pagina
from registro_acceso import RegistroAcceso
from usuario import Administrador, Usuario


class Red:
    def __init__(self, archivo_bd: str = "datos_red.json", auto_guardar: bool = True):
        self._archivo_bd = archivo_bd
        self._auto_guardar = auto_guardar
        self._estadoEncendida = False
        self._usuarios = []
        self._dispositivos = []
        self._paginas = []
        self._registros = []

    def guardar(self) -> None:
        if not self._auto_guardar or not self._archivo_bd:
            return

        datos = {
            "estadoEncendida": self._estadoEncendida,
            "usuarios": [u.to_dict() for u in self._usuarios],
            "dispositivos": [d.to_dict() for d in self._dispositivos],
            "paginas": [p.to_dict() for p in self._paginas],
            "registros": [r.to_dict() for r in self._registros],
        }

        with open(self._archivo_bd, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    @classmethod
    def cargar(cls, archivo_bd: str = "datos_red.json"):
        if not os.path.exists(archivo_bd):
            return None

        try:
            with open(archivo_bd, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Aviso: No se pudo leer la BD ({e}). Se creará una nueva.")
            return None

        red = cls(archivo_bd=archivo_bd, auto_guardar=False)
        red._estadoEncendida = bool(datos.get("estadoEncendida", False))

        mapa_usuarios = {}
        for u_data in datos.get("usuarios", []):
            if u_data.get("rol") == "Administrador":
                usuario = Administrador(u_data["id"], u_data["nombre"])
            else:
                usuario = Usuario(u_data["id"], u_data["nombre"])
            red._usuarios.append(usuario)
            mapa_usuarios[usuario.getId()] = usuario

        for d_data in datos.get("dispositivos", []):
            dispositivo = Dispositivo(d_data["ip"])
            uid = d_data.get("usuario_id")
            if uid and uid in mapa_usuarios:
                propietario = mapa_usuarios[uid]
                dispositivo.setUsuario(propietario)
                propietario._dispositivos.append(dispositivo)
            red._dispositivos.append(dispositivo)

        mapa_paginas = {}
        for p_data in datos.get("paginas", []):
            pagina = Pagina(p_data["url"], p_data.get("admitida", False))
            red._paginas.append(pagina)
            mapa_paginas[pagina.getUrl().lower()] = pagina

        for r_data in datos.get("registros", []):
            uid = r_data.get("usuario_id")
            nombre_respaldo = r_data.get("usuario_nombre", "Usuario eliminado")
            url = r_data.get("pagina_url")
            permitido = bool(r_data.get("permitido", False))
            fecha_hora = r_data.get("fechaHora")

            usuario = mapa_usuarios.get(uid) or Usuario(uid, nombre_respaldo)
            pagina = mapa_paginas.get(url.lower(), Pagina(url, permitido))
            registro = RegistroAcceso(usuario, pagina, permitido, fechaHora=fecha_hora)
            red._registros.append(registro)

        red._auto_guardar = True
        return red

    def encender(self) -> None:
        if self._estadoEncendida:
            print("Aviso: La red ya se encuentra encendida.")
        else:
            self._estadoEncendida = True
            self.guardar()
            print("Red ENCENDIDA correctamente.")

    def apagar(self) -> None:
        if not self._estadoEncendida:
            print("Aviso: La red ya se encuentra apagada.")
        else:
            self._estadoEncendida = False
            self.guardar()
            print("Red APAGADA correctamente.")

    def estaEncendida(self) -> bool:
        return self._estadoEncendida

    def registrarUsuario(self, usuario: Usuario) -> bool:
        if not isinstance(usuario, Usuario):
            print("Error: Usuario inválido.")
            return False

        if not usuario.getNombre() or not usuario.getNombre().strip():
            print("Error: El nombre es obligatorio.")
            return False

        if self.buscarUsuarioPorId(usuario.getId()) is not None:
            print(f"Error: El ID '{usuario.getId()}' ya está en uso.")
            return False

        self._usuarios.append(usuario)
        self.guardar()
        print(f"Usuario '{usuario.getNombre()}' (ID: {usuario.getId()}) registrado.")
        return True

    def agregarDispositivo(self, dispositivo) -> bool:
        if not self._estadoEncendida:
            print("Error: La red está apagada.")
            return False

        for d in self._dispositivos:
            if d.getIp() == dispositivo.getIp():
                print(f"Error: La IP '{dispositivo.getIp()}' ya está en uso en la red.")
                return False

        self._dispositivos.append(dispositivo)
        self.guardar()
        return True

    def admitirPagina(self, pagina) -> None:
        pagina.setAdmitida(True)
        if pagina not in self._paginas:
            self._paginas.append(pagina)
        self.guardar()
        print(f"Página '{pagina.getUrl()}' ADMITIDA en la red.")

    def restringirPagina(self, pagina) -> None:
        pagina.setAdmitida(False)
        if pagina not in self._paginas:
            self._paginas.append(pagina)
        self.guardar()
        print(f"Página '{pagina.getUrl()}' RESTRINGIDA en la red.")

    def registrarAcceso(self, registro) -> None:
        self._registros.append(registro)
        self.guardar()

    def buscarUsuarioPorId(self, id_usuario: str):
        for u in self._usuarios:
            if u.getId() == id_usuario.strip():
                return u
        return None

    def buscarDispositivoPorIp(self, ip: str):
        for d in self._dispositivos:
            if d.getIp() == ip.strip():
                return d
        return None

    def buscarPaginaPorUrl(self, url: str):
        for p in self._paginas:
            if p.getUrl().lower() == url.strip().lower():
                return p
        return None

    def eliminarUsuario(self, id_usuario: str) -> bool:
        usuario = self.buscarUsuarioPorId(id_usuario)
        if usuario is None:
            print(f"Error: No se encontró ningún usuario con ID '{id_usuario}'.")
            return False

        for disp in list(usuario.getDispositivos()):
            if disp in self._dispositivos:
                self._dispositivos.remove(disp)
            usuario.removerDispositivoLocal(disp)

        self._usuarios.remove(usuario)
        self.guardar()
        print(
            f"Usuario '{usuario.getNombre()}' (ID: {usuario.getId()}) "
            "y sus dispositivos fueron eliminados."
        )
        return True

    def eliminarDispositivo(self, ip: str) -> bool:
        dispositivo = self.buscarDispositivoPorIp(ip)
        if dispositivo is None:
            print(f"Error: No se encontró ningún dispositivo con IP '{ip}'.")
            return False

        propietario = dispositivo.getUsuario()
        if propietario is not None:
            propietario.removerDispositivoLocal(dispositivo)

        self._dispositivos.remove(dispositivo)
        self.guardar()
        print(f"Dispositivo con IP '{dispositivo.getIp()}' eliminado de la red.")
        return True

    def eliminarPagina(self, url: str) -> bool:
        pagina = self.buscarPaginaPorUrl(url)
        if pagina is None:
            print(f"Error: No se encontró la página '{url}' en la lista registrada.")
            return False

        self._paginas.remove(pagina)
        self.guardar()
        print(f"Página '{pagina.getUrl()}' eliminada del sistema.")
        return True

    def getUsuarios(self) -> list:
        return list(self._usuarios)

    def getDispositivos(self) -> list:
        return list(self._dispositivos)

    def getPaginas(self) -> list:
        return list(self._paginas)

    def getRegistros(self) -> list:
        return list(self._registros)