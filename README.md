Sistema de Control de Acceso a Red Empresarial

Proyecto desarrollado en Python para la asignatura de Programación (Universidad de Guadalajara). El sistema simula y audita el control de acceso de empleados a la red interna de una empresa, validando direcciones IPv4, roles con polimorfismo, políticas de navegación web, bitácora de eventos y persistencia automática en JSON.

Integrantes

Erik Pérez Mercado — Código: 225996429

Juan Manuel Maxemin Monarres — Código: 225996313

Arquitectura y Estructura del Proyecto

El código está organizado bajo una separación estricta de responsabilidades (cohesión y arquitectura por capas), donde la lógica de negocio comunica errores mediante excepciones (ValueError, PermissionError, TypeError) y la interfaz de consola se encarga exclusivamente de la interacción con el usuario:
