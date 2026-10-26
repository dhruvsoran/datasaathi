import os
from pathlib import Path
os.environ.setdefault("DATASAATHI_DB", "/tmp/datasaathi_app_test.duckdb")
from streamlit.testing.v1 import AppTest


def _ask(at, label):
    [b for b in at.button if label in b.label][0].click().run()


def test_ask_tab_shows_only_the_latest_answer_and_history_keeps_all():
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
    assert not at.exception
    for label in ("most electricity", "per student", "Cafeteria water usage"):
        _ask(at, label)
        assert not at.exception
    assert len(at.session_state.history) == 3
    answers = [m.value for m in at.markdown if 'class="answer' in m.value]
    assert len(answers) == 2          # one on the Ask tab, one reopened in the History tab (not three stacked answers)


def test_sidebar_toggle_is_not_hidden_by_the_theme():
    from datasaathi import ui
    # the re-open button lives inside stToolbar, so the stylesheet must never hide the toolbar itself
    assert '[data-testid="stToolbar"]' not in ui.CSS
    assert 'stExpandSidebarButton' in ui.CSS


def _app():
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90)


def _has_intro(at):
    return any('class="intro"' in m.value for m in at.markdown)


def test_welcome_curtain_shows_once_per_session():
    at = _app().run()
    assert _has_intro(at) and any("HACKTOBER" in m.value for m in at.markdown)
    [b for b in at.button if "most electricity" in b.label][0].click().run()
    assert not _has_intro(at)                          # not repeated after the first screen


def test_welcome_curtain_can_be_skipped_and_replayed():
    at = _app()
    at.query_params["intro"] = "0"
    at.run()
    assert not _has_intro(at)
    at2 = _app().run()
    [b for b in at2.button if "Replay welcome" in b.label][0].click().run()
    assert _has_intro(at2)
