"""Interfaz de consola para el sistema de control de acceso a red."""

import os
from modelo import Administrador, Dispositivo, Pagina, Usuario
from pruebas import ejecutar_pruebas
from red import Red

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_red.json")


def iniciar_sistema() -> Red:
    """Arranca el sistema cargando datos_red.json si existe o creando uno vacío."""
    red = Red(archivo_bd=RUTA_BD, auto_guardar=True)
    if os.path.exists(RUTA_BD):
        try:
            red.cargar(red, RUTA_BD)
        except (ValueError, KeyError, OSError):
            red.guardar(red, RUTA_BD)
    else:
        red.guardar(red, RUTA_BD)
        admin_inicial = Administrador("ADM01", "Erik Pérez")
        red.registrar(admin_inicial)
    return red


def menu() -> None:
    """Ejecuta el menú interactivo en consola."""
    red = iniciar_sistema()
    sesion: Usuario | None = red.usuarios[0] if red.usuarios else None

    while True:
        estado = "ENCENDIDA" if red.esta_encendida else "APAGADA"
        activo = f"{sesion.nombre} ({sesion.id}) [{sesion.rol}]" if sesion else "Sin sesión"
        print(f"\n=== CONTROL DE RED ({estado}) | Sesión: {activo} ===")
        print("1. Registrar usuario/admin   2. Iniciar sesión        3. Conectar dispositivo")
        print("4. Visitar página web        5. Consultar datos       6. [Admin] Encender/Apagar red")
        print("7. [Admin] Admitir/Restringir página                  8. [Admin] Revisar historial")
        print("9. Listar todo    10. Ejecutar pruebas     0. Salir")

        op = input("Opción: ").strip()
        try:
            if op == "1":
                uid = input("ID: ")
                nom = input("Nombre: ")
                es_adm = input("¿Es administrador? (s/n): ").strip().lower() == "s"
                nuevo = Administrador(uid, nom) if es_adm else Usuario(uid, nom)
                red.registrar(nuevo)
                if sesion is None:
                    sesion = nuevo
                print(f"Registrado: {nuevo}")
            elif op == "2":
                encontrado = red.buscar_usuario(input("ID de usuario: "))
                if encontrado is None:
                    raise ValueError("Usuario no encontrado.")
                sesion = encontrado
                print(f"Sesión activa: {sesion.nombre}")
            elif op == "3":
                if sesion is None:
                    raise ValueError("Primero registra o inicia sesión con un usuario.")
                disp = Dispositivo(input("IP del dispositivo: "))
                sesion.conectarse(disp, red)
                print(f"Dispositivo {disp.ip} conectado a {sesion.nombre}.")
            elif op == "4":
                if sesion is None:
                    raise ValueError("Primero inicia sesión con un usuario.")
                url = input("URL a visitar: ").strip()
                pag = red.buscar_pagina(url) or Pagina(url, False)
                sesion.visitar_pagina(pag, red)
                print(f"Acceso permitido a {pag.url}.")
            elif op == "5":
                if sesion is None:
                    raise ValueError("Primero inicia sesión con un usuario.")
                uid = input(f"ID a consultar (Enter para '{sesion.id}'): ").strip()
                obj = red.buscar_usuario(uid) if uid else sesion
                if obj is None:
                    raise ValueError("Usuario no encontrado.")
                print(sesion.consultar_datos(obj))
            elif op == "6":
                if sesion is None:
                    raise ValueError("Primero inicia sesión.")
                acc = input("1. Encender | 2. Apagar: ").strip()
                sesion.encender_red(red) if acc == "1" else sesion.apagar_red(red)
                print("Estado de red actualizado.")
            elif op == "7":
                if sesion is None:
                    raise ValueError("Primero inicia sesión.")
                url = input("URL de la página: ").strip()
                pag = red.buscar_pagina(url) or Pagina(url, False)
                acc = input("1. Admitir | 2. Restringir: ").strip()
                sesion.admitir_pagina(pag, red) if acc == "1" else sesion.restringir_pagina(pag, red)
                print(f"Política actualizada: {pag}")
            elif op == "8":
                if sesion is None:
                    raise ValueError("Primero inicia sesión.")
                for linea in sesion.revisar_historial(red):
                    print(f"- {linea}")
            elif op == "9":
                for item in red.listar():
                    print(f"- {item}")
            elif op == "10":
                ejecutar_pruebas()
            elif op == "0":
                red.guardar(red, RUTA_BD)
                print("Saliendo...")
                break
            else:
                print("Opción inválida.")
        except (ValueError, PermissionError, TypeError) as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    menu()