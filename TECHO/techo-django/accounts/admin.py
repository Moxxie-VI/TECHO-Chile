from django.contrib import admin
from .models import TokenRecuperacion

@admin.register(TokenRecuperacion)
class TokenRecuperacionAdmin(admin.ModelAdmin):
    list_display = ('token', 'user', 'creado_en', 'usado', 'es_valido')
    list_filter = ('usado', 'creado_en')
    search_fields = ('token', 'user__username', 'user__email')
    readonly_fields = ('creado_en',)
    
    def es_valido(self, obj):
        return obj.es_valido()
    es_valido.boolean = True
    es_valido.short_description = 'Válido'
