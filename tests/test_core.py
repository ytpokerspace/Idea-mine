import json

from convo_miner.core import load_export, parse_conversation, chunk_text, batches, write_batches


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
