# calculadora_avancada_color.py

import os
import math
import argparse
from datetime import datetime
from colorama import init, Fore


# constantes de cor
COL_PROMPT = Fore.CYAN
COL_ERROR = Fore.RED
COL_MENU = Fore.YELLOW
COL_RESULT = Fore.GREEN


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def ler_numero(msg):
    while True:
        entrada = input(COL_PROMPT + msg)
        if entrada.lower() == "sair":
            return "sair"
        try:
            return float(entrada)
        except ValueError:
            print(COL_ERROR + "❌ Por favor, digite um número válido.")


def calcular_resultados(n1, n2):
    # overflow customizado para potência
    try:
        if n1 not in (0, 1) and n2 * math.log10(abs(n1)) > 1000:
            raise OverflowError
        pot = n1**n2
    except (OverflowError, ValueError):
        pot = None

    # cálculos básicos
    div = None if n2 == 0 else n1 / n2
    int_div = None if n2 == 0 else n1 // n2
    mod = None if n2 == 0 else n1 % n2
    sqrt = None if n1 < 0 else math.sqrt(n1)
    log = None if n1 <= 0 else math.log(n1)

    # fatorial protegido
    try:
        if n1 < 0 or not float(n1).is_integer():
            fat = None
        else:
            fat = math.factorial(int(n1))
    except (OverflowError, ValueError):
        fat = None

    # trigonometria
    sin = math.sin(n1)
    cos = math.cos(n1)
    try:
        tan = math.tan(n1)
    except Exception:
        tan = None

    return {
        "soma": n1 + n2,
        "sub": n1 - n2,
        "mul": n1 * n2,
        "div": div,
        "int_div": int_div,
        "mod": mod,
        "pot": pot,
        "sqrt": sqrt,
        "log": log,
        "fat": fat,
        "sin": sin,
        "cos": cos,
        "tan": tan,
    }


def obter_labels(no_color=False):
    return {
        "soma": "➕ Soma",
        "sub": "➖ Subtração",
        "mul": "✖️ Multiplicação",
        "div": "➗ Divisão",
        "int_div": "🔢 Int. Divisão",
        "mod": "🔰 Resto",
        "pot": "🔥 Potência",
        "sqrt": "√ Raiz",
        "sin": "📐 Seno",
        "cos": "📐 Cosseno",
        "tan": "📐 Tangente",
        "fat": "📊 Fatorial",
        "log": "🧮 Logaritmo",
    }


def escolher_operacoes():
    opcoes = {
        "1": "soma",
        "2": "sub",
        "3": "mul",
        "4": "div",
        "5": "int_div",
        "6": "mod",
        "7": "pot",
        "8": "sqrt",
        "9": "sin",
        "10": "cos",
        "11": "tan",
        "12": "fat",
        "13": "log",
    }
    print(COL_MENU + "\n🔧 Operações disponíveis:")
    for k, v in opcoes.items():
        print(COL_MENU + f"{k:>2} - {v}")
    entrada = input(
        COL_PROMPT + "Digite os números das operações (separados por vírgula): "
    )
    return [opcoes[i.strip()] for i in entrada.split(",") if i.strip() in opcoes]


def formatar_resultados(
    resultados: dict, labels: dict, no_color: bool = False
) -> list[str]:
    """
    Gera uma lista de strings "Label: valor.0000" para cada par em resultados.
    """
    linhas = []
    for key, valor in resultados.items():
        linhas.append(f"{labels[key]}: {valor:.4f}")
    return linhas


def salvar_historico(
    n1,
    n2,
    ops,
    resultados,
    labels,
    caminho: str = "historico.txt",
):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pares = []
    for op in ops:
        val = resultados[op]
        texto = "N/A" if val is None else f"{val:.4f}"
        pares.append(f"{labels[op]}:{texto}")

    linha = (
        f'{ts} | entradas: {n1} e {n2} | ops: {",".join(ops)} | '
        f'{"; ".join(pares)}\n'
    )

    with open(caminho, "a", encoding="utf-8") as f:
        f.write(linha)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desativa cores ANSI na saída",
    )
    args = parser.parse_args()
    no_color = args.no_color

    if not no_color:
        init(autoreset=True)

    while True:
        limpar_tela()

        n1 = ler_numero("Digite o primeiro número (ou 'sair'): ")
        if n1 == "sair":
            print(COL_PROMPT + "Até logo!")
            break

        n2 = ler_numero("Digite o segundo número (ou 'sair'): ")
        if n2 == "sair":
            print(COL_PROMPT + "Até logo!")
            break

        resultados = calcular_resultados(n1, n2)
        labels = obter_labels(no_color)
        escolhidas = escolher_operacoes()

        linhas = formatar_resultados(
            {op: resultados[op] for op in escolhidas},
            {op: labels[op] for op in escolhidas},
            no_color=no_color,
        )
        print()  # linha em branco antes dos resultados
        for linha in linhas:
            if no_color:
                print(linha)
            else:
                print(COL_RESULT + linha)

        salvar_historico(n1, n2, escolhidas, resultados, labels)

        input(COL_PROMPT + "\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()
