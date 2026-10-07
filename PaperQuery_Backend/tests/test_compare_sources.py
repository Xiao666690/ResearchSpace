from core.backend.router.router_compare import _source_for_cell
from core.common.types import EvidenceChunk


def test_comparison_recovers_only_verbatim_source_in_same_paper():
    chunk = EvidenceChunk(chunk_id='stored-1', document_id='paper-a',
        knowledge_id='library', source='', page_number=2,
        text='The method uses sparse dense fusion for retrieval.')
    sources = {('paper-a', chunk.chunk_id): chunk}

    assert _source_for_cell('paper-a', {'value': 'sparse dense fusion'}, sources) is chunk
    assert _source_for_cell('paper-b', {'value': 'sparse dense fusion'}, sources) is None
    assert _source_for_cell('paper-a', {'value': 'invented method'}, sources) is None
