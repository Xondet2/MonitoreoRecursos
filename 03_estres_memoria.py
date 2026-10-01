#!/usr/bin/env python3
"""
Estrés de Memoria y Salto a la Virtual (Paginación)
====================================================
Concepto: Memoria Virtual y Archivo de Paginación (Swap).
Objetivo: Forzar al SO a usar memoria virtual (swap) creando objetos masivos.
Reto: Observar cómo crece la memoria virtual cuando la RAM física se agota.
Advertencia: Límite de seguridad implementado para no bloquear la máquina.

Cómo observarlo:
  - Linux:  htop / top / free -h  (columna SWAP)
  - Windows: Administrador de tareas → Rendimiento → Memoria → "Comprometida"
  - Mac:    Activity Monitor → Memoria → "Memoria utilizada / Swap usada"
"""

import psutil
import time
import sys
import os
import gc
from datetime import datetime

LIMITE_SEGURIDAD_RAM_PORCENTAJE = 90.0
LIMITE_SEGURIDAD_SWAP_PORCENTAJE = 70.0
CADENA_BASE = "📦 BloqueDeDatos_"
TAMANO_STRING_BASE = 10000
MUESTRAS_POR_LOTE = 50000
PAUSA_ENTRE_LOTES_SEG = 0.02


def imprimir_estado_memoria(lista, contador_elementos, inicio):
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    process = psutil.Process(os.getpid())
    proc_rss = process.memory_info().rss / (1024 ** 3)
    proc_vms = process.memory_info().vms / (1024 ** 3)

    sys.stdout.write("\033[2J\033[H")
    print("=" * 78)
    print("  🧠 ESTRÉS DE MEMORIA — PAGINACIÓN / SWAP (Memoria Virtual)")
    print("=" * 78)
    print(f"  PID del proceso     : {os.getpid()}")
    print(f"  Tiempo ejecución    : {time.time() - inicio:.1f} s")
    print(f"  Elementos en lista  : {contador_elementos:,}  ({contador_elementos / 1_000_000:.2f} M)")
    lista_tam = sum(sys.getsizeof(s) for s in lista) / (1024 ** 3)
    print(f"  Tamaño lista (aprox): {lista_tam:.2f} GB  (Strings de ~{TAMANO_STRING_BASE} chars)")
    print("-" * 78)
    print(f"  {'RECURSO':<20} {'USO':<18} {'LIBRE':<18} {'%':<10}")
    print("-" * 78)

    ram_color = "\033[91m" if mem.percent >= LIMITE_SEGURIDAD_RAM_PORCENTAJE - 10 else "\033[92m"
    swap_color = "\033[93m" if swap.percent > 10 else "\033[92m"
    proc_color = "\033[95m"
    reset = "\033[0m"

    print(f"  {'RAM Física':<20} {ram_color}{mem.used/(1024**3):>7.2f} GB{reset:<11} "
          f"{mem.available/(1024**3):>7.2f} GB / {mem.total/(1024**3):.1f}G  "
          f"{ram_color}{mem.percent:>5.1f}%{reset}")
    print(f"  {'SWAP / Virtual':<20} {swap_color}{swap.used/(1024**3):>7.2f} GB{reset:<11} "
          f"{swap.free/(1024**3):>7.2f} GB / {swap.total/(1024**3):.1f}G  "
          f"{swap_color}{swap.percent:>5.1f}%{reset}")
    print(f"  {'Proceso actual':<20} {proc_color}RSS:{proc_rss:.2f}G VMS:{proc_vms:.2f}G{reset}")
    print("-" * 78)
    print(f"  🛑 Límite seguridad : RAM > {LIMITE_SEGURIDAD_RAM_PORCENTAJE:.0f}%  |  SWAP > {LIMITE_SEGURIDAD_SWAP_PORCENTAJE:.0f}%")
    print("     (Presiona Ctrl+C en cualquier momento para liberar y salir)")
    print("=" * 78)

    return mem.percent, swap.percent


def verificar_limites_seguridad(ram_pct, swap_pct, razones_parada):
    if ram_pct >= LIMITE_SEGURIDAD_RAM_PORCENTAJE:
        razones_parada.append(f"RAM física al {ram_pct:.1f}% (límite {LIMITE_SEGURIDAD_RAM_PORCENTAJE:.0f}%)")
        return True, razones_parada
    if swap_pct >= LIMITE_SEGURIDAD_SWAP_PORCENTAJE:
        razones_parada.append(f"Swap / Virtual al {swap_pct:.1f}% (límite {LIMITE_SEGURIDAD_SWAP_PORCENTAJE:.0f}%)")
        return True, razones_parada
    return False, razones_parada


def generar_lote_strings(lote_id, cuantos):
    """
    Genera strings únicos y relativamente grandes.
    Cada string ocupa ~TAMANO_STRING_BASE * 4 bytes en memoria (Unicode).
    Alrededor de ~40KB por string → ~2GB por lote de 50k strings.
    """
    lote = []
    base = f"[{lote_id:08d}]_" + CADENA_BASE
    for i in range(cuantos):
        s = base + f"{i:07d}_" + ("x" * (TAMANO_STRING_BASE - len(base) - 8))
        lote.append(s)
    return lote


def menu_inicial():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    print("=" * 78)
    print("  ⚠️  ADVERTENCIA DE SEGURIDAD")
    print("=" * 78)
    print(f"  Este script llenará la RAM con millones de strings hasta alcanzar")
    print(f"  el {LIMITE_SEGURIDAD_RAM_PORCENTAJE:.0f}% de uso, forzando al Sistema Operativo a")
    print(f"  recurrir al archivo de paginación (SWAP / Memoria Virtual).")
    print()
    print(f"  Tu sistema:")
    print(f"    · RAM Física : {mem.total / (1024**3):.1f} GB (actual: {mem.percent:.1f}%)")
    print(f"    · SWAP / Virt: {swap.total / (1024**3):.1f} GB (actual: {swap.percent:.1f}%)")
    print()
    print(f"  🛡️  Límites de seguridad ACTIVOS (auto-detención):")
    print(f"    · Detener si RAM  > {LIMITE_SEGURIDAD_RAM_PORCENTAJE:.0f}%")
    print(f"    · Detener si SWAP > {LIMITE_SEGURIDAD_SWAP_PORCENTAJE:.0f}%")
    print("=" * 78)
    try:
        r = input("\n  ➤ ¿Iniciar prueba de estrés? [S/n]: ").strip().lower()
        if r not in ("", "s", "si", "y", "yes"):
            print("  Cancelado por el usuario.")
            return False
    except EOFError:
        return True
    return True


def main():
    if not menu_inicial():
        return

    print("\n  ⏳ Preparando entorno... ")
    gc.collect()
    gc.disable()

    lista_masiva = []
    contador_total = 0
    lote_id = 0
    inicio = time.time()
    razones_parada = []
    swap_previo = psutil.swap_memory().used

    print("\n" + " 🚀 Iniciando llenado masivo de memoria...")
    print("    (Sugerencia: abre otra terminal y ejecuta:  watch -n1 'free -h')")
    time.sleep(2)

    try:
        while True:
            lote = generar_lote_strings(lote_id, MUESTRAS_POR_LOTE)
            lista_masiva.extend(lote)
            contador_total += len(lote)
            lote_id += 1

            if lote_id % 2 == 0:
                ram_pct, swap_pct = imprimir_estado_memoria(
                    lista_masiva, contador_total, inicio
                )
                swap_actual = psutil.swap_memory().used
                if swap_actual > swap_previo + (50 * 1024 * 1024):
                    print("  🌀 ⚡ PAGINACIÓN DETECTADA: SWAP creció > 50MB en el último lote!")
                    swap_previo = swap_actual

                detener, razones_parada = verificar_limites_seguridad(
                    ram_pct, swap_pct, razones_parada
                )
                if detener:
                    break

            time.sleep(PAUSA_ENTRE_LOTES_SEG)

    except KeyboardInterrupt:
        print("\n\n  🛑 Interrumpido manualmente por el usuario.")
        razones_parada.append("Interrupción manual (Ctrl+C)")

    gc.enable()
    print("\n" + "=" * 78)
    print("  📊 RESUMEN DE LA PRUEBA")
    print("=" * 78)
    print(f"  Tiempo total        : {time.time() - inicio:.1f} segundos")
    print(f"  Elementos creados   : {contador_total:,}")
    print(f"  Motivo detención    : {', '.join(razones_parada) if razones_parada else 'Desconocido'}")
    mem_final = psutil.virtual_memory()
    swap_final = psutil.swap_memory()
    print(f"  RAM final           : {mem_final.percent:.1f}%  ({mem_final.used/(1024**3):.2f} GB)")
    print(f"  SWAP final          : {swap_final.percent:.1f}%  ({swap_final.used/(1024**3):.2f} GB)")
    print("=" * 78)

    print("\n  🧹 Liberando memoria de forma segura...")
    del lista_masiva
    gc.collect()
    mem_liberada = psutil.virtual_memory()
    print(f"  RAM tras liberar    : {mem_liberada.percent:.1f}%  "
          f"(diferencia: {(mem_final.used - mem_liberada.used) / (1024**3):.2f} GB liberados)")
    print("\n  ✅ Prueba finalizada correctamente.")
    print()
    print("  📚 Conceptos del SO ilustrados:")
    print("    1. Memoria Física (RAM) → Almacenamiento volátil de alta velocidad.")
    print("    2. Memoria Virtual (SWAP/Paging file) → Extensión en disco para cuando")
    print("       la RAM se llena; el SO mueve páginas de RAM poco usadas al disco.")
    print("    3. Thrashing → Si el SWAP crece mucho, el sistema se vuelve lento")
    print("       porque está constantemente moviendo datos entre RAM y disco.")


if __name__ == "__main__":
    main()
