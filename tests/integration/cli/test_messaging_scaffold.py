from __future__ import annotations

from pathlib import Path

import pytest

from codex_django_cli.commands.init import handle_init


def _project_dir(tmp_path: Path) -> Path:
    return tmp_path / "msgproj" / "src" / "msgproj"


@pytest.mark.integration
@pytest.mark.parametrize("with_messaging", [False, True])
def test_messaging_app_registration_matches_selection(tmp_path: Path, with_messaging: bool):
    handle_init("msgproj", str(tmp_path), with_messaging=with_messaging)

    apps = (_project_dir(tmp_path) / "core" / "settings" / "modules" / "apps.py").read_text(encoding="utf-8")
    assert ('"features.messaging"' in apps) is with_messaging


@pytest.mark.integration
def test_init_with_messaging_scaffolds_project_owned_cabinet_feature(tmp_path: Path):
    handle_init("msgproj", str(tmp_path), with_messaging=True)

    project = _project_dir(tmp_path)
    expected = [
        "features/messaging/__init__.py",
        "features/messaging/apps.py",
        "features/messaging/cabinet.py",
        "features/messaging/cabinet_urls.py",
        "features/messaging/models/thread.py",
        "features/messaging/models/message.py",
        "features/messaging/models/reply.py",
        "features/messaging/models/campaign.py",
        "features/messaging/models/system_recipient.py",
        "features/messaging/models/email_log.py",
        "features/messaging/models/email_settings.py",
        "features/messaging/selectors/mailbox.py",
        "features/messaging/selectors/campaigns.py",
        "features/messaging/selectors/recipients.py",
        "features/messaging/selectors/delivery.py",
        "features/messaging/services/cabinet_bridge.py",
        "features/messaging/services/cabinet_workflow.py",
        "features/messaging/views/cabinet.py",
        "features/messaging/templates/cabinet/messaging/mailbox.html",
        "features/messaging/templates/cabinet/messaging/campaigns.html",
        "features/messaging/templates/cabinet/messaging/campaign_form.html",
        "features/messaging/templates/cabinet/messaging/recipients.html",
        "features/messaging/templates/cabinet/messaging/delivery_log.html",
        "features/messaging/templates/cabinet/messaging/settings.html",
    ]

    for relative_path in expected:
        assert (project / relative_path).exists(), f"missing generated file: {relative_path}"


@pytest.mark.integration
def test_generated_messaging_cabinet_uses_runtime_navigation_contract(tmp_path: Path):
    handle_init("msgproj", str(tmp_path), with_messaging=True)

    cabinet_py = (_project_dir(tmp_path) / "features" / "messaging" / "cabinet.py").read_text(encoding="utf-8")
    sidebar_call = cabinet_py.split("sidebar=build_messaging_sidebar(", 1)[1].split("),", 1)[0]

    assert "build_messaging_topbar" in cabinet_py
    assert "build_messaging_sidebar" in cabinet_py
    assert 'settings_url="cabinet:messaging_settings"' in cabinet_py
    assert "Mailbox" not in cabinet_py
    assert "Campaigns" not in cabinet_py
    assert "Recipients" not in cabinet_py
    assert "Delivery log" not in cabinet_py
    assert "Settings" not in sidebar_call
    assert "Templates" not in sidebar_call


@pytest.mark.integration
def test_generated_messaging_views_set_module_and_use_presenter(tmp_path: Path):
    handle_init("msgproj", str(tmp_path), with_messaging=True)

    views_py = (_project_dir(tmp_path) / "features" / "messaging" / "views" / "cabinet.py").read_text(encoding="utf-8")

    assert 'request.cabinet_module = "messaging"' in views_py
    assert "MessagingCabinetPresenter" in views_py
    assert "self.bridge.get_mailbox_state" in views_py
    assert "self.presenter.mailbox_context(state)" in views_py


@pytest.mark.integration
def test_generated_messaging_bridge_imports_runtime_contracts(tmp_path: Path):
    handle_init("msgproj", str(tmp_path), with_messaging=True)

    bridge_py = (_project_dir(tmp_path) / "features" / "messaging" / "services" / "cabinet_bridge.py").read_text(
        encoding="utf-8"
    )

    assert "MessagingBridge" in bridge_py
    assert "MessagingActionResult" in bridge_py
    assert "MessagingCabinetPresenter" in bridge_py
    assert "MessagingCabinetWorkflowService" in bridge_py
    assert "MailboxState" in bridge_py
    assert "CampaignListState" in bridge_py
    assert "RecipientListState" in bridge_py
    assert "DeliveryLogState" in bridge_py
    assert "MessagingSettingsState" in bridge_py


@pytest.mark.integration
def test_generated_messaging_routes_match_cabinet_contract(tmp_path: Path):
    handle_init("msgproj", str(tmp_path), with_messaging=True)

    urls_py = (_project_dir(tmp_path) / "features" / "messaging" / "cabinet_urls.py").read_text(encoding="utf-8")
    cabinet_urls = (_project_dir(tmp_path) / "cabinet" / "urls.py").read_text(encoding="utf-8")

    assert 'path("", MessagingMailboxView.as_view(), name="messaging_mailbox")' in urls_py
    assert 'path("thread/<int:thread_id>/", MessagingThreadView.as_view(), name="messaging_thread")' in urls_py
    assert 'path("campaigns/", MessagingCampaignListView.as_view(), name="messaging_campaigns")' in urls_py
    assert 'path("campaigns/new/", MessagingCampaignFormView.as_view(), name="messaging_campaign_new")' in urls_py
    assert 'name="messaging_campaign_detail"' in urls_py
    assert 'path("recipients/", MessagingRecipientsView.as_view(), name="messaging_recipients")' in urls_py
    assert 'path("delivery-log/", MessagingDeliveryLogView.as_view(), name="messaging_delivery_log")' in urls_py
    assert 'path("settings/", MessagingSettingsView.as_view(), name="messaging_settings")' in urls_py
    assert 'path("messaging/", include("features.messaging.cabinet_urls"))' in cabinet_urls
