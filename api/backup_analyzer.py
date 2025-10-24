import re
from pathlib import Path
from typing import Dict, List, Set

class BackupAnalyzer:
    def __init__(self, backup_path: str = "database/backup.sql"):
        self.backup_path = Path(backup_path)
        self.tables = {}
        self.views = {}
        
    def analyze_structure(self) -> Dict:
        """Analisa a estrutura do backup SQL sem carregar tudo na memória"""
        if not self.backup_path.exists():
            return {"error": "Backup não encontrado"}
        
        print(f"🔍 Analisando backup: {self.backup_path.name}")
        
        tables_found = set()
        views_found = set()
        
        try:
            with open(self.backup_path, 'r', encoding='utf-8') as file:
                line_count = 0
                in_table_def = False
                current_table = None
                current_columns = []
                
                for line in file:
                    line_count += 1
                    line = line.strip()
                    
                    # CREATE TABLE
                    if line.upper().startswith('CREATE TABLE'):
                        # Melhor regex para capturar nomes de tabelas
                        table_match = re.search(r'CREATE TABLE (?:IF NOT EXISTS )?(?:public\.)?["`]?(\w+)["`]?', line, re.IGNORECASE)
                        if table_match:
                            table_name = table_match.group(1)
                            if table_name != 'public':  # Ignora schema name
                                tables_found.add(table_name)
                                current_table = table_name
                                current_columns = []
                                in_table_def = True
                    
                    # CREATE VIEW
                    elif 'CREATE VIEW' in line.upper() or 'CREATE OR REPLACE VIEW' in line.upper():
                        view_match = re.search(r'CREATE (?:OR REPLACE )?VIEW (?:public\.)?["`]?(\w+)["`]?', line, re.IGNORECASE)
                        if view_match:
                            view_name = view_match.group(1)
                            if view_name != 'public':  # Ignora schema name
                                views_found.add(view_name)
                    
                    # Colunas da tabela
                    elif in_table_def and current_table and line and not line.startswith('--'):
                        if line == ');' or line.startswith(');'):
                            # Fim da definição da tabela
                            if current_table and current_columns:
                                self.tables[current_table] = current_columns[:20]  # Primeiras 20 colunas
                            in_table_def = False
                            current_table = None
                        elif '(' not in line and not line.upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                            # Linha de coluna
                            col_match = re.search(r'^["`]?(\w+)["`]?\s+(\w+)', line.replace(',', ''))
                            if col_match and len(current_columns) < 20:
                                col_name = col_match.group(1)
                                col_type = col_match.group(2)
                                current_columns.append(f"{col_name} ({col_type})")
                    
                    # Para depois de ler muitas linhas para não demorar muito
                    if line_count > 100000:  # Lê até 100k linhas
                        break
            
            result = {
                "tables_count": len(tables_found),
                "views_count": len(views_found),
                "tables": sorted(list(tables_found)),
                "views": sorted(list(views_found)),
                "tables_with_columns": self.tables,
                "file_size_mb": round(self.backup_path.stat().st_size / 1024 / 1024, 1),
                "lines_analyzed": line_count
            }
            
            print(f"✅ Análise concluída:")
            print(f"   📊 {result['tables_count']} tabelas encontradas")
            print(f"   👁️ {result['views_count']} views encontradas")
            print(f"   📄 {result['file_size_mb']} MB analisados")
            
            return result
            
        except Exception as e:
            return {"error": f"Erro na análise: {str(e)}"}

if __name__ == "__main__":
    analyzer = BackupAnalyzer()
    result = analyzer.analyze_structure()
    
    if "error" not in result:
        print(f"\n📋 Primeiras 10 tabelas:")
        for table in result["tables"][:10]:
            print(f"  - {table}")
        
        print(f"\n👁️ Primeiras 10 views:")
        for view in result["views"][:10]:
            print(f"  - {view}")
    else:
        print(f"❌ {result['error']}")