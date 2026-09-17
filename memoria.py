"""Inspección del espacio de direcciones virtuales en Windows."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from dataclasses import dataclass, field

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll", use_last_error=True)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
THREAD_QUERY_INFORMATION = 0x0040

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_FREE = 0x10000
MEM_PRIVATE = 0x20000
MEM_MAPPED = 0x40000
MEM_IMAGE = 0x1000000
MEM_RELEASE = 0x8000

PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100

TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPHEAPLIST = 0x00000001
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
LIST_MODULES_ALL = 0x03
ThreadBasicInformation = 0
MAX_PATH = 260
USER_SPACE_LIMIT = 0x00007FFFFFFFFFFF
_BLOQUE_HEAP = None


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_uint64),
        ("AllocationBase", ctypes.c_uint64),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_uint64),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", wintypes.DWORD),
        ("EntryPoint", ctypes.c_void_p),
    ]


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * MAX_PATH),
    ]


class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", ctypes.c_long),
        ("tpDeltaPri", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
    ]


class HEAPLIST32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_size_t),
        ("th32ProcessID", wintypes.DWORD),
        ("th32HeapID", ctypes.c_ulonglong),
        ("dwFlags", wintypes.DWORD),
    ]


class CLIENT_ID(ctypes.Structure):
    _fields_ = [
        ("UniqueProcess", ctypes.c_void_p),
        ("UniqueThread", ctypes.c_void_p),
    ]


class THREAD_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("ExitStatus", ctypes.c_long),
        ("TebBaseAddress", ctypes.c_void_p),
        ("ClientId", CLIENT_ID),
        ("AffinityMask", ctypes.c_uint64),
        ("Priority", ctypes.c_long),
        ("BasePriority", ctypes.c_long),
    ]


class NT_TIB_PARTIAL(ctypes.Structure):
    _fields_ = [
        ("ExceptionList", ctypes.c_void_p),
        ("StackBase", ctypes.c_void_p),
        ("StackLimit", ctypes.c_void_p),
    ]


kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.VirtualQueryEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
kernel32.VirtualQueryEx.restype = ctypes.c_size_t
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.WriteProcessMemory.restype = wintypes.BOOL
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentThreadStackLimits.argtypes = [
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_uint64),
]
kernel32.GetCurrentThreadStackLimits.restype = None
kernel32.GetProcessHeaps.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
kernel32.GetProcessHeaps.restype = wintypes.DWORD
kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL
kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
kernel32.Thread32First.restype = wintypes.BOOL
kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
kernel32.Thread32Next.restype = wintypes.BOOL
kernel32.Heap32ListFirst.argtypes = [wintypes.HANDLE, ctypes.POINTER(HEAPLIST32)]
kernel32.Heap32ListFirst.restype = wintypes.BOOL
kernel32.Heap32ListNext.argtypes = [wintypes.HANDLE, ctypes.POINTER(HEAPLIST32)]
kernel32.Heap32ListNext.restype = wintypes.BOOL
kernel32.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenThread.restype = wintypes.HANDLE
kernel32.VirtualAlloc.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    wintypes.DWORD,
    wintypes.DWORD,
]
kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD]
kernel32.VirtualFree.restype = wintypes.BOOL
kernel32.VirtualProtect.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.VirtualProtect.restype = wintypes.BOOL

psapi.EnumProcessModulesEx.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.HMODULE),
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.DWORD,
]
psapi.EnumProcessModulesEx.restype = wintypes.BOOL
psapi.GetModuleFileNameExW.argtypes = [
    wintypes.HANDLE,
    wintypes.HMODULE,
    wintypes.LPWSTR,
    wintypes.DWORD,
]
psapi.GetModuleFileNameExW.restype = wintypes.DWORD
psapi.GetModuleInformation.argtypes = [
    wintypes.HANDLE,
    wintypes.HMODULE,
    ctypes.POINTER(MODULEINFO),
    wintypes.DWORD,
]
psapi.GetModuleInformation.restype = wintypes.BOOL

ntdll.NtQueryInformationThread.argtypes = [
    wintypes.HANDLE,
    ctypes.c_int,
    ctypes.c_void_p,
    wintypes.ULONG,
    ctypes.POINTER(wintypes.ULONG),
]
ntdll.NtQueryInformationThread.restype = ctypes.c_long


@dataclass
class Modulo:
    nombre: str
    ruta: str
    base: int
    tamano: int
    entrada: int
    principal: bool = False


@dataclass
class Pila:
    tid: int
    limite_bajo: int
    limite_alto: int


@dataclass
class Monticulo:
    identificador: int
    base: int


@dataclass
class Region:
    base: int
    fin: int
    tamano: int
    estado: str
    proteccion: str
    tipo: str
    clasificacion: str
    detalle: str
    protect_raw: int
    type_raw: int
    state_raw: int


@dataclass
class MapaProceso:
    pid: int
    nombre: str
    regiones: list[Region] = field(default_factory=list)
    modulos: list[Modulo] = field(default_factory=list)
    pilas: list[Pila] = field(default_factory=list)
    monticulos: list[Monticulo] = field(default_factory=list)
    error: str = ""


def _ptr(value) -> int:
    if value is None:
        return 0
    return int(value)


def fmt_addr(addr: int) -> str:
    return f"0x{addr:016X}"


def fmt_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def proteccion_texto(protect: int) -> str:
    mask = protect & 0xFF
    if mask == 0:
        return "—"
    nombres = {
        PAGE_NOACCESS: "Sin acceso",
        PAGE_READONLY: "R",
        PAGE_READWRITE: "RW",
        PAGE_WRITECOPY: "Copy-on-write",
        PAGE_EXECUTE: "X",
        PAGE_EXECUTE_READ: "RX",
        PAGE_EXECUTE_READWRITE: "RWX",
        PAGE_EXECUTE_WRITECOPY: "RX copy-on-write",
    }
    flags = [nombres.get(mask, f"0x{mask:02X}")]
    if protect & PAGE_GUARD:
        flags.append("GUARD")
    return " | ".join(flags)


def estado_texto(state: int) -> str:
    return {
        MEM_COMMIT: "Commit",
        MEM_RESERVE: "Reserve",
        MEM_FREE: "Libre",
    }.get(state, f"0x{state:X}")


def tipo_texto(mem_type: int) -> str:
    return {
        MEM_IMAGE: "Imagen",
        MEM_MAPPED: "Mapped",
        MEM_PRIVATE: "Privada",
        0: "-",
    }.get(mem_type, f"0x{mem_type:X}")


def es_ejecutable(protect: int) -> bool:
    return bool(protect & (PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))


def es_escribible(protect: int) -> bool:
    return bool(protect & (PAGE_READWRITE | PAGE_EXECUTE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_WRITECOPY))


def last_error() -> str:
    code = ctypes.get_last_error()
    return f"Win32 error {code}"


def abrir_proceso(pid: int) -> wintypes.HANDLE:
    access = (
        PROCESS_QUERY_INFORMATION
        | PROCESS_QUERY_LIMITED_INFORMATION
        | PROCESS_VM_READ
    )
    handle = kernel32.OpenProcess(access, False, pid)
    if handle:
        return handle
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, False, pid)
    if handle:
        return handle
    raise OSError(f"No se pudo abrir el PID {pid}. {last_error()}. "
                  "Algunos procesos del sistema requieren privilegios de administrador.")


def listar_procesos() -> list[tuple[int, str]]:
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE:
        return [(os.getpid(), "python.exe")]
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    procesos = []
    ok = kernel32.Process32FirstW(snap, ctypes.byref(entry))
    while ok:
        procesos.append((int(entry.th32ProcessID), entry.szExeFile))
        ok = kernel32.Process32NextW(snap, ctypes.byref(entry))
    kernel32.CloseHandle(snap)
    procesos.sort(key=lambda item: item[1].lower())
    return procesos


def enumerar_modulos(handle, pid: int) -> list[Modulo]:
    needed = wintypes.DWORD()
    if not psapi.EnumProcessModulesEx(handle, None, 0, ctypes.byref(needed), LIST_MODULES_ALL):
        return []
    count = max(needed.value // ctypes.sizeof(wintypes.HMODULE), 1)
    arr = (wintypes.HMODULE * count)()
    if not psapi.EnumProcessModulesEx(
        handle, arr, ctypes.sizeof(arr), ctypes.byref(needed), LIST_MODULES_ALL
    ):
        return []
    reales = needed.value // ctypes.sizeof(wintypes.HMODULE)
    modulos = []
    for i in range(reales):
        hmod = arr[i]
        buf = ctypes.create_unicode_buffer(MAX_PATH * 4)
        psapi.GetModuleFileNameExW(handle, hmod, buf, len(buf))
        info = MODULEINFO()
        if not psapi.GetModuleInformation(handle, hmod, ctypes.byref(info), ctypes.sizeof(info)):
            continue
        ruta = buf.value
        nombre = os.path.basename(ruta) if ruta else f"modulo_{i}"
        modulos.append(
            Modulo(
                nombre=nombre,
                ruta=ruta,
                base=_ptr(info.lpBaseOfDll),
                tamano=int(info.SizeOfImage),
                entrada=_ptr(info.EntryPoint),
                principal=(i == 0),
            )
        )
    return modulos


def enumerar_pilas(handle, pid: int) -> list[Pila]:
    pilas: list[Pila] = []
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snap != INVALID_HANDLE_VALUE:
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(THREADENTRY32)
        ok = kernel32.Thread32First(snap, ctypes.byref(entry))
        while ok:
            if entry.th32OwnerProcessID == pid:
                pila = _pila_desde_teb(handle, int(entry.th32ThreadID))
                if pila:
                    pilas.append(pila)
            ok = kernel32.Thread32Next(snap, ctypes.byref(entry))
        kernel32.CloseHandle(snap)
    if not pilas and pid == os.getpid():
        low = ctypes.c_uint64()
        high = ctypes.c_uint64()
        try:
            kernel32.GetCurrentThreadStackLimits(ctypes.byref(low), ctypes.byref(high))
            pilas.append(Pila(tid=0, limite_bajo=low.value, limite_alto=high.value))
        except Exception:
            pass
    return pilas


def _pila_desde_teb(handle, tid: int) -> Pila | None:
    th = kernel32.OpenThread(THREAD_QUERY_INFORMATION, False, tid)
    if not th:
        return None
    try:
        tbi = THREAD_BASIC_INFORMATION()
        status = ntdll.NtQueryInformationThread(
            th, ThreadBasicInformation, ctypes.byref(tbi), ctypes.sizeof(tbi), None
        )
        if status != 0 or not tbi.TebBaseAddress:
            return None
        tib = NT_TIB_PARTIAL()
        leidos = ctypes.c_size_t()
        if not kernel32.ReadProcessMemory(
            handle,
            tbi.TebBaseAddress,
            ctypes.byref(tib),
            ctypes.sizeof(tib),
            ctypes.byref(leidos),
        ):
            return None
        bajo = _ptr(tib.StackLimit)
        alto = _ptr(tib.StackBase)
        if bajo and alto and alto > bajo:
            return Pila(tid=tid, limite_bajo=bajo, limite_alto=alto)
    finally:
        kernel32.CloseHandle(th)
    return None


def enumerar_monticulos(pid: int) -> list[Monticulo]:
    monticulos: list[Monticulo] = []
    if pid == os.getpid():
        n = kernel32.GetProcessHeaps(0, None)
        if n:
            arr = (wintypes.HANDLE * n)()
            got = kernel32.GetProcessHeaps(n, arr)
            for i in range(got):
                base = _ptr(arr[i])
                monticulos.append(Monticulo(identificador=i, base=base))
        return monticulos

    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPHEAPLIST, pid)
    if snap == INVALID_HANDLE_VALUE:
        return monticulos
    entry = HEAPLIST32()
    entry.dwSize = ctypes.sizeof(HEAPLIST32)
    ok = kernel32.Heap32ListFirst(snap, ctypes.byref(entry))
    i = 0
    while ok:
        monticulos.append(Monticulo(identificador=i, base=int(entry.th32HeapID)))
        i += 1
        ok = kernel32.Heap32ListNext(snap, ctypes.byref(entry))
    kernel32.CloseHandle(snap)
    return monticulos


def _solapa(inicio: int, fin: int, a: int, b: int) -> bool:
    return inicio < b and a < fin


def clasificar(region_base: int, region_fin: int, protect: int, mem_type: int,
               modulos: list[Modulo], pilas: list[Pila], monticulos: list[Monticulo]) -> tuple[str, str]:
    for mod in modulos:
        if _solapa(region_base, region_fin, mod.base, mod.base + mod.tamano):
            if mod.principal:
                if es_ejecutable(protect):
                    return "Código", mod.nombre
                return "Datos del ejecutable", mod.nombre
            if es_ejecutable(protect):
                return "Biblioteca (código)", mod.nombre
            return "Biblioteca (datos)", mod.nombre

    for pila in pilas:
        if _solapa(region_base, region_fin, pila.limite_bajo, pila.limite_alto):
            tid = pila.tid if pila.tid else "actual"
            return "Pila", f"Hilo {tid}"
        # La página GUARD está justo debajo del stack (crece hacia abajo).
        if (protect & PAGE_GUARD) and region_fin == pila.limite_bajo:
            tid = pila.tid if pila.tid else "actual"
            return "Pila", f"Guard page, hilo {tid}"

    for heap in monticulos:
        if heap.base and region_base <= heap.base < region_fin:
            return "Montículo", f"Heap 0x{heap.base:X}"

    if mem_type == MEM_PRIVATE:
        if es_escribible(protect):
            return "Montículo / datos privados", "Reservado por el proceso (heap, runtime, etc.)"
        return "Memoria privada", ""
    if mem_type == MEM_MAPPED:
        return "Archivo proyectado", "Mapped file / sección compartida"
    if mem_type == MEM_IMAGE:
        return "Imagen", "Módulo PE"
    return "Otra", ""


def recorrer_regiones(handle, modulos, pilas, monticulos) -> list[Region]:
    regiones: list[Region] = []
    address = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while address < USER_SPACE_LIMIT:
        got = kernel32.VirtualQueryEx(
            handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)
        )
        if not got:
            break
        base = int(mbi.BaseAddress)
        size = int(mbi.RegionSize)
        if size == 0:
            break
        fin = base + size
        if mbi.State != MEM_FREE:
            clase, detalle = clasificar(base, fin, int(mbi.Protect), int(mbi.Type), modulos, pilas, monticulos)
            regiones.append(
                Region(
                    base=base,
                    fin=fin,
                    tamano=size,
                    estado=estado_texto(int(mbi.State)),
                    proteccion=proteccion_texto(int(mbi.Protect)),
                    tipo=tipo_texto(int(mbi.Type)),
                    clasificacion=clase,
                    detalle=detalle,
                    protect_raw=int(mbi.Protect),
                    type_raw=int(mbi.Type),
                    state_raw=int(mbi.State),
                )
            )
        if fin <= address:
            break
        address = fin
    return regiones


def inspeccionar(pid: int, nombre: str = "") -> MapaProceso:
    mapa = MapaProceso(pid=pid, nombre=nombre or f"PID {pid}")
    handle = None
    try:
        handle = abrir_proceso(pid)
        mapa.modulos = enumerar_modulos(handle, pid)
        mapa.pilas = enumerar_pilas(handle, pid)
        mapa.monticulos = enumerar_monticulos(pid)
        mapa.regiones = recorrer_regiones(handle, mapa.modulos, mapa.pilas, mapa.monticulos)
        if mapa.modulos:
            mapa.nombre = mapa.modulos[0].nombre
    except OSError as exc:
        mapa.error = str(exc)
    finally:
        if handle:
            kernel32.CloseHandle(handle)
    return mapa


def resumen_secciones(mapa: MapaProceso) -> dict[str, list[str]]:
    datos = {
        "código": [],
        "pila": [],
        "montículo": [],
        "bibliotecas": [],
    }
    for mod in mapa.modulos:
        linea = (
            f"{mod.nombre}: {fmt_addr(mod.base)} – {fmt_addr(mod.base + mod.tamano)} "
            f"({fmt_size(mod.tamano)})"
        )
        if mod.principal:
            datos["código"].append(linea + f"  | punto de entrada {fmt_addr(mod.entrada)}")
        else:
            datos["bibliotecas"].append(linea)
    for pila in mapa.pilas:
        tid = pila.tid or "actual"
        datos["pila"].append(
            f"Hilo {tid}: {fmt_addr(pila.limite_bajo)} – {fmt_addr(pila.limite_alto)} "
            f"({fmt_size(pila.limite_alto - pila.limite_bajo)})"
        )
    vistos = set()
    for region in mapa.regiones:
        if region.clasificacion.startswith("Montículo"):
            clave = (region.base, region.tamano)
            if clave in vistos:
                continue
            vistos.add(clave)
            if "GUARD" in region.proteccion:
                continue
            datos["montículo"].append(
                f"{fmt_addr(region.base)} – {fmt_addr(region.fin)} "
                f"({fmt_size(region.tamano)})  {region.proteccion}  {region.detalle}"
            )
    return datos


def direcciones_clasicas() -> dict[str, str]:
    """Cuatro direcciones al estilo del curso: código, pila, malloc y una DLL."""
    global _BLOQUE_HEAP
    if _BLOQUE_HEAP is None:
        ucrt = ctypes.CDLL("ucrtbase")
        ucrt.malloc.restype = ctypes.c_void_p
        ucrt.malloc.argtypes = [ctypes.c_size_t]
        _BLOQUE_HEAP = ucrt.malloc(1024)
    low = ctypes.c_uint64()
    high = ctypes.c_uint64()
    kernel32.GetCurrentThreadStackLimits(ctypes.byref(low), ctypes.byref(high))
    exe = _ptr(kernel32.GetModuleHandleW(None))
    k32 = _ptr(kernel32.GetModuleHandleW("kernel32.dll"))
    ntdll = _ptr(kernel32.GetModuleHandleW("ntdll.dll"))
    return {
        "pid": str(os.getpid()),
        "código": fmt_addr(exe),
        "pila_baja": fmt_addr(low.value),
        "pila_alta": fmt_addr(high.value),
        "montículo": fmt_addr(_ptr(_BLOQUE_HEAP)),
        "kernel32": fmt_addr(k32),
        "ntdll": fmt_addr(ntdll),
    }


def texto_evidencia(mapa: MapaProceso) -> str:
    r = resumen_secciones(mapa)
    lineas = [
        "Direcciones del proceso (son virtuales)",
        f"Proceso: {mapa.nombre}    PID {mapa.pid}",
        "",
        "Un programa normal no ve las físicas; eso lo hace la MMU.",
        "",
        "=== 1. CÓDIGO (imagen del ejecutable) ===",
        *(r["código"] or ["(sin datos)"]),
        "",
        "=== 2. PILA (stack de los hilos) ===",
        *(r["pila"] or ["(sin datos)"]),
        "",
        "=== 3. MONTÍCULO (heap / datos privados RW) ===",
        *(r["montículo"][:12] or ["(sin datos)"]),
        "",
        "=== 4. BIBLIOTECAS (DLL) ===",
        *(r["bibliotecas"][:15] or ["(sin datos)"]),
        "",
        f"Total regiones: {len(mapa.regiones)}   módulos: {len(mapa.modulos)}   "
        f"pilas: {len(mapa.pilas)}",
    ]
    return "\n".join(lineas) + "\n"


def intentar_escribir(pid: int, direccion: int, datos: bytes) -> tuple[bool, str]:
    """Intenta escribir en el proceso actual. Nunca opera sobre un PID ajeno."""
    if pid != os.getpid():
        return False, "El taller no escribe en la memoria de otros procesos."
    handle = kernel32.GetCurrentProcess()
    escritos = ctypes.c_size_t()
    buf = ctypes.create_string_buffer(datos, len(datos))
    ok = kernel32.WriteProcessMemory(
        handle, ctypes.c_void_p(direccion), buf, len(datos), ctypes.byref(escritos)
    )
    if ok:
        return True, f"Se escribieron {escritos.value} byte(s) en {fmt_addr(direccion)}"
    return False, f"La MMU/el kernel rechazaron la escritura. {last_error()}"


def asignar_pagina(proteccion: int) -> int:
    addr = kernel32.VirtualAlloc(None, 4096, MEM_COMMIT | MEM_RESERVE, proteccion)
    return _ptr(addr)


def cambiar_proteccion(direccion: int, proteccion: int) -> tuple[bool, str]:
    antigua = wintypes.DWORD()
    ok = kernel32.VirtualProtect(
        ctypes.c_void_p(direccion), 4096, proteccion, ctypes.byref(antigua)
    )
    if ok:
        return True, f"Nueva protección 0x{proteccion:X} (antes 0x{antigua.value:X})"
    return False, last_error()


def liberar_pagina(direccion: int) -> None:
    if direccion:
        kernel32.VirtualFree(ctypes.c_void_p(direccion), 0, MEM_RELEASE)


def leer_memoria(pid: int, direccion: int, n: int) -> tuple[bool, bytes | str]:
    handle = None
    cerrar = False
    try:
        if pid == os.getpid():
            handle = kernel32.GetCurrentProcess()
        else:
            handle = abrir_proceso(pid)
            cerrar = True
        buf = ctypes.create_string_buffer(n)
        leidos = ctypes.c_size_t()
        ok = kernel32.ReadProcessMemory(
            handle, ctypes.c_void_p(direccion), buf, n, ctypes.byref(leidos)
        )
        if not ok:
            return False, last_error()
        return True, buf.raw[: leidos.value]
    except OSError as exc:
        return False, str(exc)
    finally:
        if cerrar and handle:
            kernel32.CloseHandle(handle)
