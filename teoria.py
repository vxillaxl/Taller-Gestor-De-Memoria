"""Notas cortas que salen en la pestaña de la app."""

TEORIA = """
Dirección virtual y dirección física
------------------------------------

Virtual: la que usa el programa. malloc, las funciones, las DLL, todo eso
trabaja con virtuales. Cada proceso tiene las suyas. Si dos procesos
tienen el mismo número, no es la misma memoria.

Física: dónde está de verdad en la RAM. El proceso no la ve. A veces una
misma página física la comparten varios (una DLL del sistema, por ejemplo).


La MMU
------

Es hardware de la CPU. Uno le pasa la virtual y ella, con las tablas que
arma el SO, saca la física.

Si la página no está, page fault.
Si uno escribe donde no debe, Access Violation.

También mira si la página es R, RW o RX. El código casi siempre es RX,
el heap es RW.


¿Se pueden cambiar esas direcciones?
------------------------------------

Desde el mismo proceso:
  - Código: no lo muevo. Escribirle encima normalmente no deja (está RX).
  - Pila: las variables sí. La base del stack la pone Windows.
  - Heap: sí, a escribirle. malloc va saliendo en direcciones nuevas.
  - DLL: el código no; los datos de la librería sí.

Desde otro proceso:
  - No veo su mapa como si fuera mío.
  - System (PID 4) ni siquiera me deja abrirlo.
  - explorer sí me deja VER código/pila/heap/DLL, pero eso es solo lectura.
  - Escribirle a otro ya es tema de depurador, no de un programa normal.
"""

RESUMEN_CORTO = (
    "Virtual = lo que ve el proceso. Física = la RAM de verdad. "
    "La MMU traduce y mira permisos. "
    "El heap y la pila se pueden escribir. El código no se reubica. "
    "Otro proceso solo ve el mapa si Windows se lo permite."
)
