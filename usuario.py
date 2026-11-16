from registro_acceso import RegistroAcceso


class Usuario:
    MAX_DISPOSITIVOS = 2

    def __init__(self, id_usuario: str, nombre: str):
        if not id_usuario or not id_usuario.strip():
            raise ValueError("Error: El ID es obligatorio.")
        if not nombre or not nombre.strip():
            raise ValueError("Error: El nombre es obligatorio.")
        self._id = id_usuario.strip()
        self._nombre = nombre.strip()
        self._dispositivos = []

    def getId(self) -> str:
        return self._id

    def getNombre(self) -> str:
        return self._nombre

    def getDispositivos(self) -> list:
        return list(self._dispositivos)

    def removerDispositivoLocal(self, dispositivo) -> None:
        if dispositivo in self._dispositivos:
            self._dispositivos.remove(dispositivo)

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "rol": "Administrador" if isinstance(self, Administrador) else "Usuario",
        }

    def conectarse(self, dispositivo, red) -> bool:
        if not red.estaEncendida():
            print("Error: La red está apagada. No se puede conectar el dispositivo.")
            return False

        if red.buscarUsuarioPorId(self._id) is None:
            print("Error: El usuario no está registrado en la red.")
            return False

        if dispositivo in self._dispositivos:
            print(f"Aviso: El dispositivo {dispositivo.getIp()} ya está conectado a tu usuario.")
            return True

        if len(self._dispositivos) >= Usuario.MAX_DISPOSITIVOS:
            print(
                f"Error: El usuario '{self._nombre}' ya llegó al límite de "
                f"{Usuario.MAX_DISPOSITIVOS} dispositivos."
            )
            return False

        if dispositivo.getUsuario() is not None and dispositivo.getUsuario() != self:
            print("Error: El dispositivo ya pertenece a otro usuario.")
            return False

        if not red.agregarDispositivo(dispositivo):
            return False

        dispositivo.setUsuario(self)
        self._dispositivos.append(dispositivo)
        red.guardar()
        print(f"Conexión exitosa: IP {dispositivo.getIp()} asignada a {self._nombre}.")
        return True

    def visitarPagina(self, pagina, red) -> bool:
        if not red.estaEncendida():
            print("Error: La red está apagada. No se puede visitar la página.")
            return False

        if len(self._dispositivos) == 0:
            print("Error: Debes conectar al menos un dispositivo antes de navegar.")
            return False

        permitido = pagina.esAdmitida()
        registro = RegistroAcceso(self, pagina, permitido)
        registro.registrarIntento()
        red.registrarAcceso(registro)

        if permitido:
            print(f"Acceso permitido: Visitando '{pagina.getUrl()}'.")
            return True
        else:
            print(
                f"Acceso denegado: La página '{pagina.getUrl()}' "
                "no está permitida por la empresa."
            )
            return False

    def consultarDatosPropios(self, id_objetivo: str = None) -> bool:
        if id_objetivo is not None and id_objetivo.strip() != self._id:
            print("Acceso denegado: No tienes permisos para ver datos de otros usuarios.")
            return False

        print("\n--- Tus Datos de Usuario ---")
        print(f"ID: {self._id}")
        print(f"Nombre: {self._nombre}")
        if self._dispositivos:
            ips = ", ".join(d.getIp() for d in self._dispositivos)
            print(f"Dispositivos conectados ({len(self._dispositivos)}/2): {ips}")
        else:
            print("Dispositivos conectados: Ninguno (0/2)")
        return True


class Administrador(Usuario):
    def __init__(self, id_usuario: str, nombre: str):
        super().__init__(id_usuario, nombre)

    def encenderRed(self, red) -> None:
        red.encender()

    def apagarRed(self, red) -> None:
        red.apagar()

    def verUsuariosConectados(self, red) -> None:
        print("\n=== Usuarios Registrados en la Red ===")
        usuarios = red.getUsuarios()
        if not usuarios:
            print("No hay usuarios registrados.")
            return
        for u in usuarios:
            rol = "Administrador" if isinstance(u, Administrador) else "Usuario"
            print(
                f"- ID: {u.getId()} | Nombre: {u.getNombre()} | "
                f"Rol: {rol} | Dispositivos: {len(u.getDispositivos())}/2"
            )

    def verDispositivosConectados(self, red) -> None:
        print("\n=== Dispositivos Conectados en la Red ===")
        dispositivos = red.getDispositivos()
        if not dispositivos:
            print("No hay dispositivos conectados.")
            return
        for d in dispositivos:
            print(f"- {d}")

    def admitirPagina(self, pagina, red) -> None:
        red.admitirPagina(pagina)

    def restringirPagina(self, pagina, red) -> None:
        red.restringirPagina(pagina)

    def revisarHistorial(self, red) -> None:
        print("\n=== Historial de Accesos ===")
        registros = red.getRegistros()
        if not registros:
            print("No hay registros de acceso todavía.")
            return
        for r in registros:
            print(f"- {r}")

    def eliminarUsuario(self, id_usuario: str, red) -> bool:
        if id_usuario.strip() == self._id:
            print("Error: No puedes eliminar tu propia cuenta mientras tienes la sesión activa.")
            return False
        return red.eliminarUsuario(id_usuario)

    def eliminarDispositivo(self, ip: str, red) -> bool:
        return red.eliminarDispositivo(ip)

    def eliminarPagina(self, url: str, red) -> bool:
        return red.eliminarPagina(url)