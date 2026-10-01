#!/usr/bin/env python3
"""
Prioridad de Procesos (Scheduling)
===================================
Concepto: Planificación de procesos del Kernel.
Objetivo: Demostrar que no todos los procesos son iguales para el SO y que
          podemos influir en su "importancia" (prioridad de scheduling).
Reto: Ejecutar dos instancias del mismo cálculo pesado:
      · Una con prioridad "Baja"
      · Otra con prioridad "Tiempo Real" (máxima posible sin root)
      Comparar cuál termina primero.

Valores de prioridad (nice en Linux/Unix):
   -20  →  MÁXIMA prioridad  (Clase "Tiempo Real" — requiere root)
     0  →  Prioridad normal (default)
   +19  →  MÍNIMA prioridad  (Clase "Baja")

En este script se usan:
   Baja      → nice +15 (seguro, sin permisos especiales)
   TiempoReal→ nice -5  (si falla sin root, se baja a 0 con aviso)
"""

import os
import sys
import time
import subprocess
import argparse
import math
import random
import platform

import psutil


# ================================================================
# CARGA DE TRABAJO: Cálculo matemático pesado y CPU-intensivo
# ================================================================
def carga_pesada_numerica(n=2_500_000):
    """
    Cálculo intensivo en CPU: computa primos, sumas trigonométricas,
    productos de matrices pequeñas y otras operaciones matemáticas.
    Se diseña para ser imposible de optimizar por el compilador JIT/PyPy
    y depender de la prioridad que el kernel le dé al proceso.
    """
    acumulador = 0.0
    cuenta_primos = 0

    for i in range(2, n):
        # 1. Test de primalidad para generar carga de enteros
        es_primo = True
        if i % 2 == 0:
            es_primo = i == 2
        else:
            limite = int(math.isqrt(i)) + 1
            for d in range(3, limite, 2):
                if i % d == 0:
                    es_primo = False
                    break
        if es_primo:
            cuenta_primos += 1

        # 2. Operaciones en coma flotante para usar la FPU
        x = math.sin(i * 0.000123) * math.cos(i * 0.0000456) + math.log(i + 1)
        acumulador += x

        # 3. Cada cierto iter, un mini-producto de vectores
        if i % 50_000 == 0:
            a = [random.random() for _ in range(500)]
            b = [random.random() for _ in range(500)]
            dot = sum(a[j] * b[j] for j in range(500))
            acumulador += dot

    return cuenta_primos, acumulador


# ================================================================
# WORKER: Ejecuta la carga pesada CON una prioridad específica
# ================================================================
def modo_worker(prioridad_nombre: str, nice_valor: int):
    pid = os.getpid()
    proceso = psutil.Process(pid)

    try:
        proceso.nice(nice_valor)
    except (PermissionError, psutil.AccessDenied):
        print(f"  ⚠️  [PID {pid}] Sin permisos para establecer nice={nice_valor}. "
              f"Usando nice={proceso.nice()} (default). Ejecuta con 'sudo' para "
              f"prioridades < 0.", file=sys.stderr)

    nice_efectivo = proceso.nice()
    t_inicio = time.perf_counter()

    print(f"🚀 WORKER INICIADO | PID={pid} | Prioridad='{prioridad_nombre}' | "
          f"nice={nice_efectivo} | Carga≈2.5M iteraciones", flush=True)

    primos, suma = carga_pesada_numerica()

    t_total = time.perf_counter() - t_inicio

    print(f"✅ WORKER FINALIZADO | PID={pid} | Prioridad='{prioridad_nombre}' | "
          f"Duración={t_total:.3f}s | Primos={primos} | Resultado={suma:.4e}",
          flush=True)

    return t_total, primos


# ================================================================
# COORDINADOR: Lanza 2 workers en paralelo y compara resultados
# ================================================================
def modo_coordinador():
    sistema = platform.system()
    print("=" * 78)
    print("  ⚙️  SCHEDULER DEL KERNEL — COMPARACIÓN DE PRIORIDADES DE PROCESOS")
    print("=" * 78)
    print(f"  Plataforma         : {sistema}")
    print(f"  CPU núcleos lógicos: {psutil.cpu_count(logical=True)}")
    print(f"  Frecuencia base    : {getattr(psutil.cpu_freq(), 'max', '?')} MHz")
    print()

    # Ajuste de prioridades según SO
    if sistema == "Linux" or sistema == "Darwin":
        configs = [
            {"nombre": "BAJA",       "nice": 15, "arg": "--baja"},
            {"nombre": "TIEMPO_REAL", "nice": -5, "arg": "--real"},
        ]
    else:
        from psutil import (
            ABOVE_NORMAL_PRIORITY_CLASS, BELOW_NORMAL_PRIORITY_CLASS,
            HIGH_PRIORITY_CLASS, IDLE_PRIORITY_CLASS,
        )
        configs = [
            {"nombre": "BAJA",       "nice": BELOW_NORMAL_PRIORITY_CLASS, "arg": "--baja"},
            {"nombre": "TIEMPO_REAL", "nice": HIGH_PRIORITY_CLASS,         "arg": "--real"},
        ]

    print("  Configuración de prioridades para esta ejecución:")
    for c in configs:
        print(f"    · {c['nombre']:<12} → nice = {c['nice']}")
    print()
    print("  💡 Consejo: ejecuta 'sudo python3 04_prioridad_procesos.py'")
    print("     para que la prioridad Tiempo Real realmente llegue a valores")
    print("     negativos en Linux y la diferencia sea DRAMÁTICA.")
    print("=" * 78)

    # Lanzar ambos workers como procesos hijo independientes
    # (así el scheduler del SO los trata como entidades separadas)
    script_actual = os.path.abspath(__file__)
    workers = []

    for c in configs:
        cmd = [
            sys.executable, script_actual, "worker",
            "--nombre", c["nombre"], "--nice", str(c["nice"])
        ]
        print(f"\n  📤 Lanzando proceso '{c['nombre']}': {' '.join(cmd)}")
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        workers.append({"config": c, "proc": p, "lineas": []})

    print("\n  ⏳ Esperando finalización de ambos procesos...\n")

    resultados = {}
    while workers:
        for w in list(workers):
            linea = w["proc"].stdout.readline()
            if linea:
                print(f"    [{w['config']['nombre']:<11}] {linea.rstrip()}")
                w["lineas"].append(linea)
                if "WORKER FINALIZADO" in linea and w["config"]["nombre"] not in resultados:
                    import re
                    dur = re.search(r"Duración=([0-9.]+)s", linea)
                    if dur:
                        resultados[w["config"]["nombre"]] = float(dur.group(1))

            if w["proc"].poll() is not None:
                # Vaciar buffer residual
                resto = w["proc"].stdout.read()
                if resto:
                    for l in resto.splitlines():
                        if l.strip():
                            print(f"    [{w['config']['nombre']:<11}] {l}")
                workers.remove(w)

    time.sleep(0.3)
    mostrar_resultados_finales(resultados)


def mostrar_resultados_finales(resultados):
    print("\n" + "=" * 78)
    print("  🏁 RESULTADOS FINALES — PLANIFICACIÓN (Scheduling)")
    print("=" * 78)

    if not resultados:
        print("  ⚠️  No se pudieron obtener los tiempos de duración.")
        return

    ordenados = sorted(resultados.items(), key=lambda x: x[1])
    print(f"  {'#':<3} {'Prioridad':<15} {'Tiempo (s)':<14} {'Observación':<30}")
    print("-" * 78)

    for idx, (nombre, t) in enumerate(ordenados, 1):
        medalla = "🥇" if idx == 1 else "🥈"
        print(f"  {idx:<3} {nombre:<15} {t:>8.3f} s     {medalla} Ganó" if idx == 1 else f"  {idx:<3} {nombre:<15} {t:>8.3f} s     {medalla}")

    print("-" * 78)

    if len(ordenados) == 2:
        ganador_n, ganador_t = ordenados[0]
        perdedor_n, perdedor_t = ordenados[1]
        if perdedor_t > 0:
            ratio = perdedor_t / ganador_t
            print(f"\n  ⚡ Proceso '{ganador_n}' terminó {ratio:.2f}x MÁS RÁPIDO que '{perdedor_n}'.")
            diff = perdedor_t - ganador_t
            print(f"     Diferencia temporal: {diff:.3f} segundos ({diff*1000:.0f} ms).")

    print("\n" + "=" * 78)
    print("  📚 EXPLICACIÓN ARQUITECTÓNICA DEL KERNEL")
    print("=" * 78)
    print("""
  1.  Scheduler (Planificador) del Kernel:
      · Es el componente del SO que decide QUÉ proceso usa la CPU y CUÁNDO.
      · Se ejecuta millones de veces por segundo, entre cambios de contexto.

  2.  Colas de prioridad:
      · Los procesos NO se ejecutan en orden FIFO. Se agrupan por prioridad.
      · "Tiempo Real" / Alto nice → entra más frecuentemente al procesador.
      · "Baja" / Alto nice positivo → solo se ejecuta cuando el sistema está ocioso.

  3.  Quantum (rodaja de CPU):
      · A un proceso de alta prioridad se le da más tiempo de CPU (quantum mayor).
      · A un proceso de baja prioridad se le da menos tiempo y se le expulsa antes.

  4.  Cuándo importa realmente:
      · Servidores de bases de datos: alta prioridad.
      · Backups nocturnos, índices, renderizados en segundo plano: baja prioridad.
      · Procesos en tiempo real (audio/video): máxima prioridad para evitar glitches.
""")
    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="Prioridad de Procesos del Scheduler del Kernel"
    )
    sub = parser.add_subparsers(dest="modo")

    sub_worker = sub.add_parser("worker", help="Modo trabajador (llamado por el coordinador)")
    sub_worker.add_argument("--nombre", required=True, help="Nombre amigable (BAJA / TIEMPO_REAL)")
    sub_worker.add_argument("--nice", required=True, type=int, help="Valor nice de prioridad")

    args = parser.parse_args()

    if args.modo == "worker":
        modo_worker(args.nombre, args.nice)
    else:
        modo_coordinador()


if __name__ == "__main__":
    main()
