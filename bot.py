import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import json

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
FLOWISE_API_URL = os.getenv('FLOWISE_API_URL', 'https://fork.start-ai.ru/api/v1/prediction/194a0cbf-2f66-4afc-afa7-b3fa340216a4')
FLOWISE_API_KEY = os.getenv('FLOWISE_API_KEY')

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
        # Отправляем индикатор набора текста
        await update.message.chat.send_action(action="typing")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Добавляем API ключ, если он установлен
        if FLOWISE_API_KEY:
            headers['Authorization'] = f'Bearer {FLOWISE_API_KEY}'

        # Подготовка данных для отправки в FlowiseAI
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
                result = await response.json()
                # Извлекаем ответ из результата
                answer = result.get('text', 'Извините, не удалось получить ответ.')
                await update.message.reply_text(answer)
            else:
                error_msg = f"Ошибка при получении ответа: HTTP {response.status_code}"
                logger.error(error_msg)
                await update.message.reply_text(
                    "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
                )

    except httpx.TimeoutException:
        logger.error("Timeout при запросе к FlowiseAI API")
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
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 