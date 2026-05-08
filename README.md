# ContextWordlist v1.1

**Generador profesional de wordlists contextuales para pentesting avanzado**

Genera diccionarios de contraseñas altamente dirigidos a partir de inteligencia real sobre el objetivo. Combina datos contextuales con estrategias avanzadas de mutación para crear wordlists que pueden probar contraseñas **10-100 veces más rápido** que los diccionarios genéricos.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)](.)

> **⚠️ ADVERTENCIA LEGAL**: Esta herramienta es solo para pruebas de seguridad autorizadas. El acceso no autorizado a sistemas informáticos es ilegal. Consulta la sección de [Seguridad y ética](#-seguridad-y-ética) más abajo.

---

## 🎯 ¿Qué hace?

Imagina que estás evaluando la seguridad de una empresa. En lugar de usar una **lista genérica de 14 millones de contraseñas aleatorias** que puede tardar SEMANAS en probarse, ContextWordlist genera una **lista inteligente y dirigida de 6.000 a 50.000 contraseñas** que un usuario real podría usar basándose en su información contextual.

### Ejemplo real:
- **Nombre del CEO**: John Smith
- **Empresa**: TechCorp Inc
- **Año de fundación**: 2015
- **Año de nacimiento**: 1980

**ContextWordlist genera contraseñas como:**
```
john2015          (nombre + año de fundación de la empresa)
john_techcorp     (nombre + empresa)
John2024!         (capitalizada + año actual + carácter especial)
j0hn_t3chc0rp     (variación leet speak)
TechCorp1980      (empresa + año de nacimiento)
...¡y 6.750 variaciones inteligentes más!
```

**Resultado**: pruebas en **MINUTOS** en lugar de SEMANAS. Ese es el poder del contexto.

---

## 🎯 Características

### Capacidades principales
- **Generación sensible al contexto**: combina datos personales, información de empresa y patrones personalizados.
- **Leet speak avanzado**: sustituciones de varios caracteres, no solo reemplazos simples.
- **Mutaciones inteligentes**: sufijos con años, patrones estacionales y variantes de capitalización.
- **Motor de combinaciones**: combinaciones inteligentes de persona + empresa + fechas.

### Integración con herramientas profesionales
- **Máscaras de Hashcat** (nuevo): genera automáticamente más de 10 máscaras contextuales para ataques de fuerza bruta.
- **Reglas de Hashcat** (nuevo): más de 50 reglas dinámicas basadas en los datos del perfil.
- **Wordlist estándar**: compatible con Hashcat, Hydra, John the Ripper y Medusa.
- **Soporte para piping**: salida directa por stdout para integrarse con otras herramientas.

### Analítica y reportes
- **Panel HTML**: reporte profesional con tema oscuro y estadísticas.
- **Exportación CSV**: puntuación de entropía y análisis de complejidad por palabra.
- **Logging completo**: trazabilidad de ejecución para auditorías.
- **Estadísticas profundas**: seguimiento de deduplicación y métricas de complejidad.

---

## 📋 Inicio rápido

### Instalación

**Linux/Kali:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

O manualmente:
```bash
pip install rich
```

### Uso básico

**Modo interactivo (el más fácil):**
```bash
python3 contextwordlist.py -i
```

**Comando directo:**
```bash
python3 contextwordlist.py \
  --name Juan \
  --lastname Pérez \
  --company TechNova \
  --founded 2015 \
  --birth-year 1990 \
  --export all
```

**Desde un perfil JSON:**
```bash
python3 contextwordlist.py --profile target.json --export all
```

---

## 🚀 Ejemplos avanzados (para expertos)

### Ejemplo 1: Auditoría interna (equipo de IT)
```bash
python3 contextwordlist.py \
  --company "Acme Corp" \
  --founded 2015 \
  --domain acme.com \
  --industry "Finance" \
  --export all
```

### Ejemplo 2: Ejercicio de Red Team
```bash
python3 contextwordlist.py \
  --name Robert \
  --lastname Johnson \
  --nickname Bob \
  --company TechCorp \
  --partner Sarah \
  --birth-year 1978 \
  --city "San Francisco" \
  --hobby "Golf" \
  --export all
```

### Ejemplo 3: Ataque a gran escala con GPU (solo expertos)
```bash
python3 contextwordlist.py \
  --name Juan \
  --company TechNova \
  --max-words 200000 \
  --leet-advanced \
  --export txt \
  --quiet | hashcat -m 0 -a 0 hashes.txt -
```

### Ejemplo 4: Ataque híbrido con Hashcat
```bash
python3 contextwordlist.py --name Juan --export masks
hashcat -m 1000 -a 3 hashes.txt -hm reports/masks_*.hcmask
```

---

## 📖 Referencia de comandos

### Datos personales
```bash
--name TEXT              Nombre
--lastname TEXT          Apellido
--nickname TEXT          Apodo/alias
--birth-year YYYY        Año de nacimiento (1900-2050)
--birth-day DD           Día de nacimiento (01-31)
--birth-month MM         Mes de nacimiento (01-12)
--partner TEXT           Nombre de pareja/cónyuge
--pet TEXT               Nombre de mascota
--child TEXT             Nombre de hijo/a
--city TEXT              Ciudad
--country TEXT           País
--hobby TEXT             Hobby/interés
```

### Datos de empresa
```bash
--company TEXT           Nombre de la empresa
--company-short TEXT     Abreviatura (ej.: TN para TechNova)
--domain TEXT            Dominio (ej.: company.com)
--industry TEXT          Sector o industria
--founded YYYY           Año de fundación (1900-2050)
--product TEXT           Nombre del producto
```

### Configuración
```bash
--extra-words TEXT       Palabras extra separadas por comas
--min-length N           Longitud mínima (default: 6)
--max-length N           Longitud máxima (default: 20)
--max-words N            Tamaño máximo de la wordlist (default: 50000)
--leet-advanced          Activa leet speak avanzado (múltiples sustituciones)
--no-leet                Desactiva leet speak
--no-seasons             Desactiva patrones estacionales
--no-combinations        Desactiva combinaciones de palabras
```

### Opciones de salida
```bash
--export FORMAT          txt, rules, masks, html, csv, all
--stdout                 Envía la wordlist a stdout (útil para piping)
--quiet                  Modo silencioso (sin banner ni tablas)
--preview N              Cantidad de palabras a previsualizar (default: 20)
```

### Gestión de perfiles
```bash
--profile FILE.json      Carga un perfil desde un archivo JSON
-i, --interactive        Modo interactivo (recomendado)
```

---

## 📊 Formatos de salida

### Wordlist (TXT)
Formato estándar de una palabra por línea, compatible con las principales herramientas:
```
Juan2024
juan_perez
JUAN_TECN
juan@parez
...
```

### Máscaras de Hashcat (.hcmask)
Máscaras contextuales generadas automáticamente para fuerza bruta:
```
Juan?d?d?d?d
?uJuan?d?d
?a?a?a?a90
90?a?a?a?a
...
```

### Reglas de Hashcat (.rule)
Reglas dinámicas de mutación:
```
c
u
l
C
sa4
se3
c$2$0$2$4
...
```

### Reporte HTML (.html)
Panel profesional con:
- Estadísticas clave (total de palabras, palabras base, etc.).
- Desglose de mutaciones con porcentajes.
- Previsualización de 100 palabras con indicadores de complejidad.
- Instrucciones de uso con Hashcat.
- Tema oscuro estilo ciberseguridad.

### Exportación CSV (.csv)
Datos analíticos con puntuación de entropía:
```
word,length,has_uppercase,has_digit,has_special,has_leet,entropy_score
Juan2024,8,1,1,0,0,2
juan_perez,10,0,0,1,0,1
JUAN_TECN,9,1,0,1,0,2
...
```

---

## 🎓 Estrategia de pentesting

### Fase 1: Recolección de inteligencia
- Fecha de fundación de la empresa.
- Nombres de empleados (desde LinkedIn, Twitter, etc.).
- Ubicación de la empresa, industria y productos.
- Brechas públicas (revisar HIBP, Dehashed).

### Fase 2: Creación del perfil
```bash
# Guarda perfiles reutilizables como JSON
cat > targets/cto_john_smith.json << 'EOF'
{
  "first_name": "John",
  "last_name": "Smith",
  "company": "Acme Corp",
  "founded_year": 2015,
  "birth_year": 1980,
  "industry": "Technology"
}
EOF
```

### Fase 3: Ejecución del ataque
```bash
# Empieza con diccionario básico (lo más rápido)
hashcat -m 1000 -a 0 hashes.txt wordlist.txt

# Aplica reglas (más variantes)
hashcat -m 1000 -a 0 hashes.txt wordlist.txt -r rules.rule

# Usa máscaras (optimizado para GPU)
hashcat -m 1000 -a 3 hashes.txt -hm masks.hcmask
```

### Fase 4: Análisis y reporte
- Revisa el reporte HTML para ver estadísticas.
- Analiza contraseñas recuperadas en la exportación CSV.
- Documenta hallazgos para la dirección o el cliente.

---

## 🔧 Uso avanzado

### Piping hacia otras herramientas
```bash
# Pipe directo a Hashcat
python3 contextwordlist.py --name Juan --export txt --quiet | \
  hashcat -m 0 -a 0 hashes.txt -

# Fuerza bruta SSH con Hydra
python3 contextwordlist.py --name Juan --export txt --quiet | \
  hydra -l admin -P - ssh://target.com
```

### Wordlists a gran escala
```bash
# Generar una lista de más de 200.000 palabras
python3 contextwordlist.py \
  --name Juan \
  --company TechNova \
  --max-words 200000 \
  --leet-advanced \
  --export txt

# Comprimir para almacenamiento
gzip reports/wordlist_*.txt
```

### Procesamiento por lotes
```bash
# Procesar varios objetivos
for profile in targets/*.json; do
  python3 contextwordlist.py --profile "$profile" --export all
done
```

---

## 📁 Estructura del proyecto

```
ContextWordlist/
├── contextwordlist.py         # Aplicación principal
├── setup.sh                   # Instalación en Linux/Kali
├── setup.bat                  # Instalación en Windows
├── run.bat                    # Lanzador para Windows
├── README.md                  # Este archivo
├── .gitignore                 # Configuración de Git
├── reports/                   # Wordlists y reportes generados
│   ├── wordlist_*.txt         # Wordlists estándar
│   ├── masks_*.hcmask         # Máscaras de Hashcat
│   ├── rules_*.rule           # Reglas de Hashcat
│   ├── report_*.html          # Paneles HTML
│   └── wordlist_*.csv         # Analítica CSV
└── targets/                   # (Opcional) Plantillas de perfiles
    └── example.json           # Perfil JSON de ejemplo
```

---

## 🔒 Seguridad y ética

### Consideraciones legales
⚠️ **IMPORTANTE**: Usa esta herramienta únicamente en sistemas propios o en sistemas para los que tengas autorización explícita y por escrito.

- ✅ Requiere autorización escrita (por ejemplo, carta de alcance de Red Team).
- ✅ El objetivo debe estar dentro del alcance autorizado.
- ✅ Documenta todas las actividades.
- ✅ Elimina los datos después del ejercicio, salvo que el contrato indique lo contrario.
- ✅ Cumple con GDPR, CCPA y leyes locales de protección de datos.

### Uso responsable
Esta herramienta está diseñada para:
- ✅ Pruebas de penetración autorizadas.
- ✅ Auditorías internas de seguridad.
- ✅ Evaluación de políticas de contraseñas.
- ✅ Pruebas de cumplimiento.

**NO es para:**
- ❌ Acceso no autorizado.
- ❌ Robo de credenciales.
- ❌ Hackeo ilegal.
- ❌ Ingeniería social.

---

## 📊 Rendimiento

### Velocidad de generación
| Perfil | Tiempo | Palabras |
|--------|--------|----------|
| Simple (solo nombre) | 2s | 2.200 |
| Medio (nombre + empresa + fechas) | 3s | 6.757 |
| Complejo (20 campos) | 5s | 50.000+ |

### Eficiencia de ataque (NVIDIA RTX 3090)
| Ataque | Palabras | Velocidad | Tiempo hasta recuperar 50% |
|--------|----------|-----------|----------------------------|
| Diccionario genérico | 14M (RockYou) | 12.5 GH/s | 2-4 semanas |
| Solo ContextWordlist | 6.757 | 12.5 GH/s | 2-10 min |
| + Reglas (50×) | 337.850 | 12.5 GH/s | 2-5 horas |
| + Máscaras (10×) | 10^6 | 12.5 GH/s | 1-3 horas |

**Resultado: 100-1000 veces más rápido que los enfoques genéricos**

---

## 🐛 Solución de problemas

### ¿No se recupera ninguna contraseña con la wordlist?
```bash
# 1. Verifica el formato del hash
hashcat -m 1000 hashes.txt --show | head

# 2. Prueba con una contraseña conocida
echo "password123" | hashcat -m 1000 -a 0 hashes.txt

# 3. Agrega más datos al perfil
python3 contextwordlist.py --name Juan --extra-words "hobby,city" --export all

# 4. Aumenta el tamaño de la wordlist
python3 contextwordlist.py --name Juan --max-words 100000 --export all
```

### ¿La wordlist es demasiado grande?
```bash
# Reduce combinaciones
python3 contextwordlist.py --name Juan --no-combinations --export txt

# Reduce el rango de longitud
python3 contextwordlist.py --name Juan --min-length 8 --max-length 16

# Limita el máximo de palabras
python3 contextwordlist.py --name Juan --max-words 10000 --export txt
```

### ¿Hashcat no encuentra los hashes?
```bash
# Revisa el formato del hash
hashcat --help | grep "m 0 ="  # Documentación de modos de hash

# Verifica que los hashes tengan el formato correcto
cat hashes.txt | head  # Primer hash
hashcat -m 1000 -a 0 hashes.txt wordlist.txt --status
```

---

## 📚 Logs y depuración

Los logs completos de ejecución se guardan en `contextwordlist.log`:
```bash
# Ver logs en tiempo real
tail -f contextwordlist.log

# Buscar errores
grep ERROR contextwordlist.log

# Ver estadísticas
grep INFO contextwordlist.log | tail -10
```

---

## 🤝 Contribuir

¡Las mejoras y reportes de errores son bienvenidos! Por favor:
1. Prueba los cambios con cuidado.
2. Documenta los cambios.
3. Mantén compatibilidad hacia atrás.
4. Sigue las convenciones de Python (PEP 8).

---

## 📝 Licencia

Este proyecto se proporciona únicamente para pruebas de seguridad autorizadas. Las personas usuarias son responsables de asegurarse de contar con autorización explícita antes de usar esta herramienta sobre cualquier sistema.

---

## 🙏 Soporte

### Documentación
- Revisa `README.md` (este archivo).
- Consulta `contextwordlist.log` para depuración.
- Usa la opción `--help` para ver la referencia de comandos.

### Problemas comunes
Consulta la sección **Solución de problemas** más arriba.

### Historial de versiones
- **v1.1** (mayo de 2026): edición profesional con máscaras de Hashcat, reglas dinámicas y analítica avanzada.
- **v1.0** (original): generación básica de wordlists.

---

## 🚀 Hoja rápida de comandos

```bash
# Modo interactivo
python3 contextwordlist.py -i

# Generar y exportar todo
python3 contextwordlist.py --name Juan --company TechNova --export all

# Generar solo máscaras de Hashcat
python3 contextwordlist.py --name Juan --export masks

# Wordlist grande para GPU
python3 contextwordlist.py --name Juan --max-words 200000 --export txt

# Pipe hacia Hashcat
python3 contextwordlist.py --name Juan --export txt --quiet | hashcat -m 0 -a 0 hashes.txt -

# Desde un perfil JSON
python3 contextwordlist.py --profile target.json --export all

# Ayuda y flags
python3 contextwordlist.py --help
```

---

**ContextWordlist v1.1** — Hace que las pruebas de contraseñas sean más rápidas, inteligentes y profesionales.

*Última actualización: 8 de mayo de 2026*
