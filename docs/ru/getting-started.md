<!-- DOC_TYPE: GUIDE -->

> Этот репозиторий документирует пакет `codex-django-cli`. Он предоставляет леса (scaffolding) и блюпринты для инициализации проектов.

# Быстрый старт

## Почему не `django-admin startproject`?

В отличие от стандартной утилиты Django, которая создает абсолютно пустую структуру, `codex-django` генерирует полноценную архитектуру, готовую к production:
- **Современный Frontend:** Сразу подключены **HTMX 2.x** и **Alpine.js**, настроена компиляция CSS и модульная статика.
- **Готовое Ядро (Core/System):** Преднастроенные ASGI, Redis, система нотификаций, базовые шаблоны кабинета и SEO.
- **Интерактивное Меню:** Вам не нужно зубрить флаги. Основная работа идет через визуальное меню `codex-django menu`, включая `init`, добавление фичей и генерацию Docker/CI конфигураций.

## Установка CLI

Установите инструмент глобально через `uv` (рекомендуется):

```bash
uv tool install codex-django-cli
```

Либо классическая установка через `pip`:

```bash
pip install codex-django-cli
```

`codex-django-cli` требует Python 3.12+.

## Создание нового проекта

Пакет регистрирует команду `codex-django`. Вы можете запустить интерактивное меню или развернуть проект сразу со всеми флагами:

```bash
# 1. Интерактивное меню (мастер настройки)
codex-django menu

# 2. Быстрый путь для опытных пользователей (с флагами):
codex-django init myproject --i18n --languages en,ru --with-cabinet --with-booking
cd myproject
# Убедитесь, что вы работаете в виртуальном окружении
pip install -e .
python src/myproject/manage.py migrate
python src/myproject/manage.py runserver_plus
```

> [!IMPORTANT]
> **Связь с библиотекой `codex-django`**: Команда `pip install -e .` критически важна! Она скачивает и устанавливает основную библиотеку-рантайм `codex-django`. Сам `codex-django-cli` — это лишь генератор каркаса. Реальная логика (HTMX-ответы, шаблоны кабинета, нотификации, SEO-база) живет именно в `codex-django`. **Без неё ваш сгенерированный проект работать не будет.**

Меню `codex-django menu` (или просто `codex-django`) особенно удобно, если вы хотите выбрать i18n-режим, коды языков и optional modules без запоминания флагов. Но если вы опытный пользователь, явные флаги — самый быстрый путь.

Если проект уже создан, добавляйте новые модули интерактивно:

```bash
codex-django menu
# -> Выберите "🧩  Scaffolding (Apps/Modules)"
# -> Выберите целевой проект
# -> Выбирайте "Basic app", "Client Cabinet" или "Booking"
```

Генератор создаст нужные файлы и напечатает точные шаги по подключению в `settings.py`, `urls.py` и `admin.py`.

## Разработка самого CLI

При участии в разработке самого CLI (contributing):

```bash
uv sync --extra dev
uv run python tools/dev/check.py
```
