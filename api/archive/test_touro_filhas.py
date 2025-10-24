#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_mapper import SchemaMapper
from nl_to_sql import nl_to_sql_pipeline

def test_touro_filhas():
    """Testa a consulta específica que estava falhando"""
    
    query = "o touro FSC00370 tem filhas?"
    
    print(f"🧪 Testando: {query}")
    print("="*80)
    
    try:
        # Gera SQL
        success, sql_or_error, result_info = nl_to_sql_pipeline.natural_language_to_sql(query)
        
        if success:
            print(f"✅ SQL gerado com sucesso:")
            print(f"📊 SQL: {sql_or_error}")
            
            if result_info and isinstance(result_info, dict):
                print(f"💾 Resultado: {result_info.get('message', 'Sem dados')}")
                data = result_info.get('data', [])
                if data:
                    print(f"🔢 Registros encontrados: {len(data)}")
                    for i, row in enumerate(data[:3]):  # Mostra primeiros 3
                        print(f"   {i+1}: {row}")
                else:
                    print("📋 Nenhum registro retornado")
            else:
                print(f"ℹ️ Info: {result_info}")
        else:
            print(f"❌ Erro na geração: {sql_or_error}")
            if result_info:
                print(f"💬 Detalhe: {result_info}")
    
    except Exception as e:
        print(f"💥 Exceção: {e}")

if __name__ == "__main__":
    test_touro_filhas()