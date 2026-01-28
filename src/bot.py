"""
Mi Didi Tracker Pro - Bot de Telegram para análisis de rentabilidad de viajes Didi
Analiza $/km y $/hora para conductores, con persistencia en SQLite
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/didi_tracker.db')
META_PER_KM = int(os.getenv('META_PER_KM', 350))

class DidiTrackerDB:
    """Gestor de base de datos SQLite para registro de viajes"""

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Inicializa la conexión a la base de datos
        
        Args:
            db_path: Ruta del archivo de base de datos
        """
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Crea la tabla 'trips' si no existe"""
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT,
                    tariff REAL NOT NULL,
                    distance REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    per_km REAL NOT NULL,
                    per_hour REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    date TEXT NOT NULL
                )
            ''')
            conn.commit()
        logger.info("Base de datos inicializada correctamente")

    def add_trip(self, user_id: int, user_name: str, tariff: float, 
                 distance: float, duration: int) -> Tuple[float, float]:
        """
        Registra un viaje y calcula métricas
        
        Args:
            user_id: ID del usuario en Telegram
            user_name: Nombre del usuario
            tariff: Tarifa del viaje en pesos
            distance: Distancia en km
            duration: Duración en minutos
            
        Returns:
            Tupla (per_km, per_hour)
        """
        per_km = tariff / distance if distance > 0 else 0
        per_hour = (tariff / (duration / 60)) if duration > 0 else 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trips 
                (user_id, user_name, tariff, distance, duration, per_km, per_hour, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, tariff, distance, duration, per_km, per_hour, today))
            conn.commit()
        
        logger.info(f"Viaje registrado para {user_name}: ${tariff} ({distance}km, {duration}min)")
        return per_km, per_hour

    def get_daily_stats(self, user_id: int, date: Optional[str] = None) -> dict:
        """
        Obtiene estadísticas del día especificado
        
        Args:
            user_id: ID del usuario
            date: Fecha en formato YYYY-MM-DD (por defecto: hoy)
            
        Returns:
            Diccionario con estadísticas del día
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*), SUM(tariff), SUM(distance), AVG(per_km)
                FROM trips
                WHERE user_id = ? AND date = ?
            ''', (user_id, date))
            
            result = cursor.fetchone()
            trips_count, total_money, total_distance, avg_per_km = result
            
            return {
                'trips_count': trips_count or 0,
                'total_money': total_money or 0,
                'total_distance': total_distance or 0,
                'avg_per_km': avg_per_km or 0
            }

    def get_weekly_stats(self, user_id: int) -> dict:
        """
        Obtiene estadísticas de la última semana (últimos 7 días)
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con estadísticas semanales
        """
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*), SUM(tariff), SUM(distance), AVG(per_km)
                FROM trips
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            result = cursor.fetchone()
            trips_count, total_money, total_distance, avg_per_km = result
            
            return {
                'trips_count': trips_count or 0,
                'total_money': total_money or 0,
                'total_distance': total_distance or 0,
                'avg_per_km': avg_per_km or 0
            }

    def delete_daily_trips(self, user_id: int, date: Optional[str] = None):
        """
        Elimina todos los viajes de un día específico
        
        Args:
            user_id: ID del usuario
            date: Fecha en formato YYYY-MM-DD (por defecto: hoy)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM trips WHERE user_id = ? AND date = ?', 
                         (user_id, date))
            conn.commit()
        logger.info(f"Datos del {date} eliminados para usuario {user_id}")


# Instancia global de la base de datos
db = DidiTrackerDB()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /start - Menú inicial con instrucciones
    
    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la aplicación
    """
    welcome_text = f"""
*🚗 Mi Didi Tracker Pro 🚗*

¡Hola! Soy tu asistente para analizar la rentabilidad de tus viajes Didi.

*📋 Comandos disponibles:*

• `/add TARIFA KM MIN` - Registra un viaje
  Ejemplo: `/add 5200 14 28`

• `/stats` - Ver estadísticas de hoy 📊

• `/week` - Ver estadísticas de la semana 📈

• `/reset` - Borrar datos de hoy ⚠️

*💡 Cómo funciona:*
Después de cada viaje, envía `/add TARIFA KM MINUTOS`
Te mostraré tu ganancia por km (meta: ${META_PER_KM}/km) y por hora.

¡Comencemos a rastrear tus ganancias! 💰
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )
    logger.info(f"Usuario iniciado: {update.effective_user.username}")


async def add_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /add TARIFA KM MIN - Registra un viaje y calcula métricas
    
    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la aplicación
    """
    try:
        if len(context.args) != 3:
            await update.message.reply_text(
                "❌ Formato incorrecto\n\n"
                "Usa: `/add TARIFA KM MINUTOS`\n"
                "Ejemplo: `/add 5200 14 28`",
                parse_mode='Markdown'
            )
            return
        
        tariff = float(context.args[0])
        distance = float(context.args[1])
        duration = int(context.args[2])
        
        if tariff <= 0 or distance <= 0 or duration <= 0:
            await update.message.reply_text(
                "❌ Todos los valores deben ser mayores a 0",
                parse_mode='Markdown'
            )
            return
        
        user_id = update.effective_user.id
        user_name = update.effective_user.username or update.effective_user.first_name
        
        per_km, per_hour = db.add_trip(user_id, user_name, tariff, distance, duration)
        
        # Determinar emoji basado en meta
        status_emoji = "✅" if per_km >= META_PER_KM else "⚠️"
        
        response_text = f"""
{status_emoji} *Viaje Registrado*

💰 Tarifa: ${tariff:,.0f}
🚗 Distancia: {distance:.1f} km
⏱️  Duración: {duration} min

*Rentabilidad:*
📊 $/km: ${per_km:.0f} (meta: ${META_PER_KM}/km)
💵 $/hora: ${per_hour:.0f}

{status_emoji if per_km >= META_PER_KM else '🔴'} {'¡Superaste la meta!' if per_km >= META_PER_KM else 'Por debajo de la meta'}
"""
        
        await update.message.reply_text(
            response_text,
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Error en los valores ingresados\n\n"
            "Verifica que sean números válidos:\n"
            "`/add TARIFA KM MINUTOS`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error al agregar viaje: {str(e)}")
        await update.message.reply_text(
            "❌ Error al registrar el viaje. Intenta nuevamente.",
            parse_mode='Markdown'
        )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /stats - Muestra estadísticas del día actual
    
    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la aplicación
    """
    try:
        user_id = update.effective_user.id
        stats_data = db.get_daily_stats(user_id)
        
        if stats_data['trips_count'] == 0:
            await update.message.reply_text(
                "📊 *Estadísticas de Hoy*\n\n"
                "No hay viajes registrados aún.",
                parse_mode='Markdown'
            )
            return
        
        status_emoji = "✅" if stats_data['avg_per_km'] >= META_PER_KM else "⚠️"
        
        stats_text = f"""
📊 *Estadísticas de Hoy*

🚗 Viajes: {stats_data['trips_count']}
💰 Total ganado: ${stats_data['total_money']:,.0f}
📍 KM totales: {stats_data['total_distance']:.1f} km
📈 Promedio $/km: ${stats_data['avg_per_km']:.0f} (meta: ${META_PER_KM}/km)

{status_emoji} {'¡Superaste la meta!' if stats_data['avg_per_km'] >= META_PER_KM else 'Por debajo de la meta'}
"""
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        await update.message.reply_text(
            "❌ Error al obtener estadísticas.",
            parse_mode='Markdown'
        )


async def week_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /week - Muestra estadísticas de la última semana
    
    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la aplicación
    """
    try:
        user_id = update.effective_user.id
        stats_data = db.get_weekly_stats(user_id)
        
        if stats_data['trips_count'] == 0:
            await update.message.reply_text(
                "📈 *Estadísticas de la Semana*\n\n"
                "No hay viajes registrados en los últimos 7 días.",
                parse_mode='Markdown'
            )
            return
        
        status_emoji = "✅" if stats_data['avg_per_km'] >= META_PER_KM else "⚠️"
        
        stats_text = f"""
📈 *Estadísticas de la Última Semana*

🚗 Viajes: {stats_data['trips_count']}
💰 Total ganado: ${stats_data['total_money']:,.0f}
📍 KM totales: {stats_data['total_distance']:.1f} km
📊 Promedio $/km: ${stats_data['avg_per_km']:.0f} (meta: ${META_PER_KM}/km)

{status_emoji} {'¡Excelente desempeño!' if stats_data['avg_per_km'] >= META_PER_KM else 'Busca mejorar tus ganancias'}
"""
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas semanales: {str(e)}")
        await update.message.reply_text(
            "❌ Error al obtener estadísticas.",
            parse_mode='Markdown'
        )


async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /reset - Borra todos los viajes del día actual
    
    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la aplicación
    """
    try:
        user_id = update.effective_user.id
        
        # Confirmación de seguridad
        if len(context.args) == 0 or context.args[0].lower() != 'confirm':
            await update.message.reply_text(
                "⚠️ *Confirmación Requerida*\n\n"
                "Esto borrará todos los viajes de hoy.\n\n"
                "Para confirmar, usa: `/reset confirm`",
                parse_mode='Markdown'
            )
            return
        
        db.delete_daily_trips(user_id)
        
        await update.message.reply_text(
            "✅ Datos de hoy eliminados correctamente.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error al resetear datos: {str(e)}")
        await update.message.reply_text(
            "❌ Error al borrar los datos.",
            parse_mode='Markdown'
        )


def main():
    """Función principal - Inicia el bot"""
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN no está configurado en .env")
        raise ValueError("BOT_TOKEN es requerido")
    
    # Crear aplicación
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_trip))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("week", week_stats))
    app.add_handler(CommandHandler("reset", reset_data))
    
    # Iniciar bot
    logger.info("🚀 Bot iniciado - polling activo")
    print("=" * 50)
    print("🚗 Mi Didi Tracker Pro - Ejecutándose")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
