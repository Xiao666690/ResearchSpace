from core.backend.services.document_path import resolve_document_path


def test_legacy_document_paths_use_configured_directories(monkeypatch, tmp_path):
    pdf = tmp_path / 'pdf'
    temporary = tmp_path / 'temporary'
    monkeypatch.setenv('PAPER_SAVE_DIR', str(pdf))
    monkeypatch.setenv('TMP_PAPER_SAVE_DIR', str(temporary))

    assert resolve_document_path('/res/pdf/paper.pdf') == str(pdf / 'paper.pdf')
    assert resolve_document_path('/res/tmppdf/paper.pdf') == str(temporary / 'paper.pdf')
