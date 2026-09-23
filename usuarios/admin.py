from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Cargo


class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ["cargo", "email"]

    # O UserAdmin padrão referencia "username" nas telas de criar/editar e na
    # ordenação (foi desenhado pro usuário padrão do Django, login por
    # username). Como removemos esse campo (login é só por email), tudo isso
    # precisa ser sobrescrito.
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informações pessoais",
            {"fields": ("first_name", "last_name", "cargo")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "cargo",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


class CargoAdmin(admin.ModelAdmin):
    list_display = ["nome"]


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cargo, CargoAdmin)
