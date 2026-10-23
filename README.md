# base_developing_agent

По заветам Лехи Голобурдина. Пишем своего кодинг-агента.

Первоисточник вот здесь, обязательно посмотри:
https://www.youtube.com/watch?v=H7FSTj4x4xQ&t=53s

# Agentloop

ИИ-агент - связка большой языковой модели и доступных для вызова ею инструментов.

Ядро агентного цикла может быть реализован в 6 строках кода:
```python
while True:
    response = callLLM(messages)
    if response.toolCalls:
        messages.append(executeTools(response.toolCalls))
    else:
        return response
```

# Инструменты

