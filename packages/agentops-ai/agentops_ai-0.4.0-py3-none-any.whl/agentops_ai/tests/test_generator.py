from agentops_ai.agentops_core.services.test_generator import TestGenerator
import os
import tempfile


def test_parse_code_success():
    code = """
def foo(x):
    return x + 1
"""
    tg = TestGenerator(api_key="sk-test")  # Use a dummy key for parse test
    result = tg.parse_code(code)
    assert result["success"]
    assert isinstance(result["structure"], dict)


def test_parse_code_syntax_error():
    code = "def foo(x): return x + "  # Invalid Python
    tg = TestGenerator(api_key="sk-test")
    result = tg.parse_code(code)
    assert not result["success"]
    assert "error" in result


def test_create_prompt():
    tg = TestGenerator(api_key="sk-test")
    code = """
def foo(x):
    return x + 1
"""
    structure = {
        "functions": [type("F", (), {"name": "foo", "parameters": [{"name": "x"}]})()],
        "classes": [],
    }
    prompt = tg._create_prompt(code, structure, "pytest")
    assert "foo(x)" in prompt
    assert "pytest" in prompt
    assert "Full code to test:" in prompt


def test_process_response_success():
    tg = TestGenerator(api_key="sk-test")

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChoice:
        def __init__(self, message):
            self.message = message

    class FakeResponse:
        def __init__(self, choices):
            self.choices = choices

    fake_response = {
        "success": True,
        "data": FakeResponse(
            [FakeChoice(FakeMessage("def test_foo():\n    assert foo(1) == 2"))]
        ),
    }
    result = tg._process_response(fake_response, "pytest")
    assert result["success"]
    assert "def test_foo" in result["tests"]
    assert result["confidence"] == 1.0


def test_process_response_failure():
    tg = TestGenerator(api_key="sk-test")
    fake_response = {"success": False, "error": "API error"}
    result = tg._process_response(fake_response, "pytest")
    assert not result["success"]
    assert "error" in result


def test_write_tests_to_file():
    tg = TestGenerator(api_key="sk-test")
    test_code = "def test_foo():\n    assert foo(1) == 2"
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tg.write_tests_to_file(
            test_code, output_dir=tmpdir, base_name="test_temp.py"
        )
        assert os.path.exists(file_path)
        with open(file_path) as f:
            content = f.read()
        assert "def test_foo" in content
