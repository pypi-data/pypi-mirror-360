# openmailer/template_engine.py
from jinja2 import Template

def render_template(template_str, context):
    return Template(template_str).render(**context)