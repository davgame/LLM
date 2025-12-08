# LLM

## Для успешного тестирования qwen2.5:7b
Powershell
```sh
ollama pull qwen2.5:7b
```
далее
```sh
ollama serve
```
далее:запуск и тестирование сервера Fast API с корня, не переходя в /src
```sh
uvicorn src.server:app --reload --port 3001
```
Хостинг Fast API
http://localhost:3001/docs


### Compile и холодный запуск фронта

```sh
npm run dev
```
планирую запустить модель на фронте и протестировать

Языковая модель для рекомендательной системы qwen2.5:7b

