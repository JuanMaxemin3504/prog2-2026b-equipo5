"""Capa de presentación (interfaz de consola) para el sistema de control de red."""

import os
import tempfile
from dispositivo import Dispositivo
from pagina import Pagina
from red import Red
from usuario import Administrador, Usuario

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_red.json")


def inicializar_datos() -> tuple[Red, Usuario]:
    """Carga la base de datos existente o crea una nueva con datos iniciales."""
    red = Red(archivo_bd=RUTA_BD, auto_guardar=True)

    if os.path.exists(RUTA_BD):
        try:
            red.cargar(red, RUTA_BD)
            print(f"Base de datos cargada desde: {RUTA_BD}")
            usuarios = red.usuarios
            if usuarios:
                return red, usuarios[0]
        except (ValueError, KeyError, OSError) as error:
            print(f"Aviso: No se pudo cargar la BD ({error}). Se creará una nueva.")

    print("Creando base de datos inicial en 'datos_red.json'...")
    admin = Administrador("ADM01", "Erik Pérez")
    usr1 = Usuario("USR01", "Juan Manuel")
    usr2 = Usuario("USR02", "Ana López")

    red.registrar(admin)
    red.registrar(usr1)
    red.registrar(usr2)

    admin.encender_red(red)

    admin.admitir_pagina(Pagina("https://intranet.empresa.com", True), red)
    admin.admitir_pagina(Pagina("https://correo.empresa.com", True), red)
    admin.restringir_pagina(Pagina("https://youtube.com", False), red)
    admin.restringir_pagina(Pagina("https://netflix.com", False), red)

    return red, admin


def ejecutar_pruebas_automatizadas() -> None:
    """Ejecuta pruebas de error y pruebas exitosas detallando cada acción y limpiando al final."""
    ruta_prueba = os.path.join(tempfile.gettempdir(), "datos_prueba_temporal.json")
    print("\n==================================================================")
    print(" SUITE DE PRUEBAS AUTOMATIZADAS (CASOS DE ERROR Y CASOS EXITOSOS)")
    print("==================================================================")

    red_prueba = Red(archivo_bd=ruta_prueba, auto_guardar=True)

    try:
        print("\n--- BLOQUE A: PRUEBAS DE ERROR (VALIDACIONES Y EXCEPCIONES) ---")

        print("\n[Caso Error 1] Intentar crear un usuario con nombre vacío:")
        try:
            Usuario("USR_ERR", "   ")
            raise AssertionError("El sistema permitió crear un usuario con nombre vacío.")
        except ValueError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 2] Intentar registrar un ID de usuario duplicado:")
        admin = Administrador("ADM_P", "Admin Prueba")
        usr1 = Usuario("USR_P1", "Carlos")
        red_prueba.registrar(admin)
        red_prueba.registrar(usr1)
        try:
            red_prueba.registrar(Usuario("USR_P1", "Carlos Duplicado"))
            raise AssertionError("El sistema permitió registrar un ID duplicado.")
        except ValueError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 3] Intentar crear un dispositivo con IP inválida ('999.168.1.1'):")
        try:
            Dispositivo("999.168.1.1")
            raise AssertionError("El sistema permitió crear un dispositivo con IP inválida.")
        except ValueError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 4] Intentar asignar un dispositivo cuando la red está APAGADA:")
        d1 = Dispositivo("192.168.50.1")
        red_prueba.registrar(d1)
        try:
            red_prueba.asignar("192.168.50.1", "USR_P1")
            raise AssertionError("El sistema permitió asignar un dispositivo con la red apagada.")
        except ValueError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 5] Intentar encender la red siendo un Usuario estándar (polimorfismo):")
        try:
            usr1.encender_red(red_prueba)
            raise AssertionError("El sistema permitió que un usuario normal encendiera la red.")
        except PermissionError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 6] Intentar conectar un tercer dispositivo al mismo usuario (límite 2):")
        admin.encender_red(red_prueba)
        d2 = Dispositivo("192.168.50.2")
        d3 = Dispositivo("192.168.50.3")
        red_prueba.registrar(d2)
        red_prueba.registrar(d3)
        red_prueba.asignar("192.168.50.1", "USR_P1")
        red_prueba.asignar("192.168.50.2", "USR_P1")
        try:
            red_prueba.asignar("192.168.50.3", "USR_P1")
            raise AssertionError("El sistema permitió conectar un tercer dispositivo.")
        except ValueError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 7] Intentar visitar una página restringida por la empresa:")
        pag_restringida = Pagina("https://youtube.com", False)
        red_prueba.registrar(pag_restringida)
        try:
            usr1.visitar_pagina(pag_restringida, red_prueba)
            raise AssertionError("El sistema permitió visitar una página restringida.")
        except PermissionError as error:
            print(f"  -> Bloqueado correctamente ({type(error).__name__}): {error}")

        print("\n[Caso Error 8] Usuario estándar intenta consultar los datos de otro usuario:")
        try:
            usr1.consultar_datos(admin)
            raise AssertionError("El sistema permitió consultar los datos de otro usuario.")
        except PermissionError as error:
            print(f"  -> Rechazado correctamente ({type(error).__name__}): {error}")

        print("\n--- BLOQUE B: PRUEBAS EXITOSAS (FLUJO NORMAL Y CONTRATO) ---")

        print("\n[Caso Éxito 1] Registrar un nuevo usuario válido mediante red.registrar():")
        usr2 = Usuario("USR_P2", "María")
        red_prueba.registrar(usr2)
        print(f"  -> Éxito: {usr2} dado de alta en la red.")

        print("\n[Caso Éxito 2] Registrar y asignar un dispositivo válido mediante red.asignar():")
        d4 = Dispositivo("192.168.50.10")
        red_prueba.registrar(d4)
        red_prueba.asignar("192.168.50.10", "USR_P2")
        print(f"  -> Éxito: Dispositivo {d4.ip} asignado a {usr2.nombre}.")

        print("\n[Caso Éxito 3] Registrar una página, admitirla y navegar hacia ella:")
        pag_empresa = Pagina("https://intranet.empresa.com", False)
        red_prueba.registrar(pag_empresa)
        red_prueba.asignar("https://intranet.empresa.com", True)
        acceso = usr2.visitar_pagina(pag_empresa, red_prueba)
        print(f"  -> Éxito: Acceso concedido ({acceso}) a '{pag_empresa.url}'.")

        print("\n[Caso Éxito 4] Consultar datos propios de usuario:")
        datos_usr = usr2.consultar_datos()
        print(f"  -> Éxito: {datos_usr}")

        print("\n[Caso Éxito 5] Listar todos los elementos registrados mediante red.listar():")
        elementos = red_prueba.listar()
        print(f"  -> Éxito: {len(elementos)} elementos registrados listados correctamente.")

        print("\n[Caso Éxito 6] Guardar estado con guardar(sistema, ruta) y reconstruir con cargar(sistema, ruta):")
        red_prueba.guardar(red_prueba, ruta_prueba)
        red_cargada = Red(archivo_bd=None, auto_guardar=False)
        red_cargada.cargar(red_cargada, ruta_prueba)
        assert len(red_cargada.usuarios) == 3
        assert len(red_cargada.dispositivos) == 4
        assert len(red_cargada.registros) == 2
        print(
            f"  -> Éxito: BD reconstruida con {len(red_cargada.usuarios)} usuarios, "
            f"{len(red_cargada.dispositivos)} dispositivos y {len(red_cargada.registros)} registros."
        )

    finally:
        print("\n--- LIMPIEZA DE DATOS DE PRUEBA ---")
        for usuario in list(red_prueba.usuarios):
            red_prueba.eliminar_usuario(usuario.id)
        for pagina in list(red_prueba.paginas):
            red_prueba.eliminar_pagina(pagina.url)
        if os.path.exists(ruta_prueba):
            os.remove(ruta_prueba)
        print(f"  -> Archivo temporal '{os.path.basename(ruta_prueba)}' y registros de prueba eliminados.")
        print("==================================================================\n")
    """Ejecuta una batería de pruebas automatizadas sobre el contrato y las validaciones."""
    print("\n================ EJECUTANDO PRUEBAS AUTOMATIZADAS ================")
    red_test = Red(archivo_bd=None, auto_guardar=False)
    admin = Administrador("ADM_TEST", "Admin Test")
    usr1 = Usuario("USR_TEST1", "Usuario Uno")
    usr2 = Usuario("USR_TEST2", "Usuario Dos")

    # 1. Alta mediante contrato registrar() y validación de nombre vacío
    red_test.registrar(admin)
    red_test.registrar(usr1)
    red_test.registrar(usr2)

    try:
        Usuario("U_ERR", "   ")
        raise AssertionError("Debió lanzar ValueError por nombre vacío.")
    except ValueError:
        print("[OK] 1. Rechazo con ValueError por nombre vacío.")

    # 2. Validación de ID duplicado en registrar()
    try:
        red_test.registrar(Usuario("USR_TEST1", "Duplicado"))
        raise AssertionError("Debió lanzar ValueError por ID duplicado.")
    except ValueError:
        print("[OK] 2. Rechazo con ValueError por ID duplicado en registrar().")

    # 3. Validación estricta de IPv4
    try:
        Dispositivo("999.168.1.1")
        raise AssertionError("Debió lanzar ValueError por IP inválida.")
    except ValueError:
        print("[OK] 3. Rechazo con ValueError por IPv4 inválida.")

    # 4. Asignación mediante contrato asignar() con la red apagada
    d1 = Dispositivo("10.0.0.1")
    d2 = Dispositivo("10.0.0.2")
    d3 = Dispositivo("10.0.0.3")
    red_test.registrar(d1)
    red_test.registrar(d2)
    red_test.registrar(d3)

    try:
        red_test.asignar("10.0.0.1", "USR_TEST1")
        raise AssertionError("Debió lanzar ValueError al asignar con la red apagada.")
    except ValueError:
        print("[OK] 4. Rechazo con ValueError al asignar dispositivo con red apagada.")

    # 5. Polimorfismo: Usuario estándar intenta ejecutar acción de Administrador
    try:
        usr1.encender_red(red_test)
        raise AssertionError("Debió lanzar PermissionError para usuario estándar.")
    except PermissionError:
        print("[OK] 5. Polimorfismo: PermissionError cuando Usuario intenta acción de Admin.")

    # 6. Encendido de red y validación del límite máximo de 2 dispositivos
    admin.encender_red(red_test)
    red_test.asignar("10.0.0.1", "USR_TEST1")
    red_test.asignar("10.0.0.2", "USR_TEST1")

    try:
        red_test.asignar("10.0.0.3", "USR_TEST1")
        raise AssertionError("Debió lanzar ValueError al superar 2 dispositivos.")
    except ValueError:
        print("[OK] 6. Rechazo con ValueError al superar el límite de 2 dispositivos.")

    # 7. Políticas de navegación (admitida vs restringida) y registro en historial
    p_ok = Pagina("https://intranet.test.com", False)
    p_no = Pagina("https://video.test.com", True)
    red_test.registrar(p_ok)
    red_test.registrar(p_no)
    red_test.asignar("https://intranet.test.com", True)
    red_test.asignar("https://video.test.com", False)

    assert usr1.visitar_pagina(p_ok, red_test) is True
    try:
        usr1.visitar_pagina(p_no, red_test)
        raise AssertionError("Debió lanzar PermissionError en página restringida.")
    except PermissionError:
        print("[OK] 7. Bloqueo con PermissionError en página restringida y registro en bitácora.")

    # 8. Privacidad de datos entre usuarios estándar
    try:
        usr1.consultar_datos(usr2)
        raise AssertionError("Debió lanzar PermissionError al consultar otro usuario.")
    except PermissionError:
        print("[OK] 8. Rechazo con PermissionError al consultar datos de otro usuario.")

    # 9. Contrato listar()
    elementos = red_test.listar()
    assert len(elementos) == 8
    print(f"[OK] 9. Contrato listar() devolvió {len(elementos)} elementos registrados.")

    # 10. Contrato guardar(sistema, ruta) y cargar(sistema, ruta)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        ruta_tmp = tmp.name

    try:
        red_test.guardar(red_test, ruta_tmp)
        red_reconstruida = Red(archivo_bd=None, auto_guardar=False)
        red_reconstruida.cargar(red_reconstruida, ruta_tmp)
        assert len(red_reconstruida.usuarios) == 3
        assert len(red_reconstruida.dispositivos) == 3
        assert len(red_reconstruida.registros) == 2
        assert len(red_reconstruida.buscar_usuario_por_id("USR_TEST1").dispositivos) == 2
        print("[OK] 10. Contrato guardar(sistema, ruta) y cargar(sistema, ruta) verificado.")
    finally:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)

    print("==================================================================")
    print(" TODAS LAS PRUEBAS AUTOMATIZADAS PASARON EXITOSAMENTE (10/10)")
    print("==================================================================\n")


def menu() -> None:
    """Ejecuta el ciclo principal de interacción por consola."""
    red, usuario_actual = inicializar_datos()

    while True:
        estado_red = "ENCENDIDA" if red.esta_encendida else "APAGADA"

        print("\n==============================================")
        print(f" SISTEMA DE CONTROL DE RED | Estado: {estado_red}")
        print(
            f" Sesión activa: {usuario_actual.nombre} "
            f"(ID: {usuario_actual.id}) [{usuario_actual.rol}]"
        )
        print("==============================================")
        print("0. Salir")
        print("1. Cambiar usuario activo (iniciar sesión)")
        print("2. Conectar dispositivo a la red")
        print("3. Visitar página web")
        print("4. Consultar datos de usuario")
        print("5. [Admin] Registrar nuevo usuario")
        print("6. [Admin] Encender / Apagar red")
        print("7. [Admin] Admitir / Restringir página")
        print("8. [Admin] Ver usuarios y dispositivos conectados")
        print("9. [Admin] Revisar historial de accesos")
        print("10. [Admin] Eliminar usuario, dispositivo o página")
        print("11. Listar todos los elementos registrados")
        print("12. Ejecutar pruebas automatizadas")

        opcion = input("\nSelecciona una opción: ").strip()

        try:
            if opcion == "1":
                id_buscar = input("Ingresa el ID del usuario con el que deseas entrar: ").strip()
                encontrado = red.buscar_usuario_por_id(id_buscar)
                if encontrado is None:
                    raise ValueError(f"No existe un usuario con ID '{id_buscar}'.")
                usuario_actual = encontrado
                print(f"Sesión cambiada a: {usuario_actual.nombre}")

            elif opcion == "2":
                ip = input("Ingresa la dirección IP del dispositivo (ej. 192.168.1.25): ")
                dispositivo = Dispositivo(ip)
                usuario_actual.conectarse(dispositivo, red)
                print(f"Conexión exitosa: IP {dispositivo.ip} asignada a {usuario_actual.nombre}.")

            elif opcion == "3":
                print("\nPáginas registradas en el sistema:")
                for pagina in red.paginas:
                    print(f" - {pagina}")
                url = input("Ingresa la URL a visitar: ").strip()
                pagina = red.buscar_pagina_por_url(url)
                if pagina is None:
                    pagina = Pagina(url, False)
                usuario_actual.visitar_pagina(pagina, red)
                print(f"Acceso permitido: Visitando '{pagina.url}'.")

            elif opcion == "4":
                id_consulta = input(
                    f"Ingresa el ID a consultar (Enter para ver '{usuario_actual.id}'): "
                ).strip()
                if not id_consulta or id_consulta == usuario_actual.id:
                    print(f"\n--- Datos de Usuario ---\n{usuario_actual.consultar_datos()}")
                else:
                    objetivo = red.buscar_usuario_por_id(id_consulta)
                    if objetivo is None:
                        raise ValueError(f"No se encontró el usuario con ID '{id_consulta}'.")
                    print(f"\n--- Datos de Usuario ---\n{usuario_actual.consultar_datos(objetivo)}")

            elif opcion == "5":
                id_nuevo = input("Ingresa el ID del nuevo usuario: ")
                nombre_nuevo = input("Ingresa el nombre del nuevo usuario: ")
                nuevo_usuario = Usuario(id_nuevo, nombre_nuevo)
                usuario_actual.registrar_nuevo_usuario(nuevo_usuario, red)
                print(f"Usuario '{nuevo_usuario.nombre}' (ID: {nuevo_usuario.id}) registrado.")

            elif opcion == "6":
                accion = input("Escribe '1' para ENCENDER o '2' para APAGAR la red: ").strip()
                if accion == "1":
                    usuario_actual.encender_red(red)
                    print("Red ENCENDIDA correctamente.")
                elif accion == "2":
                    usuario_actual.apagar_red(red)
                    print("Red APAGADA correctamente.")
                else:
                    raise ValueError("Opción inválida. Debes ingresar '1' o '2'.")

            elif opcion == "7":
                url = input("Ingresa la URL de la página: ").strip()
                pagina = red.buscar_pagina_por_url(url)
                if pagina is None:
                    pagina = Pagina(url, False)
                accion = input("Escribe '1' para ADMITIR o '2' para RESTRINGIR: ").strip()
                if accion == "1":
                    usuario_actual.admitir_pagina(pagina, red)
                    print(f"Página '{pagina.url}' ADMITIDA en la red.")
                elif accion == "2":
                    usuario_actual.restringir_pagina(pagina, red)
                    print(f"Página '{pagina.url}' RESTRINGIDA en la red.")
                else:
                    raise ValueError("Opción inválida. Debes ingresar '1' o '2'.")

            elif opcion == "8":
                usuarios_fmt = usuario_actual.ver_usuarios_conectados(red)
                dispositivos_fmt = usuario_actual.ver_dispositivos_conectados(red)
                print("\n=== Usuarios Registrados ===")
                for linea in usuarios_fmt:
                    print(f"- {linea}")
                print("\n=== Dispositivos Conectados ===")
                if not dispositivos_fmt:
                    print("No hay dispositivos conectados.")
                for linea in dispositivos_fmt:
                    print(f"- {linea}")

            elif opcion == "9":
                historial = usuario_actual.revisar_historial(red)
                print("\n=== Historial de Accesos ===")
                if not historial:
                    print("No hay registros de acceso todavía.")
                for linea in historial:
                    print(f"- {linea}")

            elif opcion == "10":
                print("\n--- Eliminar Elemento Individual ---")
                print("1. Eliminar un usuario (por ID)")
                print("2. Eliminar un dispositivo (por IP)")
                print("3. Eliminar una página (por URL)")
                print("0. Cancelar")
                sub = input("Elige una opción: ").strip()

                if sub == "1":
                    for linea in usuario_actual.ver_usuarios_conectados(red):
                        print(f"- {linea}")
                    id_borrar = input("\nIngresa el ID del usuario a eliminar: ").strip()
                    usuario_actual.eliminar_usuario(id_borrar, red)
                    print(f"Usuario '{id_borrar}' eliminado correctamente.")

                elif sub == "2":
                    for linea in usuario_actual.ver_dispositivos_conectados(red):
                        print(f"- {linea}")
                    ip_borrar = input("\nIngresa la IP del dispositivo a eliminar: ").strip()
                    usuario_actual.eliminar_dispositivo(ip_borrar, red)
                    print(f"Dispositivo '{ip_borrar}' eliminado correctamente.")

                elif sub == "3":
                    for pagina in red.paginas:
                        print(f"- {pagina}")
                    url_borrar = input("\nIngresa la URL de la página a eliminar: ").strip()
                    usuario_actual.eliminar_pagina(url_borrar, red)
                    print(f"Página '{url_borrar}' eliminada correctamente.")

                elif sub == "0":
                    print("Operación cancelada.")
                else:
                    raise ValueError("Opción inválida.")

            elif opcion == "11":
                print("\n=== Elementos Registrados en la Red ===")
                for elemento in red.listar():
                    print(f"- {elemento}")

            elif opcion == "12":
                ejecutar_pruebas_automatizadas()

            elif opcion == "0":
                red.guardar(red, RUTA_BD)
                print("Datos guardados. Saliendo del sistema...")
                break

            else:
                print("Opción no válida. Intenta de nuevo.")

        except (ValueError, PermissionError, TypeError, FileNotFoundError, AssertionError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu()