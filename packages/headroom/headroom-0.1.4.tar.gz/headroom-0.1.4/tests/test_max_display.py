from max_display import format_output

def test_format_output_json():
    json_text = '{"a": 1, "b": 2}'
    colored = format_output(json_text, output_type="json")
    assert isinstance(colored, str)
    assert "a" in colored and "b" in colored

def test_format_output_plain():
    text = "plain text"
    output = format_output(text, output_type="text")
    assert output == text