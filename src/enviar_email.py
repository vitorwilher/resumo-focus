"""Envia o resumo HTML do Focus por e-mail, via SMTP do Gmail (App Password).

Diferente do conector do Gmail (que só cria rascunho), este módulo DISPARA a
mensagem de fato — é a peça que torna o processo 100% automático, sem revisão
manual. O HTML gerado em output/focus/ vai como corpo do e-mail.

As credenciais NUNCA ficam no código nem no repositório: são lidas de variáveis
de ambiente (no GitHub Action, vêm dos Secrets; numa Routine, da config dela):

    FOCUS_SMTP_USER          e-mail Gmail remetente (ex.: voce@gmail.com)
    FOCUS_SMTP_APP_PASSWORD  senha de app de 16 dígitos gerada no Google
    FOCUS_EMAIL_DEST         destinatário(s), separados por vírgula
    FOCUS_EMAIL_BCC          (opcional) cópia oculta, ex.: você mesmo

Uso:
    python src/enviar_email.py                          # envia o HTML mais recente
    python src/enviar_email.py --html caminho/arq.html  # envia um HTML específico
    python src/enviar_email.py --dry-run                # monta e mostra, NÃO envia
    python src/enviar_email.py --dest a@x.com,b@y.com    # sobrescreve destinatário
"""

import argparse
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # porta SSL


def html_mais_recente(pasta):
    """Retorna o focus_*.html mais recente de `pasta`, ou None se não houver.

    Como a nomenclatura é focus_AAAA-MM-DD.html, a ordem alfabética coincide
    com a ordem cronológica — o último da lista é o mais novo.
    """
    htmls = sorted(Path(pasta).glob("focus_*.html"))
    return htmls[-1] if htmls else None


def data_do_nome(html_path):
    """Extrai a data AAAA-MM-DD do nome do arquivo (focus_AAAA-MM-DD.html)."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(html_path).name)
    return m.group(1) if m else None


def montar_mensagem(html_path, remetente, destinatarios, assunto, bcc=None):
    """Monta um EmailMessage com corpo HTML (e um fallback de texto simples).

    `destinatarios` e `bcc` são listas de endereços. Retorna o EmailMessage
    pronto para ser enviado.
    """
    html = Path(html_path).read_text(encoding="utf-8")

    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = assunto
    if bcc:
        msg["Bcc"] = ", ".join(bcc)

    # Fallback em texto puro para clientes que não renderizam HTML; o corpo
    # rico (logo + formatação) vai na parte HTML.
    msg.set_content(
        "Seu cliente de e-mail não exibe HTML. Resumo do Focus em anexo HTML."
    )
    msg.add_alternative(html, subtype="html")
    return msg


def enviar(msg, usuario, senha):
    """Envia a mensagem pelo SMTP do Gmail usando SSL e a App Password."""
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.login(usuario, senha)
        smtp.send_message(msg)


def main():
    """CLI: monta o e-mail a partir do HTML do resumo e o envia via Gmail."""
    parser = argparse.ArgumentParser(
        description="Envia o resumo HTML do Focus por e-mail (SMTP do Gmail)."
    )
    parser.add_argument(
        "--html",
        help="Caminho de um HTML específico. Se omitido, usa o focus_*.html "
        "mais recente de output/focus/.",
    )
    parser.add_argument(
        "--dest",
        help="Destinatário(s), separados por vírgula. Sobrescreve "
        "FOCUS_EMAIL_DEST.",
    )
    parser.add_argument(
        "--assunto",
        help="Assunto do e-mail. Padrão: 'Resumo Focus — AAAA-MM-DD'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Monta e exibe o e-mail, mas NÃO envia (não exige credenciais).",
    )
    args = parser.parse_args()

    raiz = Path(__file__).resolve().parent.parent

    # 1) Localiza o HTML do resumo (informado ou o mais recente em output/focus/).
    if args.html:
        html_path = Path(args.html)
    else:
        html_path = html_mais_recente(raiz / "output" / "focus")
        if html_path is None:
            print(
                "Nenhum HTML encontrado em output/focus/. "
                "A Routine precisa gerar o resumo antes de enviar.",
                file=sys.stderr,
            )
            return 1
    if not html_path.exists():
        print(f"Arquivo não encontrado: {html_path}", file=sys.stderr)
        return 1

    # 2) Resolve destinatários (flag tem prioridade sobre a variável de ambiente).
    dest_raw = args.dest or os.environ.get("FOCUS_EMAIL_DEST", "")
    destinatarios = [e.strip() for e in dest_raw.split(",") if e.strip()]
    if not destinatarios:
        print(
            "Sem destinatário. Defina FOCUS_EMAIL_DEST ou use --dest.",
            file=sys.stderr,
        )
        return 1

    bcc_raw = os.environ.get("FOCUS_EMAIL_BCC", "")
    bcc = [e.strip() for e in bcc_raw.split(",") if e.strip()]

    # 3) Monta o assunto a partir da data do arquivo, salvo override.
    data = data_do_nome(html_path) or "recente"
    assunto = args.assunto or f"Resumo Focus — {data}"

    remetente = os.environ.get("FOCUS_SMTP_USER", "")
    msg = montar_mensagem(html_path, remetente or "focus@local", destinatarios, assunto, bcc)

    # 4a) Modo simulação: mostra o cabeçalho e sai sem enviar nem exigir senha.
    if args.dry_run:
        print("=== DRY-RUN (nada foi enviado) ===")
        print(f"De:      {remetente or '(FOCUS_SMTP_USER não definido)'}")
        print(f"Para:    {', '.join(destinatarios)}")
        if bcc:
            print(f"Bcc:     {', '.join(bcc)}")
        print(f"Assunto: {assunto}")
        print(f"Corpo:   {html_path} ({html_path.stat().st_size} bytes de HTML)")
        return 0

    # 4b) Envio real: exige remetente + App Password no ambiente.
    senha = os.environ.get("FOCUS_SMTP_APP_PASSWORD", "")
    if not remetente or not senha:
        print(
            "Credenciais ausentes. Defina FOCUS_SMTP_USER e "
            "FOCUS_SMTP_APP_PASSWORD (senha de app do Gmail).",
            file=sys.stderr,
        )
        return 1

    enviar(msg, remetente, senha)
    print(f"E-mail enviado para {', '.join(destinatarios)} — assunto: {assunto}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
