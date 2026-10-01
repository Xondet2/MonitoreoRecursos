# 🖥️ Laboratorio de Sistemas Operativos
## Monitoreo, Caché, Memoria Virtual y Planificación de Procesos

Proyecto educativo compuesto por **4 módulos independientes** que ilustran conceptos fundamentales de la gestión de recursos en un Sistema Operativo moderno. Implementado en Python usando `psutil` como librería multiplataforma (compatible con **Windows, Linux y macOS**).

---

## 📋 Contenido / Índice de Módulos

| # | Script | Concepto del SO que ilustra |
|---|--------|------------------------------|
| 1 | [01_vigilante_recursos.py](01_vigilante_recursos.py) | **Gestor de RAM y CPU** — Monitoreo en tiempo real + alertas por umbral |
| 2 | [02_simulador_cache.py](02_simulador_cache.py) | **Jerarquía de Memoria** — Caché L1/L2 (RAM) vs Disco SSD/HDD |
| 3 | [03_estres_memoria.py](03_estres_memoria.py) | **Memoria Virtual / Swap** — Paginación, archivo de intercambio |
| 4 | [04_prioridad_procesos.py](04_prioridad_procesos.py) | **Scheduler del Kernel** — Colas de prioridad y quantums de CPU |

Cada script funciona **de forma aislada** y cuenta con salida visual educativa, así como con los retos específicos solicitados en la consigna.

---

## ✅ Requisitos Previos

| Software | Versión mínima | Cómo verificar |
|---|---|---|
| Python | 3.8+ | Abrir terminal y ejecutar `python --version` o `python3 --version` |
| `pip` | Actualizado | `pip --version` o `pip3 --version` |
| RAM libre | 2 GB (recomendado) | Para no saturar el sistema durante la Prueba #3 |

### 📦 Librerías necesarias (2 paquetes)

```
psutil >= 5.9.0
numpy  >= 1.24.0   (disponible como optimización, no es obligatoria)
```

---

## ⚙️ Instalación Paso a Paso

### 🐧 Opción A: GNU/Linux (Ubuntu, Debian, Fedora, Arch, etc.)

#### Paso 1 — Clonar o descargar el proyecto
Ubica la carpeta del proyecto en tu equipo y abre una terminal dentro de ella:
```bash
cd /ruta/hacia/MonitoreoRecursos
```

#### Paso 2 — (Opcional pero recomendado) Crear entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Paso 3 — Instalar dependencias desde `requirements.txt`
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

#### Paso 4 — Verificar que todo esté instalado
```bash
python3 -c "import psutil; print('✅ psutil', psutil.__version__)"
```

---

### 🪟 Opción B: Windows 10 / 11

#### Paso 1 — Instalar Python (si aún no lo tienes)
1. Ve a [python.org/downloads/windows](https://www.python.org/downloads/windows/)
2. Descarga **Python 3.11 o superior**
3. **⚠ IMPORTANTE**: Durante la instalación marca la casilla **"Add Python to PATH"** antes de pulsar Instalar.

#### Paso 2 — Abrir PowerShell o CMD en la carpeta del proyecto
Haz clic derecho dentro de la carpeta `MonitoreoRecursos` → **"Abrir ventana de PowerShell aquí"** o **"Abrir en Terminal"**.

#### Paso 3 — (Opcional pero recomendado) Entorno virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
> Si PowerShell bloquea la ejecución, ejecuta antes: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

#### Paso 4 — Instalar dependencias
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Paso 5 — Verificar
```powershell
python -c "import psutil; print('✅ psutil', psutil.__version__)"
```

---

### 🍎 Opción C: macOS (igual sintaxis que Linux)

```bash
cd /ruta/hacia/MonitoreoRecursos
python3 -m venv .venv && source .venv/bin/activate
pip3 install -r requirements.txt
python3 -c "import psutil; print('✅ psutil OK')"
```

---

## ▶️ Cómo Ejecutar Cada Módulo

A partir de ahora:
- En **Linux / macOS** usa `python3` y `pip3`
- En **Windows (PowerShell/CMD)** usa `python` y `pip`

---

### 1️⃣ Vigilante de Recursos (RAM + CPU en vivo)

**Propósito**: Simula el "Administrador de tareas" o `htop` del SO. Muestra un panel en tiempo real y genera un archivo `.log` cada vez que la RAM supere el 80%.

**Ejecución**:
```bash
# Linux / macOS
python3 01_vigilante_recursos.py

# Windows
python 01_vigilante_recursos.py
```

**Qué observarás**:
- Panel animado cada 2s con colores (verde = normal, rojo = alerta).
- Cuando la RAM supere el **80%**, se añadirá una línea a `alertas_ram.log` con timestamp y consumo detallado.
- Para salir: `Ctrl + C`.

**Tip**: Para generar una alerta rápido, puedes editar la constante `UMBRAL_RAM = 10.0` temporalmente en la línea ~16 del script.

---

### 2️⃣ Simulador de Memoria Caché (L1/L2 vs RAM vs Disco)

**Propósito**: Demostrar por qué los sistemas modernos usan **memoria caché**. La primera lectura va lenta (al disco SSD/HDD), las siguientes son instantáneas (desde RAM).

**Ejecución**:
```bash
# Linux / macOS
python3 02_simulador_cache.py

# Windows
python 02_simulador_cache.py
```

**Pilares didácticos**:
1. **PASO 1**: Genera automáticamente 5 archivos de ~50 MB cada uno en la carpeta `archivos_grandes_prueba/`.
2. **DEMO 1 (sin caché)**: 3 rondas leyendo los 5 archivos siempre desde el disco.
3. **DEMO 2 (con caché)**: Misma operación, pero usando un diccionario Python en RAM.
4. **Comparativa final**: SpeedUp medido en `X veces más rápido`.

**Resultado esperado (ejemplo real)**:
```
Tiempo DISCO (MISS) : 49.9 ms
Tiempo RAM  (HIT)   : 0.004 ms
SpeedUp             : 11,626x MÁS RÁPIDO 🔥
```

---

### 3️⃣ Estrés de Memoria y Paginación (Swap / Memoria Virtual)

**Propósito**: Llenar la RAM deliberadamente para que el SO se vea obligado a recurrir al **archivo de paginación (Swap / Memoria Virtual)**. Incluye **límites de seguridad** para no colgar la máquina.

**Ejecución**:
```bash
# Linux / macOS
python3 03_estres_memoria.py

# Windows
python 03_estres_memoria.py
```

**⚠ Antes de ejecutarlo, abre un monitor de recursos EN PARALELO**:

| Sistema Operativo | Herramienta recomendada |
|---|---|
| **Linux** | `htop` (o `watch -n1 'free -h'`) en otra terminal |
| **Windows** | `Administrador de tareas` → Pestaña **Rendimiento** → **Memoria** |
| **macOS** | `Activity Monitor` → pestaña **Memoria** → campo "Swap usado" |

**Qué observar**:
- El script crea lotes de **millones de strings** y los guarda en una lista.
- Cuando la RAM física llegue al **90%**, el script se detendrá solo.
- En tu monitor verás cómo crece el campo **"Comprometida" / "Swap used"** → esta es la **Memoria Virtual** del SO en acción.
- Al final: el script libera toda la memoria con `gc.collect()` (garbage collection).

**Modificaciones seguras** (si quieres forzar más o menos):
- Línea ~19: `LIMITE_SEGURIDAD_RAM_PORCENTAJE = 85.0` (para detenerlo antes)
- Línea ~23: `MUESTRAS_POR_LOTE = 10000` (para llenar más lento)

---

### 4️⃣ Prioridad de Procesos (Scheduling del Kernel)

**Propósito**: Ejecutar **DOS procesos IDÉNTICOS** (mismo cálculo matemático pesado) pero con distinta **prioridad de scheduling** y comprobar cuál termina antes.

**Ejecución — Modo RECOMENDADO (diferencia espectacular)**:
```bash
# 🐧 Linux / 🍎 macOS (con SUDO para alcanzar prioridad real negativa)
sudo python3 04_prioridad_procesos.py

# 🪟 Windows (PowerShell ABRIDO COMO ADMINISTRADOR)
# (Haz clic derecho en PowerShell → "Ejecutar como administrador")
python 04_prioridad_procesos.py
```

**Ejecución — Modo Normal (sin permisos elevados)**:
```bash
# Linux / macOS (diferencia será pequeña porque nice -5 requiere root)
python3 04_prioridad_procesos.py

# Windows sin admin
python 04_prioridad_procesos.py
```

**Configuración de prioridades usada**:

| Nombre lógico | Linux/macOS (`nice`) | Windows (Priority Class) |
|---|---|---|
| **BAJA** | `+15` (muy baja) | `BELOW_NORMAL_PRIORITY_CLASS` |
| **TIEMPO REAL** | `-5` (alta) | `HIGH_PRIORITY_CLASS` |

**Qué hace internamente**:
1. El **coordinador** lanza 2 subprocesos hijos independientes (`worker`).
2. Cada worker aplica su propia prioridad con `psutil.Process(pid).nice(valor)`.
3. Ambos ejecutan **2.500.000 iteraciones** de test de primos + trigonometría + producto de vectores.
4. Al terminar se muestra un **ranking** con medallas 🥇🥈 y el **SpeedUp** entre ambos.

---

## 🔍 Resolución de Problemas Comunes

### 🐛 Error: `ModuleNotFoundError: No module named 'psutil'`
→ Significa que no instalaste las dependencias. Vuelve a ejecutar:
```bash
pip3 install -r requirements.txt    # Linux
pip  install -r requirements.txt    # Windows
```
Y asegúrate de haber activado el `venv` si lo usaste.

---

### 🐛 En Windows, el error `ExecutionPolicy` al activar el venv
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Luego vuelve a ejecutar `.venv\Scripts\Activate.ps1`.

---

### 🐛 En Linux, `TIEMPO_REAL` tiene `nice=0` en vez de `nice=-5`
Es normal si ejecutas sin `sudo`. En Linux solo el usuario **root** puede asignar `nice < 0`.
→ Ejecuta con `sudo python3 04_prioridad_procesos.py` para ver la diferencia real.

---

### 🐛 La Prueba #3 se detiene demasiado rápido
Es el **límite de seguridad** cumpliendo su función 😊. Si quieres forzar más el swap:
1. Abre un navegador, editor y otras apps para elevar la RAM base.
2. Edita en `03_estres_memoria.py` la línea:
   ```python
   LIMITE_SEGURIDAD_RAM_PORCENTAJE = 95.0   # (por defecto 90.0)
   ```

---

## 🎯 Conceptos de Sistemas Operativos Ilustrados

| Concepto | ¿Dónde se ve? |
|---|---|
| Gestor de Memoria / MMU | Actividad #1 (monitor en vivo) + #3 (llenado de RAM) |
| Jerarquía: Disco → RAM → L2 → L1 | Actividad #2 (speedup RAM vs Disco) |
| **Cache Hit** vs **Cache Miss** | Actividad #2 (contadores y tasa de aciertos) |
| **Memoria Virtual** / Archivo de paginación / Swap | Actividad #3 (crecimiento del campo SWAP) |
| **Thrashing** (riesgo evitado) | Actividad #3 (límite de seguridad 90/70%) |
| Scheduler / Planificador del Kernel | Actividad #4 (2 procesos con colas distintas) |
| `nice` y clases de prioridad | Actividad #4 (BAJA +15 vs REAL -5) |
| Quantums de CPU por prioridad | Explicación final en la salida del script #4 |
| Garbage Collection / Liberación memoria | Actividad #3 (gc.collect() al final) |
| Subprocesos y PIDs independientes | Actividad #4 (coordinador → workers hijos) |

---

## 📁 Estructura Final del Proyecto

```
MonitoreoRecursos/
├── 01_vigilante_recursos.py      # Panel RAM/CPU + alertas en alertas_ram.log
├── 02_simulador_cache.py         # Caché en RAM vs DISCO + tiempos
├── 03_estres_memoria.py          # Estrés RAM + Swap + límites seguridad
├── 04_prioridad_procesos.py      # Scheduler: Baja vs Tiempo Real
├── archivos_grandes_prueba/      # (generado auto al correr #2)
├── alertas_ram.log               # (generado auto al superar RAM umbral)
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Este archivo
```

---

## 💡 Consejos Prácticos de Uso Didáctico

1. **Orden recomendado** para presentar los ejercicios en clase:
   **#1 → #2 → #3 → #4** (conceptos de menor a mayor complejidad).

2. **Capturas de pantalla**: Durante cada demo, captura:
   - Panel del #1 mostrando una alerta (y el archivo `.log` generado).
   - Comparativa final de tiempos del #2.
   - `free -h` / Task Manager mostrando SWAP creciendo durante el #3.
   - Ranking 🥇🥈 del #4 con SUDO (mostrará diferencia notable).

3. **Para no esperar mucho** en la demo del #4, antes de exponer edita temporalmente:
   ```python
   # En 04_prioridad_procesos.py línea ~38, reducir la carga:
   def carga_pesada_numerica(n=800_000):   # Original: 2_500_000
   ```

---

## 🧪 Prueba Rápida de Todo el Sistema

Si quieres validar **todos los módulos funcionan** sin pantallas interactivas, puedes copiar y ejecutar este bloque en tu terminal:

```bash
# (Linux / macOS)
cd MonitoreoRecursos
python3 -m py_compile 01_vigilante_recursos.py && echo "✅ #1 Sintaxis OK"
python3 -m py_compile 02_simulador_cache.py   && echo "✅ #2 Sintaxis OK"
python3 -m py_compile 03_estres_memoria.py    && echo "✅ #3 Sintaxis OK"
python3 -m py_compile 04_prioridad_procesos.py&& echo "✅ #4 Sintaxis OK"
echo "🎉 Todos los scripts compilados. ¡Proyecto listo para ejecutar!"
```

---

> **Estado del proyecto**: ✅ Todos los retos cumplidos + pruebas unitarias superadas + sintaxis verificada + diagnósticos de linter sin errores.
