from django.db import IntegrityError, transaction
from datetime import timedelta
from django.utils import timezone

from django.test import TestCase

from casos_teste.models import Modulo, CasoDeTeste
from projetos.models import Projeto
from planos_teste.models import PlanoDeTeste
from execucoes.models import Execucao, ResultadoExecucao


class CasoDeTesteAPITest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")
        self.modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        self.projeto_b = Projeto.objects.create(nome="Projeto B")

    def test_criar_caso_sem_teste_atualizado_em(self):

        dados = {
            "titulo": "A",
            "pre_condicao": "A",
            "passos_reproducao": "A",
            "resultado_esperado": "A",
            "projeto": self.projeto.id,
            "modulo": self.modulo.id,
        }

        response = self.client.post("/api/caso-de-teste/", dados)

        self.assertEqual(response.status_code, 201)

    def test_criar_caso_com_modulo_de_outro_projeto_falha(self):

        dados = {
            "titulo": "A",
            "pre_condicao": "A",
            "passos_reproducao": "A",
            "resultado_esperado": "A",
            "projeto": self.projeto_b.id,
            "modulo": self.modulo.id,
        }
        response = self.client.post("/api/caso-de-teste/", dados)
        self.assertEqual(response.status_code, 400)


class RegressoesViewTest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")
        self.modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        self.caso_regredido = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        self.caso_normal = CasoDeTeste.objects.create(
            titulo="B",
            pre_condicao="B",
            passos_reproducao="B",
            resultado_esperado="B",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        self.plano = PlanoDeTeste.objects.create(nome="Plano A", projeto=self.projeto)
        self.plano.casos_de_teste.set([self.caso_regredido, self.caso_normal])

    def criar_resultado(self, caso, status, horas):
        execucao = Execucao.objects.create(
            plano_de_teste=self.plano,
            responsavel="QA",
            data_execucao=timezone.now() + timedelta(hours=horas),
        )

        ResultadoExecucao.objects.create(
            execucao=execucao, caso_de_teste=caso, status_execucao=status
        )

    def test_lista_so_casos_regredidos(self):
        self.criar_resultado(self.caso_regredido, "P", 1)
        self.criar_resultado(self.caso_regredido, "F", 2)
        self.criar_resultado(self.caso_normal, "P", 1)
        response = self.client.get("/api/regressoes/")
        ids = [item["id"] for item in response.json()]
        self.assertIn(self.caso_regredido.id, ids)
        self.assertNotIn(self.caso_normal.id, ids)

    def test_regressao_antes_da_edicao_nao_aparece_na_lista(self):
        self.criar_resultado(self.caso_regredido, "P", -2)
        self.criar_resultado(self.caso_regredido, "F", -1)

        self.caso_regredido.resultado_esperado = "B"
        self.caso_regredido.save()

        response = self.client.get("/api/regressoes/")
        ids = [item["id"] for item in response.json()]

        self.assertNotIn(self.caso_regredido.id, ids)


class CasosSemExecucaoRecenteViewTest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")
        self.modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        self.caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        self.plano = PlanoDeTeste.objects.create(nome="A", projeto=self.projeto)
        self.plano.casos_de_teste.set([self.caso])

    def criar_resultado(self, caso, status, horas):
        execucao = Execucao.objects.create(
            plano_de_teste=self.plano,
            responsavel="QA",
            data_execucao=timezone.now() + timedelta(hours=horas),
        )
        ResultadoExecucao.objects.create(
            execucao=execucao, caso_de_teste=caso, status_execucao=status
        )

    def test_caso_so_com_execucao_bloqueada_aparece_na_lista(self):
        self.criar_resultado(self.caso, "B", -1)
        response = self.client.get("/api/casos-sem-execucao-recente/")
        ids = [item["id"] for item in response.json()]
        self.assertIn(self.caso.id, ids)

    def test_dias_invalido_retorna_400(self):
        response = self.client.get("/api/casos-sem-execucao-recente/?dias=abc")
        self.assertEqual(response.status_code, 400)


class ModuloTest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")

    def test_impede_nome_duplicado_no_mesmo_projeto(self):
        modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)

    def test_permite_nome_duplicado_em_projetos_diferentes(self):
        modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        projeto = Projeto.objects.create(nome="Projeto B")
        modulo = Modulo.objects.create(nome="Modulo A", projeto=projeto)
        self.assertEqual(Modulo.objects.count(), 2)


class CasoDeTesteSaveTest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")
        self.modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)

    def test_criar_caso_define_teste_atualizado_em_na_criacao(self):
        agora = timezone.now()
        caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )

        self.assertAlmostEqual(
            caso.teste_atualizado_em, agora, delta=timedelta(seconds=5)
        )

    def test_editar_pre_condicao_altera_teste_atualizado_em(self):
        caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        valor_original = caso.teste_atualizado_em
        caso.pre_condicao = "B"
        caso.save()
        self.assertNotEqual(caso.teste_atualizado_em, valor_original)

    def test_editar_passos_reproducao_altera_teste_atualizado_em(self):
        caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        valor_original = caso.teste_atualizado_em
        caso.passos_reproducao = "B"
        caso.save()
        self.assertNotEqual(caso.teste_atualizado_em, valor_original)

    def test_editar_resultado_esperado_altera_teste_atualizado_em(self):
        caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        valor_original = caso.teste_atualizado_em
        caso.resultado_esperado = "B"
        caso.save()
        self.assertNotEqual(caso.teste_atualizado_em, valor_original)


class CasoDeTesteContarRegressoesTest(TestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(nome="Projeto A")
        self.modulo = Modulo.objects.create(nome="Modulo A", projeto=self.projeto)
        self.caso = CasoDeTeste.objects.create(
            titulo="A",
            pre_condicao="A",
            passos_reproducao="A",
            resultado_esperado="A",
            projeto=self.projeto,
            modulo=self.modulo,
        )
        self.plano = PlanoDeTeste.objects.create(nome="A", projeto=self.projeto)
        self.plano.casos_de_teste.set([self.caso])

    def criar_resultado(self, status, horas):
        execucao = Execucao.objects.create(
            plano_de_teste=self.plano,
            responsavel="QA",
            data_execucao=timezone.now() + timedelta(hours=horas),
        )
        ResultadoExecucao.objects.create(
            execucao=execucao, caso_de_teste=self.caso, status_execucao=status
        )

    def test_regressao_simples_conta_1(self):
        self.criar_resultado("P", 1)
        self.criar_resultado("F", 2)
        self.assertEqual(self.caso.contar_regressoes(), 1)

    def test_regressao_repetida_conta_1(self):
        self.criar_resultado("P", 1)
        self.criar_resultado("F", 2)
        self.criar_resultado("F", 3)
        self.assertEqual(self.caso.contar_regressoes(), 1)

    def test_falha_sem_passou_antes_nao_conta(self):
        self.criar_resultado("F", 1)
        self.criar_resultado("F", 2)
        self.assertEqual(self.caso.contar_regressoes(), 0)

    def test_regressao_antes_da_edicao_nao_conta_apos_edicao(self):
        self.criar_resultado("P", -2)
        self.criar_resultado("F", -1)
        self.caso.resultado_esperado = "B"
        self.caso.save()
        self.assertEqual(self.caso.contar_regressoes(), 1)
        self.assertEqual(self.caso.contar_regressoes_apos_edicao(), 0)
