#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_mapper import SchemaMapper
from nl_to_sql import nl_to_sql_pipeline

def test_business_rules():
    """Testa as novas regras de negócio implementadas"""
    
    test_queries = [
        "mostre as filhas do touro FSC00072",
        "quantos partos teve a vaca FSC78202",
        "qual a produção vitalícia da vaca FSC78202", 
        "mostre todos os descendentes do touro FSC00072",
        "vacas que tiveram cobertura",
        "primeira lactação das vacas"
    ]
    
    print("🧪 Testando novas regras de negócio")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 🔍 Testando: '{query}'")
        print("-" * 60)
        
        try:
            success, sql_or_error, result_info = nl_to_sql_pipeline.natural_language_to_sql(query)
            
            if success:
                print(f"✅ SQL: {sql_or_error}")
                
                if result_info and isinstance(result_info, dict):
                    data = result_info.get('data', [])
                    if data:
                        print(f"📊 Registros: {len(data)}")
                        # Mostra primeiro registro como exemplo
                        if data:
                            print(f"📝 Exemplo: {data[0]}")
                    else:
                        print("📋 Sem dados")
                        
            else:
                print(f"❌ Erro: {sql_or_error}")
                if result_info:
                    print(f"💬 Detalhe: {result_info}")
                    
        except Exception as e:
            print(f"💥 Exceção: {e}")
        
        print()

if __name__ == "__main__":
    test_business_rules()