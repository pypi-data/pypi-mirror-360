from utils import truncate_history

def test_truncate_history():
    history = [{"prompt": str(i), "response": str(i)} for i in range(20)]
    truncated = truncate_history(history, max_entries=5)
    assert len(truncated) == 5
    assert truncated == history[-5:]