<!-- DOC_TYPE: GUIDE -->

# Blueprint Workflow

## Как Работают Scaffold-Команды

Каждый крупный CLI-flow переводит намерение разработчика в один или несколько blueprint renders.

Типичный flow:

1. Вы выбираете сценарий вроде `init`, расширения проекта через меню или генерации repository config files.
2. Команда или orchestration-layer определяет нужное blueprint family.
3. `CLIEngine` рендерит шаблоны и копирует static assets в target project или repository.
4. Команда печатает follow-up шаги, которые еще нужно применить вручную.

## Семейства Blueprints

Blueprint tree в CLI организован по типу результата:

- `repo` для repository shell files;
- `project` для базовой Django project layout;
- `cabinet` для отдельного project-local cabinet layer;
- `features` для cross-cutting functional bundles;
- `apps` для lower-level app building blocks;
- `deploy` для operational и deployment-oriented output.

## Безопасный Рабочий Паттерн

Используйте такой порядок при добавлении новой функциональности:

1. Сгенерировать файлы.
2. Прочитать follow-up instructions.
3. Довести wiring в settings, admin, URLs и migrations.
4. Прогнать локальные проверки.

## Почему Это Важно

`codex-django` это не только пакет с reusable modules.
Это еще и project-construction framework, поэтому blueprint workflow является частью самого продукта.

## Связанные Страницы

- [Getting Started](../getting-started.md)
- [CLI Architecture](../architecture/cli/README.md)
- [CLI Blueprints](../architecture/cli/blueprints.md)
