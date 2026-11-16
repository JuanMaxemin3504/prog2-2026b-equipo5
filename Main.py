import os
from dispositivo import Dispositivo
from pagina import Pagina
from red import Red
from usuario import Administrador, Usuario

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_red.json")


def inicializar_datos():
    red = Red.cargar(RUTA_BD)

    if red is not None:
        print(f"Base de datos cargada desde: {RUTA_BD}")
        usuarios = red.getUsuarios()
        admin = next((u for u in usuarios if isinstance(u, Administrador)), None)
        usuario_inicial = admin if admin else (usuarios[0] if usuarios else None)
        if usuario_inicial is not None:
            return red, usuario_inicial

    print("Creando base de datos inicial en 'datos_red.json'...")
    red = Red(archivo_bd=RUTA_BD, auto_guardar=True)

    admin = Administrador("ADM01", "Erik Pérez")
    usr1 = Usuario("USR01", "Juan Manuel")
    usr2 = Usuario("USR02", "Ana López")

    red.registrarUsuario(admin)
    red.registrarUsuario(usr1)
    red.registrarUsuario(usr2)

    admin.encenderRed(red)

    admin.admitirPagina(Pagina("https://intranet.empresa.com", True), red)
    admin.admitirPagina(Pagina("https://correo.empresa.com", True), red)
    admin.restringirPagina(Pagina("https://youtube.com", False), red)
    admin.restringirPagina(Pagina("https://netflix.com", False), red)

    return red, admin


def verificar_es_admin(usuario_actual) -> bool:
    if not isinstance(usuario_actual, Administrador):
        print("Acceso denegado: Solo el administrador puede realizar esta acción.")
        return False
    return True


def menu():
    red, usuario_actual = inicializar_datos()

    while True:
        rol = "Administrador" if isinstance(usuario_actual, Administrador) else "Usuario"
        estado_red = "ENCENDIDA" if red.estaEncendida() else "APAGADA"

        print("\n==============================================")
        print(f" SISTEMA DE CONTROL DE RED | Estado: {estado_red}")
        print(f" Sesión activa: {usuario_actual.getNombre()} (ID: {usuario_actual.getId()}) [{rol}]")
        print("==============================================")
        print("0. Salir")
        print("1. Cambiar usuario activo (iniciar sesión)")
        print("2. Conectar dispositivo a la red")
        print("3. Visitar página web")
        print("4. Consultar datos de usuario")
        if isinstance(usuario_actual, Administrador):
            print("5. [Admin] Registrar nuevo usuario")
            print("6. [Admin] Encender / Apagar red")
            print("7. [Admin] Admitir / Restringir página")
            print("8. [Admin] Ver usuarios y dispositivos conectados")
            print("9. [Admin] Revisar historial de accesos")
            print("10. [Admin] Eliminar usuario, dispositivo o página")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            id_buscar = input("Ingresa el ID del usuario con el que deseas entrar: ").strip()
            encontrado = red.buscarUsuarioPorId(id_buscar)
            if encontrado:
                usuario_actual = encontrado
                print(f"Sesión cambiada a: {usuario_actual.getNombre()}")
            else:
                print("Error: No existe un usuario con ese ID.")

        elif opcion == "2":
            ip = input("Ingresa la dirección IP del dispositivo (ej. 192.168.1.25): ")
            try:
                dispositivo = Dispositivo(ip)
                usuario_actual.conectarse(dispositivo, red)
            except ValueError as e:
                print(e)

        elif opcion == "3":
            print("\nPáginas registradas en el sistema:")
            for p in red.getPaginas():
                print(f" - {p}")
            url = input("Ingresa la URL a visitar: ").strip()
            if not url:
                print("Error: La URL no puede estar vacía.")
                continue
            pagina = red.buscarPaginaPorUrl(url)
            if pagina is None:
                pagina = Pagina(url, False)
            usuario_actual.visitarPagina(pagina, red)

        elif opcion == "4":
            if isinstance(usuario_actual, Administrador):
                id_consulta = input("Ingresa el ID a consultar (o Enter para ver los tuyos): ").strip()
                if not id_consulta or id_consulta == usuario_actual.getId():
                    usuario_actual.consultarDatosPropios()
                else:
                    objetivo = red.buscarUsuarioPorId(id_consulta)
                    if objetivo:
                        objetivo.consultarDatosPropios()
                    else:
                        print("Error: Usuario no encontrado.")
            else:
                id_consulta = input(
                    f"Ingresa el ID a consultar (tu ID es {usuario_actual.getId()}): "
                ).strip()
                usuario_actual.consultarDatosPropios(id_consulta)

        elif opcion == "5":
            if verificar_es_admin(usuario_actual):
                id_nuevo = input("Ingresa el ID del nuevo usuario: ")
                nombre_nuevo = input("Ingresa el nombre del nuevo usuario: ")
                try:
                    nuevo_usuario = Usuario(id_nuevo, nombre_nuevo)
                    red.registrarUsuario(nuevo_usuario)
                except ValueError as e:
                    print(e)

        elif opcion == "6":
            if verificar_es_admin(usuario_actual):
                accion = input("Escribe '1' para ENCENDER o '2' para APAGAR la red: ").strip()
                if accion == "1":
                    usuario_actual.encenderRed(red)
                elif accion == "2":
                    usuario_actual.apagarRed(red)
                else:
                    print("Opción inválida.")

        elif opcion == "7":
            if verificar_es_admin(usuario_actual):
                url = input("Ingresa la URL de la página: ").strip()
                if not url:
                    print("Error: La URL no puede estar vacía.")
                    continue
                pagina = red.buscarPaginaPorUrl(url)
                if pagina is None:
                    pagina = Pagina(url, False)
                accion = input("Escribe '1' para ADMITIR o '2' para RESTRINGIR: ").strip()
                if accion == "1":
                    usuario_actual.admitirPagina(pagina, red)
                elif accion == "2":
                    usuario_actual.restringirPagina(pagina, red)
                else:
                    print("Opción inválida.")

        elif opcion == "8":
            if verificar_es_admin(usuario_actual):
                usuario_actual.verUsuariosConectados(red)
                usuario_actual.verDispositivosConectados(red)

        elif opcion == "9":
            if verificar_es_admin(usuario_actual):
                usuario_actual.revisarHistorial(red)

        elif opcion == "10":
            if verificar_es_admin(usuario_actual):
                print("\n--- Eliminar Elemento Individual ---")
                print("1. Eliminar un usuario (por ID)")
                print("2. Eliminar un dispositivo (por IP)")
                print("3. Eliminar una página (por URL)")
                print("0. Cancelar")
                sub = input("Elige una opción: ").strip()

                if sub == "1":
                    usuario_actual.verUsuariosConectados(red)
                    id_borrar = input("\nIngresa el ID del usuario a eliminar: ").strip()
                    if id_borrar:
                        usuario_actual.eliminarUsuario(id_borrar, red)

                elif sub == "2":
                    usuario_actual.verDispositivosConectados(red)
                    ip_borrar = input("\nIngresa la IP del dispositivo a eliminar: ").strip()
                    if ip_borrar:
                        usuario_actual.eliminarDispositivo(ip_borrar, red)

                elif sub == "3":
                    print("\nPáginas registradas:")
                    for p in red.getPaginas():
                        print(f" - {p}")
                    url_borrar = input("\nIngresa la URL de la página a eliminar: ").strip()
                    if url_borrar:
                        usuario_actual.eliminarPagina(url_borrar, red)

                elif sub == "0":
                    print("Operación cancelada.")
                else:
                    print("Opción inválida.")

        elif opcion == "0":
            red.guardar()
            print("Datos guardados. Saliendo del sistema...")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()