# Fluxo de uma requisição na API (DRF)

Notas de estudo — como uma requisição HTTP vira um registro salvo no banco,
usando o `Módulo` como exemplo (mesmo padrão vale pra qualquer model).

## O dado caminhando de verdade — exemplo de `POST` (criar)

Cliente manda um `POST /api/modulo/` com esse corpo:

```json
{"nome": "Crédito", "projeto": 3}
```

```
Cliente
  │  POST /api/modulo/  { "nome": "Crédito", "projeto": 3 }
  ▼
Router
  │  "essa URL bate com o prefixo 'modulo' → manda pro ModuloViewSet"
  │  (não olha o conteúdo do dado, só a URL)
  ▼
ModuloViewSet
  │  "é um POST → chama a ação de criar, usando o serializer_class"
  ▼
ModuloSerializer(data={"nome": "Crédito", "projeto": 3})
  │  is_valid() → confere: nome é texto? projeto=3 existe na tabela Projeto?
  │  validated_data = {"nome": "Crédito", "projeto": <Projeto: Portal Corretor>}
  │  .save() → transforma isso num objeto Modulo de verdade
  ▼
Modulo (banco)
  │  INSERT na tabela casos_teste_modulo
  │  vira: Modulo(id=1, nome="Crédito", projeto_id=3)
  ▼
  ── agora o caminho volta, pra responder o cliente ──
  ▲
ModuloSerializer(modulo_criado)
  │  .data → transforma o objeto de volta em algo serializável
  │  {"id": 1, "nome": "Crédito", "projeto": 3}
  ▲
ModuloViewSet
  │  monta a Response com esse JSON + status 201 (Created)
  ▲
Cliente
     recebe: 201 { "id": 1, "nome": "Crédito", "projeto": 3 }
```

## O dado caminhando de verdade — exemplo de `GET` (listar)

Cliente pede `GET /api/modulo/` (sem corpo, só pedindo a lista):

```
Cliente
  │  GET /api/modulo/
  ▼
Router
  │  "essa URL bate com o prefixo 'modulo' → manda pro ModuloViewSet"
  ▼
ModuloViewSet
  │  "é um GET (lista) → pega o queryset inteiro"
  │  Modulo.objects.all() → [Modulo(id=1, nome="Crédito", ...), Modulo(id=2, ...)]
  ▼
ModuloSerializer(queryset, many=True)
  │  many=True: percorre CADA objeto da lista, um por um,
  │  convertendo cada um pra dict
  │  [{"id": 1, "nome": "Crédito", "projeto": 3},
  │   {"id": 2, "nome": "Subscrição", "projeto": 3}]
  ▲
ModuloViewSet
  │  monta a Response com essa lista de JSON + status 200 (OK)
  ▲
Cliente
     recebe: 200 [{"id": 1, "nome": "Crédito", "projeto": 3},
                   {"id": 2, "nome": "Subscrição", "projeto": 3}]
```

Repara na diferença chave entre os dois: no `POST`, o dado entra como **texto
bruto** (JSON) e sai do Serializer como **objeto Python validado** — o
Serializer traduz "pra dentro". No `GET`, é o contrário: o dado entra como
**objeto(s) Python** (vindo do `queryset`) e sai como **JSON** — o Serializer
traduz "pra fora". É a mesma classe fazendo os dois sentidos, dependendo de
como você a chama (`Serializer(data=...)` vs `Serializer(objeto)`).

## Mapa

```
                         ┌───────────────────────────────┐
                         │       /api/modulo/  (URL)      │
                         │  Router direciona a requisição │
                         │  pro ViewSet certo              │
                         └───────────────┬─────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │         ModuloViewSet            │
                         │  Recebe a requisição HTTP         │
                         │  (GET, POST, PUT, DELETE)         │
                         │  queryset = quais registros       │
                         │  serializer_class = quem traduz   │
                         └───────────────┬─────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │       ModuloSerializer            │
                         │  Traduz JSON <-> objeto Python    │
                         │  Valida os dados                   │
                         └───────────────┬─────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │             Modulo                 │
                         │      (model / banco de dados)      │
                         └───────────────────────────────┘
```

## 1. URL / Router — o direcionador

Decide **pra qual `ViewSet`** uma requisição deve ir, olhando só o endereço
(`/api/modulo/`, `/api/projetos/`...). Não sabe nada sobre o dado em si —
só sabe "essa URL pertence a esse ViewSet".

O `DefaultRouter` gera **sozinho** as 5 rotas padrão (listar, criar, ver um,
editar, deletar) a partir de uma única linha de registro:

```python
router = DefaultRouter()
router.register("modulo", ModuloViewSet)   # prefixo -> ViewSet
router.register("projetos", ProjetoViewSet)
```

Isso é incluído no `urlpatterns` principal, sob um prefixo geral (`api/`):

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
```

Resultado: `GET /api/modulo/` → lista; `POST /api/modulo/` → cria;
`GET /api/modulo/1/` → detalhe do registro 1; etc. — tudo gerado pelo router,
sem escrever cada rota na mão.

## 2. ViewSet — quem recebe e orquestra

Depois que o Router decidiu pra onde mandar, o `ViewSet` é quem efetivamente
processa a requisição. Um `ModelViewSet` já vem com as 5 operações CRUD
prontas — você só declara **onde buscar os dados** e **quem traduz**:

```python
class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()       # quais registros esse ViewSet trabalha
    serializer_class = ModuloSerializer   # quem faz a tradução JSON <-> objeto
```

Exemplo do que acontece num `POST` (criar): o ViewSet recebe o JSON bruto do
corpo da requisição, passa pro `serializer_class` validar, e se for válido,
manda salvar. Num `GET` (listar): o ViewSet pega o `queryset`, passa cada
objeto pelo serializer (objeto → JSON), e devolve a lista.

## 3. Serializer — o tradutor

Converte nos dois sentidos, e valida no caminho de entrada:

**Objeto Python → JSON** (quando alguém pede dados, ex: `GET`):

```python
modulo = Modulo.objects.get(id=1)
serializer = ModuloSerializer(modulo)
serializer.data
# {'id': 1, 'nome': 'Crédito', 'projeto': 3}
```

**JSON → objeto validado** (quando alguém envia dados, ex: `POST`):

```python
dados = {"nome": "Subscrição", "projeto": 3}
serializer = ModuloSerializer(data=dados)
serializer.is_valid()          # True se os dados baterem com as regras do model
serializer.validated_data      # dado limpo, pronto pra virar objeto
serializer.save()              # cria (ou atualiza) o registro no banco
```

A classe `Meta` dentro do serializer diz **qual model** ele representa e
**quais campos** expor — mesmo nome (`Meta`) usado no `models.py` pra
`unique_together`, só que aqui configurando outra coisa (é sempre "config da
classe onde está dentro", o conteúdo muda conforme o contexto).

```python
class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = "__all__"   # expõe todos os campos do model
```

## 4. Model — onde o dado vive de verdade

Depois que o serializer valida e chama `.save()`, o dado vira (ou atualiza)
uma linha na tabela `casos_teste_modulo` do banco — o mesmo model que já
usamos no Admin, sem nenhuma diferença. API e Admin são só **duas portas de
entrada diferentes** pro mesmo dado.

## Resumo de uma linha cada

- **URL/Router** → decide pra onde a requisição vai.
- **ViewSet** → recebe, orquestra (usa `queryset` + `serializer_class`).
- **Serializer** → traduz e valida (JSON ↔ objeto Python).
- **Model** → onde o dado realmente vive (banco).
