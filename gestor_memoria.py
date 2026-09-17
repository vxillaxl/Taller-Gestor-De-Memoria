#!/usr/bin/env python3
"""Taller del Gestor de Memoria — Sistemas Operativos."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import ctypes

from memoria import (
    PAGE_READONLY,
    PAGE_READWRITE,
    asignar_pagina,
    cambiar_proteccion,
    fmt_addr,
    fmt_size,
    inspeccionar,
    intentar_escribir,
    leer_memoria,
    liberar_pagina,
    listar_procesos,
    resumen_secciones,
    texto_evidencia,
)
from teoria import RESUMEN_CORTO, TEORIA

APP_TITULO = "Gestor de Memoria — Taller de Sistemas Operativos"
FONDO = "#eef2f7"
AZUL = "#1b365d"
ORO = "#b0892e"
TEXTO = "#1f2933"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITULO)
        self.geometry("1280x800")
        self.minsize(1024, 680)
        self.configure(bg=FONDO)
        self.mapa = None
        self.procesos: list[tuple[int, str]] = []
        self._pid_var = tk.StringVar()
        self._filtro = tk.StringVar(value="Todas")
        self._estado = tk.StringVar(value="Listo.")
        self._configurar_estilo()
        self._construir()
        self.after(80, self.cargar_procesos)
        self.after(200, self.analizar_actual)

    def _configurar_estilo(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=FONDO)
        style.configure("TLabel", background=FONDO, foreground=TEXTO, font=("Segoe UI", 10))
        style.configure("Titulo.TLabel", background=AZUL, foreground="white", font=("Segoe UI Semibold", 16))
        style.configure("Sub.TLabel", background=AZUL, foreground="#d6e4f5", font=("Segoe UI", 9))
        style.configure("Header.TFrame", background=AZUL)
        style.configure("TNotebook", background=FONDO)
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", background=ORO, foreground="white", font=("Segoe UI Semibold", 10))
        style.map("Accent.TButton", background=[("active", "#c9a227")])
        style.configure(
            "Treeview",
            font=("Consolas", 9),
            rowheight=24,
            background="white",
            fieldbackground="white",
        )
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 9), background="#d9e2ef")
        style.configure("Estado.TLabel", background="#d9e2ef", foreground=AZUL, font=("Segoe UI", 9))

    def _construir(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="  Taller del Gestor de Memoria", style="Titulo.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Label(
            header,
            text="  código, pila, heap y DLL de un proceso",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=12, pady=10)
        ttk.Label(barra, text="Proceso:").pack(side="left")
        self.combo = ttk.Combobox(barra, textvariable=self._pid_var, width=48, state="readonly")
        self.combo.pack(side="left", padx=8)
        ttk.Button(barra, text="Actualizar lista", command=self.cargar_procesos).pack(side="left", padx=4)
        ttk.Button(barra, text="Analizar proceso", style="Accent.TButton", command=self.analizar_elegido).pack(
            side="left", padx=8
        )
        ttk.Button(barra, text="Este Python", command=self.analizar_actual).pack(side="left")
        ttk.Button(barra, text="Proceso de prueba", command=self.lanzar_demo).pack(side="left", padx=4)
        ttk.Button(barra, text="Guardar txt", command=self.guardar_evidencia).pack(side="left")

        ttk.Label(barra, text="Filtro:").pack(side="left", padx=(18, 4))
        filtro = ttk.Combobox(
            barra,
            textvariable=self._filtro,
            width=22,
            state="readonly",
            values=("Todas", "Código", "Pila", "Montículo", "Bibliotecas", "Otras"),
        )
        filtro.pack(side="left")
        filtro.bind("<<ComboboxSelected>>", lambda _e: self._pintar_tabla())

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.tab_mapa = ttk.Frame(nb)
        self.tab_clave = ttk.Frame(nb)
        self.tab_exp = ttk.Frame(nb)
        self.tab_teoria = ttk.Frame(nb)
        nb.add(self.tab_mapa, text="  Mapa de memoria  ")
        nb.add(self.tab_clave, text="  Direcciones clave  ")
        nb.add(self.tab_exp, text="  Experimentos  ")
        nb.add(self.tab_teoria, text="  Notas  ")

        self._construir_mapa()
        self._construir_clave()
        self._construir_experimentos()
        self._construir_teoria()

        pie = ttk.Label(self, textvariable=self._estado, style="Estado.TLabel", anchor="w", padding=6)
        pie.pack(fill="x")

    def _construir_mapa(self) -> None:
        cols = ("base", "fin", "tamano", "estado", "prot", "tipo", "clase", "detalle")
        self.tree = ttk.Treeview(self.tab_mapa, columns=cols, show="headings", selectmode="browse")
        headings = {
            "base": ("Inicio", 150),
            "fin": ("Fin", 150),
            "tamano": ("Tamaño", 90),
            "estado": ("Estado", 80),
            "prot": ("Protección", 130),
            "tipo": ("Tipo", 90),
            "clase": ("Clasificación", 180),
            "detalle": ("Detalle", 320),
        }
        for cid, (titulo, ancho) in headings.items():
            self.tree.heading(cid, text=titulo)
            self.tree.column(cid, width=ancho, anchor="w")
        ys = ttk.Scrollbar(self.tab_mapa, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(self.tab_mapa, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.tab_mapa.rowconfigure(0, weight=1)
        self.tab_mapa.columnconfigure(0, weight=1)
        self.tree.tag_configure("Código", background="#fde68a")
        self.tree.tag_configure("Pila", background="#bbf7d0")
        self.tree.tag_configure("Montículo", background="#bfdbfe")
        self.tree.tag_configure("Biblioteca", background="#e9d5ff")

    def _construir_clave(self) -> None:
        intro = ttk.Label(
            self.tab_clave,
            text="Acá salen las cuatro cosas que pide el taller. El botón de guardar txt deja el listado en un archivo.",
            wraplength=1100,
        )
        intro.pack(anchor="w", padx=8, pady=8)
        grid = ttk.Frame(self.tab_clave)
        grid.pack(fill="both", expand=True, padx=8, pady=4)
        self.textos_clave: dict[str, scrolledtext.ScrolledText] = {}
        titulos = [
            ("código", "1. Código"),
            ("pila", "2. Pila"),
            ("montículo", "3. Montículo (heap)"),
            ("bibliotecas", "4. Bibliotecas (DLL)"),
        ]
        for i, (clave, titulo) in enumerate(titulos):
            marco = ttk.LabelFrame(grid, text=titulo)
            marco.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            txt = scrolledtext.ScrolledText(marco, height=12, font=("Consolas", 9), wrap="word")
            txt.pack(fill="both", expand=True)
            self.textos_clave[clave] = txt
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def _construir_experimentos(self) -> None:
        izq = ttk.Frame(self.tab_exp)
        izq.pack(side="left", fill="y", padx=10, pady=10)
        der = ttk.Frame(self.tab_exp)
        der.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(izq, text="Este proceso", font=("Segoe UI Semibold", 11)).pack(anchor="w", pady=(0, 6))
        ttk.Button(izq, text="1. Pedir memoria en el heap", command=self.exp_malloc).pack(fill="x", pady=3)
        ttk.Button(izq, text="2. Escribir en el heap", command=self.exp_escribir_heap).pack(fill="x", pady=3)
        ttk.Button(izq, text="3. Ver protección del código", command=self.exp_escribir_codigo).pack(fill="x", pady=3)
        ttk.Button(izq, text="4. Página de solo lectura", command=self.exp_proteccion).pack(fill="x", pady=3)

        ttk.Separator(izq, orient="horizontal").pack(fill="x", pady=14)
        ttk.Label(izq, text="Otro proceso", font=("Segoe UI Semibold", 11)).pack(anchor="w")
        ttk.Label(
            izq,
            text="El 5 es el proceso System, casi nunca\n"
            "deja abrirlo. El 6 mira explorer, solo\n"
            "para ver el mapa, no le escribe nada.",
            justify="left",
        ).pack(anchor="w", pady=6)
        ttk.Button(izq, text="5. Intentar abrir System (PID 4)", command=self.exp_proceso_sistema).pack(
            fill="x", pady=3
        )
        ttk.Button(izq, text="6. Ver mapa de explorer.exe", command=self.exp_explorer).pack(
            fill="x", pady=3
        )

        ttk.Label(der, text="Salida", font=("Segoe UI Semibold", 11)).pack(anchor="w")
        self.log = scrolledtext.ScrolledText(der, font=("Consolas", 10), wrap="word", bg="#0f172a", fg="#e2e8f0")
        self.log.pack(fill="both", expand=True, pady=(6, 0))
        self.log.tag_configure("ok", foreground="#86efac")
        self.log.tag_configure("fail", foreground="#fca5a5")
        self.log.tag_configure("info", foreground="#93c5fd")
        self._heap_addr = None
        self._heap_buf = None
        self._pagina_demo = 0
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _construir_teoria(self) -> None:
        ttk.Label(self.tab_teoria, text=RESUMEN_CORTO, wraplength=1180, font=("Segoe UI", 10)).pack(
            anchor="w", padx=10, pady=8
        )
        txt = scrolledtext.ScrolledText(self.tab_teoria, font=("Consolas", 10), wrap="word")
        txt.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        txt.insert("1.0", TEORIA.strip())
        txt.configure(state="disabled")

    def _log(self, msg: str, tag: str = "info") -> None:
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")

    def cargar_procesos(self) -> None:
        self.procesos = listar_procesos()
        valores = [f"{pid:>6}   {nombre}" for pid, nombre in self.procesos]
        self.combo["values"] = valores
        actual = os.getpid()
        for i, (pid, _) in enumerate(self.procesos):
            if pid == actual:
                self.combo.current(i)
                break
        self._estado.set(f"{len(self.procesos)} procesos visibles.")

    def _pid_elegido(self) -> tuple[int, str] | None:
        idx = self.combo.current()
        if idx < 0 or idx >= len(self.procesos):
            return None
        return self.procesos[idx]

    def analizar_actual(self) -> None:
        self._analizar(os.getpid(), "python.exe")

    def analizar_elegido(self) -> None:
        sel = self._pid_elegido()
        if not sel:
            messagebox.showinfo("Proceso", "Elige un proceso de la lista.")
            return
        self._analizar(*sel)

    def _analizar(self, pid: int, nombre: str) -> None:
        self._estado.set(f"Inspeccionando PID {pid}…")
        self.update_idletasks()

        def trabajo() -> None:
            mapa = inspeccionar(pid, nombre)
            self.after(0, lambda: self._aplicar_mapa(mapa))

        threading.Thread(target=trabajo, daemon=True).start()

    def _aplicar_mapa(self, mapa) -> None:
        self.mapa = mapa
        if mapa.error:
            self._estado.set(mapa.error)
            messagebox.showwarning("Acceso denegado", mapa.error)
            return
        self._pintar_tabla()
        self._pintar_clave()
        self._estado.set(
            f"{mapa.nombre}  PID {mapa.pid}  ·  {len(mapa.regiones)} regiones  ·  "
            f"{len(mapa.modulos)} módulos  ·  {len(mapa.pilas)} pilas  ·  {len(mapa.monticulos)} heaps"
        )

    def _pintar_tabla(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if not self.mapa:
            return
        filtro = self._filtro.get()
        for r in self.mapa.regiones:
            if filtro == "Código" and r.clasificacion != "Código":
                continue
            if filtro == "Pila" and r.clasificacion != "Pila":
                continue
            if filtro == "Montículo" and not r.clasificacion.startswith("Montículo"):
                continue
            if filtro == "Bibliotecas" and not r.clasificacion.startswith("Biblioteca"):
                continue
            if filtro == "Otras" and (
                r.clasificacion in {"Código", "Pila"}
                or r.clasificacion.startswith("Montículo")
                or r.clasificacion.startswith("Biblioteca")
            ):
                continue
            tag = r.clasificacion.split()[0]
            self.tree.insert(
                "",
                "end",
                values=(
                    fmt_addr(r.base),
                    fmt_addr(r.fin),
                    fmt_size(r.tamano),
                    r.estado,
                    r.proteccion,
                    r.tipo,
                    r.clasificacion,
                    r.detalle,
                ),
                tags=(tag,),
            )

    def _pintar_clave(self) -> None:
        datos = resumen_secciones(self.mapa)
        for clave, widget in self.textos_clave.items():
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            lineas = datos.get(clave) or ["(sin datos: el proceso puede estar protegido)"]
            widget.insert("1.0", "\n".join(lineas))
            widget.configure(state="disabled")

    def exp_malloc(self) -> None:
        bloque = (ctypes.c_char * 4096)()
        self._heap_addr = ctypes.addressof(bloque)
        self._heap_buf = bloque
        self._log(
            f"Heap: pedí 4096 bytes y salió en {fmt_addr(self._heap_addr)}",
            "ok",
        )

    def exp_escribir_heap(self) -> None:
        if not self._heap_addr:
            self.exp_malloc()
        ok, msg = intentar_escribir(os.getpid(), self._heap_addr, b"TALLER-SO")
        self._log(f"Escribir en el heap: {msg}", "ok" if ok else "fail")
        ok_r, data = leer_memoria(os.getpid(), self._heap_addr, 9)
        if ok_r and isinstance(data, bytes):
            self._log(f"Leí de vuelta: {data!r}", "ok")

    def exp_escribir_codigo(self) -> None:
        if not self.mapa or not self.mapa.modulos:
            self.analizar_actual()
            messagebox.showinfo("Código", "Primero se analiza el proceso; pulsa de nuevo el botón.")
            return
        destino = None
        prot = "desconocida"
        for r in self.mapa.regiones:
            if r.clasificacion == "Código" and r.estado == "Commit":
                destino = r.base
                prot = r.proteccion
                break
        if destino is None:
            destino = self.mapa.modulos[0].base
        self._log(
            f"El código está en {fmt_addr(destino)}, protección {prot}.",
            "info",
        )
        self._log(
            "Esas páginas casi siempre son RX. Si uno intenta escribir ahí a lo bruto, Windows lo tira.",
            "fail",
        )
        self._log(
            "No le voy a escribir al .exe. El punto 4 prueba lo mismo con una página mía de solo lectura.",
            "info",
        )

    def exp_proteccion(self) -> None:
        if self._pagina_demo:
            liberar_pagina(self._pagina_demo)
        self._pagina_demo = asignar_pagina(PAGE_READONLY)
        if not self._pagina_demo:
            self._log("No pude reservar la página.", "fail")
            return
        self._log(f"Página de solo lectura en {fmt_addr(self._pagina_demo)}", "info")
        ok, msg = intentar_escribir(os.getpid(), self._pagina_demo, b"NO")
        self._log(f"Intenté escribir (R): {msg}", "ok" if ok else "fail")
        ok_p, msg_p = cambiar_proteccion(self._pagina_demo, PAGE_READWRITE)
        self._log(f"Cambié protección a RW: {msg_p}", "ok" if ok_p else "fail")
        ok2, msg2 = intentar_escribir(os.getpid(), self._pagina_demo, b"SI")
        self._log(f"Volví a escribir: {msg2}", "ok" if ok2 else "fail")
        self._log(
            "O sea: yo sí le puedo cambiar los permisos a una página mía. Eso no mueve la dirección.",
            "info",
        )

    def exp_proceso_sistema(self) -> None:
        mapa = inspeccionar(4, "System")
        if mapa.error:
            self._log(f"PID 4 (System): no me dejó. {mapa.error}", "fail")
            self._log(
                "Tiene sentido, ese proceso está protegido. Sin permiso no veo nada de él.",
                "info",
            )
            return
        self._log("Raro, System sí se dejó abrir.", "ok")

    def exp_explorer(self) -> None:
        self.cargar_procesos()
        objetivo = next((p for p in self.procesos if p[1].lower() == "explorer.exe"), None)
        if not objetivo:
            self._log("No está explorer.exe corriendo.", "fail")
            return
        pid, nombre = objetivo
        mapa = inspeccionar(pid, nombre)
        if mapa.error:
            self._log(f"explorer PID {pid}: {mapa.error}", "fail")
            return
        r = resumen_secciones(mapa)
        self._log(f"explorer.exe PID {pid} (solo miré, no escribí):", "ok")
        if r["código"]:
            self._log("  código: " + r["código"][0], "ok")
        if r["pila"]:
            self._log("  pila:   " + r["pila"][0], "ok")
        if r["montículo"]:
            self._log("  heap:   " + r["montículo"][0], "ok")
        if r["bibliotecas"]:
            self._log(f"  dll:    {len(r['bibliotecas'])} (ej. {r['bibliotecas'][0]})", "ok")
        self._log(
            "Desde afuera sí se puede ver el mapa si Windows deja. Ver no es modificar.",
            "info",
        )

    def lanzar_demo(self) -> None:
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proceso_demo.py")
        subprocess.Popen(
            [sys.executable, ruta],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
        self._estado.set("Se abrió el proceso de prueba. Actualiza la lista y míralo por el PID.")

    def guardar_evidencia(self) -> None:
        if not self.mapa or self.mapa.error:
            messagebox.showinfo("Guardar", "Primero analiza un proceso.")
            return
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencia_ejecucion.txt")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(texto_evidencia(self.mapa))
        self._estado.set(f"Quedó en {ruta}")
        messagebox.showinfo("Guardar", f"Listo:\n{ruta}")

    def _al_cerrar(self) -> None:
        if self._pagina_demo:
            liberar_pagina(self._pagina_demo)
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
