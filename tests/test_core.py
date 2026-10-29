import json

from convo_miner.core import (load_export, parse_conversation, chunk_text, batches, write_batches, write_search_index, search_index)


def sample_export():
    return [{
        "id": "abc123",
        "title": "Test idea",
        "create_time": 10,
        "mapping": {
            "root": {"message": None},
            "u1": {"message": {
                "author": {"role": "user"},
                "create_time": 11,
                "content": {"content_type": "text", "parts": ["Build a parser"]},
            }},
            "a1": {"message": {
                "author": {"role": "assistant"},
                "create_time": 12,
                "content": {"content_type": "text", "parts": ["Use Python", {"text": "and tests"}]},
            }},
        },
    }]


def test_load_export_reads_user_and_assistant_messages(tmp_path):
    f = tmp_path / "conversations.json"
    f.write_text(json.dumps(sample_export()), encoding="utf-8")
    items = load_export(f)
    assert len(items) == 1
    assert items[0].conversation_id == "abc123"
    assert [m.role for m in items[0].messages] == ["user", "assistant"]
    assert items[0].messages[1].text == "Use Python\nand tests"


def test_simplified_schema_supported():
    c = parse_conversation({"id": "x", "title": "t", "messages": [{"role": "user", "text": "hi"}]})
    assert c is not None and c.messages[0].text == "hi"


def test_chunk_text_preserves_all_characters():
    text = ("abc\n" * 120) + ("z" * 350)
    chunks = chunk_text(text, 150)
    assert "".join(chunks).replace("\n", "") == text.replace("\n", "")
    assert all(len(c) <= 150 for c in chunks)


def test_batching_handles_partial_final_batch():
    conversations = [
        parse_conversation({"id": str(i), "messages": [{"role": "user", "text": str(i)}]})
        for i in range(11)
    ]
    groups = batches(conversations, 5)
    assert [len(g) for g in groups] == [5, 5, 1]


def test_write_batches_includes_stable_message_ids(tmp_path):
    c = parse_conversation({"id": "x", "title": "idea", "messages": [{"role": "user", "text": "find the idea"}]})
    paths = write_batches([c], tmp_path, batch_size=5)
    assert len(paths) == 2
    assert "Conversation ID: `x`" in paths[0].read_text(encoding="utf-8")
    manifest = json.loads(paths[1].read_text(encoding="utf-8"))
    assert manifest["conversation_ids"] == ["x"]



def test_search_index_finds_all_terms_and_preserves_source_ids(tmp_path):
    conversations = [
        parse_conversation({
            "id": "alpha",
            "title": "CSC LCH design",
            "messages": [
                {"role": "user", "text": "Semantic compression keeps useful context."},
                {"role": "assistant", "text": "Lazy hydration retrieves source details when needed."},
            ],
        }),
        parse_conversation({
            "id": "beta",
            "title": "Unrelated note",
            "messages": [{"role": "user", "text": "Semantic ideas can be useful."}],
        }),
    ]
    index_path = tmp_path / "private" / "search-index.json"
    write_search_index(conversations, index_path)

    results = search_index(index_path, "semantic context")
    assert len(results) == 1
    assert results[0]["conversation_id"] == "alpha"
    assert results[0]["message_id"].startswith("MSG-")
    assert results[0]["role"] == "user"
    assert "Semantic compression" in results[0]["excerpt"]


def test_search_index_ranks_repeated_terms_and_applies_limit(tmp_path):
    conversations = [
        parse_conversation({
            "id": "first",
            "title": "Topic",
            "messages": [{"role": "user", "text": "token token context"}],
        }),
        parse_conversation({
            "id": "second",
            "title": "Topic",
            "messages": [{"role": "user", "text": "token context"}],
        }),
    ]
    index_path = tmp_path / "search-index.json"
    write_search_index(conversations, index_path)

    results = search_index(index_path, "token context", limit=1)
    assert len(results) == 1
    assert results[0]["conversation_id"] == "first"


def test_search_index_rejects_empty_query_and_invalid_limit(tmp_path):
    index_path = tmp_path / "search-index.json"
    index_path.write_text("[]", encoding="utf-8")

    import pytest

    with pytest.raises(ValueError, match="searchable word"):
        search_index(index_path, "   ")
    with pytest.raises(ValueError, match="limit"):
        search_index(index_path, "idea", limit=0)
