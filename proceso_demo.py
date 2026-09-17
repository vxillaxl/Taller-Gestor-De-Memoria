"""Imprime código, pila, heap y DLL, y espera para poder inspeccionarlo."""

from memoria import direcciones_clasicas

d = direcciones_clasicas()
print("proceso de prueba")
print("PID:", d["pid"])
print()
print("codigo:     ", d["código"])
print("pila:       ", d["pila_baja"], "->", d["pila_alta"])
print("heap malloc:", d["montículo"])
print("kernel32:   ", d["kernel32"])
print("ntdll:      ", d["ntdll"])
print()
print("estas dirs son virtuales, en otra corrida pueden salir otras")
print("en la app: actualizar lista, busca este PID y dale analizar")
print()
input("enter para salir ")
