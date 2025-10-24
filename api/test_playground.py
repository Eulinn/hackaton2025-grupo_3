#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playground de testes para NL -> SQL.

Uso:
  - Interativo:  venv/Scripts/python.exe test_playground.py
  - Uma pergunta: venv/Scripts/python.exe test_playground.py -q "sua pergunta aqui"
  - Limitar linhas exibidas: adicione -n 5

Exemplos:
  venv/Scripts/python.exe test_playground.py -q "o touro FSC00370 tem filhas?"
  venv/Scripts/python.exe test_playground.py -q "forneça a genealogia até a terceira geração do animal FSC78202"
"""
import sys
import os
import argparse
from typing import Optional

# Garante import do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nl_to_sql import nl_to_sql_pipeline  # type: ignore


def run_query(q: str, show_rows: int = 10) -> None:
    print("🔎 Pergunta:", q)
    success, sql_or_error, result_info = nl_to_sql_pipeline.natural_language_to_sql(q)

    if success:
        print("\n📊 SQL gerada:")
        print(sql_or_error)
        if isinstance(result_info, dict):
            print("\n✅ Execução:", result_info.get("message", ""))
            data = result_info.get("data") or []
            if data:
                print(f"\n🔢 Primeiras {min(show_rows, len(data))} linhas:")
                for i, row in enumerate(data[:show_rows], 1):
                    print(f" {i:02d}: {row}")
            else:
                print("\n📋 Sem dados retornados")

            analysis = result_info.get("analysis") or {}
            if analysis:
                print("\n🧠 Análise (resumo):")
                tables = analysis.get("tables_identified") or []
                fields = analysis.get("fields_identified") or []
                print(" - Tabelas:", ", ".join(tables) if tables else "-")
                print(" - Campos:", ", ".join(fields) if fields else "-")
        else:
            print("\nℹ️ Info:", result_info)
    else:
        print("\n❌ Falha na geração/execução")
        print("🧩 Conteúdo:")
        print(sql_or_error)
        if result_info:
            print("\n💬 Detalhes:")
            print(result_info)


def interactive_loop(limit: int) -> None:
    print("\n🧪 Playground NL->SQL (digite 'sair' para encerrar)\n")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Encerrando.")
            break
        if not q:
            continue
        if q.lower() in {"sair", "exit", "quit"}:
            print("👋 Encerrando.")
            break
        run_query(q, show_rows=limit)
        print()


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Playground de testes NL->SQL")
    parser.add_argument("-q", "--query", help="Pergunta em linguagem natural", default=None)
    parser.add_argument("-n", "--limit", type=int, help="Quantidade de linhas para exibir", default=10)
    args = parser.parse_args(argv)

    if args.query:
        run_query(args.query, show_rows=args.limit)
    else:
        interactive_loop(args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
