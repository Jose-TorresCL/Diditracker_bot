# 🚗 Mi Didi Tracker Pro

Bot profesional de Telegram para analizar la rentabilidad de viajes Didi. Calcula automáticamente tu ganancia por km y por hora con persistencia en SQLite.

## 📋 Características

- ✅ Registra viajes con tarifa, km y duración
- 📊 Calcula $/km y $/hora automáticamente
- 📈 Estadísticas diarias y semanales
- 💾 Persistencia en SQLite3
- 🎯 Indicador de meta ($/km >= $350)
- 🔒 Multi-usuario seguro
- 🎨 Mensajes con formato Markdown
- 📱 Diseño profesional con emojis

## 🛠️ Requisitos

- Python 3.11+
- pip (gestor de paquetes)
- Cuenta de Telegram
- Token de bot de Telegram

## ⚙️ Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <tu-repositorio>
cd Mi-Didi-Tracker-Pro
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env` y reemplaza `tu_token_aqui` con tu token de bot:

```bash
cp .env.example .env
```

**Edita `.env`:**
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
DATABASE_PATH=data/didi_tracker.db
META_PER_KM=350
```

### 5. Obtener tu Token de Telegram

1. Abre Telegram y busca `@BotFather`
2. Envía `/newbot` y sigue las instrucciones
3. Copia el token que te proporciona
4. Pégalo en tu archivo `.env`

## 🚀 Uso

### Ejecutar desde terminal

```bash
python src/bot.py
```

### Ejecutar desde VS Code

**Opción 1: Usar tasks (Ctrl+Shift+P)**
- Presiona `Ctrl+Shift+P`
- Busca "Tasks: Run Task"
- Selecciona "Run Bot"

**Opción 2: Usar debugger (F5)**
- Presiona `F5` para iniciar con depuración
- Establece breakpoints según sea necesario

## 📝 Comandos del Bot

### `/start`
Muestra el menú inicial con instrucciones

```
/start
```

### `/add TARIFA KM MINUTOS`
Registra un viaje y calcula métricas

```
/add 5200 14 28
```

Respuesta:
```
✅ Viaje Registrado

💰 Tarifa: $5,200
🚗 Distancia: 14.0 km
⏱️ Duración: 28 min

Rentabilidad:
📊 $/km: $371 (meta: $350/km)
💵 $/hora: $783

✅ ¡Superaste la meta!
```

### `/stats`
Ver estadísticas del día actual

```
/stats
```

Respuesta:
```
📊 Estadísticas de Hoy

🚗 Viajes: 5
💰 Total ganado: $26,000
📍 KM totales: 70.5 km
📈 Promedio $/km: $369 (meta: $350/km)

✅ ¡Superaste la meta!
```

### `/week`
Ver estadísticas de la última semana

```
/week
```

### `/reset`
Borrar datos del día actual (requiere confirmación)

```
/reset confirm
```

## 📊 Estructura del Proyecto

```
Mi-Didi-Tracker-Pro/
├── src/
│   └── bot.py                 # Código principal del bot
├── data/
│   └── didi_tracker.db        # Base de datos SQLite (auto-creada)
├── .vscode/
│   ├── tasks.json             # Tareas para ejecutar
│   └── launch.json            # Configuración de debugger
├── .env                       # Variables de entorno
├── .gitignore                 # Archivos a ignorar en git
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## 🗄️ Base de Datos

### Tabla `trips`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Clave primaria |
| user_id | INTEGER | ID de usuario Telegram |
| user_name | TEXT | Nombre del usuario |
| tariff | REAL | Tarifa del viaje en pesos |
| distance | REAL | Distancia en km |
| duration | INTEGER | Duración en minutos |
| per_km | REAL | Ganancia por km |
| per_hour | REAL | Ganancia por hora |
| timestamp | DATETIME | Fecha y hora del registro |
| date | TEXT | Fecha en formato YYYY-MM-DD |

## 🔧 Troubleshooting

### Error: "BOT_TOKEN no está configurado"
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Comprueba que `BOT_TOKEN=` tiene un valor válido

### Error: "Permiso denegado" en data/
- Verifica que tu usuario tiene permiso de escritura en la carpeta
- Crea manualmente la carpeta `data/` si no existe

### El bot no responde
- Verifica que el token es correcto
- Comprueba que tienes conexión a internet
- Revisa los logs en la consola

## 📦 Dependencias

- **python-telegram-bot**: Cliente oficial de Telegram para Python
- **python-dotenv**: Carga variables de entorno desde archivo `.env`
- **sqlite3**: Base de datos incluida en Python (no requiere instalación)

## 🤝 Contribuir

¿Tienes sugerencias o mejoras? ¡Crear un issue o pull request!

## 📄 Licencia

Este proyecto es de uso libre.

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en la consola
2. Verifica la configuración de `.env`
3. Asegúrate de que el token sea válido

---

**Hecho con ❤️ para conductores Didi**
