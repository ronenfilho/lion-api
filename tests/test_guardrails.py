import pytest

from app.exceptions import SensitiveDataError
from app.services.guardrails import (
    check_citations,
    detect_personal_data,
    ensure_no_personal_data,
)


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("Meu CPF é 123.456.789-09, tenho restituição?", "CPF"),
        ("cpf 12345678909 pode ser dependente?", "CPF"),
        ("CPF 123456789-09", "CPF"),
        ("Meu e-mail é fulano.tal@gmail.com", "e-mail"),
        ("contato: a_b+irpf@empresa.gov.br", "e-mail"),
        ("Liga no (62) 99876-5432", "telefone"),
        ("62 99876-5432", "telefone"),
        ("+55 62 99876-5432", "telefone"),
        ("+5562998765432", "telefone"),
        ("celular 99876-5432", "telefone"),
        ("fixo (61) 3333-4444", "telefone"),
        ("fixo 6233334444", "telefone"),
    ],
)
def test_detecta_dado_pessoal(text: str, kind: str) -> None:
    assert detect_personal_data(text) == kind


@pytest.mark.parametrize(
    "text",
    [
        "Qual o limite de dedução com educação?",
        "No ano-calendário 2025-2026 qual é o prazo?",
        "A dedução de R$ 2.275,08 por dependente vale em 2026?",
        "O art. 8º da Lei 9.250/1995 ainda vale?",
        "Recebi 12000 reais de aluguel e R$ 28.559,70 de salário",
        "Qual a alíquota para quem ganha 4664,68 por mês?",
    ],
)
def test_pergunta_sem_dado_pessoal_passa(text: str) -> None:
    assert detect_personal_data(text) is None
    ensure_no_personal_data(text)


def test_bloqueio_explica_motivo_sem_ecoar_o_dado() -> None:
    with pytest.raises(SensitiveDataError) as exc_info:
        ensure_no_personal_data("Meu CPF é 123.456.789-09", field="pergunta")

    message = str(exc_info.value)
    assert "CPF" in message
    assert "pergunta" in message
    assert "123.456.789-09" not in message
    assert exc_info.value.kind == "CPF"


def test_citacoes_renumeradas_na_ordem_da_primeira_ocorrencia_sem_duplicar() -> None:
    result = check_citations("Primeiro [2]. Depois [1]. De novo [2].", available=2)

    assert result.sources == [1, 0]
    assert result.text == "Primeiro [1]. Depois [2]. De novo [1]."


def test_citacao_inexistente_e_removida_do_texto() -> None:
    result = check_citations("Vale a regra [1] e também a outra [7]. Fim [0].", available=3)

    assert result.sources == [0]
    assert result.text == "Vale a regra [1] e também a outra. Fim."


def test_resposta_sem_citacao_valida_nao_tem_fontes() -> None:
    assert check_citations("Resposta sem nenhuma fonte [5].", available=2).sources == []
