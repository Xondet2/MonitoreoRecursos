#!/usr/bin/env python3
"""
El Simulador de Memoria Caché (L1/L2 vs RAM)
=============================================
Concepto: Jerarquía de memoria y optimización.
Objetivo: Implementar una caché en memoria (Diccionario) para evitar acceso
          constante al disco (memoria secundaria).
Reto: Medir el tiempo de ejecución en ambos casos usando time.time().

Jerarquía simulada:
  DISCO (lento, persistente) → RAM (caché, rápido, volátil)
  Análogo real: Disco → RAM → L2 → L1 → Registros CPU
"""

import os
import time
import sys
import random
import string

DIRECTORIO_ARCHIVOS = "archivos_grandes_prueba"
NUM_ARCHIVOS = 5
TAMANO_ARCHIVO_MB = 50  # Tamaño por archivo en MB


class CacheMemoria:
    """Simula una caché L1/L2 en RAM usando diccionarios."""

    def __init__(self, capacidad_elementos=None):
        self._cache = {}
        self._estadisticas = {
            "hit": 0,
            "miss": 0,
            "lecturas_disco": 0,
            "lecturas_cache": 0,
        }
        self._capacidad = capacidad_elementos

    @property
    def tamanio_bytes(self):
        return sum(len(v.encode("utf-8", errors="replace")) if isinstance(v, str)
                   else sys.getsizeof(v) for v in self._cache.values())

    @property
    def tasa_hit(self):
        total = self._estadisticas["hit"] + self._estadisticas["miss"]
        return (self._estadisticas["hit"] / total * 100) if total > 0 else 0.0

    def contiene(self, clave):
        return clave in self._cache

    def obtener(self, clave):
        if self.contiene(clave):
            self._estadisticas["hit"] += 1
            self._estadisticas["lecturas_cache"] += 1
            return self._cache[clave], True
        self._estadisticas["miss"] += 1
        return None, False

    def almacenar(self, clave, valor):
        if self._capacidad and len(self._cache) >= self._capacidad:
            eliminada = next(iter(self._cache))
            del self._cache[eliminada]
            print(f"  [Cache] Llenada — se reemplazó entrada más antigua: {eliminada[:40]}...")
        self._cache[clave] = valor

    def mostrar_estadisticas(self):
        print("\n" + "=" * 70)
        print("  📊 ESTADÍSTICAS DE LA CACHÉ")
        print("=" * 70)
        print(f"  Elementos en caché  : {len(self._cache)}")
        print(f"  Tamaño en RAM       : {self.tamanio_bytes / (1024**2):.2f} MB")
        print(f"  Hits (desde RAM)    : {self._estadisticas['hit']}")
        print(f"  Miss (ir a disco)   : {self._estadisticas['miss']}")
        print(f"  Tasa de aciertos    : {self.tasa_hit:.1f}%")
        print(f"  Lecturas totales    : {self._estadisticas['lecturas_disco'] + self._estadisticas['lecturas_cache']}")
        print("=" * 70)

    def registrar_lectura_disco(self):
        self._estadisticas["lecturas_disco"] += 1


def generar_archivos_prueba():
    """Crea archivos grandes con texto aleatorio para simular archivos de datos."""
    os.makedirs(DIRECTORIO_ARCHIVOS, exist_ok=True)
    archivos_creados = []

    for i in range(NUM_ARCHIVOS):
        nombre_archivo = os.path.join(DIRECTORIO_ARCHIVOS, f"dataset_{i:03d}.txt")
        archivos_creados.append(nombre_archivo)

        if os.path.exists(nombre_archivo) and os.path.getsize(nombre_archivo) > 0:
            print(f"  ✅ Archivo existente: {nombre_archivo} ({os.path.getsize(nombre_archivo) / (1024**2):.1f} MB)")
            continue

        print(f"  ⏳ Generando {nombre_archivo} (~{TAMANO_ARCHIVO_MB} MB)...", end=" ", flush=True)
        tamano_bytes = TAMANO_ARCHIVO_MB * 1024 * 1024
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            escritos = 0
            while escritos < tamano_bytes:
                linea = "".join(random.choices(string.ascii_letters + string.digits + " \n", k=1024))
                f.write(linea)
                escritos += len(linea.encode("utf-8"))
        print("LISTO")

    return archivos_creados


def leer_desde_disco(ruta_archivo):
    """Lee un archivo desde el disco (memoria secundaria — lenta)."""
    inicio = time.time()
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()
    tiempo = time.time() - inicio
    return contenido, tiempo


def leer_con_cache(cache: CacheMemoria, ruta_archivo):
    """Busca primero en la caché (RAM), si no existe, lee desde disco y almacena."""
    inicio_total = time.time()

    cache_data, hit = cache.obtener(ruta_archivo)
    if hit:
        tiempo_total = time.time() - inicio_total
        return cache_data, tiempo_total, "RAM (HIT)"

    contenido, tiempo_disco = leer_desde_disco(ruta_archivo)
    cache.almacenar(ruta_archivo, contenido)
    cache.registrar_lectura_disco()

    tiempo_total = time.time() - inicio_total
    return contenido, tiempo_total, f"DISCO (MISS → +{tiempo_disco*1000:.1f}ms)"


def demo_sin_cache(archivos, repeticiones=3):
    """Demuestra lectura sin caché: todas las veces desde disco."""
    print("\n" + "=" * 70)
    print("  🧪 DEMOSTRACIÓN 1: LECTURA SIN CACHÉ (todas desde DISCO)")
    print("=" * 70)

    tiempos_por_archivo = {a: [] for a in archivos}

    for ronda in range(repeticiones):
        print(f"\n  --- Ronda {ronda + 1}/{repeticiones} ---")
        for ruta in archivos:
            nombre = os.path.basename(ruta)
            contenido, t = leer_desde_disco(ruta)
            tiempos_por_archivo[ruta].append(t)
            print(f"    [DISCO] {nombre:<20} → {t*1000:>8.1f} ms  ({len(contenido)/1024**2:.1f} MB leídos)")

    print("\n  📋 Resumen sin caché:")
    tiempos_totales = []
    for ruta, tiempos in tiempos_por_archivo.items():
        avg = sum(tiempos) / len(tiempos)
        tiempos_totales.extend(tiempos)
        print(f"    {os.path.basename(ruta):<20} → Avg: {avg*1000:.1f} ms  | Min: {min(tiempos)*1000:.1f} ms  | Max: {max(tiempos)*1000:.1f} ms")
    promedio_general = sum(tiempos_totales) / len(tiempos_totales)
    print(f"    {'PROMEDIO GENERAL':<20} → {promedio_general*1000:.1f} ms/lectura")
    return promedio_general


def demo_con_cache(archivos, repeticiones=3):
    """Demuestra lectura con caché: primera vez disco, siguientes RAM."""
    print("\n" + "=" * 70)
    print("  🚀 DEMOSTRACIÓN 2: LECTURA CON CACHÉ (L1/L2 en RAM)")
    print("=" * 70)
    print("  (Primera ronda = MISS → carga desde DISCO)")
    print("  (Rondas siguientes = HIT → lectura desde RAM)")

    cache = CacheMemoria()
    tiempos_por_tipo = {"MISS": [], "HIT": []}

    for ronda in range(repeticiones):
        print(f"\n  --- Ronda {ronda + 1}/{repeticiones} ---")
        for ruta in archivos:
            nombre = os.path.basename(ruta)
            _, t, origen = leer_con_cache(cache, ruta)
            tipo = "HIT" if "RAM" in origen else "MISS"
            tiempos_por_tipo[tipo].append(t)
            print(f"    [{tipo:>4}] {nombre:<20} → {t*1000:>8.1f} ms  vía {origen}")

    print("\n  📋 Resumen con caché:")
    for tipo in ["MISS", "HIT"]:
        if tiempos_por_tipo[tipo]:
            tiempos = tiempos_por_tipo[tipo]
            print(f"    {tipo:<20} → {len(tiempos)} lecturas | Avg: {sum(tiempos)/len(tiempos)*1000:.1f} ms  | Min: {min(tiempos)*1000:.1f} ms  | Max: {max(tiempos)*1000:.1f} ms")

    cache.mostrar_estadisticas()

    hit_avg = sum(tiempos_por_tipo["HIT"]) / len(tiempos_por_tipo["HIT"]) if tiempos_por_tipo["HIT"] else 0
    miss_avg = sum(tiempos_por_tipo["MISS"]) / len(tiempos_por_tipo["MISS"]) if tiempos_por_tipo["MISS"] else 0
    return miss_avg, hit_avg


def main():
    print("=" * 70)
    print("   🏗️  SIMULADOR DE JERARQUÍA DE MEMORIA: CACHE L1/L2 vs DISCO")
    print("=" * 70)
    print(f"   Archivos a generar: {NUM_ARCHIVOS} x ~{TAMANO_ARCHIVO_MB} MB")
    print(f"   Directorio de datos: {os.path.abspath(DIRECTORIO_ARCHIVOS)}")
    print("=" * 70)

    print("\n📦 PASO 1: Preparando archivos de prueba (simulando Disco / SSD)...")
    archivos = generar_archivos_prueba()

    t_sin_cache = demo_sin_cache(archivos)
    t_miss, t_hit = demo_con_cache(archivos)

    print("\n" + "=" * 70)
    print("  🏆 COMPARATIVA FINAL DE RENDIMIENTO")
    print("=" * 70)
    print(f"    Sin caché (promedio disco)          : {t_sin_cache*1000:.1f} ms")
    print(f"    Con caché — MISS (disco + carga)    : {t_miss*1000:.1f} ms")
    print(f"    Con caché — HIT (solo RAM)          : {t_hit*1000:.3f} ms")
    if t_hit > 0:
        speedup = t_sin_cache / t_hit
        print(f"    ⚡ SpeedUp (RAM vs Disco)           : ~{speedup:.0f}x MÁS RÁPIDO")
    print("=" * 70)
    print("\n💡 Explicación arquitectónica:")
    print("   - La primera lectura es un 'cache miss': el SO debe buscar en el")
    print("     bloque de datos del disco (memoria secundaria), operación lenta.")
    print("   - Las lecturas siguientes son 'cache hit': los datos ya están en")
    print("     la RAM (caché L2/L1 del SO), por lo que el acceso es instantáneo.")
    print("   - Esta jerarquía (Disco → RAM → Cachés L2/L1) optimiza el rendimiento")
    print("     de cualquier sistema operativo moderno.")


if __name__ == "__main__":
    main()
