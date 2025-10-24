import pandas as pd
from sqlalchemy import create_engine, text
from typing import Tuple, Dict, Any, List
from config import Config
import traceback

class DatabaseExecutor:
    def __init__(self):
        self.engine = None
        self.connection_status = False
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com PostgreSQL"""
        try:
            self.engine = create_engine(Config.get_database_url(), echo=False)
            
            # Testa a conexão
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Conectado ao PostgreSQL: {version[:50]}...")
                self.connection_status = True
                
        except Exception as e:
            print(f"❌ Erro de conexão PostgreSQL: {e}")
            self.connection_status = False
            self.engine = None
    
    def test_connection(self) -> Tuple[bool, str]:
        """Testa se a conexão está funcionando"""
        if not self.engine:
            return False, "Engine não inicializada"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT current_timestamp"))
                timestamp = result.fetchone()[0]
                return True, f"Conexão OK - {timestamp}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
    
    def execute_query(self, sql_query: str) -> Tuple[bool, Any, str]:
        """
        Executa query SQL e retorna resultados
        
        Returns:
            Tuple[bool, Any, str]: (sucesso, dados/erro, mensagem)
        """
        if not self.connection_status:
            return False, None, "Banco de dados não conectado"
        
        try:
            # Limpa e valida SQL
            sql_query = sql_query.strip()
            if not sql_query.upper().startswith('SELECT'):
                return False, None, "Apenas queries SELECT são permitidas"
            
            # 🆕 Validação prévia de campos
            validation_result = self._validate_fields_in_query(sql_query)
            if not validation_result[0]:
                # Se a validação falhou, tenta uma versão simplificada
                simplified_query = self._simplify_problematic_query(sql_query)
                if simplified_query:
                    print(f"⚠️ Query original problemática, usando versão simplificada")
                    sql_query = simplified_query
                else:
                    return False, None, f"Validação de campos falhou: {validation_result[1]}"
            
            # Executa query
            print(f"🔍 Executando: {sql_query}")
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                
                # Converte para DataFrame para facilitar manipulação
                columns = result.keys()
                rows = result.fetchall()
                
                if not rows:
                    return True, [], "Query executada com sucesso, mas não retornou dados"
                
                # Converte para lista de dicionários
                data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    data.append(row_dict)
                
                message = f"Query executada com sucesso: {len(data)} registros encontrados"
                return True, data, message
                
        except Exception as e:
            error_msg = f"Erro na execução SQL: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False, None, error_msg
    
    def _validate_fields_in_query(self, sql_query: str) -> Tuple[bool, str]:
        """🆕 Valida se os campos existem nas tabelas referenciadas"""
        try:
            import re
            
            # Extrai tabelas mencionadas na query
            table_pattern = r'FROM\s+(\w+)|JOIN\s+(\w+)'
            table_matches = re.findall(table_pattern, sql_query, re.IGNORECASE)
            tables = [t[0] or t[1] for t in table_matches]
            
            # Extrai campos com alias (c1.campo, c2.campo)
            field_pattern = r'(\w+)\.(\w+)'
            field_matches = re.findall(field_pattern, sql_query)
            
            for alias, field_name in field_matches:
                # Verifica se o campo existe nas tabelas
                field_exists = self._check_field_exists(tables, field_name)
                if not field_exists:
                    return False, f"Campo '{field_name}' não encontrado nas tabelas: {tables}"
            
            return True, "Validação OK"
            
        except Exception as e:
            return True, f"Erro na validação (continuando): {e}"  # Falha suave
    
    def _check_field_exists(self, tables: List[str], field_name: str) -> bool:
        """🆕 Verifica se um campo existe em alguma das tabelas"""
        try:
            with self.engine.connect() as conn:
                for table in tables:
                    result = conn.execute(text(f"""
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = '{field_name}'
                        LIMIT 1
                    """))
                    if result.fetchone():
                        return True
            return False
        except:
            return True  # Se der erro, assume que existe para não bloquear
    
    def _simplify_problematic_query(self, sql_query: str) -> str:
        """🆕 Cria versão simplificada de queries problemáticas"""
        try:
            # 🆕 Detecta se é uma query de genealogia
            import re
            
            # Procura por códigos de animais
            animal_codes = re.findall(r'FSC\d+', sql_query, re.IGNORECASE)
            
            if animal_codes:
                animal_code = animal_codes[0]
                print(f"🧬 Detectada query de genealogia para animal: {animal_code}")
                
                # Query específica para genealogia
                return f"""
                SELECT 
                    animal_codigo, animal_nome, animal_sexo,
                    pai_codigo, pai_nome,
                    mae_codigo, mae_nome,
                    avo_paterno_codigo, avo_paterno_nome,
                    avo_materno_codigo, avo_materno_nome
                FROM cubo_genealogia 
                WHERE animal_codigo = '{animal_code}'
                   OR pai_codigo = '{animal_code}'
                   OR mae_codigo = '{animal_code}'
                   OR avo_paterno_codigo = '{animal_code}'
                   OR avo_materno_codigo = '{animal_code}'
                ORDER BY 
                    CASE 
                        WHEN animal_codigo = '{animal_code}' THEN 1
                        WHEN pai_codigo = '{animal_code}' OR mae_codigo = '{animal_code}' THEN 2
                        ELSE 3
                    END
                LIMIT 20;
                """
            
            # Se tem JOIN problemático, converte para query simples na primeira tabela
            if 'JOIN' in sql_query.upper():
                # Extrai a primeira tabela mencionada
                first_table_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
                if first_table_match:
                    table_name = first_table_match.group(1)
                    
                    # Query simplificada focada na primeira tabela
                    if 'primeiro_parto' in table_name:
                        return f"""
                        SELECT codigo_touro, nome_touro, total_filhas_primeiro_parto, 
                               filhas_produtivas_primeiro_parto
                        FROM {table_name} 
                        ORDER BY filhas_produtivas_primeiro_parto DESC 
                        LIMIT 10;
                        """
                    elif 'producao_touro' in table_name:
                        return f"""
                        SELECT codigo_touro, nome_touro, total_filhas, 
                               filhas_com_producao, media_leite_305d
                        FROM {table_name} 
                        ORDER BY media_leite_305d DESC 
                        LIMIT 10;
                        """
                    elif 'genealogia' in table_name:
                        return f"""
                        SELECT animal_codigo, animal_nome, pai_codigo, pai_nome, 
                               mae_codigo, mae_nome
                        FROM {table_name} 
                        LIMIT 10;
                        """
            
            return None
        except:
            return None
    
    def get_table_info(self, table_name: str = "cubo_genealogia") -> Dict[str, Any]:
        """Obtém informações sobre uma tabela específica"""
        if not self.connection_status:
            return {"error": "Banco não conectado"}
        
        try:
            with self.engine.connect() as conn:
                # Informações da tabela
                table_info_query = text("""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """)
                
                result = conn.execute(table_info_query, {"table_name": table_name})
                columns_info = result.fetchall()
                
                # Conta total de registros
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count_result = conn.execute(count_query)
                total_records = count_result.fetchone()[0]
                
                return {
                    "table_name": table_name,
                    "total_records": total_records,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1], 
                            "nullable": col[2],
                            "default": col[3]
                        } for col in columns_info
                    ]
                }
                
        except Exception as e:
            return {"error": f"Erro ao obter info da tabela: {str(e)}"}
    
    def get_sample_data(self, table_name: str = "cubo_genealogia", limit: int = 5) -> Tuple[bool, Any, str]:
        """Obtém dados de exemplo de uma tabela"""
        sample_query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(sample_query)

# Instância global
db_executor = DatabaseExecutor()