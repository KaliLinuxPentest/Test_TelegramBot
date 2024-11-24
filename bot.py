import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import json
from telegram.error import TimedOut, NetworkError

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FLOWISE_API_URL = os.getenv('FLOWISE_API_URL')
FLOWISE_API_KEY = os.getenv('FLOWISE_API_KEY')

# Настройки для подключения
CONNECT_TIMEOUT = 30.0
READ_TIMEOUT = 30.0
WRITE_TIMEOUT = 30.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Привет! Я бот-ассистент. Отправьте мне ваш вопрос, и я постараюсь помочь.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text('Отправьте мне текстовое сообщение с вашим вопросом.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    try:
        await update.message.chat.send_action(action="typing")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if FLOWISE_API_KEY:
            headers['Authorization'] = f'Bearer {FLOWISE_API_KEY}'

        payload = {
            "question": update.message.text,
            "overrideConfig": {
                "returnSourceDocuments": True
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                FLOWISE_API_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                try:
                    result_json = response.json()  # Используем встроенный метод json()
                    answer = result_json.get('text', 'Извините, не удалось получить ответ.')
                    await update.message.reply_text(answer)
                except json.JSONDecodeError:
                    logger.error("Ошибка при разборе JSON ответа")
                    await update.message.reply_text(
                        "Извините, произошла ошибка при обработке ответа. Попробуйте позже."
                    )
            else:
                error_msg = f"Ошибка при получении ответа: HTTP {response.status_code}"
                logger.error(error_msg)
                await update.message.reply_text(
                    "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
                )

    except (httpx.TimeoutException, TimedOut, NetworkError) as e:
        logger.error(f"Timeout или сетевая ошибка: {str(e)}")
        await update.message.reply_text(
            "Извините, время ожидания ответа истекло. Попробуйте повторить запрос."
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    if update.message:
        await update.message.reply_text(
            "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
        )

def main() -> None:
    """Запуск бота"""
    # Создаем приложение с настройками таймаутов
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(CONNECT_TIMEOUT)
        .read_timeout(READ_TIMEOUT)
        .write_timeout(WRITE_TIMEOUT)
        .build()
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 