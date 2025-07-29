# 🚀 FastFSX

📁 **Роутинг FastAPI на основе структуры файловой системы**  
Вдохновлён подходом [Next.js](https://nextjs.org/docs/routing) — вы описываете маршруты через структуру папок и файлы `route.py`, а `fastfsx` автоматически подключает их в ваше FastAPI-приложение.

---

## 🔧 Установка

С помощью pip:

```bash
pip install fastfsx
````

Или через Poetry:

```bash
poetry add fastfsx
```

---

## ⚙️ Использование

```python
from fastapi import FastAPI
from fastfsx import FileRouter

app = FastAPI()
app.include_router(FileRouter("pages").build())
```

---

## 📁 Пример структуры папок

```text
pages/
├── users/
│   ├── [id]/              # динамический маршрут: /users/{id}
│   │   └── route.py
│   └── route.py           # маршрут: /users
├── (admin)/               # группирующая папка, игнорируется в маршруте
│   └── dashboard/
│       └── route.py       # маршрут: /dashboard
└── route.py               # корневой маршрут: /
```

Каждый файл `route.py` должен экспортировать FastAPI `APIRouter`:

```python
# pages/users/route.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_users():
    return [{"id": 1, "name": "Alice"}]
```

---

## ✨ Возможности

* 📁 Построение маршрутов на основе структуры папок
* 📌 Поддержка динамических сегментов маршрута (`[id]` → `{id}`)
* 🚫 Игнорирование группирующих папок (`(admin)`)
* 🔀 Глубоко вложенные маршруты
* ✅ Минимум конфигурации, максимум гибкости

---

## 📦 Устройство

Функциональность обернута в класс `FileRouter`, который строит дерево маршрутов и возвращает `APIRouter`, готовый для подключения к приложению FastAPI.

---

## 🛠 В планах

* Поддержка маршрутов `[[...slug]]` → `{slug:path}`
* Хуки и расширения
* Поддержка префиксов и middlewares на уровне папок

---

## 📄 Лицензия

Проект распространяется под лицензией MIT.
