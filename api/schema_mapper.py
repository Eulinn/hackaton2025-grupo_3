import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from database_schema_loader import db_schema_loader

class SchemaMapper:
    def __init__(self, schema_json_path: str = "schema_descriptions.json"):
        self.schema_json_path = Path(schema_json_path)
        self.schema_data = {}
        self.keyword_mappings = {}
        self.use_backup = False
        self.dicts_data = {}  # 🆕 Para os dicionários
        
        # Carrega schema e dicionários
        self.load_schema()
        self.load_dictionaries()  # 🆕 Carrega dicionários
        self.build_keyword_mappings()
    
    def load_dictionaries(self) -> bool:
        """🆕 Carrega dicionários da pasta dicts/"""
        dicts_path = Path("dicts")
        
        if not dicts_path.exists():
            print("⚠️ Pasta dicts/ não encontrada")
            return False
        
        dict_files = list(dicts_path.glob("*.json"))
        if not dict_files:
            print("⚠️ Nenhum dicionário JSON encontrado em dicts/")
            return False
        
        loaded_count = 0
        for dict_file in dict_files:
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    dict_data = json.load(f)
                    table_name = dict_data.get("tabela", dict_file.stem)
                    self.dicts_data[table_name] = dict_data
                    loaded_count += 1
                    print(f"📖 Dicionário carregado: {dict_file.name}")
            except Exception as e:
                print(f"❌ Erro ao carregar {dict_file.name}: {e}")
        
        print(f"✅ {loaded_count} dicionários carregados da pasta dicts/")
        return loaded_count > 0
    
    def load_schema(self) -> bool:
        """Carrega schema do backup.sql ou do JSON como fallback"""
        
        # 🆕 Tenta carregar do backup SQL primeiro
        backup_path = Path("database/backup.sql")
        if backup_path.exists():
            print("🔍 Detectado backup.sql - carregando schema automático...")
            if db_schema_loader.load_schema():
                self.use_backup = True
                print("✅ Schema carregado do backup.sql")
                return True
            else:
                print("⚠️ Falha ao carregar backup, tentando JSON...")
        
        # Fallback para JSON
        try:
            if not self.schema_json_path.exists():
                print(f"❌ Nem backup.sql nem {self.schema_json_path} encontrado")
                return False
                
            with open(self.schema_json_path, 'r', encoding='utf-8') as file:
                self.schema_data = json.load(file)
            
            print(f"✅ Schema JSON carregado: {len(self.schema_data)} tabelas")
            self.use_backup = False
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar schema: {e}")
            return False
    
    def build_keyword_mappings(self):
        """Constrói mapeamento de palavras-chave com prioridade para dicionários"""
        
        # 🆕 Prioridade 1: Dicionários específicos
        if self.dicts_data:
            self._build_from_dictionaries()
        
        if self.use_backup:
            # Prioridade 2: Schema do backup.sql
            backup_mappings = db_schema_loader.build_keyword_mappings()
            self._merge_mappings(backup_mappings)
            return
        
        # Prioridade 3: Método original para JSON
        if not self.schema_data:
            return
        
        for table_info in self.schema_data:
            table_name = table_info.get("tabela", "")
            table_desc = table_info.get("descricao", "")
            campos = table_info.get("campos", {})
            queries_exemplo = table_info.get("queries_exemplo", {})
            
            # Mapeia palavras da descrição da tabela
            self._add_keyword_mapping(table_desc.lower(), "table", table_name)
            
            # Mapeia campos e suas descrições
            for campo_name, campo_info in campos.items():
                descricao = campo_info.get("descricao", "").lower()
                exemplo = str(campo_info.get("exemplo", "")).lower()
                valores = [str(v).lower() for v in campo_info.get("valores", [])]
                
                # Mapeia palavras da descrição do campo
                self._add_keyword_mapping(descricao, "field", campo_name)
                self._add_keyword_mapping(exemplo, "field", campo_name)
                
                # Mapeia valores possíveis
                for valor in valores:
                    self._add_keyword_mapping(valor, "value", campo_name)
            
            # Mapeia queries de exemplo
            for query_name, query_sql in queries_exemplo.items():
                self._add_keyword_mapping(query_name.lower(), "query_pattern", query_sql)
    
    def _build_from_dictionaries(self):
        """🆕 Constrói mapeamentos dos dicionários"""
        for table_name, dict_data in self.dicts_data.items():
            # Mapeia descrição da tabela
            descricao = dict_data.get("descricao", "")
            self._add_keyword_mapping(descricao.lower(), "table", table_name)
            
            # 🆕 Mapeamentos específicos e prioritários
            if "genealogia" in table_name:
                # Palavras-chave prioritárias para genealogia
                genealogy_keywords = [
                    "genealogia", "genealógica", "genealógicas", "linhagem", 
                    "ascendencia", "descendencia", "geração", "gerações",
                    "pai", "mae", "avo", "ava", "bisavo", "trisavo",
                    "animal", "codigo", "FSC"
                ]
                for keyword in genealogy_keywords:
                    self._add_keyword_mapping(keyword, "table_priority", table_name)
            
            # Mapeia diferencial (conceito único)
            diferencial = dict_data.get("diferencial", "")
            if diferencial:
                self._add_keyword_mapping(diferencial.lower(), "table", table_name)
            
            # Mapeia campos - suporte para estrutura aninhada
            campos = dict_data.get("campos", {})
            if isinstance(campos, dict):
                self._map_nested_fields(campos, table_name)
            
            # Mapeia campos principais (estrutura nova)
            campos_principais = dict_data.get("campos_principais", {})
            if isinstance(campos_principais, dict):
                self._map_nested_fields(campos_principais, table_name)
            
            # Mapeia estatísticas para palavras-chave
            stats = dict_data.get("estatisticas_gerais", {})
            for stat_key, stat_value in stats.items():
                # Converte nomes de estatísticas em palavras-chave
                stat_words = stat_key.replace("_", " ")
                self._add_keyword_mapping(stat_words, "field", stat_key)
    
    def _map_nested_fields(self, fields_dict: dict, table_name: str, prefix: str = ""):
        """🆕 Mapeia campos em estrutura aninhada"""
        for field_name, field_info in fields_dict.items():
            if isinstance(field_info, dict):
                if "descricao" in field_info:
                    # É um campo final
                    full_name = f"{prefix}{field_name}" if prefix else field_name
                    descricao = field_info.get("descricao", "").lower()
                    exemplo = str(field_info.get("exemplo", "")).lower()
                    uso = field_info.get("uso", "").lower()
                    
                    self._add_keyword_mapping(descricao, "field", full_name)
                    self._add_keyword_mapping(exemplo, "field", full_name)
                    self._add_keyword_mapping(uso, "field", full_name)
                    
                    # Mapeia valores possíveis
                    valores = field_info.get("valores", [])
                    for valor in valores:
                        self._add_keyword_mapping(str(valor).lower(), "value", full_name)
                else:
                    # É uma categoria, recursão
                    self._map_nested_fields(field_info, table_name, f"{field_name}.")
    
    def _merge_mappings(self, new_mappings: dict):
        """🆕 Mescla mapeamentos de diferentes fontes"""
        for word, mappings in new_mappings.items():
            if word not in self.keyword_mappings:
                self.keyword_mappings[word] = []
            self.keyword_mappings[word].extend(mappings)
    
    def _add_keyword_mapping(self, text: str, mapping_type: str, target: str):
        """Adiciona mapeamento de palavras-chave"""
        if not text:
            return
            
        # Extrai palavras significativas
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        for word in words:
            if word not in self.keyword_mappings:
                self.keyword_mappings[word] = []
            
            self.keyword_mappings[word].append({
                "type": mapping_type,
                "target": target,
                "source": text[:50]  # Para debug
            })
    
    def analyze_query(self, natural_language_query: str) -> Dict[str, Any]:
        """Analisa a query em linguagem natural e retorna componentes identificados"""
        query_lower = natural_language_query.lower()
        
        analysis = {
            "tables": set(),
            "fields": set(),
            "conditions": [],
            "query_patterns": [],
            "suggested_columns": [],
            "detected_keywords": [],
            "priority_tables": set()  # 🆕 Tabelas com prioridade
        }
        
        # 🆕 Detecta códigos de animais (padrão FSC seguido de números)
        import re
        animal_codes = re.findall(r'FSC\d+', query_lower.upper())
        if animal_codes:
            analysis["detected_keywords"].append({
                "keyword": animal_codes[0],
                "type": "animal_code",
                "target": "codigo_animal"
            })
            # Se tem código de animal, prioriza genealogia
            analysis["priority_tables"].add("cubo_genealogia")
        
        # Procura por palavras-chave no mapeamento
        for word, mappings in self.keyword_mappings.items():
            if word in query_lower:
                for mapping in mappings:
                    analysis["detected_keywords"].append({
                        "keyword": word,
                        "type": mapping["type"],
                        "target": mapping["target"]
                    })
                    
                    if mapping["type"] == "table":
                        analysis["tables"].add(mapping["target"])
                    elif mapping["type"] == "table_priority":
                        analysis["priority_tables"].add(mapping["target"])
                    elif mapping["type"] == "field":
                        analysis["fields"].add(mapping["target"])
                    elif mapping["type"] == "query_pattern":
                        analysis["query_patterns"].append(mapping["target"])
        
        # 🆕 Se há tabelas prioritárias, usa apenas elas
        if analysis["priority_tables"]:
            analysis["tables"] = analysis["priority_tables"]
        
        # Sugere colunas baseadas nas tabelas identificadas
        if analysis["tables"]:
            for table_name in analysis["tables"]:
                if table_name in self.dicts_data:
                    # Usa campos dos dicionários
                    dict_data = self.dicts_data[table_name]
                    campos = dict_data.get("campos", {})
                    main_fields = list(campos.keys())[:5]
                    analysis["suggested_columns"].extend(main_fields)
                else:
                    # Fallback para JSON
                    table_info = self._find_table_info(table_name)
                    if table_info:
                        campos = table_info.get("campos", {})
                        main_fields = list(campos.keys())[:5]
                        analysis["suggested_columns"].extend(main_fields)
        
        return analysis
    
    def _find_table_info(self, table_name: str) -> Optional[Dict]:
        """Encontra informações de uma tabela específica"""
        for table_info in self.schema_data:
            if table_info.get("tabela") == table_name:
                return table_info
        return None
    
    def generate_sql_prompt(self, natural_language_query: str, analysis: Dict) -> str:
        """Gera o prompt para o LLM baseado na análise"""
        
        # 🆕 Prioridade para dicionários específicos
        if self.dicts_data:
            schema_description = self._generate_enhanced_schema_description(analysis)
        elif self.use_backup:
            # Usa schema do backup.sql
            schema_description = db_schema_loader.generate_schema_description()
        else:
            # Constrói descrição das tabelas relevantes do JSON
            tables_description = ""
            for table_name in analysis["tables"]:
                table_info = self._find_table_info(table_name)
                if table_info:
                    tables_description += self._format_table_description(table_info)
            
            # Se não encontrou tabelas específicas, usa todas
            if not tables_description:
                tables_description = "TODAS AS TABELAS DISPONÍVEIS:\n\n"
                for table_info in self.schema_data:
                    tables_description += self._format_table_description(table_info)
            
            schema_description = tables_description
        
        # Constrói informações de análise para contexto
        analysis_context = ""
        if analysis["detected_keywords"]:
            analysis_context = "PALAVRAS-CHAVE IDENTIFICADAS:\n"
            for kw in analysis["detected_keywords"][:10]:  # Limita para não ficar muito longo
                analysis_context += f"- '{kw['keyword']}' → {kw['type']}: {kw['target']}\n"
            analysis_context += "\n"
        
        # 🆕 Adiciona contexto específico sobre códigos de animais
        animal_codes = re.findall(r'FSC\d+', natural_language_query.upper())
        if animal_codes:
            analysis_context += f"CÓDIGO DE ANIMAL DETECTADO: {animal_codes[0]}\n"
            analysis_context += f"OBRIGATÓRIO: Use WHERE animal_codigo = '{animal_codes[0]}'\n\n"

        prompt = f"""
Query: "{natural_language_query}"

TABELAS E ESTRUTURAS:
filhas_touro: codigo_touro, nome_touro, codigo_filha, nome_filha
cubo_genealogia: animal_codigo, animal_nome, pai_codigo, mae_codigo
eventos_vaca: animal_codigo, tipo_evento, data_evento
cubo_resumo_vaca: codigo_bovino, nome_vaca, lactacoes_encerradas, numero_partos, producao_vitalicia_leite
cubo_producao_touro_filhas: codigo_touro, nome_touro, media_leite_305d, total_filhas, tem_amostra_significativa
cubo_producao_touro_descendentes: codigo_touro, nome_touro, media_leite_305d, total_descendentes, tem_amostra_significativa
cubo_primeiro_parto_filhas: codigo_touro, nome_touro, media_producao_primeiro_parto, total_filhas_primeiro_parto, amostra_representativa

REGRAS:
- Um SELECT apenas
- Terminar com ;
- Sem JOINs
- Códigos sempre FSC (nunca Touro)
- Geral: LIMIT 10

EXEMPLOS CORRETOS:
- "filhas FSC00370": SELECT codigo_filha, nome_filha FROM filhas_touro WHERE codigo_touro = 'FSC00370';
- "genealogia FSC78202": SELECT animal_codigo, animal_nome, pai_codigo, mae_codigo FROM cubo_genealogia WHERE animal_codigo = 'FSC78202';
- "resumo vaca Vaca33614": SELECT nome_vaca, codigo_bovino, lactacoes_encerradas, numero_partos, producao_vitalicia_leite FROM cubo_resumo_vaca WHERE nome_vaca = 'Vaca33614';
- "resumo vaca FSC33614": SELECT nome_vaca, codigo_bovino, lactacoes_encerradas, numero_partos, producao_vitalicia_leite FROM cubo_resumo_vaca WHERE codigo_bovino = 'FSC33614';
- "genealogia terceira geração FSC173798": SELECT animal_codigo, animal_nome, pai_nome, mae_nome, avo_paterno_nome, avo_paterna_nome, avo_materno_nome, avo_materna_nome FROM cubo_genealogia WHERE animal_codigo = 'FSC173798';
- "touro com maior média de produção das filhas": SELECT codigo_touro, nome_touro, media_leite_305d, total_filhas FROM cubo_producao_touro_filhas WHERE tem_amostra_significativa = true ORDER BY media_leite_305d DESC LIMIT 1;
- "touro com maior média de produção dos descendentes": SELECT codigo_touro, nome_touro, media_leite_305d, total_descendentes FROM cubo_producao_touro_descendentes WHERE tem_amostra_significativa = true ORDER BY media_leite_305d DESC LIMIT 1;
- "maior média de lactação ao primeiro parto (filhas)": SELECT codigo_touro, nome_touro, media_producao_primeiro_parto, total_filhas_primeiro_parto FROM cubo_primeiro_parto_filhas WHERE amostra_representativa = true ORDER BY media_producao_primeiro_parto DESC LIMIT 1;
- "média da produção vitalícia das filhas do Touro04078": SELECT nome_touro, codigo_touro, media_producao_vitalicia, total_filhas FROM cubo_producao_touro_filhas WHERE nome_touro = 'Touro04078' LIMIT 1;
- "média da produção vitalícia das filhas do FSC04078": SELECT nome_touro, codigo_touro, media_producao_vitalicia, total_filhas FROM cubo_producao_touro_filhas WHERE codigo_touro = 'FSC04078' LIMIT 1;
- "o que é a raça01?": SELECT 'raça01' AS raca_codigo, 'Holandesa' AS raca_nome, 'Raça Holandesa' AS descricao;

SELECT"""
        return prompt
    
    def _generate_enhanced_schema_description(self, analysis: Dict) -> str:
        """🆕 Gera descrição de schema baseada nos dicionários"""
        description = ""
        
        # Se há tabelas identificadas, foca nelas
        target_tables = analysis.get("tables", set())
        if not target_tables:
            # Se não identificou tabelas específicas, usa as principais
            target_tables = set(self.dicts_data.keys())
        
        for table_name in target_tables:
            if table_name in self.dicts_data:
                dict_data = self.dicts_data[table_name]
                description += self._format_enhanced_table_description(dict_data)
        
        # Se ainda não tem descrição, inclui todas as tabelas dos dicionários
        if not description:
            description = "TODAS AS TABELAS DISPONÍVEIS:\n\n"
            for dict_data in self.dicts_data.values():
                description += self._format_enhanced_table_description(dict_data)
        
        return description
    
    def _format_enhanced_table_description(self, dict_data: Dict) -> str:
        """🆕 Formata descrição de tabela baseada no dicionário"""
        table_name = dict_data.get("tabela", "")
        descricao = dict_data.get("descricao", "")
        diferencial = dict_data.get("diferencial", "")
        
        description = f"📊 TABELA: {table_name}\n"
        description += f"   Descrição: {descricao}\n"
        
        if diferencial:
            description += f"   Diferencial: {diferencial}\n"
        
        # Adiciona estatísticas gerais se disponível
        stats = dict_data.get("estatisticas_gerais", {})
        if stats:
            description += f"   Estatísticas:\n"
            for key, value in list(stats.items())[:5]:  # Primeiras 5
                description += f"   - {key}: {value}\n"
        
        # Adiciona campos principais
        description += f"   CAMPOS PRINCIPAIS:\n"
        
        # Campos simples
        campos = dict_data.get("campos", {})
        for campo_name, campo_info in list(campos.items())[:10]:  # Primeiros 10
            if isinstance(campo_info, dict) and "descricao" in campo_info:
                tipo = campo_info.get("tipo", "")
                desc = campo_info.get("descricao", "")
                description += f"   - {campo_name} ({tipo}): {desc}\n"
        
        # Campos principais (estrutura nova)
        campos_principais = dict_data.get("campos_principais", {})
        for categoria, campos_cat in list(campos_principais.items())[:3]:  # 3 categorias
            description += f"   [{categoria.upper()}]:\n"
            for campo_name, campo_info in list(campos_cat.items())[:5]:  # 5 campos por categoria
                if isinstance(campo_info, dict) and "descricao" in campo_info:
                    tipo = campo_info.get("tipo", "")
                    desc = campo_info.get("descricao", "")
                    description += f"     - {campo_name} ({tipo}): {desc}\n"
        
        description += "\n"
        return description
    
    def _format_table_description(self, table_info: Dict) -> str:
        """Formata a descrição de uma tabela para o prompt"""
        table_name = table_info.get("tabela", "")
        table_desc = table_info.get("descricao", "")
        campos = table_info.get("campos", {})
        
        description = f"📊 TABELA: {table_name}\n"
        description += f"   Descrição: {table_desc}\n"
        description += f"   CAMPOS:\n"
        
        for campo_name, campo_info in campos.items():
            campo_desc = campo_info.get("descricao", "")
            campo_tipo = campo_info.get("tipo", "")
            exemplo = campo_info.get("exemplo", "")
            valores = campo_info.get("valores", [])
            
            description += f"   - {campo_name} ({campo_tipo}): {campo_desc}"
            
            if exemplo:
                description += f" | Ex: {exemplo}"
            
            if valores:
                description += f" | Valores: {', '.join(map(str, valores))}"
            
            description += "\n"
        
        # Adiciona queries de exemplo
        queries_exemplo = table_info.get("queries_exemplo", {})
        if queries_exemplo:
            description += f"   EXEMPLOS DE USO:\n"
            for query_name, query_sql in list(queries_exemplo.items())[:3]:  # Limita a 3 exemplos
                description += f"   - {query_name}: {query_sql}\n"
        
        description += "\n"
        return description

# Instância global
schema_mapper = SchemaMapper()