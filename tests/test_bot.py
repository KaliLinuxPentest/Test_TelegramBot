import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from telegram import Update, Message, Chat, User
import sys
import json

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import (
    handle_message, FLOWISE_API_URL, FLOWISE_API_KEY,
    start, help_command, error_handler, main, TELEGRAM_TOKEN
)

# Фикстура для создания мок-объекта Update
@pytest.fixture
def mock_update():
    update = AsyncMock(spec=Update)
    message = AsyncMock(spec=Message)
    chat = AsyncMock(spec=Chat)
    user = AsyncMock(spec=User)
    
    # Настройка атрибутов
    user.id = 12345
    user.first_name = "Test User"
    chat.id = 12345
    message.chat = chat
    message.from_user = user
    message.text = "Как называется фильм о создании Леонардо да Винчи?"
    update.message = message
    
    return update

# Фикстура для создания мок-объекта Context
@pytest.fixture
def mock_context():
    context = MagicMock()
    return context

# Фикстура для создания мок-объекта AsyncClient
@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.__aenter__.return_value = client
    return client

# Тест успешного запроса к FlowiseAI
@pytest.mark.asyncio
async def test_successful_message_handling(mock_update, mock_context, mock_client):
    # Подготовка мок-ответа от FlowiseAI
    mock_response = {
        "text": "Фильм о Леонардо да Винчи называется 'Leonardo'. Он был выпущен в 2023 году."
    }
    
    mock_response_obj = AsyncMock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_client.post.return_value = mock_response_obj
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    # Проверяем, что был отправлен правильный запрос
    mock_client.post.assert_called_once_with(
        FLOWISE_API_URL,
        json={
            "question": mock_update.message.text,
            "overrideConfig": {
                "returnSourceDocuments": True
            }
        },
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {FLOWISE_API_KEY}'
        } if FLOWISE_API_KEY else {'Content-Type': 'application/json'},
        timeout=30.0
    )
    
    # Проверяем, что ответ был отправлен пользователю
    mock_update.message.reply_text.assert_called_once_with(mock_response["text"])

# Тест обработки ошибки HTTP
@pytest.mark.asyncio
async def test_http_error_handling(mock_update, mock_context, mock_client):
    mock_client.post.return_value = AsyncMock(status_code=500)
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    # Проверяем сообщение об ошибке
    mock_update.message.reply_text.assert_called_once_with(
        "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
    )

# Тест обработки таймаута
@pytest.mark.asyncio
async def test_timeout_handling(mock_update, mock_context, mock_client):
    mock_client.post.side_effect = httpx.TimeoutException("Connection timeout")
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    # Проверяем сообщение о таймауте
    mock_update.message.reply_text.assert_called_once_with(
        "Извините, время ожидания ответа истекло. Попробуйте повторить запрос."
    )

# Тест на проверку формата ответа от FlowiseAI
@pytest.mark.asyncio
async def test_flowise_response_format(mock_update, mock_context, mock_client):
    # Подготовка мок-ответа с дополнительными полями
    mock_response = {
        "text": "Тестовый ответ",
        "sourceDocuments": [
            {"pageContent": "Исходный документ 1"},
            {"pageContent": "Исходный документ 2"}
        ]
    }
    
    mock_response_obj = AsyncMock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_client.post.return_value = mock_response_obj
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    # Проверяем, что используется только поле text из ответа
    mock_update.message.reply_text.assert_called_once_with(mock_response["text"])

# Тест на проверку отправки typing action
@pytest.mark.asyncio
async def test_typing_action(mock_update, mock_context, mock_client):
    mock_response_obj = AsyncMock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.return_value = {"text": "Тестовый ответ"}
    mock_client.post.return_value = mock_response_obj
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    # Проверяем, что был отправлен typing action
    mock_update.message.chat.send_action.assert_called_once_with(action="typing")

# Тест команды /start
@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        'Привет! Я бот-ассистент. Отправьте мне ваш вопрос, и я постараюсь помочь.'
    )

# Тест команды /help
@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        'Отправьте мне текстовое сообщение с вашим вопросом.'
    )

# Тест обработчика ошибок
@pytest.mark.asyncio
async def test_error_handler(mock_update, mock_context):
    # Создаем тестовую ошибку
    test_error = Exception("Test error")
    mock_context.error = test_error
    
    await error_handler(mock_update, mock_context)
    
    # Проверяем логирование ошибки
    assert mock_update.message.reply_text.called
    mock_update.message.reply_text.assert_called_once_with(
        "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
    )

# Тест обработчика ошибок без сообщения
@pytest.mark.asyncio
async def test_error_handler_no_message():
    update = AsyncMock(spec=Update)
    update.message = None
    context = MagicMock()
    context.error = Exception("Test error")
    
    await error_handler(update, context)
    
    # Проверяем, что ошибка обработана без исключений
    assert True

# Тест функции main
def test_main():
    mock_application = MagicMock()
    mock_builder = MagicMock()
    mock_builder.token.return_value.build.return_value = mock_application
    
    with patch('telegram.ext.Application.builder', return_value=mock_builder):
        main()
        
        # Проверяем, что токен использован правильно
        mock_builder.token.assert_called_once_with(TELEGRAM_TOKEN)
        
        # Проверяем, что все обработчики добавлены
        assert mock_application.add_handler.call_count == 3
        assert mock_application.add_error_handler.call_count == 1
        
        # Проверяем, что бот запущен
        mock_application.run_polling.assert_called_once()

# Тест обработки некорректного JSON-ответа
@pytest.mark.asyncio
async def test_invalid_json_response(mock_update, mock_context, mock_client):
    mock_response_obj = AsyncMock()
    mock_response_obj.status_code = 200
    mock_response_obj.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_client.post.return_value = mock_response_obj
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once_with(
        "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
    )

# Тест на отсутствие поля text в ответе
@pytest.mark.asyncio
async def test_missing_text_field(mock_update, mock_context, mock_client):
    mock_response = {
        "sourceDocuments": [
            {"pageContent": "Исходный документ 1"}
        ]
    }
    
    mock_response_obj = AsyncMock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_client.post.return_value = mock_response_obj
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once_with(
        "Извините, не удалось получить ответ."
    )

# Тест на обработку сетевых ошибок
@pytest.mark.asyncio
async def test_network_error(mock_update, mock_context, mock_client):
    mock_client.post.side_effect = httpx.NetworkError("Connection failed")
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        await handle_message(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once_with(
        "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
    )