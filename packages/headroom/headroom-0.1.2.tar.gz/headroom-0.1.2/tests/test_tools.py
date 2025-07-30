from tools import execute_command

def test_execute_command_success():
    result = execute_command("echo hello", stream_output=False)
    assert result["success"]
    assert "hello" in result["output"]

def test_execute_command_failure():
    result = execute_command("nonexistentcommand", stream_output=False)
    assert not result["success"]