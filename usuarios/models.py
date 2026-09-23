from django.db import models

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class Cargo(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


# Gerenciador customizado: o UserManager padrão do Django (herdado junto com
# AbstractUser) espera "username" como identificador principal — como o
# nosso login é por email, precisamos reescrever create_user/create_superuser
# usando email no lugar.
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # setdefault: só define esses valores se quem chamou não tiver
        # passado algo diferente.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# Herda de AbstractUser (não de models.Model) pra ganhar de graça todos os
# campos e a lógica de um usuário real do Django (senha com hash, permissões,
# login, etc.)
class Usuario(AbstractUser):
    # Remove o campo username herdado — o login é só por email, então ele não
    # serve pra nada aqui (evita ter dois "identificadores" concorrendo).
    username = None

    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, blank=True, null=True)
    # Sobrescreve o `email` herdado do AbstractUser (lá ele não é único nem
    # obrigatório) — aqui precisa ser único porque vira o login (USERNAME_FIELD).
    email = models.EmailField(unique=True, null=False, blank=False)

    # Define e-mail como usuário de login
    USERNAME_FIELD = "email"
    # Campos obrigatórios, além do login e senha, pedidos ao criar um usuário
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Substitui o gerenciador padrão (que dependia de username) pelo nosso.
    objects = UsuarioManager()

    def __str__(self):
        return self.email
