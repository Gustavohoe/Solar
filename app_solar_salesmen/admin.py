from django.contrib import admin

# admin.py
from .models import Produto, Venda

admin.site.register(Produto)
admin.site.register(Venda)
