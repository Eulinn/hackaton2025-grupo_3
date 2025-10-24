# -*- coding: utf-8 -*-
"""
Validador e normalizador de SQL para o pipeline NL->SQL.
- Garante SELECT único
- Proíbe JOINs (remove blocos de JOIN se presentes)
- Remove aliases de tabela (c1., ft., etc.)
- Corrige colunas comuns para tabelas conhecidas (ex.: filhas_touro)
- Garante LIMIT (default 10)
"""
from __future__ import annotations
import re
from typing import Tuple

try:
    import sqlglot  # type: ignore
except Exception:  # sqlglot é opcional, regex fallback será usado
    sqlglot = None


_SINGLE_SELECT_RE = re.compile(r"SELECT[\s\S]*?;", re.IGNORECASE)
_ALIAS_PREFIX_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.")
_FROM_ALIAS_RE = re.compile(r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+[a-zA-Z_][a-zA-Z0-9_]*\b", re.IGNORECASE)
_JOIN_BLOCK_RE = re.compile(r"\bJOIN\b[\s\S]*?(?=\bJOIN\b|\bWHERE\b|\bGROUP\b|\bORDER\b|;|$)", re.IGNORECASE)
_DANGEROUS = {"DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"}


def _strip_to_single_select(sql: str) -> str:
    sql_up = sql.upper()
    if "SELECT" not in sql_up:
        return sql.strip()
    m = _SINGLE_SELECT_RE.search(sql)
    if m:
        return m.group(0).strip()
    # fallback: do SELECT até fim e adiciona ;
    start = sql_up.find("SELECT")
    frag = sql[start:].strip()
    if not frag.endswith(";"):
        frag += ";"
    return frag


def _remove_joins(sql: str) -> str:
    # Remove blocos de JOIN
    sql2 = _JOIN_BLOCK_RE.sub("", sql)
    # Remove possíveis vírgulas extras em FROM ... , ...
    sql2 = re.sub(r",\s*(WHERE|GROUP|ORDER)\b", r" \1", sql2, flags=re.IGNORECASE)
    # Remove aliases tipo c1., ft., etc.
    sql2 = _ALIAS_PREFIX_RE.sub("", sql2)
    # Remove alias após o nome da tabela no FROM
    sql2 = _FROM_ALIAS_RE.sub(r"FROM \1", sql2)
    return sql2


def _strip_aliases(sql: str) -> str:
    """Remove prefixos de alias (c1.campo) e alias após o nome da tabela no FROM."""
    s = _ALIAS_PREFIX_RE.sub("", sql)
    s = _FROM_ALIAS_RE.sub(r"FROM \1", s)
    return s


def _ensure_semicolon(sql: str) -> str:
    sql = sql.strip()
    return sql if sql.endswith(";") else sql + ";"


def _ensure_limit(sql: str, default_limit: int = 10) -> str:
    # Se já tem LIMIT, mantém
    if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        return sql
    # Insere antes do ;
    return re.sub(r";\s*$", f" LIMIT {default_limit};", sql)


def _block_dangerous(sql: str) -> None:
    up = sql.upper()
    for kw in _DANGEROUS:
        if re.search(rf"\b{kw}\b", up):
            raise ValueError(f"Comando proibido detectado: {kw}")


def _rewrite_known_tables(sql: str) -> str:
    # filhas_touro: codigo_touro, nome_touro, codigo_filha, nome_filha, codigo_mae, nome_mae
    if re.search(r"\bFROM\s+filhas_touro\b", sql, re.IGNORECASE):
        sql = re.sub(r"\banimal_codigo\b", "codigo_filha", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\bpai_codigo\b", "codigo_touro", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\bmae_codigo\b", "codigo_mae", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\banimal_nome\b", "nome_filha", sql, flags=re.IGNORECASE)
    # cubo_genealogia não tem codigo_filha/codigo_touro
    if re.search(r"\bFROM\s+cubo_genealogia\b", sql, re.IGNORECASE):
        sql = re.sub(r"\bcodigo_filha\b", "animal_codigo", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\bcodigo_touro\b", "pai_codigo", sql, flags=re.IGNORECASE)
        # Corrige nomes inexistentes para nomes válidos
        sql = re.sub(r"\bnome_touro\b", "animal_nome", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\bnome_filha\b", "animal_nome", sql, flags=re.IGNORECASE)
    return sql


def validate_and_fix(sql: str) -> Tuple[bool, str, str]:
    """Valida e corrige SQL.
    Retorna (ok, sql_corrigida, mensagem).
    """
    original = sql
    try:
        # 1) Deixa apenas o primeiro SELECT
        sql = _strip_to_single_select(sql)
        # 2) Bloqueia statements perigosos
        _block_dangerous(sql)
        # 3) Remover joins (se houver)
        if re.search(r"\bJOIN\b", sql, re.IGNORECASE):
            sql = _remove_joins(sql)
        # 3.1) Remover aliases sempre
        sql = _strip_aliases(sql)
        # 4) Reescrever colunas conhecidas
        sql = _rewrite_known_tables(sql)
        # 5) Garantir ; e LIMIT
        sql = _ensure_semicolon(sql)
        sql = _ensure_limit(sql)
        # 6) Validação sintática básica via sqlglot (opcional)
        if sqlglot is not None:
            try:
                sqlglot.parse_one(sql, read="postgres")
            except Exception as e:
                return False, sql, f"Falha de parse (sqlglot): {e}"
        return True, sql, "SQL validada e normalizada"
    except Exception as e:
        return False, original, f"Falha na validação: {e}"
