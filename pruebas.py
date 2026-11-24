"""Suite de pruebas automatizadas del contrato y validaciones del sistema."""

import os
import tempfile
from modelo import Administrador, Dispositivo, Pagina, Usuario
from red import Red


def ejecutar_pruebas() -> None:
    """Ejecuta casos de error y casos exitosos limpiando el archivo temporal al finalizar."""
    ruta_tmp = os.path.join(tempfile.gettempdir(), "test_red_udg.json")
    red = Red(archivo_bd=ruta_tmp, auto_guardar=True)
    print("\n=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS ===")

    try:
        # 1. Arranque limpio vacío
        assert len(red.usuarios) == 0 and len(red.listar()) == 0
        print("[OK] 1. Arranque limpio con red vacía.")

        # 2. Rechazo por campo obligatorio vacío
        try:
            Usuario("U1", "   ")
            raise AssertionError("Debió rechazar nombre vacío.")
        except ValueError as e:
            print(f"[OK] 2. Error capturado (nombre vacío): {e}")

        # 3. Rechazo por formato IP inválido
        try:
            Dispositivo("300.168.1.1")
            raise AssertionError("Debió rechazar IP inválida.")
        except ValueError as e:
            print(f"[OK] 3. Error capturado (IP inválida): {e}")

        # 4. Alta y rechazo por ID duplicado
        admin = Administrador("ADM01", "Erik Pérez")
        usr1 = Usuario("USR01", "Juan Manuel")
        usr2 = Usuario("USR02", "Ana López")
        red.registrar(admin)
        red.registrar(usr1)
        red.registrar(usr2)
        try:
            red.registrar(Usuario("USR01", "Duplicado"))
            raise AssertionError("Debió rechazar ID duplicado.")
        except ValueError as e:
            print(f"[OK] 4. Error capturado (ID duplicado): {e}")

        # 5. Rechazo al asignar con red apagada y por usuario estándar (polimorfismo)
        d1, d2, d3 = Dispositivo("192.168.1.10"), Dispositivo("192.168.1.11"), Dispositivo("192.168.1.12")
        red.registrar(d1)
        red.registrar(d2)
        red.registrar(d3)
        try:
            red.asignar("192.168.1.10", "USR01")
            raise AssertionError("Debió rechazar asignación con red apagada.")
        except ValueError as e:
            print(f"[OK] 5. Error capturado (red apagada): {e}")

        try:
            usr1.encender_red(red)
            raise AssertionError("Debió rechazar acción de admin a usuario normal.")
        except PermissionError as e:
            print(f"[OK] 6. Error capturado (permisos polimórficos): {e}")

        # 7. Asignación exitosa, doble asignación y límite de 2 dispositivos
        admin.encender_red(red)
        red.asignar("192.168.1.10", "USR01")
        try:
            red.asignar("192.168.1.10", "USR01")
            raise AssertionError("Debió rechazar doble asignación.")
        except ValueError as e:
            print(f"[OK] 7. Error capturado (doble asignación): {e}")

        red.asignar("192.168.1.11", "USR01")
        try:
            red.asignar("192.168.1.12", "USR01")
            raise AssertionError("Debió rechazar tercer dispositivo.")
        except ValueError as e:
            print(f"[OK] 8. Error capturado (límite de 2 dispositivos): {e}")

        # 9. Navegación admitida vs restringida y privacidad de datos
        p_ok, p_no = Pagina("https://intranet.empresa.com", False), Pagina("https://youtube.com", True)
        red.registrar(p_ok)
        red.registrar(p_no)
        red.asignar("https://intranet.empresa.com", True)
        red.asignar("https://youtube.com", False)
        assert usr1.visitar_pagina(p_ok, red) is True
        try:
            usr1.visitar_pagina(p_no, red)
            raise AssertionError("Debió bloquear página restringida.")
        except PermissionError as e:
            print(f"[OK] 9. Error capturado (página restringida): {e}")

        try:
            usr1.consultar_datos(usr2)
            raise AssertionError("Debió bloquear consulta ajena.")
        except PermissionError as e:
            print(f"[OK] 10. Error capturado (privacidad entre usuarios): {e}")

        # 11. Listar polimórfico, guardar(sistema, ruta) y cargar(sistema, ruta)
        assert len(red.listar()) == 8
        red.guardar(red, ruta_tmp)
        red_copia = Red(archivo_bd=None, auto_guardar=False)
        red_copia.cargar(red_copia, ruta_tmp)
        assert len(red_copia.usuarios) == 3 and len(red_copia.registros) == 2
        print("[OK] 11. Contrato listar(), guardar() y cargar() verificados.")
        print("=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE (11/11) ===\n")
    finally:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)


if __name__ == "__main__":
    ejecutar_pruebas()