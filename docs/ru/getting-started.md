<!-- DOC_TYPE: GUIDE -->

> Этот репозиторий документирует пакет `codex-django-cli`. Он предоставляет леса (scaffolding) и блюпринты для инициализации проектов.

# Быстрый старт

## Почему не `django-admin startproject`?

В отличие от стандартной утилиты Django, которая создает абсолютно пустую структуру, `codex-django` собирает гораздо более насыщенную базовую архитектуру:
- **Современный Frontend:** Сразу подключены **HTMX 2.x** и **Alpine.js**, настроены модульная статика, базовые темы и CSS-структура.
- **Готовое Ядро (Core/System):** Преднастроены ASGI, Redis, SEO/admin-основа, reusable project settings и opinionated runtime-layout, который затем можно расширять cabinet-, conversations-, booking- и service-worker слоями.
- **Интерактивное Меню:** Вам не нужно зубрить флаги. Через `codex-django menu` можно создать новый проект, расширить существующий, сгенерировать repo config файлы и подготовить Docker/CI-обвязку из одного menu-flow.

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
python src/myproject/manage.py startserver
```

> [!IMPORTANT]
> **Связь с библиотекой `codex-django`**: Команда `pip install -e .` критически важна! Она скачивает и устанавливает основную runtime-библиотеку `codex-django`. Сам `codex-django-cli` — это генератор архитектурного каркаса. Реальная runtime-логика HTMX-ответов, cabinet templates, reusable settings и SEO support живет именно в `codex-django`. **Без неё ваш сгенерированный проект работать не будет.**

Меню `codex-django menu` (или просто `codex-django`) особенно удобно, если вы хотите выбрать i18n-режим, коды языков, слои генерации и compare-copy сценарии для уже найденных модулей без запоминания флагов.

Если проект уже создан, добавляйте новые модули интерактивно:

```bash
codex-django menu
# -> Выберите "🧩  Extend existing Django project"
# -> Выберите целевой проект из src/
# -> Выберите Cabinet, Conversations, Booking engine, Booking cabinet integration или compare-copy сценарий
```

Генератор создаст нужные файлы и напечатает точные дальнейшие шаги по подключению и проверке результата.

## Разработка самого CLI

При участии в разработке самого CLI (contributing):

```bash
uv sync --extra dev
uv run python tools/dev/check.py
```
