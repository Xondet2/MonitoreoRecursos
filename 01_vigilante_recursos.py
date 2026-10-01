#!/usr/bin/env python3
"""
Vigilante de Recursos (Monitoreo de RAM y CPU)
==============================================
Concepto: Gestor de memoria y E/S.
Objetivo: Monitorear en tiempo real el consumo de recursos y generar alertas
          si se supera un umbral, simulando un panel de control del SO.
Reto: Guardar un log en un archivo .txt cada vez que la RAM supere el 80%.
"""

import psutil
import time
from datetime import datetime
import os
import sys

UMBRAL_RAM = 80.0
UMBRAL_CPU = 90.0
INTERVALO_SEGUNDOS = 2
ARCHIVO_LOG = "alertas_ram.log"


def obtener_uso_recursos():
    ram = psutil.virtual_memory()
    cpu_porcentaje = psutil.cpu_percent(interval=0.5)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ram_porcentaje": ram.percent,
        "ram_usada_gb": ram.used / (1024 ** 3),
        "ram_total_gb": ram.total / (1024 ** 3),
        "ram_disponible_gb": ram.available / (1024 ** 3),
        "cpu_porcentaje": cpu_porcentaje,
        "swap_porcentaje": psutil.swap_memory().percent,
        "swap_usada_gb": psutil.swap_memory().used / (1024 ** 3),
    }


def registrar_alerta_ram(datos):
    mensaje = (
        f"[{datos['timestamp']}] ALERTA RAM: {datos['ram_porcentaje']:.1f}% "
        f"| Usada: {datos['ram_usada_gb']:.2f}GB / {datos['ram_total_gb']:.2f}GB "
        f"| Disponible: {datos['ram_disponible_gb']:.2f}GB "
        f"| CPU: {datos['cpu_porcentaje']:.1f}%\n"
    )
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(mensaje)
    print(f"\n⚠️  ALERTA REGISTRADA en {ARCHIVO_LOG}: {mensaje.strip()}")


def imprimir_panel(datos):
    sys.stdout.write("\033[2J\033[H")
    print("=" * 70)
    print("       PANEL DE CONTROL DEL SISTEMA OPERATIVO - MONITOREO")
    print("=" * 70)
    print(f"  Hora actual        : {datos['timestamp']}")
    print("-" * 70)
    print(f"  {'RECURSO':<20} {'USO':<15} {'DETALLES':<30}")
    print("-" * 70)

    ram_color = "\033[91m" if datos["ram_porcentaje"] >= UMBRAL_RAM else "\033[92m"
    cpu_color = "\033[91m" if datos["cpu_porcentaje"] >= UMBRAL_CPU else "\033[92m"
    swap_color = "\033[93m" if datos["swap_porcentaje"] > 0 else "\033[92m"
    reset = "\033[0m"

    print(
        f"  {'RAM':<20} {ram_color}{datos['ram_porcentaje']:>5.1f}%{reset:<10} "
        f"{datos['ram_usada_gb']:.2f}GB / {datos['ram_total_gb']:.2f}GB"
    )
    print(
        f"  {'CPU':<20} {cpu_color}{datos['cpu_porcentaje']:>5.1f}%{reset:<10} "
        f"{psutil.cpu_count(logical=True)} núcleos lógicos"
    )
    print(
        f"  {'SWAP / Virtual':<20} {swap_color}{datos['swap_porcentaje']:>5.1f}%{reset:<10} "
        f"{datos['swap_usada_gb']:.2f}GB usados"
    )
    print("-" * 70)
    print(f"  Umbrales: RAM > {UMBRAL_RAM}% → Alerta   |   CPU > {UMBRAL_CPU}% → Aviso")
    print("  Presiona Ctrl+C para detener")
    print("=" * 70)


def main():
    print("Iniciando vigilante de recursos...")
    print(f"Umbral de alerta RAM: {UMBRAL_RAM}%")
    print(f"Archivo de log: {os.path.abspath(ARCHIVO_LOG)}")
    time.sleep(1.5)

    try:
        while True:
            datos = obtener_uso_recursos()
            imprimir_panel(datos)

            if datos["ram_porcentaje"] >= UMBRAL_RAM:
                registrar_alerta_ram(datos)

            if datos["cpu_porcentaje"] >= UMBRAL_CPU:
                print(f"  ⚡ Aviso: CPU bajo carga crítica ({datos['cpu_porcentaje']:.1f}%)")

            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor detenido por el usuario.")
        if os.path.exists(ARCHIVO_LOG):
            print(f"📄 Log de alertas: {os.path.abspath(ARCHIVO_LOG)}")


if __name__ == "__main__":
    main()
