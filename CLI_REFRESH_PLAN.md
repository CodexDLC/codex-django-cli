# План рефреша `codex-django-cli` → v0.4.0

> **Как пользоваться.** План разбит на самодостаточные этапы. Каждый этап — отдельная задача для Sonnet в новом чате: в каждом указаны входные файлы, что делаем, какие тесты пишем, как проверяем. Контекст между этапами минимальный — ключевое состояние фиксируется коммитами и зелёными тестами.
>
> **Правила выполнения:**
> 1. Один этап = один коммит (или несколько осмысленных коммитов одной темы).
> 2. В конце этапа: `pytest -q` зелёный + ручная проверка "dry-run" для затронутого блюпринта, где возможно.
> 3. Галочки `- [ ]` ставить после фактической проверки тестами. Не полагаться только на «глазом посмотрел».
> 4. Этап 10 (ручная проверка на тестовом стенде) и Этап 11 (релиз) — только после всех технических этапов.
> 5. По завершении всех этапов файл удалить из корня репозитория.
>
> **Архитектурный принцип генерируемого кода (применять во всех этапах):**
> - **Thin Views** — вью только принимает запрос и вызывает метод сервиса/селектора. HTTP-логика не смешивается с бизнес-логикой.
> - **Services** — write-операции (create, update, cancel и т.п.) в отдельном модуле `services/<domain>.py`. Каждый метод — самодостаточная функция, тестируемая без Django test client.
> - **Selectors** — read-операции (запросы к БД, агрегации) в `selectors/<domain>.py`. Принимают plain-аргументы, возвращают QuerySet или dataclass.
> - **Структура файлов:** если вью одна — файл `views/<domain>.py`; если несколько — папка `views/<domain>/` с `__init__.py`.
> - **Цель:** каждый `service.method()` и `selector.query()` должен тестироваться unit-тестом без запуска HTTP-стека.

---

## Контекст

**Зачем рефреш:** текущий CLI (v0.3.0) сильно устарел относительно `codex-django` библиотеки, к которой он генерирует проекты.

**Что произошло в codex-django:**
- Введён **Cabinet 2.0 API**: регистрация модулей через `declare(space, module, topbar, sidebar)` + публичные типы (`TopbarEntry`, `SidebarItem`, `DataTableData`, `CalendarGridData`, и т.д.).
- **`DashboardSelector.extend(cache_key=..., cache_ttl=...)`** — декоратор для провайдеров данных (Redis кэш, JSON сериализация).
- **Adapter pattern** для booking: библиотека не импортирует модели, проект регистрирует адаптеры.
- **Booking split** (Block 6 ✅): solo/multi сервисы, ChainFinder из codex-services.
- Публичный API собран в `codex_django.cabinet` и `codex_django.booking`.

**Что устарело в CLI:**
1. **Баг "standard init ставит booking в cabinet"** — частично зафикшен (booking вынесен в отдельный блюпринт `cabinet_booking/`), но остались рудименты:
   - `cabinet/services/booking.py.j2` — **дубликат** того, что теперь в `cabinet_booking/services/booking.py.j2`.
   - `cabinet/views/booking.py.j2` — дубликат, не удалён.
   - `cabinet/booking_bridge.py.j2` — **отсутствует в HEAD** (удалён корректно), остался только в `cabinet_booking/`.
   - `cabinet/services/analytics.py.j2` и `cabinet/context_processors.py.j2` — mock-данные содержат hardcoded «bookings» без обёртки в `{%- if with_booking %}`.
   - `MODULE_MARKERS["booking_cabinet"]` указывает на `cabinet/booking_bridge.py` — путь корректный только если booking установлен.
   - Нет negative-теста «standard init → в выходе нет `cabinet/booking/*`, `booking_bridge.py`, `services/booking.py`».
2. **Блюпринты не на Cabinet 2.0 API** — `cabinet.py.j2` hook-файлы требуют проверки/переписывания под `declare()`.
3. **Hardcoded константы** — `LOGIN_URL = "/cabinet/login/"` (settings/modules/codex.py.j2), имена app, demo-данные на русском.
4. **Нет `settings/modules/booking.py.j2`, `notifications.py.j2`** — вся конфигурация booking/notifications размазана.
5. **Рудиментные комментарии** `{# CODEX_DJANGO_CLI BLUEPRINT STATUS: MOVE_TO_CLI_BLUEPRINT #}` в шаблонах (шаблон уже в блюпринте — это устаревший маркер).
6. **Нет DRF API scaffold** — только Django views.
7. **i18n частично нарушена** — hardcoded русские строки в analytics, context_processors.

**Итог:** готовим **v0.4.0** (minor bump: ломающие изменения в модели блюпринтов, но CLI surface стабилен).

---

## Входные файлы для всего плана

**Критические файлы CLI (читать перед началом):**
- [src/codex_django_cli/commands/install.py](src/codex_django_cli/commands/install.py) — оркестратор scaffold.
- [src/codex_django_cli/main.py](src/codex_django_cli/main.py) — меню/CLI args/wizards.
- [src/codex_django_cli/prompts.py](src/codex_django_cli/prompts.py) — questionary-prompts.
- [src/codex_django_cli/engine.py](src/codex_django_cli/engine.py) — Jinja-рендер, обход блюпринтов.
- [src/codex_django_cli/commands/init.py](src/codex_django_cli/commands/init.py) — entry-point `codex-django init`.
- [tests/unit/cli/test_install.py](tests/unit/cli/test_install.py) — unit-тесты install.
- [tests/integration/cli/test_scaffold_quality.py](tests/integration/cli/test_scaffold_quality.py) — интеграционные тесты.
- [tests/e2e/cli/test_init_e2e.py](tests/e2e/cli/test_init_e2e.py) — e2e.

**Блюпринты:**
- [src/codex_django_cli/blueprints/cabinet/](src/codex_django_cli/blueprints/cabinet/) — UI shell cabinet (без booking).
- [src/codex_django_cli/blueprints/cabinet_booking/](src/codex_django_cli/blueprints/cabinet_booking/) — booking-слой для cabinet (untracked — первым делом добавить в git).
- [src/codex_django_cli/blueprints/features/](src/codex_django_cli/blueprints/features/) — booking_core, booking_public, conversations, notifications, client_cabinet.
- [src/codex_django_cli/blueprints/project/](src/codex_django_cli/blueprints/project/) — Django base (settings, templates, static, system, features/main).

**Документация:**
- [docs/release-prep-plan.md](docs/release-prep-plan.md) — релизный трекер (читать перед релизом).
- [docs/en/architecture/cli/blueprints.md](docs/en/architecture/cli/blueprints.md) — инвентаризация блюпринтов.
- [CHANGELOG.md](CHANGELOG.md) — история релизов (дописать 0.4.0 в Этапе 9).

---

## Этап 0. Подготовка

**Цель:** базовая гигиена перед рефактором.

**Задачи:**
- [ ] Создать ветку `feat/cli-refresh-v0.4` от `main`.
- [ ] Этот файл (`CLI_REFRESH_PLAN.md`) уже лежит в корне — закоммитить его первым коммитом: `chore(plan): add CLI refresh plan for v0.4.0`.
- [ ] `git add src/codex_django_cli/blueprints/cabinet_booking/` — **добавить untracked blueprint в индекс** (он уже используется в [install.py:166](src/codex_django_cli/commands/install.py#L166), но физически не закоммичен).
- [ ] Закоммитить удаления старых файлов cabinet/booking/* (они уже в `git status` как `D`) + новый cabinet_booking: `refactor(blueprints): split booking out of cabinet into dedicated blueprint`.
- [ ] Проверить `pytest -q` → все тесты зелёные (баг-фиксы из `ed0ea95`, `d47cef1` должны уже проходить).
- [ ] Проверить `ruff check . && ruff format --check .`

**Выход:** рабочая ветка, зелёная база, план в репо.

---

## Этап 1. Негативный тест на баг «standard init без booking»

**Цель:** зафиксировать поведение «если booking не выбран — в выходе НЕТ booking-файлов» регрессионным тестом. По текущему анализу баг уже 95% закрыт (см. контекст), но тест отсутствует.

**Входные файлы:**
- [tests/unit/cli/test_install.py](tests/unit/cli/test_install.py)
- [tests/integration/cli/test_scaffold_quality.py](tests/integration/cli/test_scaffold_quality.py)
- [src/codex_django_cli/commands/install.py:160-180](src/codex_django_cli/commands/install.py#L160)

**Задачи:**
- [ ] В [test_install.py](tests/unit/cli/test_install.py) добавить `test_scaffold_new_project_standard_does_not_include_booking`:
  - Вызов `scaffold_new_project` с `InstallSelection(cabinet=True, booking=False, conversations=True)`.
  - Assert: в зафиксированных `engine.scaffold(...)` вызовах **нет** `"cabinet_booking"` и нет `"features/booking_core"`.
  - Assert: `"features/booking_public"` тоже отсутствует.
- [ ] Добавить `test_scaffold_existing_project_without_booking_skips_cabinet_booking` — аналогично для `_scaffold_modules_to_target`.
- [ ] В новом файле `tests/integration/cli/test_booking_isolation.py` (или расширение существующего quality-теста):
  - Сгенерировать реальный проект в `tmp_path` через `CLIEngine` напрямую (не subprocess) с `with_booking=False`.
  - Assert: на диске **нет** следующих путей:
    - `src/<project>/cabinet/booking_bridge.py`
    - `src/<project>/cabinet/views/booking.py`
    - `src/<project>/cabinet/services/booking.py`
    - `src/<project>/cabinet/templates/cabinet/booking/` (директория)
  - Прочитать сгенерированный `src/<project>/cabinet/urls.py`, assert: нет импортов из `.views.booking`.
  - Прочитать сгенерированный `src/<project>/core/settings/modules/apps.py`, assert: нет `"features.booking"` в INSTALLED_APPS.
- [ ] Добавить зеркальный позитивный тест `test_scaffold_with_booking_includes_cabinet_booking_files` на тот же шаблон: с `with_booking=True` все файлы **должны** присутствовать.
- [ ] Запустить `pytest tests/unit/cli/test_install.py tests/integration/cli/test_booking_isolation.py -v` → зелёные.

**Коммит:** `test(cli): add regression tests for booking isolation in standard init`

**Выход:** тесты на месте; они защитят от повторного появления бага в следующих этапах.

---

## Этап 2. Чистка cabinet блюпринта от booking-рудиментов

**Цель:** удалить всё, что в `cabinet/` относится к booking (дубли, demo-данные, hardcoded упоминания).

**Входные файлы:**
- [src/codex_django_cli/blueprints/cabinet/services/analytics.py.j2](src/codex_django_cli/blueprints/cabinet/services/analytics.py.j2)
- [src/codex_django_cli/blueprints/cabinet/context_processors.py.j2](src/codex_django_cli/blueprints/cabinet/context_processors.py.j2)
- `src/codex_django_cli/blueprints/cabinet/services/booking.py.j2` — **удалить** (дубликат `cabinet_booking/services/booking.py.j2`).
- `src/codex_django_cli/blueprints/cabinet/views/booking.py.j2` — **удалить**, если присутствует.
- Все шаблоны `cabinet/templates/**/*.html` с комментарием `{# CODEX_DJANGO_CLI BLUEPRINT STATUS: MOVE_TO_CLI_BLUEPRINT ... #}`.

**Задачи:**
- [ ] Grep по блюпринту cabinet: `grep -rn "MOVE_TO_CLI_BLUEPRINT" src/codex_django_cli/blueprints/cabinet/` — удалить найденные комментарии (устаревший маркер).
- [ ] В [cabinet/services/analytics.py.j2](src/codex_django_cli/blueprints/cabinet/services/analytics.py.j2):
  - Обернуть все блоки с "bookings" в `{%- if with_booking %} ... {%- endif %}`.
  - Альтернатива (предпочтительно): переделать на паттерн `DashboardSelector.extend(...)` с условной регистрацией (см. Этап 3).
- [ ] В [cabinet/context_processors.py.j2](src/codex_django_cli/blueprints/cabinet/context_processors.py.j2):
  - Убрать или обернуть `{%- if with_booking %}` все booking-related demo-ключи.
- [ ] Удалить `cabinet/services/booking.py.j2` — оставить только в `cabinet_booking/services/booking.py.j2`.
- [ ] Удалить `cabinet/views/booking.py.j2` если присутствует.
- [ ] Проверить, что `cabinet_booking/` блюпринт содержит эти файлы полностью (читать и сравнить с удалёнными).
- [ ] `grep -rn "booking" src/codex_django_cli/blueprints/cabinet/` — ручной аудит всех оставшихся упоминаний; то что должно остаться (`booking_shared.js`, условия `with_booking` в urls.py.j2) — задокументировать в комментарии блюпринта.

**Тесты:**
- [ ] Расширить `test_booking_isolation.py` из Этапа 1: проверять, что после standard-init в `cabinet/services/analytics.py` нет слова `booking` (case-insensitive regex).
- [ ] Проверить, что с `with_booking=True` аналитика всё ещё корректно рендерится и содержит booking-данные.

**Коммит:** `refactor(cabinet): remove booking residue from cabinet blueprint`

---

## Этап 3. Приведение `cabinet.py.j2` модулей под Cabinet 2.0 API (`declare`)

**Цель:** блюпринты генерируют код под актуальный публичный API `codex_django.cabinet`.

**Входные файлы:**
- [src/codex_django_cli/blueprints/cabinet/cabinet.py.j2](src/codex_django_cli/blueprints/cabinet/cabinet.py.j2) — auto-discovered hook cabinet-ядра.
- `src/codex_django_cli/blueprints/features/booking_core/features/booking/cabinet.py.j2` — booking feature cabinet hook.
- `src/codex_django_cli/blueprints/features/conversations/features/conversations/cabinet.py.j2` — conversations cabinet hook.
- `src/codex_django_cli/blueprints/cabinet_booking/booking_bridge.py.j2` — bridge к codex_django.booking.
- **Reference (реальный API):** исходники `codex-django` (путь указан в рабочем проекте пользователя через pyproject path) — `src/codex_django/cabinet/__init__.py`.

**Задачи:**
- [ ] Прочитать исходники `codex_django.cabinet` — зафиксировать актуальные сигнатуры `declare()`, `TopbarEntry`, `SidebarItem`, `DashboardSelector.extend()`, `DataTableData`, `CalendarGridData` и др. (из memory-графа: полный публичный API).
- [ ] Переписать [cabinet/cabinet.py.j2](src/codex_django_cli/blueprints/cabinet/cabinet.py.j2) под `declare(space="staff", module="cabinet", topbar=..., sidebar=...)`.
- [ ] Переписать `features/booking_core/.../cabinet.py.j2` — `declare(space="staff", module="booking", topbar=TopbarEntry(group="services", label=_("Booking"), icon="bi-calendar", url=...), sidebar=[SidebarItem(...)])`.
- [ ] Переписать `features/conversations/.../cabinet.py.j2` аналогично.
- [ ] Переписать `cabinet/views/analytics.py.j2` + `cabinet/services/analytics.py.j2` под `@DashboardSelector.extend(cache_key="analytics.main", cache_ttl=300)` паттерн с JSON-сериализуемыми dataclass-ами (НЕ pickle).
- [ ] Импорты во всех `cabinet.py.j2`: только из `codex_django.cabinet` (публичный API), не из `codex_django.cabinet.declare.api` и т.п. внутренних путей.
- [ ] Проверить `cabinet_booking/booking_bridge.py.j2` — должен re-export'ить только публичные имена из `codex_django.booking`.

**Тесты:**
- [ ] Новый `tests/integration/cli/test_cabinet_api_surface.py`:
  - Сгенерировать проект с `with_cabinet=True, with_booking=True, with_conversations=True`.
  - Для каждого `cabinet.py` в выходе: прочитать, assert наличие `from codex_django.cabinet import ... declare` и `declare(space=`.
  - Assert: нет импортов из внутренних путей (`codex_django.cabinet._internal`, `.declare.api`, etc.) — regex по запрещённым префиксам.
- [ ] Регрессия: все предыдущие тесты зелёные.

**Коммит:** `refactor(blueprints): align cabinet hooks with Cabinet 2.0 declare API`

---

## Этап 4. `settings/modules/booking.py.j2` и `notifications.py.j2`

**Цель:** каждая фича имеет свой модуль настроек, подключается условно.

**Входные файлы:**
- [src/codex_django_cli/blueprints/project/core/settings/base.py.j2](src/codex_django_cli/blueprints/project/core/settings/base.py.j2)
- [src/codex_django_cli/blueprints/project/core/settings/modules/](src/codex_django_cli/blueprints/project/core/settings/modules/)
- [src/codex_django_cli/blueprints/project/core/settings/modules/codex.py.j2](src/codex_django_cli/blueprints/project/core/settings/modules/codex.py.j2) — здесь сейчас частично лежат cabinet-настройки.

**Задачи:**
- [ ] Создать `project/core/settings/modules/booking.py.j2`:
  - `BOOKING_DEFAULT_SLOT_MINUTES`, `BOOKING_MAX_ADVANCE_DAYS`, `BOOKING_OVERLAP_ALLOWED`, `BOOKING_CHAIN_MODE`, `BOOKING_PROVIDERS` — из `codex_services.booking` контрактов.
  - Обёрнут в `{%- if with_booking %}` на уровне содержимого (файл всегда генерируется, но содержимое пустое без booking).
- [ ] Создать `project/core/settings/modules/notifications.py.j2`:
  - `NOTIFICATIONS_ARQ_REDIS_URL`, `NOTIFICATIONS_EMAIL_BACKEND`, `NOTIFICATIONS_DEFAULT_FROM_EMAIL`, и т.п.
  - Условно генерируется если пользователь выбрал notifications (новый флаг — см. Этап 5).
- [ ] В [base.py.j2](src/codex_django_cli/blueprints/project/core/settings/base.py.j2) добавить:
  ```jinja
  {%- if with_booking %}
  from .modules.booking import *  # noqa: F401, F403
  {%- endif %}
  {%- if with_notifications %}
  from .modules.notifications import *  # noqa: F401, F403
  {%- endif %}
  ```
- [ ] Вынести hardcoded `LOGIN_URL = "/cabinet/login/"` из [codex.py.j2](src/codex_django_cli/blueprints/project/core/settings/modules/codex.py.j2) в settings-переменную `CABINET_LOGIN_URL` с defaultом, параметризуемым через env.

**Тесты:**
- [ ] `tests/integration/cli/test_settings_modules.py`:
  - Генерация с `with_booking=True` → файл `core/settings/modules/booking.py` существует и содержит `BOOKING_DEFAULT_SLOT_MINUTES`.
  - Генерация без booking → файл может существовать, но пустой/без настроек (или отсутствует — выбрать один вариант).
  - `base.py` содержит правильные `from .modules.booking import *` условно.
  - `codex.py` больше не содержит hardcoded `/cabinet/login/`.

**Коммит:** `feat(settings): extract booking/notifications into dedicated settings modules`

---

## Этап 5. Обновление `prompts.py` + `main.py` + `install.py` — семантика флагов

**Цель:** очистить путаницу с `booking` vs `booking_engine` vs `booking_cabinet`, добавить `notifications` в меню.

**Входные файлы:**
- [src/codex_django_cli/prompts.py](src/codex_django_cli/prompts.py)
- [src/codex_django_cli/main.py:101-116](src/codex_django_cli/main.py#L101) — `_build_selection_from_modules`
- [src/codex_django_cli/commands/install.py:22-78](src/codex_django_cli/commands/install.py#L22) — `InstallSelection`, `resolve_install_selection`

**Задачи:**
- [ ] Проанализировать текущую семантику: `booking_cabinet` — это "кабинет + booking integration" (UI в cabinet), `booking_engine` — только features/booking_core. Сейчас они фактически сливаются в `booking=True`. **Решение:** упростить до единого флага `booking` (он включает: `features/booking_core` + `cabinet_booking/` если cabinet есть). Убрать отдельно `booking_cabinet` и `booking_engine`.
- [ ] В [MODULE_LABELS](src/codex_django_cli/prompts.py#L9):
  - Удалить `booking_engine`, `booking_cabinet`.
  - Оставить: `cabinet`, `booking`, `public_booking`, `conversations`, `notifications` (новый), `sw`.
- [ ] В `ask_install_modules` — новый список `module_names = ["cabinet", "conversations", "booking", "public_booking", "notifications", "sw"]`.
- [ ] В [InstallSelection](src/codex_django_cli/commands/install.py#L22):
  - Удалить поле `booking_cabinet`.
  - Добавить поле `notifications: bool = False`.
- [ ] В [resolve_install_selection](src/codex_django_cli/commands/install.py#L67):
  - Убрать логику с `booking_cabinet`.
  - `with_booking = selection.booking or selection.public_booking`.
  - `with_notifications = selection.notifications` (или автоматически True если booking/conversations).
- [ ] Обновить [MODULE_MARKERS](src/codex_django_cli/commands/install.py#L12):
  - Убрать `booking_engine` и `booking_cabinet`.
  - Добавить `booking` (маркер `features/booking/apps.py`, `cabinet/booking_bridge.py`).
  - Добавить `notifications` (маркер `features/notifications/apps.py`).
- [ ] Обновить [_build_selection_from_modules](src/codex_django_cli/main.py#L101) под новые имена.
- [ ] Обновить argparse в [_handle_cli_args](src/codex_django_cli/main.py#L301): `--with-booking`, `--with-notifications`, убрать legacy флаги.
- [ ] В `scaffold_new_project` добавить `if plan.notifications: engine.scaffold("features/notifications", ...)`.

**Тесты:**
- [ ] Обновить `tests/unit/cli/test_install.py`:
  - Перенумеровать ожидаемые scaffold-вызовы под новую модель.
  - Добавить тест `test_notifications_module_scaffolded_when_requested`.
  - Удалить тесты, использующие `booking_cabinet` отдельно.
- [ ] `test_prompts.py` (если есть) — обновить MODULE_LABELS assertions.

**Коммит:** `refactor(cli): simplify module selection model; add notifications option`

---

## Этап 6. Demo-data → JSON/YAML fixtures

**Цель:** весь demo-контент (русские mock-ы) вынесен из Python-блюпринтов в fixtures.

**Входные файлы:**
- [src/codex_django_cli/blueprints/cabinet/services/analytics.py.j2](src/codex_django_cli/blueprints/cabinet/services/analytics.py.j2) — hardcoded демо-метрики.
- [src/codex_django_cli/blueprints/cabinet/context_processors.py.j2](src/codex_django_cli/blueprints/cabinet/context_processors.py.j2) — hardcoded данные.

**Задачи:**
- [ ] Выделить все hardcoded demo-структуры в JSON-файлы в `blueprints/cabinet/fixtures/`:
  - `analytics_demo.json.j2` (если нужна параметризация через Jinja — иначе просто `.json`).
  - `context_demo.json.j2`.
- [ ] В `analytics.py.j2` / `context_processors.py.j2` — читать JSON через `json.load` на import-time **или** через `Path(__file__).parent / "fixtures" / "analytics_demo.json"`.
- [ ] Решить: fixtures идут в `cabinet/fixtures/` пакета проекта или в `cabinet/seed_data/`? — выбрать одно имя, задокументировать.
- [ ] Все user-facing строки в fixtures: привести к мульти-языковому формату `{"ru": "Записи", "en": "Bookings"}` с селектором по `settings.LANGUAGE_CODE`, либо оставить на английском и работать через `gettext_lazy` в Python-слое (см. Этап 8).

**Тесты:**
- [ ] `tests/integration/cli/test_demo_data.py`:
  - После генерации: в `cabinet/services/analytics.py` нет русских строк (regex `[а-яёА-ЯЁ]`).
  - В `cabinet/fixtures/` есть ожидаемые JSON-файлы.
  - `json.loads()` от них проходит без ошибок.

**Коммит:** `refactor(cabinet): extract demo data into JSON fixtures`

---

## Этап 7. DRF API scaffold

**Цель:** опциональная генерация REST API через Django REST Framework.

**Входные файлы:**
- Новый блюпринт `src/codex_django_cli/blueprints/api/` (или расширение существующих с `api/` subfolder).
- [src/codex_django_cli/blueprints/project/core/settings/modules/](src/codex_django_cli/blueprints/project/core/settings/modules/) — добавить `api.py.j2` с DRF-настройками.
- [src/codex_django_cli/prompts.py](src/codex_django_cli/prompts.py) — добавить опцию `api` в меню.

**Задачи:**
- [ ] Создать блюпринт `blueprints/api/` с scaffold для:
  - `api/serializers/cabinet.py.j2`, `api/serializers/booking.py.j2`, `api/serializers/conversations.py.j2`.
  - `api/views/cabinet.py.j2`, `api/views/booking.py.j2`, `api/views/conversations.py.j2` (ViewSet'ы).
  - `api/urls.py.j2` — DRF DefaultRouter с опциональной регистрацией под Jinja условиями.
  - `api/permissions.py.j2` — базовые IsAuthenticated + custom permissions.
- [ ] Создать `project/core/settings/modules/api.py.j2`:
  - `REST_FRAMEWORK = { "DEFAULT_AUTHENTICATION_CLASSES": [...], "DEFAULT_PAGINATION_CLASS": ..., "PAGE_SIZE": ... }`.
- [ ] Добавить `djangorestframework>=3.15` в `project/pyproject.toml.j2` условно (под `{% if with_api %}`).
- [ ] В [install.py](src/codex_django_cli/commands/install.py) и `InstallSelection`: добавить `api: bool = False`, `plan.api` + `engine.scaffold("api", ...)`.
- [ ] В [prompts.py](src/codex_django_cli/prompts.py) MODULE_LABELS: `"api": "REST API (DRF)"`.
- [ ] В [main.py:_handle_cli_args](src/codex_django_cli/main.py#L301): `--with-api`.

**Тесты:**
- [ ] `tests/unit/cli/test_install.py`: `test_api_scaffolded_when_requested`.
- [ ] `tests/integration/cli/test_api_blueprint.py`:
  - Генерация с `with_api=True, with_cabinet=True, with_booking=True` → файлы `api/serializers/booking.py`, `api/views/booking.py`, `api/urls.py` существуют.
  - `core/settings/modules/api.py` содержит `REST_FRAMEWORK`.
  - Без `with_api` — директории `api/` нет.

**Коммит:** `feat(blueprints): add optional DRF API scaffold`

---

## Этап 8. i18n: `gettext_lazy` для всех user-facing строк

**Цель:** все hardcoded русские/английские строки в Python-блюпринтах обёрнуты в `_()` / `gettext_lazy()`.

**Входные файлы:**
- Все `.py.j2` в `blueprints/cabinet/`, `blueprints/features/`, `blueprints/project/system/`, `blueprints/project/features/main/`.

**Задачи:**
- [ ] Найти все hardcoded user-facing строки: `grep -rn -E '"[^"]*[а-яА-ЯёЁ]' src/codex_django_cli/blueprints/ --include="*.py.j2"` + `grep -rn "verbose_name\s*=" ...`.
- [ ] Обернуть в `gettext_lazy(...)` (`from django.utils.translation import gettext_lazy as _`).
- [ ] В каждом `apps.py.j2`: `verbose_name = _("Cabinet")` и т.п.
- [ ] Проверить `translations.py.j2` в features — обновить или удалить, если не используется.
- [ ] В условии `{%- if enable_i18n %}` в settings/modules/i18n.py.j2 — убедиться, что `USE_I18N = True`, `LANGUAGES = [...]` корректно.

**Тесты:**
- [ ] `tests/integration/cli/test_i18n_compliance.py`:
  - После генерации: пройти по всем `.py` файлам в `src/<project>/cabinet/`, `features/`, `system/`.
  - Regex-assert: нет hardcoded строк с кириллицей вне `_(...)` контекста.
  - Assert: все `verbose_name` обёрнуты в `_(...)`.
- [ ] Ручная инвентаризация (в CHANGELOG Этапа 9): список всех файлов, где изменили i18n.

**Коммит:** `i18n(blueprints): wrap all user-facing strings in gettext_lazy`

---

## Этап 9. Документация + CHANGELOG

**Цель:** доки и changelog отражают v0.4.0.

**Входные файлы:**
- [docs/en/architecture/cli/blueprints.md](docs/en/architecture/cli/blueprints.md)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [docs/release-prep-plan.md](docs/release-prep-plan.md)

**Задачи:**
- [ ] Обновить [docs/en/architecture/cli/blueprints.md](docs/en/architecture/cli/blueprints.md):
  - Новая инвентаризация: `cabinet/`, `cabinet_booking/` (отдельный!), `features/booking_core`, `features/booking_public`, `features/conversations`, `features/notifications`, `api/`.
  - Описать контекст каждого блюпринта: какие переменные Jinja он ожидает.
  - Зависимости между блюпринтами.
- [ ] Обновить [CHANGELOG.md](CHANGELOG.md) — раздел `## [0.4.0] - YYYY-MM-DD`:
  - **Added:** `cabinet_booking/` extracted; `settings/modules/booking.py` и `notifications.py`; DRF API blueprint; `notifications` option в меню.
  - **Changed:** упрощена модель селекции модулей (`booking` вместо `booking_engine`+`booking_cabinet`); Cabinet 2.0 API (`declare()`) в hook-файлах.
  - **Removed:** `booking_cabinet` флаг; рудиментные комментарии `MOVE_TO_CLI_BLUEPRINT`; hardcoded demo-данные в Python-слое.
  - **Fixed:** standard-init больше не генерирует booking-слой в cabinet; `LOGIN_URL` параметризована.
- [ ] Обновить [README.md](README.md) — примеры `codex-django init` с новыми флагами.
- [ ] Обновить [docs/release-prep-plan.md](docs/release-prep-plan.md) — чеклист по v0.4.0 (или завести новый трекер).

**Коммит:** `docs: update architecture docs and CHANGELOG for v0.4.0`

---

## Этап 10. Ручная проверка на тестовом стенде

**Цель:** проверить генерацию на реальном проекте, где `pyproject.toml` уже ссылается на `codex-django` и `codex-django-cli` через `path=...`.

**Этап выполняется человеком, не автоматом.** Sonnet сюда не пускать — только после прохождения всех тестов Этапов 1–9.

**Задачи:**
- [ ] В тестовом проекте (подтянуть ветку `feat/cli-refresh-v0.4` через path-ссылку): `uv sync` или `pip install -e .`.
- [ ] Сценарий A — **standard init без booking:**
  - `codex-django init test_standard`
  - Выбрать Standard в меню.
  - Проверить вручную: нет `src/test_standard/cabinet/booking_bridge.py`, нет `cabinet/views/booking.py`, нет `cabinet/templates/cabinet/booking/`.
  - Запустить `cd test_standard && python manage.py check` — 0 ошибок.
  - Запустить `python manage.py makemigrations --dry-run` — без cabinet_booking миграций.
- [ ] Сценарий B — **custom init с booking:**
  - `codex-django init test_booking` → Custom → `[cabinet, conversations, booking]`.
  - Проверить: все booking-файлы присутствуют (`cabinet/booking_bridge.py`, `cabinet/views/booking.py`, `features/booking/apps.py`).
  - `python manage.py check` — 0 ошибок.
  - Запустить dev-server, проверить URL `/cabinet/booking/` открывается.
- [ ] Сценарий C — **extend existing project:**
  - Взять проект из Сценария A → добавить booking через `codex-django menu → Extend → [booking]`.
  - Проверить идемпотентность и корректность структуры.
- [ ] Сценарий D — **init --with-api:**
  - `codex-django init test_api --with-api --with-booking`.
  - Проверить наличие `api/serializers/booking.py`, `api/views/booking.py`, `api/urls.py`.
  - `python manage.py check` — 0 ошибок.
  - DRF endpoint `/api/v1/bookings/` доступен после миграций.
- [ ] Сценарий E — **i18n проверка:**
  - `codex-django init test_i18n --i18n --languages "en,ru,de,uk"`.
  - `python manage.py makemessages -l ru` — генерируются .po файлы со всеми строками.
  - `python manage.py compilemessages` — успех.
- [ ] Записать найденные баги обратно как точечные задачи перед релизом. Повторить соответствующие сценарии.

**Выход:** стенд подтверждает, что генерация корректна.

---

## Этап 11. Релиз 0.4.0

**Выполняется только после подтверждения Этапа 10 пользователем.**

**Задачи:**
- [ ] `pyproject.toml` — bump version `0.3.0` → `0.4.0`.
- [ ] `uv lock` — обновить лок.
- [ ] Коммит: `build(release): bump version to 0.4.0`.
- [ ] Создать тег `v0.4.0`, push ветки и тега.
- [ ] Создать PR в `main` с референсом на этот план.
- [ ] После merge — GitHub Release с выдержкой из CHANGELOG.
- [ ] Удалить `CLI_REFRESH_PLAN.md` из корня — `chore: remove completed CLI refresh plan`.

---

## Верификация (end-to-end)

**Должны быть зелёными перед PR:**
- [ ] `pytest tests/unit/cli/ -q`
- [ ] `pytest tests/integration/cli/ -q`
- [ ] `pytest tests/e2e/cli/ -q` (если есть)
- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy src/codex_django_cli/` (если настроен)
- [ ] Все сценарии Этапа 10 подтверждены пользователем.

**Метрики успеха плана:**
- Тест `test_scaffold_new_project_standard_does_not_include_booking` ловит регресс (проверено mutation-вручную — откатить Этап 2 → тест должен упасть).
- Генерация проекта на тестовом стенде запускается через `manage.py check` без единой ошибки импорта из `codex_django`.
- Сгенерированные `cabinet.py` файлы используют `declare()` (grep подтверждает).
- В сгенерированном коде 0 строк с кириллицей вне `_(...)` обёрток.

---

## Примечания для исполнителя (Sonnet)

- **Не пропускать тесты этапа.** Если тест не пишется — значит этап не готов к коммиту.
- **Не объединять этапы.** Каждый — отдельный коммит, чтобы можно было легко откатиться.
- **Если упираешься в неизвестный API codex_django** — не гадай. Прочитай исходники через путь, прописанный в корневом `pyproject.toml` тестового проекта (там `path=` до `codex-django`).
- **Не создавать новые абстракции** — только то, что требуется. План намеренно без `core/refactoring` этапов.
- **Если во время этапа обнаружен новый баг вне скоупа** — зафиксировать в отдельном issue/TODO, НЕ чинить в текущем этапе.
