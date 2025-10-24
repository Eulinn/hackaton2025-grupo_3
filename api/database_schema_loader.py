import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from backup_analyzer import BackupAnalyzer

class DatabaseSchemaLoader:
    """Carrega schema automaticamente do backup.sql"""
    
    def __init__(self, backup_path: str = "database/backup.sql"):
        self.backup_path = Path(backup_path)
        self.analyzer = BackupAnalyzer(str(backup_path))
        self.schema_info = None
        
    def load_schema(self) -> bool:
        """Carrega e analisa o schema do backup"""
        try:
            self.schema_info = self.analyzer.analyze_structure()
            
            if "error" in self.schema_info:
                print(f"❌ Erro ao carregar schema: {self.schema_info['error']}")
                return False
            
            print(f"✅ Schema carregado do backup:")
            print(f"   📊 {self.schema_info['tables_count']} tabelas")
            print(f"   👁️ {self.schema_info['views_count']} views")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar schema: {e}")
            return False
    
    def get_all_tables(self) -> List[str]:
        """Retorna lista de todas as tabelas"""
        if not self.schema_info:
            return []
        return self.schema_info.get("tables", [])
    
    def get_all_views(self) -> List[str]:
        """Retorna lista de todas as views"""
        if not self.schema_info:
            return []
        return self.schema_info.get("views", [])
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Retorna colunas de uma tabela específica"""
        if not self.schema_info:
            return []
        
        tables_with_cols = self.schema_info.get("tables_with_columns", {})
        return tables_with_cols.get(table_name, [])
    
    def generate_schema_description(self) -> str:
        """Gera descrição textual do schema para o LLM"""
        if not self.schema_info:
            return "❌ Schema não carregado"
        
        description = "ESQUEMA DO BANCO DE DADOS (DO BACKUP.SQL):\n\n"
        
        # Tabelas principais
        description += "📊 TABELAS PRINCIPAIS:\n"
        for table in self.get_all_tables()[:10]:  # Primeiras 10
            description += f"   - {table}"
            
            columns = self.get_table_columns(table)
            if columns:
                description += f" ({len(columns)} colunas)"
                # Mostra primeiras colunas
                if len(columns) > 0:
                    description += f": {', '.join(columns[:5])}"
                    if len(columns) > 5:
                        description += f"..."
            description += "\n"
        
        if len(self.get_all_tables()) > 10:
            description += f"   ... e mais {len(self.get_all_tables()) - 10} tabelas\n"
        
        # Views principais
        description += "\n👁️ VIEWS PRINCIPAIS:\n"
        for view in self.get_all_views()[:10]:  # Primeiras 10
            description += f"   - {view}\n"
        
        if len(self.get_all_views()) > 10:
            description += f"   ... e mais {len(self.get_all_views()) - 10} views\n"
        
        # Estatísticas
        description += f"\n📈 ESTATÍSTICAS:\n"
        description += f"   Total de objetos: {self.schema_info['tables_count'] + self.schema_info['views_count']}\n"
        description += f"   Tamanho do backup: {self.schema_info['file_size_mb']} MB\n"
        
        return description
    
    def build_keyword_mappings(self) -> Dict[str, List[Dict]]:
        """Constrói mapeamentos de palavras-chave baseado no schema real"""
        keyword_mappings = {}
        
        # Mapeia nomes de tabelas
        for table in self.get_all_tables():
            # Palavras do nome da tabela
            words = re.findall(r'\w+', table.lower())
            for word in words:
                if len(word) >= 3:  # Palavras com 3+ caracteres
                    if word not in keyword_mappings:
                        keyword_mappings[word] = []
                    
                    keyword_mappings[word].append({
                        "type": "table",
                        "target": table,
                        "source": f"tabela_{table}"
                    })
        
        # Mapeia nomes de views
        for view in self.get_all_views():
            words = re.findall(r'\w+', view.lower())
            for word in words:
                if len(word) >= 3:
                    if word not in keyword_mappings:
                        keyword_mappings[word] = []
                    
                    keyword_mappings[word].append({
                        "type": "view", 
                        "target": view,
                        "source": f"view_{view}"
                    })
        
        # Mapeia colunas conhecidas das tabelas
        for table_name, columns in self.schema_info.get("tables_with_columns", {}).items():
            for column in columns:
                # Extrai nome da coluna (remove tipo)
                col_name = column.split(' ')[0] if ' ' in column else column
                words = re.findall(r'\w+', col_name.lower())
                
                for word in words:
                    if len(word) >= 3:
                        if word not in keyword_mappings:
                            keyword_mappings[word] = []
                        
                        keyword_mappings[word].append({
                            "type": "field",
                            "target": f"{table_name}.{col_name}",
                            "source": f"campo_{table_name}_{col_name}"
                        })
        
        print(f"🔗 Mapeamentos criados: {len(keyword_mappings)} palavras-chave")
        return keyword_mappings

# Instância global
db_schema_loader = DatabaseSchemaLoader()