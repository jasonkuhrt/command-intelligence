check:
    uv run --no-project --with jsonschema==4.26.0 python conformance/validate.py
    uv run --no-project --with jsonschema==4.26.0 python -m unittest discover -s conformance -p 'test_*.py'
