# Quality Hub — Projeto Django

## O que é
Sistema de gestão de qualidade em Django: casos de teste, planos de teste, execuções e
documentação de projetos. Estudo/projeto pessoal do Marlon.

## Como estamos trabalhando

Formato tutorial socrático — regra explícita do Marlon: ele **não quer ser um
"copiador de código"**, quer construir autonomia real com Django ao longo do tempo.

- **Código de aplicação (models, views, templates, forms, lógica de negócio):**
  NUNCA mostrar a sintaxe pronta, nem quando ele pedir "me dá um exemplo". Em vez
  disso: explicar o conceito, fazer perguntas que guiem ele até a solução sozinho.
  Ele escreve, eu reviso/aponto problemas depois — mas a primeira versão sai da
  cabeça dele, não da minha. Isso vale mesmo que pareça mais lento.
- **Comandos de terminal / ferramental (venv, pip, migrate, startapp, runserver):**
  esses eu posso continuar passando prontos — é mecânica de tooling, não lógica de
  negócio, e ele já validou esse modo antes.
- Se em algum momento não estiver claro se algo é "conceito de negócio" (não mostrar
  pronto) ou "mecânica de ferramenta" (pode mostrar pronto), perguntar antes de decidir.
- **Comentários no código**: Marlon quer código comentado (breve, explicando o "porquê"
  de mecânica Django/Python — `Meta`, `on_delete`, `choices`, `__str__`, etc. — não
  restating o óbvio). Código já existente até a Fase 4 foi comentado numa passada só.
  Daqui pra frente, comentar junto conforme o código é escrito, discutindo com ele
  o que vale comentar (mesmo espírito socrático, aplicado a comentário).
- **Exercícios de fixação ao final de cada sub-etapa** (não só ao final da Fase inteira
  — fases longas como a 6 têm sub-etapas naturais, tipo um model de cada vez, mesmo
  padrão usado na Fase 3): pausa pra revisão antes de avançar pra próxima sub-etapa —
  mistura de (1) perguntas conceituais sobre mecânica Django/Python vista até ali,
  (2) exercícios de código isolados (não mexe no projeto real), e (3) práticas de
  busca/query via shell do Django nos models já existentes. Cobre tanto mecânica
  técnica quanto decisões de modelagem/domínio — **incluindo lógica de programação
  de verdade** (validações customizadas, permissões, campos calculados, filtros),
  sempre **dentro do contexto do Quality Hub**, não exercício abstrato/desconectado
  do projeto (ex: DRF puxa validação customizada de serializer, filtro de queryset
  por permissão, etc. — isso já cobre a lógica, não precisa de trilha separada).

## Modelo de domínio decidido (v1)

- **Projeto** — produto/sistema sendo testado. Tudo mais pendura aqui.
- **Módulo** — agrupa Casos de Teste dentro de um Projeto (ex: no Portal Corretor:
  crédito, subscrição, nomeação, endosso). Cadastro livre, criado conforme surge —
  não é lista fixa no código. Pertence a um Projeto (cada projeto tem seu próprio
  conjunto de módulos, isolado dos outros). Nome genérico de propósito, pra servir
  a qualquer tipo de projeto futuro, não só o domínio de seguros que inspirou a ideia.
- **Caso de Teste** — unidade atômica, vive numa "biblioteca" reutilizável (não pertence
  a um único plano). Campos: título, pré-condições, passos, resultado esperado,
  prioridade, status (rascunho/ativo/obsoleto), comentário/observação (campo único,
  geral sobre o caso). Pertence a um Projeto e a um Módulo (relação simples, um caso
  pertence a **um único** Módulo — não N:N; um caso que toca duas regras ao mesmo
  tempo vira seu próprio Módulo, ex: "Renovação com exceção de crédito/subscrição").
  Numeração do caso usa o `id` autoincrementado padrão do Django — não precisa de
  código customizado tipo "A1, A2, B1". Revisor **não** é campo do Caso de Teste —
  ver Plano de Teste abaixo.
- **Plano de Teste** — agrupa vários Casos de Teste via relação N:N (um caso pode estar
  em vários planos). Pertence a um Projeto (um único; planos não cruzam projetos).
  Não precisa corresponder a um Módulo inteiro — um plano pode ser um recorte pequeno
  e ad-hoc (ex: "PR #1234 - ajuste crédito/subscrição", pegando só alguns casos de
  dois Módulos diferentes do mesmo Projeto), ao lado de planos maiores "oficiais"
  que rodam todos os casos de um Módulo. Já suportado pela relação N:N, sem precisar
  de nenhum campo ou entidade extra. Tem campo de **revisor** (texto livre no MVP —
  vira `ForeignKey` de usuário customizado na Fase 5, ver roadmap) — revisão é do
  plano como um todo, não caso a caso.
- **Execução** — uma "rodada" de um Plano de Teste específico, com data, responsável e
  ambiente. Execução **só acontece via plano** (não há execução avulsa de caso solto no MVP).
- **Resultado de Execução** — para cada caso dentro de uma Execução: status (passou /
  falhou / bloqueado / não executado), executor, observações.
- **Bug/Issue** — decisão revisada na Fase 7: **não faz parte do Quality Hub**,
  nem como model leve com referência externa. Gerenciar ciclo de vida de bug
  (criar, mover entre estados, medir tempo de correção) é papel de uma
  ferramenta de fluxo de trabalho (ex: o projeto de Kanban cogitado
  separadamente, ver "Visão de longo prazo"), não de um sistema de gestão de
  **teste**. O que antes pareceria precisar de um Bug (ex: "eficácia dos
  casos de teste") já é resolvido só com o histórico de `Resultado de
  Execução` do mesmo Caso de Teste ao longo de várias Execuções (ver Fase 7)
  — o ciclo QA-aciona-Dev-corrige-QA-reexecuta fica todo capturado sem
  precisar de nenhum model novo.
- **Documento** — múltiplos documentos por Projeto (não um campo único), cada um com
  título, categoria, conteúdo. Estilo wiki interna. Pertence a um Projeto (obrigatório)
  e opcionalmente a um Módulo (`null=True, blank=True` no `ForeignKey` — ex: documento
  "Regras de Negócio - Crédito" ligado ao Módulo Crédito, pra navegar entre a
  documentação da regra e os casos de teste dela; documentos mais gerais, tipo análise
  de requisitos ou atas, ficam só no Projeto, sem Módulo). **Categoria** vira sua
  própria entidade (`CategoriaDocumento`), **global** — compartilhada entre todos os
  Projetos, não isolada por projeto (diferente de Módulo), porque categoria de
  documento (Ata de Reunião, Regra de Negócio, Análise de Requisitos) é conceito
  universal de projeto de software, não específico do domínio de um projeto.
  `CategoriaDocumento.nome` deve ter `unique=True` (evita duplicata exata).

Decisões conscientes de escopo:
- Sem versionamento/histórico de alteração de casos de teste no MVP (pode virar
  limitação ao gerar relatórios históricos, já que o caso pode mudar depois de já ter
  sido executado — aceito por enquanto). **Confirmado na prática na Fase 7**: os
  relatórios de **Regressões** e **Eficácia dos Casos de Teste** comparam
  `Resultado de Execução` ao longo do tempo pro mesmo `CasoDeTeste`, mas se o caso
  foi **editado** entre um resultado e outro (ex: resultado esperado mudou de "A"
  pra "B", passos de reprodução mudaram, pré-condição mudou), comparar um "Passou"
  antigo com um "Falhou" novo pode dar sinal falso — são, na prática, dois testes
  diferentes usando o mesmo registro. Sem versionamento, não dá pra saber
  automaticamente se uma edição foi "cosmética" ou mudou o teste de verdade.
  Mitigação mais simples cogitada (não implementada, decisão consciente de não
  fazer agora): campo `atualizado_em` no `CasoDeTeste`, usado pra ignorar
  resultados anteriores à última edição nos cálculos de Regressões/Eficácia.
  Revisitar se aparecer problema real na prática.
- **Decisão nova do Marlon**: adicionar `criado_em` (`auto_now_add=True`) e
  `atualizado_em` (`auto_now=True`) em 5 models específicos — `CasoDeTeste`,
  `Documento`, `PlanoDeTeste`, `Execucao`, `ResultadoExecucao` — não em todos
  os models do sistema (`Projeto`, `Módulo`, `CategoriaDocumento` continuam
  sem campo de data, decisão original mantida; `Usuario` já tem `date_joined`
  de graça via `AbstractUser`; `Execucao` já tem `data_execucao`, que é uma
  data de negócio diferente de "quando o registro foi criado/editado no
  sistema", os dois vão coexistir). **Implementado**: campos adicionados nos
  5 models, migration gerada e aplicada (registros existentes receberam
  `timezone.now()` como valor único de backfill, já que não tinha como saber
  a data real de criação deles). `manage.py check` limpo, dados de teste
  preservados. Motivação concreta que fez isso ser priorizado: é a peça que
  falta pra resolver a ressalva de confiabilidade de **Regressões**/**Eficácia
  dos Casos de Teste** (ver acima) — os cálculos ainda **não** usam
  `atualizado_em` pra ignorar resultados anteriores à última edição do caso;
  isso é o próximo passo pendente (ver "Próximo passo imediato").
- Caso de Teste continua pertencendo a um único Projeto no MVP (biblioteca reutilizável
  só *dentro* do projeto, via N:N com Planos de Teste). Reuso de casos de teste **entre
  projetos diferentes** (ex: projeto novo que precisa aplicar casos escritos
  originalmente pra outro projeto) não é suportado no MVP — cenário real, mas raro
  ("às vezes"), segundo o Marlon. Se precisar, contorna copiando o caso manualmente
  por enquanto. Vira candidato a revisão pós-MVP (Caso de Teste como biblioteca
  verdadeiramente global, sem dono de Projeto).
- Sem auditoria completa (quem mudou qual campo, valor antigo/novo) no MVP — nem em
  Projeto, nem em outros models. Depende de autenticação (Fase 5, ainda não existe) e
  de uma estrutura própria de histórico (tabela separada por alteração), que é maior
  que um campo simples. Por enquanto, `Projeto` não tem nenhum campo de data — nem
  criação, nem última atualização. Simplicidade decidida conscientemente; fácil
  adicionar depois via migration se aparecer necessidade real.
- Sem suporte a Gherkin no MVP. `Caso de Teste` usa só o formato tradicional
  (título, pré-condições, passos, resultado esperado) — sem campo de formato,
  sem estrutura genérica pra caber os dois estilos. Se precisar de Gherkin depois,
  fica pra revisão pós-MVP.
- `CategoriaDocumento` sendo sua própria tabela (com `unique=True` no nome) só evita
  **duplicata exata** (mesmo texto, letra por letra). Não evita **duplicata
  disfarçada** — nomes diferentes pro mesmo conceito (ex: "Ata de Reunião" vs "Atas"
  vs "Minuta de Reunião" cadastrados como categorias separadas). O banco não tem como
  saber que strings diferentes significam a mesma coisa pra um humano. Isso é
  limitação conhecida do MVP; resolve de duas formas possíveis mais pra frente, nenhuma
  delas é campo de model: (1) processo — restringir quem pode criar categoria nova
  (só via Admin, por exemplo); (2) interface — mostrar categorias já existentes de
  forma bem visível (dropdown com busca) antes de deixar criar uma nova, na Fase 6.
  **Consequência nova, identificada na Fase 7** (métrica de Documentação por
  módulo, que introduziu `CategoriaDocumento.obrigatoria`): a mesma
  ambiguidade fica **mais grave** aqui — se alguém criar "Regra XPTO" em vez
  de reusar "Regra de Negócio" (marcada obrigatória), um Módulo com
  documento só na categoria "errada" conta como **não documentado**, mesmo
  tendo o conteúdo certo. Mitigação aceita por enquanto: igual às duas
  acima — como categorias obrigatórias são um conjunto pequeno e deliberado
  (mudado raramente), processo (conferir lista existente antes de marcar
  nova categoria como obrigatória) resolve por ora; `list_filter` no Admin
  de `CategoriaDocumento` já ajuda a ver as existentes de relance. Pré-
  preencher/restringir o campo `nome` dinamicamente quando `obrigatoria` é
  marcado foi cogitado e descartado — exigiria JS customizado no Admin,
  desproporcional pro estágio do projeto.

## Roadmap (fases)

- [x] Fase 0 — Concepção / modelo de domínio (feito, ver acima)
- [x] Fase 1 — Ambiente (venv Python 3.14.6, instalar Django, `startproject qualityhub .`,
      `runserver`, `pip freeze > requirements.txt`) — feito e conferido
- [x] Fase 2 — Estrutura de apps: `projetos`, `casos_teste`, `planos_teste`,
      `execucoes`, `documentos` (nomes em português, `startapp` de cada um +
      registrados em `INSTALLED_APPS`) — feito e conferido. Model `Módulo` mora
      dentro de `casos_teste` (só ele depende de Módulo hoje; entidade usada por
      um app só fica junto do dono, só ganha app própria quando vários apps
      dependem dela — foi o critério usado pra `Projeto` também). Modelo tratado
      como vivo: ajustar sem medo se a prática mostrar necessidade, sem tentar
      prever tudo agora.
- [x] Fase 3 — Modelagem (models.py de cada app + migrations) — feito e conferido.
      8 models: `Projeto`, `Módulo`, `Caso de Teste`, `Plano de Teste`, `Execução`,
      `Resultado de Execução`, `CategoriaDocumento`, `Documento`. Restrições de
      unicidade aplicadas em todos os pontos identificados numa revisão (`Projeto`,
      `Módulo`, `PlanoDeTeste`, `ResultadoExecucao`, `CategoriaDocumento`).
      `on_delete` revisado caso a caso (`CASCADE` pra dependência forte, `PROTECT`
      pra `Documento → CategoriaDocumento`, `SET_NULL` pra `Documento → Módulo`
      por ser vínculo opcional).
- [x] Fase 4 — Django Admin (CRUD rápido pra validar o modelo) — feito e conferido.
      8 models registrados nos 5 `admin.py`, todos com `ModelAdmin` customizado
      (`list_display`, `search_fields`, e `list_filter` onde fez sentido). Lição
      aprendida na prática: `search_fields`/`list_display` não aceitam `ForeignKey`
      direto — precisam de sintaxe de duplo underscore apontando pra um campo de
      texto do model relacionado (ex: `"projeto__nome"`).
- [ ] Fase 5 — Autenticação e permissões (usuários/grupos). Autenticação (usuário
      customizado, login por e-mail, superusuário) concluída; permissões
      conscientemente adiadas pro final do projeto (ver item abaixo). Detalhe:
      - [x] App `usuarios` criado, com `Cargo` (cadastro livre, `nome` único) e
            `Usuario(AbstractUser)`.
      - [x] Login por **e-mail**, não por username: `email` sobrescrito
            (`unique=True`, obrigatório), `USERNAME_FIELD = "email"`,
            `username = None` (removido de vez — não usado). Exigiu um
            `UsuarioManager` customizado (`create_user`/`create_superuser`
            usando email em vez de username, já que o `UserManager` padrão do
            Django depende de username).
      - [x] `cargo` é opcional (`blank=True, null=True`, `on_delete=PROTECT`) —
            de propósito, pra não travar a criação do primeiro superusuário
            (não existe Cargo cadastrado ainda nesse momento).
      - [x] `AUTH_USER_MODEL = 'usuarios.Usuario'` configurado em `settings.py`.
      - [x] Banco e migrations resetados (sem dado real, ok apagar) — reaplicado
            do zero com `usuarios` já no lugar certo, sem o erro de
            `InconsistentMigrationHistory` que dava antes.
      - [x] Admin customizado (`UsuarioAdmin(UserAdmin)`) — `fieldsets`/
            `add_fieldsets`/`ordering` do `UserAdmin` padrão tiveram que ser
            reescritos (eles assumem username, que não existe mais aqui).
      - [x] Superusuário real criado (`marlon.nunes94@gmail.com`, via
            `createsuperuser` no terminal do Marlon) — confirmado
            `is_staff=True`, `is_superuser=True`.
      - [x] Campo `revisor` de `Plano de Teste` migrado de texto livre pra
            `ForeignKey` do `Usuario` (`on_delete=PROTECT`, opcional — mesmo
            raciocínio de sempre: preserva o plano se o revisor for
            deletado). Admin (`list_filter`) ajustado pra `revisor__first_name`.
      - [ ] Grupos/permissões (quem pode fazer o quê) — decisão consciente do
            Marlon: adiar pro final do projeto, quando já existir tela de uso
            real (Fase 6+) pra saber quais regras de acesso realmente importam
            na prática, em vez de especular agora sem contexto de uso.
- [ ] Fase 6 — API com Django REST Framework (DRF). Decisão tomada: entre SSR
      clássico, HTMX e DRF, o Marlon escolheu **DRF** — motivo: quer praticar
      o mesmo padrão de arquitetura do trabalho (backend/API + frontend
      separado, como o `Portal Corretor`). Escopo sequenciado em duas partes:
      **Fase 6a (agora)** — só a API (serializers, views/viewsets,
      autenticação e permissões de API), testável pela API navegável do DRF
      sem precisar de frontend nenhum ainda. **Fase 6b (fase futura, separada)**
      — frontend de verdade consumindo essa API; framework JS (React, Vue,
      etc.) ainda não decidido, decisão adiada de propósito pra não travar o
      progresso agora. Ideia de UX já registrada pra essa fase: na tela de
      montar um Plano de Teste, filtrar a lista de Casos de Teste por
      Módulo/categoria (crédito, subscrição...) com checkbox pra selecionar —
      e permitir criar um Caso de Teste novo sem sair da tela (duas chamadas
      de API — criar caso, depois salvar o plano — já suportado pela API
      atual, confirmado em teste; a "costura" de UX fica pra Fase 6b).
      - [x] `Projeto`: `ProjetoSerializer` (`ModelSerializer`, `fields = "__all__"`),
            `ProjetoViewSet` (`ModelViewSet`) registrado no `DefaultRouter` em
            `qualityhub/urls.py`, prefixo `/api/` (cuidado já visto na prática:
            não repetir o mesmo prefixo dentro do `router.register()` e no
            `path()` de fora, duplica a URL). Testado de ponta a ponta (GET/POST
            via `Client` de teste) — funcionando. Novo processo de exercício de
            fixação por sub-etapa aplicado pela primeira vez aqui, funcionou bem.
      - [x] `Módulo` (`casos_teste`): `ModuloSerializer`, `ModuloViewSet`,
            registrado no router com prefixo `"modulo"` (cuidado: prefixo
            deve descrever o **recurso**, não o app — `"casos_teste"` seria
            errado aqui, já que esse nome é do outro model do mesmo app).
            Testado ponta a ponta, incluindo `unique_together` (via ORM,
            `IntegrityError` real) e relação reversa (`projeto.modulo_set.all()`).
      - [x] `Caso de Teste` (`casos_teste`): `CasoDeTesteSerializer`,
            `CasoDeTesteViewSet`, prefixo `"caso-de-teste"`. Testado ponta a
            ponta. Bug pego na revisão: `Meta.model` ficou apontando pro
            `Modulo` (copy-paste do serializer anterior sem trocar o model).
      - [x] `Plano de Teste` (`planos_teste`): `PlanoDeTesteSerializer`,
            `PlanoDeTesteViewSet`, prefixo `"plano-de-teste"`. Testado ponta a
            ponta, incluindo criar com a relação N:N via lista de ids no POST
            (`casos_de_teste: [id1, id2]`). Decisão: `casos_de_teste` fica
            representado como lista de ids (padrão do `ModelSerializer`,
            `PrimaryKeyRelatedField`), não nested — decisão consciente de
            adiar, mesma lógica de sempre. Nested exigiria lógica de escrita
            customizada (`create`/`update`) sem ganho comprovado ainda, já que
            não existe frontend consumindo isso. Revisitar se/quando a Fase 6b
            (frontend) mostrar necessidade real.
      - [x] `Execução`/`Resultado de Execução` (`execucoes`): `ExecucaoSerializer`/
            `ExecucaoViewSet` (prefixo `"execucao"`) e `ResultadoExecucaoSerializer`/
            `ResultadoExecucaoViewSet` (prefixo `"resultado-teste"`). Testado ponta
            a ponta, incluindo `unique_together` (execucao+caso_de_teste) vindo
            como `400` com mensagem clara pela API — o `ModelSerializer` converte
            a restrição do model em validação automática, em vez do erro cru de
            banco que víamos direto no ORM.
      - [x] `Documento`/`CategoriaDocumento` (`documentos`): `DocumentoSerializer`/
            `DocumentoViewSet` (prefixo `"documento"`) e
            `CategoriaDocumentoSerializer`/`CategoriaDocumentoViewSet` (prefixo
            `"categoria-documento"`). Testado ponta a ponta. Bug pego na revisão:
            `router.register("categoria-documento", ...)` apontava pro
            `CasoDeTesteViewSet` por engano (autocomplete do editor) — o próprio
            Router recusou com `ImproperlyConfigured` (basename duplicado),
            evitando o erro silencioso.
      - [x] **Fase 6a concluída** — os 8 models têm API funcionando (serializer +
            viewset + rota), todos testados ponta a ponta. Falta só autenticação/
            permissões de API de verdade, adiada pro final do projeto (ver abaixo).
      - [ ] Autenticação/permissões de API (hoje só testado via login de sessão
            do Admin, ainda não configuramos autenticação de API "de verdade",
            tipo token) — **decisão consciente de adiar pro final do projeto**,
            mesma lógica de grupos/permissões da Fase 5. Não é bloqueio pra
            considerar um model "pronto" na Fase 6a; não reabrir isso a cada
            model novo.
- [ ] Fase 7 — Funcionalidades específicas (relatórios, dashboard de cobertura, export).
      Ideia futura registrada: management command de **importação automatizada** dos
      arquivos `.md` de regra de negócio do `EmissorMonorepo`
      (`~/Documentos/workspace/EmissorMonorepo`, ver `backend/templates/` e
      `backend/src/features/`) pra virarem `Documento` aqui no Quality Hub — extrair
      título/conteúdo de cada `.md` e criar os registros via código, não manualmente.
      Quantidade de arquivos ainda não levantada; decidir isso ajuda a confirmar se
      compensa automatizar (provável, já que Marlon confirmou que quer automatizado).

      **Escopo decidido pra Fase 7** (baseado num apêndice real de métricas de
      qualidade discutido com o time do Marlon — o que depende de ferramenta
      externa tipo SonarQube foi descartado, fora do escopo do Quality Hub):
      - **`Bug`/`Defeito` REMOVIDO do escopo do Quality Hub** (decisão
            revisada — ver nota na descrição do domínio, lá em cima). Chegamos
            a criar o app `defeitos` (`startapp` + `INSTALLED_APPS`) antes de
            perceber o problema conceitual — app removido de novo, sem nenhum
            model chegando a ser escrito. Raciocínio: gerenciar ciclo de vida
            de bug (criar, mover entre estados, medir tempo de correção) não é
            papel de um sistema de gestão de **teste** — é papel de uma
            ferramenta de fluxo de trabalho (o projeto de Kanban cogitado
            separadamente). Métricas de fluxo de bug (**bugs novos x
            resolvidos**, **tempo médio de correção**, **bugs de UX**,
            **vazamento de defeitos**, **bugs por ambiente**) saem de vez do
            escopo do Quality Hub — ficam só como ideia pro futuro projeto de
            Kanban, não anotadas aqui.
      - [x] **Regressões** — design fechado após discussão, **implementado e
            testado com dado real** (ver "Regressões concluída" em "Próximo
            passo imediato" pra detalhe). Correção
            importante: **não** é escopado por Plano de Teste — é por Caso de
            Teste, através de **todo** o histórico de `Resultado de Execução`
            dele, não importa de qual Plano/Execução cada resultado veio, já
            que o mesmo Caso pode estar em vários Planos). Definição: "está
            regredido agora" = resultado mais recente é "Falhou" **E** existe
            pelo menos um resultado anterior "Passou" (as duas condições
            juntas — um caso executado pela 1ª vez que falhou não conta,
            falta a segunda condição). Mais um dado complementar (não
            substitui a lista principal): contador de quantas vezes cada caso
            já regrediu no histórico completo (mesmo os já corrigidos depois)
            — sinaliza casos "instáveis"/flaky. Endpoint: **não** é uma ação
            de um recurso específico (nem de Plano, nem de Caso individual) —
            é um endpoint geral (`APIView`, não `ModelViewSet`), tipo
            `GET /api/regressoes/`, mostrando todos os casos regredidos do
            sistema (filtrável por Projeto se necessário). Não precisa de
            model novo, só query.
      - **`Eficácia dos Casos de Teste` REMOVIDA do escopo da Fase 7**
            (decisão revisada, mesmo padrão de revisão que já tinha tirado
            `Bug`/`Defeito` — ver nota no topo do domínio). Discussão que
            levou à remoção: a ideia original era aproximar a métrica de
            mercado **Test Effectiveness** (`defeitos encontrados /
            (encontrados + escapados)`) contando `Resultado de Execução`
            que vai de "Falhou" pra "Passou" no mesmo Caso de Teste — mas
            duas fragilidades reais apareceram ao revisar de perto:
            (1) **falso positivo de causa** — um F→P não prova que um
            defeito real foi corrigido; pode ser ambiente instável, reexecução
            sem mudança real, ou o próprio Caso de Teste que tinha erro
            (não o sistema testado). Sem o model `Bug` (removido do escopo)
            pra confirmar causa, a métrica infere causalidade a partir de
            correlação; (2) **granularidade errada** — a métrica de mercado
            conta **defeitos**, a aproximação contaria **execuções de caso**;
            um defeito real pode derrubar vários Casos de Teste ao mesmo
            tempo, e corrigi-lo vira vários F→P simultâneos — contando isso
            como "vários acertos" em vez de "um defeito corrigido", a métrica
            infla o número sem medir o que realmente promete medir. Diferente
            de Regressões (onde a aproximação é só "conservadora", perde
            sinal mas não inventa um sinal errado — ver ressalva do
            `teste_atualizado_em`), aqui a aproximação corria risco de
            **mentir** sobre o que está medindo. Não fica nem como ideia de
            "Quality Hub 2.0" — precisaria do model `Bug` (que já foi
            descartado por decisão de escopo do produto, não só falta de
            tempo) pra fazer sentido de verdade.
      - [x] **Cobertura de Execução** — implementada. **Correção de escopo
            feita na discussão**: não é "% do Plano inteiro, somando todo o
            histórico" (isso bateria 100% pra sempre depois da primeira
            rodada, e nunca refletiria uma rodada nova começando do zero)
            — é **por `Execucao`** (uma rodada específica), já que um Plano
            pode ter várias Execuções ao longo do tempo. Fórmula: `(nº de
            Casos do Plano com `Resultado de Execução` nesta Execução / nº
            total de Casos do Plano) * 100`. Vira método
            `Execucao.calcular_cobertura_execucao()`, exposto no
            `ExecucaoSerializer` como `qtd_cobertura_execucao`
            (`SerializerMethodField`, mesmo padrão de `qtd_regressoes`) —
            model e serializer no mesmo arquivo/app (`execucoes`), sem
            import cruzado. Trata divisão por zero (Plano sem nenhum caso
            → devolve `0`, não erro). Docstring adicionada. `manage.py
            check` limpo. **Não testado com dado real ainda** — o cenário
            de teste existente (`pl1`/`c1`) só tem 1 caso, então sempre daria
            100%; testar cobertura parcial de verdade exigiria um Plano com
            vários casos, alguns executados e outros não.
      - [x] **Documentação por módulo** — implementada, com **correção de
            regra feita na discussão**: a versão original ("tem pelo menos
            1 documento") foi considerada insuficiente pelo Marlon — um
            Módulo pode ter só o documento de "Fluxo" e faltar o de "Regra
            de Negócio" (ou vice-versa), e ainda assim contaria como
            documentado. Exigiu **model novo** (revisando o "não precisa de
            model novo" original): campo `CategoriaDocumento.obrigatoria`
            (`BooleanField`, `default=False`, migration gerada e aplicada)
            — Admin (`CategoriaDocumentoAdmin`) ganhou `obrigatoria` em
            `list_display` + `list_filter`, pra ver de relance quais
            categorias já estão marcadas (`BooleanField` vira checkbox no
            Admin automaticamente, sem precisar de `choices` — `choices` é
            pra 3+ opções, não pra sim/não). Escopo: **por Projeto**
            (mesma lógica de Cobertura de Execução — não faz sentido
            misturar Projetos diferentes numa média só). `Projeto
            .calcular_cobertura_documentacao()`: pra cada Módulo do
            Projeto, checa se ele tem documento de **todas** as categorias
            obrigatórias (não só alguma) — só aí conta como documentado.
            Devolve `0` se o Projeto não tiver módulo nenhum (protegido
            contra divisão por zero, mesmo padrão de Cobertura de
            Execução). Exposto no `ProjetoSerializer` como
            `cobertura_documentacao`. Docstring adicionada. Testado com
            dado real, incrementalmente: sem documento (`0.0`) → só
            "Regra de Negócio" (`0.0`, confirma que 1 categoria só não
            basta) → "Regra de Negócio" + "Fluxo" (`100.0`) — os 3 bateram
            com o esperado. **Limitação nova identificada** (ver nota
            atualizada na seção de decisões de escopo, sobre duplicata
            disfarçada de `CategoriaDocumento`): a métrica fica vulnerável
            a nomes de categoria inconsistentes — mitigação por processo,
            não por código, por enquanto.
      - [x] **Plano de Teste filtrado por prioridade** — implementada, com
            **duas correções de escopo feitas na discussão**: (1) nome
            original era impreciso — não é o **Plano** que é filtrado, são
            os **Casos de Teste dentro dele**; (2) não é **filtro**
            (esconder casos), é **ordenação** — todos os casos aparecem,
            só os de prioridade Alta vêm primeiro (decisão do Marlon depois
            de comparar as duas opções concretamente). Segue **sem**
            cruzar com Resultado de Execução (mantido). `PlanoDeTeste
            .casos_ordenados_por_prioridade()` — mapeia prioridade pra
            número (`{"A": 1, "M": 2, "B": 3}`) e usa `sorted(casos,
            key=lambda caso: mapa[caso.prioridade])`. Decisão consciente
            de ordenar em **Python** (`sorted`), não no banco (`Case`/
            `When` do Django) — lista pequena (casos de 1 Plano, não o
            sistema inteiro), e mais consistente com o estilo já usado no
            projeto. Exposto no `PlanoDeTesteSerializer` como
            `casos_ordenados`. Bug pego na revisão: método devolve uma
            **lista de objetos** `CasoDeTeste` (não um número, diferente de
            `qtd_regressoes`) — precisa passar por `CasoDeTesteSerializer
            (lista, many=True).data` antes de retornar, senão não vira
            JSON. Docstring adicionada. Testado com dado real (sem erro;
            plano de teste só tinha 1 caso no momento, então a ordenação
            em si não foi visualmente confirmada com múltiplas
            prioridades — mecanismo validado, cenário rico fica pendente
            se aparecer necessidade real de confirmar visualmente).
      - [x] **Casos de Teste "esquecidos"** — implementada. **Decisão de
            design**: "recente" não é fixo no código — vem como parâmetro
            na URL (`?dias=`, padrão 30), pra não travar num número
            arbitrário. `CasosEsquecidosView` (`APIView`, em
            `casos_teste/views_relatorios.py`, junto do `RegressoesView`),
            registrada em `qualityhub/urls.py` como
            `path("api/casos-esquecidos/", ...)`. Loop em
            `CasoDeTeste.objects.all()`, checando pra cada um se existe
            `ResultadoExecucao` com `execucao__data_execucao__gte` a data
            de corte (`timezone.now() - timedelta(dias)`) — se não existe
            (`.exists()` é `False`), é esquecido (cobre tanto "nunca
            executado" quanto "executado, mas há muito tempo", com a mesma
            checagem). Docstring adicionada. Testado com dado real via
            `APIRequestFactory` (não `Client` — `ALLOWED_HOSTS` vazio no
            `settings.py` bloqueia o `Client` de teste, pendência à parte,
            não relacionada a essa feature): `?dias=30` devolveu lista
            vazia (caso de teste executado há poucos dias), `?dias=1`
            devolveu o caso (mais de 1 dia desde a última execução) —
            os dois batem com o esperado. Bugs pegos na revisão: import
            errado de `timezone` (`datetime.timezone` em vez de
            `django.utils.timezone` — **terceira vez** que esse erro
            específico aparece nesta sessão, ver lição já registrada);
            `request.query_params.get()` devolve **string**, precisou de
            `int()` explícito antes de usar em `timedelta`; rota na
            `urls.py` inicialmente apontando pra `RegressoesView` por
            copy-paste (mesmo padrão de erro já visto no
            `categoria-documento`).
      - [x] **Resultados com falha, com observações** — implementada.
            **Discussão de escopo**: cogitado trazer falhas do sistema
            inteiro, mas decidido manter escopo por **uma Execução**
            específica (como já estava registrado) — evita misturar falha
            já corrigida (de rodada antiga) com falha atual, mesma lógica
            de não confundir "problema resolvido" com "problema em aberto"
            que já apareceu em Regressões/Eficácia. Também esclarecido que
            `ResultadoExecucaoViewSet` (`/api/resultado-teste/`) não
            resolve isso sozinho — serve bem pra CRUD (criar/editar/apagar
            resultado), mas não filtra nada, devolveria tudo sem distinção;
            relatório e CRUD são necessidades diferentes, cada um com sua
            ferramenta. `ResultadosComFalhaView` (`APIView`, junto das
            outras em `casos_teste/views_relatorios.py`), id da Execução
            vindo da **URL** (`<int:execucao_id>`, diferente do `?dias=`
            de Casos Esquecidos, que vinha por query param) — registrada
            como `path("api/execucao/<int:execucao_id>/falhas/", ...)`.
            Sem loop dessa vez — só um `.filter(execucao=execucao_id,
            status_execucao="F")` direto, serializado com
            `ResultadoExecucaoSerializer`. Docstring adicionada. Testado
            com dado real via `APIRequestFactory` — devolveu o resultado
            "F" esperado da execução testada.
      - Descartado do apêndice do time (depende de ferramenta externa, fora
        do escopo do Quality Hub): densidade de defeitos, complexidade
        ciclomática, cobertura de código (linha/ramificação) — os dois
        primeiros dependem do SonarQube ("em estudo" pelo time do Marlon), o
        terceiro é cobertura de **código**, conceito diferente do "dashboard
        de cobertura" do Quality Hub (que é % de Casos de Teste executados).
      - Também descartado por depender só parcialmente do Bug (tempo médio de
        correção, bugs de UX, vazamento de defeitos, bugs novos x resolvidos)
        — não fechados no MVP da Fase 7, revisar depois que o model `Bug`
        existir e mostrar o que realmente é fácil de tirar dele.
- [ ] Fase 8 — Documentação (app `docs`). Ideia já discutida: (1) docstrings
      nas classes/métodos (`class`/`def`), diferente dos comentários `#` que já
      usamos — documenta a classe/função inteira, legível por ferramentas
      (`help()`, IDE, gerador de doc); (2) documentação de API "de verdade"
      (comportamento, campos obrigatório/opcional) via `drf-spectacular` —
      gera documentação interativa (estilo Swagger/OpenAPI) **automaticamente**
      a partir dos serializers/viewsets já existentes, sem escrever na mão.
- [ ] Fase 9 — Testes automatizados do próprio sistema
- [ ] Fase 10 — Deploy

## Visão de longo prazo (pós-MVP, "Quality Hub 2.0")

Fora do escopo das Fases 0-10 acima — só atacar depois do MVP estar rodando de
verdade. Registrado pra não esquecer, não é compromisso de quando fazer.

- **Rastreabilidade completa dentro do SDLC**: Requisito → Desenvolvimento →
  Teste → Defeito, com evidências documentadas. Precisa de peças novas que hoje
  não existem:
  - **Requisito** como entidade estruturada e rastreável (linkável a Casos de
    Teste específicos que o cobrem) — diferente do `Documento` atual, que é só
    texto livre estilo wiki, sem essa rastreabilidade. Desbloquearia
    **Cobertura de Requisitos** (`% de requisitos com pelo menos um Caso de
    Teste vinculado`) — métrica de mercado citada com frequência, diferente
    da "Cobertura de Execução" da Fase 7 (que mede execução de Casos de
    Teste, não relação com requisito). Chegou a ser cogitado pra dentro da
    Fase 7 (mais central ao propósito do Quality Hub do que o Bug/Defeito
    era), mas o Marlon recuou pra pensar melhor na modelagem — fica
    registrada a descoberta importante feita na discussão: **não é só
    `Requisito`, é uma hierarquia de duas entidades**:
    ```
    Feature (nome ainda em aberto — "Funcionalidade"? "Demanda"?)
      - representa o pedido do cliente como um todo
      - carrega Definition of Ready (DoR) e Definition of Done (DoD)
        — POSIÇÃO AINDA EM ABERTO, ver questionamento abaixo
      ├── Requisito 1
      ├── Requisito 2
      └── Requisito 3
    ```
    **Questionamento em aberto, ainda não resolvido**: DoR/DoD deveria ficar
    na **Feature** (um "pronto"/"concluído" só, pro pedido inteiro — faz
    sentido se os Requisitos de uma Feature são sempre desenvolvidos/
    entregues juntos, em bloco) ou em **cada Requisito individualmente**
    (faz sentido se, na prática, um Requisito de uma Feature pode já estar
    pronto pra desenvolver enquanto outro da mesma Feature ainda está em
    discussão — progresso independente, não em bloco). Depende de como o
    Marlon trabalha de verdade no dia a dia — resolver quando retomar.
    Outras perguntas em aberto: nome da entidade "Feature" em português; se
    Feature pertence a um Projeto; se DoR/DoD é texto livre ou estruturado
    (checklist); relação Requisito↔Caso de Teste (provável N:N, não
    confirmado).
  - **Defeito/Bug** de verdade (já reservado conceitualmente desde a Fase 0,
    "vai se ligar a Resultados de Execução com falha", mas nunca modelado).
  - **Desenvolvimento**: vínculo com commits/PRs/branches do controle de
    versão (ex: GitHub, no caso do `EmissorMonorepo`).
  - **Evidências**: suporte a anexo/upload de arquivo (print, log) — nenhum
    model hoje suporta isso.
- **Integração com ferramentas de terceiros**: New Relic, Sentry, SonarQube.
  Tecnicamente viável via API de cada ferramenta (ex: Resultado de Execução
  com falha linkando a um erro do Sentry; Defeito se auto-criando a partir de
  um alerta). Exigiria management commands/jobs agendados buscando dados
  dessas APIs.
- **Geração de Casos de Teste por IA a partir de Documentos**: pegar o
  `conteudo` de um `Documento` (regra de negócio) e mandar pra uma API de LLM
  (Claude, ou outra), recebendo de volta uma sugestão estruturada de Caso de
  Teste (título, pré-condição, passos, resultado esperado). Tecnicamente
  viável — é basicamente "ler texto, gerar sugestão estruturada". Pontos a
  decidir quando for atacado: custo por chamada de API, chave de API, e um
  fluxo de revisão humana antes do caso virar "Ativo" (já resolvido
  parcialmente pelo model: a IA geraria com `status="R"` — Rascunho — e um QA
  revisaria/ativaria depois, sem precisar de campo novo).

## Ambiente técnico
- Python usado no projeto: **3.14.6** (via pyenv, `~/.pyenv/versions/3.14.6`) — decisão
  consciente do Marlon, substitui a ideia inicial de usar o 3.11 do sistema.
- Nome do projeto Django (settings): `qualityhub`
- Projeto separado do `django_basico` (outro projeto de estudo em
  `~/Estudo/DJANGO_BASICO`), sem relação entre os dois.
- Banco de dados: **SQLite mantido** durante desenvolvimento (Fases 2-4, modelagem).
  Troca pra PostgreSQL fica planejada pra perto da Fase 5 (autenticação/múltiplos
  usuários) ou Fase 10 (Deploy), quando escrita concorrente passa a importar de
  verdade. Decisão consciente — o ORM abstrai a troca, então não há ganho em
  antecipar antes de ter schema estável.

## Próximo passo imediato
**Fase 6a concluída** — os 8 models têm API completa, todos testados ponta a
ponta (ver detalhes na linha da Fase 6 do roadmap). Nota de estudo em
`notas_estudo/drf_fluxo_api.md`.

**Bateria de revisão de ORM concluída** — filtro simples, filtro combinado,
`.count()`, relação reversa, `save()`/criação, `.update()`, `.exclude()`,
todos praticados de verdade no shell com os models reais do projeto. Objetivo
era ajustar o ritmo dos exercícios (tinham subido de dificuldade rápido
demais); segue valendo aplicar isso daqui pra frente.

**Escopo da Fase 7 já decidido** (ver linha da Fase 7 no roadmap pra detalhe
completo) — baseado num apêndice real de métricas de qualidade do time do
Marlon + brainstorm "se eu fosse QA". `Bug`/`Defeito` foi **removido** do
escopo (decisão revisada — não é papel do Quality Hub, ver nota na descrição
do domínio). Fase 7 nasceu como "só relatórios/consultas, nenhum model
novo" — **revisado na prática**: 2 dos 7 itens acabaram exigindo campo
novo (`teste_atualizado_em` em `CasoDeTeste`, pra resolver a ressalva de
confiabilidade de Regressões; `CategoriaDocumento.obrigatoria`, pra
Documentação por módulo) — sempre pequeno o suficiente pra não virar model
novo de verdade, mas a promessa original de "zero mudança de schema" não
se sustentou no fim. **Fase 7 concluída** — os 7 itens do roadmap
resolvidos (Eficácia removida por decisão consciente, os outros 6
implementados e testados):
1. Regressões.
2. ~~Eficácia dos Casos de Teste~~ — **removida** (ver linha da Fase 7 no
   roadmap): a aproximação sem `Bug` corria risco de inferir causa errada
   e contar granularidade errada (execução de caso, não defeito).
3. ~~Cobertura de Execução~~ — **feita** (ver linha da Fase 7 no roadmap;
   escopo corrigido pra ser por Execução/rodada, não por Plano inteiro).
   "Cobertura de Requisitos" — a versão mais citada no mercado — fica pra
   depois, precisa do `Requisito`, ver Visão de longo prazo.
4. ~~Documentação por módulo~~ — **feita** (ver linha da Fase 7; regra
   corrigida pra exigir TODAS as categorias obrigatórias, não só alguma —
   exigiu campo novo `CategoriaDocumento.obrigatoria`).
5. ~~Plano de Teste filtrado por prioridade~~ — **feita** (ver linha da
   Fase 7; virou ordenação de Casos de Teste dentro de um Plano, não
   filtro — sem cruzar com Resultado de Execução).
6. ~~Casos de Teste "esquecidos"~~ — **feita** (ver linha da Fase 7 no
   roadmap; prazo "recente" configurável via `?dias=` na URL).
7. ~~Resultados com falha, com observações~~ — **feita** (ver linha da
   Fase 7 no roadmap; escopo por Execução, id vem da URL).

Frontend (Fase 6b) confirmado como "a última coisa do projeto". Geração de
Casos de Teste por IA registrada só como visão de longo prazo (ver seção
acima), fora do escopo imediato. Ideia à parte, ainda só "elucubração", não
registrada como escopo: projeto de Kanban separado, reaproveitando
autenticação do Quality Hub — retomar só se o Marlon trouxer de novo.

**Regressões concluída** (design já fechado, ver linha da Fase 7):
- [x] `RegressoesView` (`APIView`, não `ModelViewSet`) criada em
      `casos_teste/views_relatorios.py`, registrada em `qualityhub/urls.py`
      como `path("api/regressoes/", RegressoesView.as_view())` — sem passar
      pelo `router` (isso é só pra `ModelViewSet`).
- [x] Loop em `CasoDeTeste.objects.all()`, checando pra cada um: mais recente
      é "F" (`ResultadoExecucao.objects.filter(caso_de_teste=caso).order_by("-execucao__data_execucao").first()`)
      **e** existe "P" anterior (`.filter(caso_de_teste=caso, status_execucao="P").exists()`).
      Decisão consciente de manter o loop simples (não otimizar com
      `Subquery`/`Exists` de anotação) — versão eficiente de query única fica
      pra depois, se o volume real de dados um dia justificar.
      Bug pego na revisão: primeira versão do `.filter()` do "mais recente"
      estava sem `caso_de_teste=caso` — pegava o resultado mais recente do
      **sistema inteiro**, não do caso do loop (provado com um segundo Caso
      de Teste sem nenhum resultado próprio, que "herdava" resultado de
      outro caso).
      Resultado serializado com `CasoDeTesteSerializer(regredidos, many=True).data`.
      Testado ponta a ponta (`GET /api/regressoes/`) — funcionando.
- [x] Contador de "quantas vezes já regrediu" — decidido e implementado.
      Virou **método do model** `CasoDeTeste.contar_regressoes()` (não função
      solta em `views_relatorios.py`): decisão pelo critério "recebe um único
      argumento, que é o próprio objeto sendo calculado" → sinal de que deveria
      ser `self`, não parâmetro solto. Regra: conta toda vez que o resultado
      **imediatamente anterior** (cronologicamente) foi "P" e o atual é "F"
      (uma sequência de vários "F" seguidos conta só 1 vez, não uma regressão
      nova a cada repetição). Exposto no `CasoDeTesteSerializer` como campo
      `qtd_regressoes` via `SerializerMethodField` (**Opção A**, escolhida
      sobre serializer separado: aparece automaticamente em qualquer lugar que
      já usa esse serializer, sem precisar caçar endpoint por endpoint) —
      hoje aparece em `/api/caso-de-teste/` e `/api/regressoes/`; não aparece
      em `/api/plano-de-teste/` porque esse serializer representa
      `casos_de_teste` só como lista de ids, não nested. Trade-off consciente:
      o cálculo roda de novo a cada serialização (mesma lógica de "loop
      simples, otimizar depois se o volume justificar" da Regressões).
      Testado no shell com objeto criado dentro de `transaction.atomic()` +
      rollback (sem sujar o banco) — confirmado que o campo aparece e calcula
      `0` pra caso sem histórico. Comentários no código novo: adicionados,
      curtos (2 no model + 1 no serializer) — Marlon pediu pra evitar
      comentário demais mesmo quando é do tipo "porquê" (regra é sempre
      "algum adiciona valor", não quantidade).
      **Testado com histórico real** (sessão seguinte): cenário completo
      criado no shell — `Projeto`, `Modulo`, `CasoDeTeste`, `PlanoDeTeste`
      (`ManyToManyField` exige salvar o Plano **antes** de associar casos,
      via `pl1.casos_de_teste.set([c1])` — não dá pra passar `casos_de_teste=`
      direto no construtor, erro real reproduzido: `TypeError: Direct
      assignment to the forward side of a many-to-many set is prohibited`),
      7 `Execucao` com `data_execucao` crescente (`timezone.now() +
      timedelta(hours=N)`) e 7 `ResultadoExecucao` simulando a sequência
      `P, P, F, P, F, F, P`. `c1.contar_regressoes()` devolveu **2** (bate com
      o esperado) e `CasoDeTesteSerializer(c1).data["qtd_regressoes"]` também
      devolveu **2** — confirmado ponta a ponta, model e serializer batendo.
      **Contador de regressões: fechado.**

**Lição de hoje pra lembrar**: `.save()` sempre devolve `None` — nunca
encadear `Model(...).save()` numa variável que você vai reusar depois
(`var = Model(...).save()` deixa `var` como `None`). Sempre em duas linhas
separadas.

**Lição nova**: import circular real entre apps (`casos_teste` ↔ `execucoes`
↔ `planos_teste`) quebrou o `manage.py check` inteiro quando um método novo em
`casos_teste/models.py` importou `ResultadoExecucao` no **topo** do arquivo.
Solução: import **local**, dentro do método/função que usa a classe (só
executa em tempo de chamada, quando todos os apps já carregaram) — não no
topo do módulo. Confirmado reproduzindo o erro antes de corrigir.

**`criado_em`/`atualizado_em` implementados** (sessão seguinte à do contador
de regressões) — nos 5 models combinados (`CasoDeTeste`, `Documento`,
`PlanoDeTeste`, `Execucao`, `ResultadoExecucao`), migration gerada e aplicada,
dados de teste preservados (ver decisão detalhada acima). Motivo de ter sido
retomado agora: é pré-requisito pra resolver a ressalva já registrada de que
Regressões/Eficácia comparam resultados sem saber se o Caso de Teste foi
editado no meio do caminho (sinal falso). **Pendência nova, mais específica**:
usar `atualizado_em` dentro de `contar_regressoes`/`RegressoesView` pra
ignorar `Resultado de Execução` anteriores à última edição do caso — ainda
não feito.

**Ressalva de confiabilidade resolvida** (mesma sessão): decisão, ao
discutir a implementação, de **não** reaproveitar `atualizado_em`
(`auto_now=True`, dispara em qualquer save) pra esse filtro — campos
irrelevantes pro teste em si (`titulo`, `status`, `prioridade`,
`observacao`) não deveriam "resetar" o corte de confiabilidade, só os que
definem o teste de fato: `pre_condicao`, `passos_reproducao`,
`resultado_esperado`. Implementado:
- [x] Campo novo `teste_atualizado_em` em `CasoDeTeste` (migration à parte
      de `atualizado_em`) — nasce igual ao momento da criação, só muda
      quando um dos 3 campos relevantes muda de verdade.
- [x] `save()` customizado no model: na criação, seta
      `teste_atualizado_em = timezone.now()`; na edição, busca a versão
      ainda salva no banco (`CasoDeTeste.objects.get(id=self.id)`) e só
      atualiza o campo se `pre_condicao`/`passos_reproducao`/
      `resultado_esperado` mudaram. Bug real pego e corrigido durante a
      construção: import errado (`from datetime import timezone` em vez de
      `from django.utils import timezone` — `datetime.timezone` não tem
      `.now()`), reproduzido com `AttributeError` real antes de corrigir.
      Testado com dado real: editar campo irrelevante (`titulo`) não mudou
      `teste_atualizado_em`; editar `resultado_esperado` mudou — confirmado
      nos dois sentidos.
- [x] **Decisão de manter as duas métricas** (total e filtrada) em vez de
      substituir — mesma lógica já usada em Regressões (lista principal +
      contador complementar, duas leituras do mesmo dado). Refatorado pra
      evitar duplicar a regra de contagem em dois lugares: `contar_regressoes`
      (histórico inteiro) e `contar_regressoes_apos_edicao` (novo, filtra
      por `execucao__data_execucao__gte=self.teste_atualizado_em`) só montam
      a query certa e delegam pra `_contar_regressoes_filtradas` (privado,
      só conta — a regra "P antes, F agora" mora aqui uma vez só).
- [x] Exposto no `CasoDeTesteSerializer` como `qtd_regressoes_apos_edicao`
      (mesmo mecanismo de `SerializerMethodField` de antes).
- [x] Testado ponta a ponta com dado real: resultado bateu `2` (total) e
      `1` (filtrado) — o "1" foi **verificado manualmente**, campo a campo,
      comparando `teste_atualizado_em` contra a data de cada Execução (não
      é `0` porque as datas de teste usavam `timedelta(hours=N)` a partir de
      uma sessão passada, e parte delas ainda cai depois do corte — não é
      bug, é artefato de como o cenário de teste foi montado).
      Comentários curtos adicionados no código novo (model + serializer).
      Docstrings adicionadas em `contar_regressoes`, `contar_regressoes_apos_edicao`,
      `_contar_regressoes_filtradas` e `save()` (explicam o quê/porquê do
      método inteiro — diferente do comentário `#`, que explica um detalhe
      pontual de uma linha).

**Limitação conhecida, aceita conscientemente** (achada pelo Marlon
revisando o `save()`): comparar `pre_condicao`/`passos_reproducao`/
`resultado_esperado` com `!=` distingue **quais campos** importam, mas
**não** distingue, dentro desses 3 campos, uma correção cosmética (typo)
de uma mudança real de sentido — qualquer diferença de texto, por menor
que seja, empurra `teste_atualizado_em`. Resolver isso de verdade exigiria
comparação semântica de texto (fora de escopo, tipo NLP/IA). Pior caso
prático: um typo corrigido reseta o corte de `contar_regressoes_apos_edicao`
mais do que precisaria, perdendo histórico ainda válido — não gera número
errado, só um pouco mais conservador. Mesma família do problema já
registrado acima ("não dá pra saber se uma edição foi cosmética ou mudou
o teste de verdade"), só que agora restrito aos 3 campos relevantes em vez
dos 7 campos inteiros.