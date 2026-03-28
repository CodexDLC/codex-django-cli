<!-- DOC_TYPE: GUIDE -->

# Runtime И CLI

> После разделения пакетов CLI-слой живет в `codex-django-cli`, а runtime-слой остается в `codex-django`.

## Два Слоя Внутри codex-django

В `codex-django` есть два связанных, но разных слоя:

- runtime modules, которые импортируются Django-проектом после установки;
- CLI/scaffolding tooling, которое создает или расширяет этот проект.

Это разделение помогает и в навигации по документации, и в понимании того, что должно жить в production.

## Runtime Layer

Runtime-слой это то, что Django-приложение реально импортирует и исполняет:

- `codex_django.core`
- `codex_django.system`
- `codex_django.notifications`
- `codex_django.booking`
- `codex_django.cabinet`

Здесь находятся переиспользуемые модели, mixins, selectors, adapters, Redis helpers, templates и integration points.

## CLI Layer

CLI-слой это то, чем разработчик создает и развивает структуру проекта:

- `codex_django.cli.main`
- command handlers в `codex_django.cli.commands`
- blueprint trees в `codex_django.cli.blueprints`
- rendering logic в `codex_django.cli.engine`

Этот слой отвечает за generation, orchestration и project assembly.

## Как Проводить Границу

- runtime code живет в долгой жизни приложения;
- CLI code работает до или вокруг runtime path, создавая файлы, wiring и стартовые defaults;
- generated output становится уже вашим проектным кодом и дальше может эволюционировать независимо.

## Практическое Правило

Если вопрос звучит как "что мой Django app импортирует в runtime?", оставайтесь в runtime modules.
Если вопрос звучит как "какая команда создает или расширяет эту структуру?", переходите в CLI guides и architecture pages.

## Связанные Страницы

- [Getting Started](../getting-started.md)
- [Режимы установки](./installation-modes.md)
- [Структура проекта](./project-structure.md)
- [CLI Architecture](../architecture/cli/README.md)
