import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
from inventory.models import PricingRule
from django.forms import modelform_factory

Form = modelform_factory(PricingRule, fields='__all__')
f = Form()
for name, field in f.fields.items():
    widget = field.widget
    widget_html = widget.render(name, None, attrs={'id': f'id_{name}'})
    # Just print the name attribute that will appear in POST
    print(f"Field: {name} -> Widget: {widget.__class__.__name__} -> HTML name attr: {name}")
