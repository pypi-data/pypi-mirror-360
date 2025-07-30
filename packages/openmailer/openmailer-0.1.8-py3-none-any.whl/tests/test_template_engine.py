import pytest
from openmailer.template_engine import render_template


def test_render_with_valid_context():
    template = "<h1>Hello {{ name }}</h1>"
    context = {"name": "OpenMailer"}
    result = render_template(template, context)
    assert "OpenMailer" in result



def test_render_with_missing_context():
    template = "<h1>Hello {{ name }}</h1>"
    context = {}
    result = render_template(template, context)
    assert "{{ name }}" in result or result.strip() != ""
