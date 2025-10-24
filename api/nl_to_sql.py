import requests
import json
import re
from typing import Tuple, Dict, Any
from config import Config
from sql_validator import validate_and_fix
from schema_mapper import schema_mapper
from database_executor import db_executor

class NLToSQLPipeline:
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.model_name = Config.MODEL_NAME
        
        # 🆕 Carrega schema do JSON
        print("📖 Carregando schema das descrições JSON...")
        if not schema_mapper.load_schema():
            print("❌ Não foi possível carregar o schema JSON")
    
    def natural_language_to_sql(self, query: str) -> Tuple[bool, str, Any]:
        """
        Pipeline completo com análise de palavras-chave
        """
        print(f"🔍 Analisando: '{query}'")
        
        # Passo 1: Análise da query para identificar componentes
        analysis = schema_mapper.analyze_query(query)
        print(f"📊 Análise: {len(analysis['tables'])} tabelas, {len(analysis['fields'])} campos identificados")

        # Atalho inteligente: consultas sobre "filhas do touro <FSCxxxx>"
        qlower = query.lower()
        import re as _re
        codes = _re.findall(r"FSC\d+", query.upper())
        if codes and any(w in qlower for w in ["filhas", "filha", "descendentes"]):
            code = codes[0]
            sql_query = f"SELECT codigo_filha, nome_filha FROM filhas_touro WHERE codigo_touro = '{code}' LIMIT 10;"
            print(f"🧭 Atalho aplicado (filhas_touro): {sql_query}")
            # Validação e normalização
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if ok:
                sql_query = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            # Executa diretamente
            success, data, db_message = db_executor.execute_query(sql_query)
            if success:
                result_info = {
                    "message": db_message,
                    "query": sql_query,
                    "data": data,
                    "analysis": {
                        "tables_identified": list(analysis["tables"]),
                        "fields_identified": list(analysis["fields"]),
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, sql_query, result_info
            else:
                return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"

        # 🆕 Atalho inteligente: "touro com filhas com maior média de produção" (cubo_producao_touro_filhas)
        wants_top_bull_daughters_avg = (
            any(term in qlower for term in ["maior média", "maior media", "top", "ranking"]) and
            any(term in qlower for term in ["filhas", "filha"]) and
            any(term in qlower for term in ["produção", "producao", "leite", "305"]) and
            any(term in qlower for term in ["touro", "reprodutor"]) and
            not codes  # evita conflito com perguntas sobre um FSC específico
        )
        if wants_top_bull_daughters_avg:
            # Retorna dois registros: com e sem amostra significativa
            union_sql = (
                "SELECT * FROM ("
                "  SELECT 'com_amostra' AS categoria, codigo_touro, nome_touro, media_leite_305d, total_filhas "
                "  FROM cubo_producao_touro_filhas "
                "  WHERE tem_amostra_significativa = true "
                "  ORDER BY media_leite_305d DESC "
                "  LIMIT 1"
                ") t1 "
                "UNION ALL "
                "SELECT * FROM ("
                "  SELECT 'sem_amostra' AS categoria, codigo_touro, nome_touro, media_leite_305d, total_filhas "
                "  FROM cubo_producao_touro_filhas "
                "  WHERE (tem_amostra_significativa = false OR tem_amostra_significativa IS NULL) "
                "  ORDER BY media_leite_305d DESC "
                "  LIMIT 1"
                ") t2;"
            )
            print(f"🧭 Atalho aplicado (cubo_producao_touro_filhas - top média 305d, 2 categorias): {union_sql}")
            ok, fixed_sql, val_msg = validate_and_fix(union_sql)
            if ok:
                union_sql = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(union_sql)
            if success:
                result_info = {
                    "message": db_message,
                    "query": union_sql,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_producao_touro_filhas"],
                        "fields_identified": ["categoria", "codigo_touro", "nome_touro", "media_leite_305d", "total_filhas"],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, union_sql, result_info
            else:
                return False, union_sql, f"SQL gerado mas erro na execução: {db_message}"

        # Atalho inteligente: resumo de vaca (cubo_resumo_vaca)
        # Detecta consultas com termos de lactação/parto/produção e referência a vaca por nome (Vaca123) ou código (FSC123)
        name_matches = _re.findall(r"Vaca\d+", query)
        wants_resumo = ("vaca" in qlower) and any(term in qlower for term in ["lacta", "parto", "produc", "vital"])  # cobre lactações, partos, produção vitalícia
        if wants_resumo and (name_matches or codes):
            filtro = None
            if name_matches:
                filtro = f"nome_vaca = '{name_matches[0]}'"
            elif codes:
                filtro = f"codigo_bovino = '{codes[0]}'"

            sql_query = (
                "SELECT nome_vaca, codigo_bovino, lactacoes_encerradas, numero_partos, producao_vitalicia_leite "
                "FROM cubo_resumo_vaca "
                f"WHERE {filtro} LIMIT 1;"
            )
            print(f"🧭 Atalho aplicado (cubo_resumo_vaca): {sql_query}")
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if ok:
                sql_query = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(sql_query)
            if success:
                result_info = {
                    "message": db_message,
                    "query": sql_query,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_resumo_vaca"],
                        "fields_identified": [
                            "nome_vaca", "codigo_bovino", "lactacoes_encerradas", "numero_partos", "producao_vitalicia_leite"
                        ],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, sql_query, result_info
            else:
                return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"

        # 🆕 Atalho inteligente: média da produção vitalícia das filhas de um touro específico
        # Exemplos de detecção: "produção vitalícia", "producao vitalicia", "vitalícia", "vitalicia"
        bull_name_matches = _re.findall(r"Touro\d+", query)
        wants_vitalicia_filhas = (
            any(term in qlower for term in ["vitalícia", "vitalicia"]) and
            any(term in qlower for term in ["filhas", "filha"]) and
            any(term in qlower for term in ["touro", "reprodutor"]) and
            (bull_name_matches or codes)
        )
        if wants_vitalicia_filhas:
            if bull_name_matches:
                filtro = f"nome_touro = '{bull_name_matches[0]}'"
            else:
                filtro = f"codigo_touro = '{codes[0]}'"
            sql_query = (
                "SELECT nome_touro, codigo_touro, media_producao_vitalicia, total_filhas "
                "FROM cubo_producao_touro_filhas "
                f"WHERE {filtro} LIMIT 1;"
            )
            print(f"🧭 Atalho aplicado (cubo_producao_touro_filhas - média vitalícia filhas): {sql_query}")
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if ok:
                sql_query = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(sql_query)
            if success:
                result_info = {
                    "message": db_message,
                    "query": sql_query,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_producao_touro_filhas"],
                        "fields_identified": ["nome_touro", "codigo_touro", "media_producao_vitalicia", "total_filhas"],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, sql_query, result_info
            else:
                return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"

        # 🆕 Atalho simples: mapeamento de raça01 → Raça Holandesa
        # Responde perguntas do tipo: "o que é a raça01?" ou "raça 01"
        if _re.search(r"\bra[cç]a\s*0*1\b", qlower):
            sql_query = "SELECT 'raça01' AS raca_codigo, 'Holandesa' AS raca_nome, 'Raça Holandesa' AS descricao;"
            print(f"🧭 Atalho aplicado (mapeamento raça01): {sql_query}")
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if ok:
                sql_query = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(sql_query)
            if success:
                result_info = {
                    "message": db_message,
                    "query": sql_query,
                    "data": data,
                    "analysis": {
                        "tables_identified": [],
                        "fields_identified": ["raca_codigo", "raca_nome", "descricao"],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, sql_query, result_info
            else:
                return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"

        # Atalho inteligente: genealogia até a terceira geração (cubo_genealogia)
        wants_genealogy = any(term in qlower for term in ["genealogia", "geração", "geracoes", "geraçao", "geracões"]) and bool(codes)
        if wants_genealogy and codes:
            code = codes[0]
            sql_query = (
                "SELECT "
                "animal_codigo, animal_nome, animal_sexo, animal_raca, "
                "pai_codigo, pai_nome, mae_codigo, mae_nome, "
                "avo_paterno_codigo, avo_paterno_nome, avo_paterna_codigo, avo_paterna_nome, "
                "avo_materno_codigo, avo_materno_nome, avo_materna_codigo, avo_materna_nome "
                "FROM cubo_genealogia "
                f"WHERE animal_codigo = '{code}' LIMIT 1;"
            )
            print(f"🧭 Atalho aplicado (cubo_genealogia 3ª geração): {sql_query}")
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if ok:
                sql_query = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(sql_query)
            if success:
                result_info = {
                    "message": db_message,
                    "query": sql_query,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_genealogia"],
                        "fields_identified": [
                            "animal_codigo","animal_nome","pai_codigo","pai_nome","mae_codigo","mae_nome",
                            "avo_paterno_codigo","avo_paterno_nome","avo_paterna_codigo","avo_paterna_nome",
                            "avo_materno_codigo","avo_materno_nome","avo_materna_codigo","avo_materna_nome"
                        ],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, sql_query, result_info
            else:
                return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"

        # 🆕 Atalho inteligente: descendentes (filhas + netas) com maior média
        wants_top_bull_descendants_avg = (
            any(term in qlower for term in ["descendente", "descendentes", "netas", "filhas e netas"]) and
            any(term in qlower for term in ["maior média", "maior media", "top", "ranking"]) and
            any(term in qlower for term in ["produção", "producao", "leite", "305"]) and
            any(term in qlower for term in ["touro", "reprodutor"]) and
            not codes
        )
        if wants_top_bull_descendants_avg:
            union_sql = (
                "SELECT * FROM ("
                "  SELECT 'com_amostra' AS categoria, codigo_touro, nome_touro, media_leite_305d, total_descendentes "
                "  FROM cubo_producao_touro_descendentes "
                "  WHERE tem_amostra_significativa = true "
                "  ORDER BY media_leite_305d DESC "
                "  LIMIT 1"
                ") t1 "
                "UNION ALL "
                "SELECT * FROM ("
                "  SELECT 'sem_amostra' AS categoria, codigo_touro, nome_touro, media_leite_305d, total_descendentes "
                "  FROM cubo_producao_touro_descendentes "
                "  WHERE (tem_amostra_significativa = false OR tem_amostra_significativa IS NULL) "
                "  ORDER BY media_leite_305d DESC "
                "  LIMIT 1"
                ") t2;"
            )
            print(f"🧭 Atalho aplicado (cubo_producao_touro_descendentes - top média): {union_sql}")
            ok, fixed_sql, val_msg = validate_and_fix(union_sql)
            if ok:
                union_sql = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(union_sql)
            if success:
                result_info = {
                    "message": db_message,
                    "query": union_sql,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_producao_touro_descendentes"],
                        "fields_identified": ["categoria", "codigo_touro", "nome_touro", "media_leite_305d", "total_descendentes"],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, union_sql, result_info
            else:
                return False, union_sql, f"SQL gerado mas erro na execução: {db_message}"

        # 🆕 Atalho inteligente: maior média de lactação no primeiro parto (filhas)
        wants_first_calving_avg = (
            any(term in qlower for term in ["primeiro parto", "1o parto", "1º parto", "primeira lactação", "primeira lactacao"]) and
            any(term in qlower for term in ["lactação", "lactacao"]) and
            any(term in qlower for term in ["maior média", "maior media", "top", "ranking"]) and
            any(term in qlower for term in ["filhas", "filha"]) and
            any(term in qlower for term in ["touro", "reprodutor"]) and
            not codes
        )
        if wants_first_calving_avg:
            base_sql = (
                "SELECT codigo_touro, nome_touro, media_producao_primeiro_parto, total_filhas_primeiro_parto "
                "FROM cubo_primeiro_parto_filhas "
                "WHERE amostra_representativa = true "
                "ORDER BY media_producao_primeiro_parto DESC "
                "LIMIT 1;"
            )
            print(f"🧭 Atalho aplicado (cubo_primeiro_parto_filhas - top média 1º parto): {base_sql}")
            ok, fixed_sql, val_msg = validate_and_fix(base_sql)
            if ok:
                base_sql = fixed_sql
            else:
                print(f"⚠️ Validação avisou: {val_msg}")
            success, data, db_message = db_executor.execute_query(base_sql)
            if success and data:
                result_info = {
                    "message": db_message,
                    "query": base_sql,
                    "data": data,
                    "analysis": {
                        "tables_identified": ["cubo_primeiro_parto_filhas"],
                        "fields_identified": ["codigo_touro", "nome_touro", "media_producao_primeiro_parto", "total_filhas_primeiro_parto"],
                        "keywords_detected": analysis["detected_keywords"][:5]
                    }
                }
                return True, base_sql, result_info
            else:
                # Fallback sem filtro de amostra
                fallback_sql = (
                    "SELECT codigo_touro, nome_touro, media_producao_primeiro_parto, total_filhas_primeiro_parto "
                    "FROM cubo_primeiro_parto_filhas "
                    "ORDER BY media_producao_primeiro_parto DESC "
                    "LIMIT 1;"
                )
                print(f"↩️ Fallback sem filtro (1º parto): {fallback_sql}")
                ok2, fixed_sql2, val_msg2 = validate_and_fix(fallback_sql)
                if ok2:
                    fallback_sql = fixed_sql2
                success2, data2, db_message2 = db_executor.execute_query(fallback_sql)
                if success2:
                    result_info = {
                        "message": db_message2,
                        "query": fallback_sql,
                        "data": data2,
                        "analysis": {
                            "tables_identified": ["cubo_primeiro_parto_filhas"],
                            "fields_identified": ["codigo_touro", "nome_touro", "media_producao_primeiro_parto", "total_filhas_primeiro_parto"],
                            "keywords_detected": analysis["detected_keywords"][:5]
                        }
                    }
                    return True, fallback_sql, result_info
                else:
                    return False, fallback_sql, f"SQL gerado mas erro na execução: {db_message2}"
        
        # Passo 2: Gerar prompt baseado na análise
        prompt = schema_mapper.generate_sql_prompt(query, analysis)
        
        # Passo 3: Chamar LLM para gerar SQL
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                return False, f"Erro Ollama: {response.status_code}", None
            
            sql_query = response.json()["response"]
            sql_query = self.clean_sql_response(sql_query)
            
            print(f"📊 SQL Gerado: {sql_query}")
            
            # Validação e normalização avançada
            ok, fixed_sql, val_msg = validate_and_fix(sql_query)
            if not ok:
                # Ainda assim tenta executar a melhor versão que temos
                print(f"⚠️ Validação avisou: {val_msg}")
            else:
                sql_query = fixed_sql
                print(f"🧹 SQL Normalizada: {sql_query}")
            
            # Validação básica final
            is_valid = self._validate_sql_syntax(sql_query)
            
            if is_valid:
                # 🆕 Executa a query no PostgreSQL
                success, data, db_message = db_executor.execute_query(sql_query)
                
                if success:
                    result_info = {
                        "message": db_message,
                        "query": sql_query,
                        "data": data,
                        "analysis": {
                            "tables_identified": list(analysis["tables"]),
                            "fields_identified": list(analysis["fields"]),
                            "keywords_detected": analysis["detected_keywords"][:5]
                        }
                    }
                    return True, sql_query, result_info
                else:
                    return False, sql_query, f"SQL gerado mas erro na execução: {db_message}"
            else:
                return False, sql_query, "SQL gerado possui sintaxe inválida"
            
        except requests.exceptions.Timeout:
            return False, "Timeout: Ollama não respondeu a tempo", None
        except Exception as e:
            return False, f"Erro: {str(e)}", None
    
    def clean_sql_response(self, sql_response: str) -> str:
        """Limpa a resposta do LLM para extrair apenas o SQL"""
        # Remove markdown code blocks
        sql_response = re.sub(r'```sql|```', '', sql_response)
        
        # 🆕 Corrige problema comum: "AND LIMIT" → "LIMIT"
        sql_response = re.sub(r'\bAND\s+LIMIT\b', 'LIMIT', sql_response, flags=re.IGNORECASE)
        
        # 🆕 DETECÇÃO ESPECÍFICA: Se não há SELECT, é explicação pura
        if 'SELECT' not in sql_response.upper():
            print("⚠️ LLM retornou explicação sem SQL - gerando fallback")
            return self._generate_fallback_sql(sql_response)
        
        # 🆕 Remove explicações extensas que a LLM adiciona
        sql_response = re.sub(r'Obrigado.*?;', ';', sql_response, flags=re.IGNORECASE | re.DOTALL)
        sql_response = re.sub(r'Lembre-se.*', '', sql_response, flags=re.IGNORECASE | re.DOTALL)
        sql_response = re.sub(r'\d+\.\s+.*?(?=SELECT|$)', '', sql_response, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove explicações comuns
        sql_response = re.sub(r'Aqui.*?SQL:', '', sql_response, flags=re.IGNORECASE | re.DOTALL)
        sql_response = re.sub(r'Retorne.*?SELECT', 'SELECT', sql_response, flags=re.IGNORECASE | re.DOTALL)
        
        # Extrai apenas o SELECT
        select_match = re.search(r'SELECT.*?;', sql_response, re.IGNORECASE | re.DOTALL)
        if select_match:
            return select_match.group(0).strip()
        
        # Fallback se não achou SQL válido
        return self._generate_fallback_sql(sql_response)
    
    def _generate_fallback_sql(self, original_response: str) -> str:
        """Gera SQL de fallback quando LLM não retorna SQL válido"""
        # Extrai códigos FSC se houver
        fsc_codes = re.findall(r'FSC\d+', original_response.upper())
        
        if fsc_codes:
            code = fsc_codes[0]
            # Detecta se é sobre filhas de touro
            if any(word in original_response.lower() for word in ['filhas', 'filha', 'descendentes']):
                return f"SELECT codigo_filha, nome_filha FROM filhas_touro WHERE codigo_touro = '{code}' LIMIT 10;"
            else:
                # Genealogia geral
                return f"SELECT animal_codigo, animal_nome FROM cubo_genealogia WHERE animal_codigo = '{code}';"
        else:
            # Fallback genérico
            return "SELECT animal_codigo, animal_nome FROM cubo_genealogia LIMIT 10;"
        
        if not sql_lines:
            # Fallback: procura SELECT em qualquer lugar
            select_match = re.search(r'SELECT.*?;', sql_response, re.IGNORECASE | re.DOTALL)
            if select_match:
                return select_match.group(0).strip()
            else:
                # Último recurso: pega do primeiro SELECT até o final
                select_pos = sql_response.upper().find('SELECT')
                if select_pos != -1:
                    sql_response = sql_response[select_pos:]
                    # Remove até o primeiro ;
                    semicolon_pos = sql_response.find(';')
                    if semicolon_pos != -1:
                        sql_response = sql_response[:semicolon_pos + 1]
        else:
            sql_response = '\n'.join(sql_lines)
        
        # Limpeza final
        sql_response = sql_response.strip()
        if not sql_response.endswith(';'):
            sql_response += ';'
            
        return sql_response
    
    def _validate_sql_syntax(self, sql_query: str) -> bool:
        """Validação básica de sintaxe SQL"""
        sql_upper = sql_query.upper().strip()
        
        # Verifica se começa com SELECT
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Verifica se não contém operações perigosas
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True

# Instância global do pipeline
nl_to_sql_pipeline = NLToSQLPipeline()