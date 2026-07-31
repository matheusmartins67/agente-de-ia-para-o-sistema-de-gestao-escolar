import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SYSTEM_PROMPT = (Path(__file__).resolve().parent.parent / "prompts" / "school_system_prompt.md").read_text(encoding="utf-8")


class TutorService:
    """School assistant provider boundary with safe offline guidance."""

    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider

    def reply(self, message: str, student_level: int | None = None) -> str:
        if self.provider == "openai_compatible":
            return self._openai_compatible_reply(message, student_level)
        if self.provider != "mock":
            raise RuntimeError("Unknown LLM provider. Use mock or openai_compatible.")
        return self._offline_guidance(message)

    @staticmethod
    def _offline_guidance(message: str) -> str:
        text = message.lower()
        if "cadastr" in text and "aluno" in text:
            return "**Resposta:** Acesse **Alunos** e escolha a opção para incluir um novo aluno.\n\n**Passos:**\n1. Abra **Alunos**.\n2. Clique em incluir novo aluno.\n3. Preencha os dados obrigatórios.\n4. Confirme o cadastro.\n5. Para matriculá-lo, abra **Turmas** e use **Gerenciar alunos**.\n\n**Atenção:** o aluno precisa estar cadastrado antes da matrícula na turma."
        if "média" in text or "media" in text or ("nota" in text and "nota da" not in text):
            return "**Resposta:** O sistema calcula a média a partir de três notas lançadas para o aluno.\n\n**Passos:**\n1. Acesse **Notas**.\n2. Selecione a turma e o aluno.\n3. Lance as três avaliações.\n4. Confira a média calculada automaticamente.\n\n**Atenção:** não consigo consultar notas reais sem uma integração autenticada com o sistema."
        if "frequ" in text or "falta" in text:
            return "**Resposta:** O registro de frequência é feito por turma.\n\n**Passos:**\n1. Acesse o módulo de **Frequência**.\n2. Selecione a turma.\n3. Informe a presença ou falta de cada aluno.\n4. Salve o registro.\n\n**Atenção:** confirme a turma e a data antes de salvar, pois o registro tem impacto acadêmico."
        if "pagamento" in text or "parcela" in text or "financeir" in text:
            return "**Resposta:** Posso orientar o registro, mas não confirmar um pagamento sem uma integração autorizada e os dados validados.\n\n**Passos:**\n1. Acesse o módulo **Comercial** ou **Financeiro**.\n2. Localize o aluno e a matrícula.\n3. Confira a parcela, o valor e a data.\n4. Confirme os dados antes de registrar o pagamento.\n\n**Atenção:** pagamentos têm impacto financeiro e exigem confirmação explícita dos dados corretos."
        if "erro" in text or "não abre" in text or "nao abre" in text:
            return "Para ajudar com o erro, envie a mensagem completa apresentada, a tela utilizada e o que tentou fazer. Não envie senha, chave ou dados sensíveis. Com essas informações, posso sugerir verificações seguras."
        if any(word in text for word in ("nota da", "faltas", "qual é", "qual e", "valor", "dados do aluno")):
            return "Não tenho acesso aos dados cadastrados nesta conversa. Posso explicar onde consultar essa informação no sistema."
        return "Olá! Posso orientar o uso de alunos, cursos, turmas, matrículas, notas, frequência, acompanhamento pedagógico, financeiro e relatórios. Qual processo você deseja realizar?"

    def _openai_compatible_reply(self, message: str, student_level: int | None) -> str:
        api_key = os.getenv("LLM_API_KEY")
        model = os.getenv("LLM_MODEL")
        if not api_key or not model:
            raise RuntimeError("LLM_API_KEY and LLM_MODEL are required for openai_compatible mode.")
        learner_context = f"Learner level: {student_level or 'unknown'}."
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": learner_context},
                {"role": "user", "content": message},
            ],
            "temperature": 0.4,
        }).encode("utf-8")
        url = os.getenv("LLM_API_URL") or "https://api.openai.com/v1/chat/completions"
        request = Request(url, data=payload, headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"
        }, method="POST")
        try:
            with urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (HTTPError, URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise RuntimeError("The LLM provider request failed; check provider settings and logs.") from exc
