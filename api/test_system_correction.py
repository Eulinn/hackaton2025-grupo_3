#!/usr/bin/env python3
"""
Teste do sistema corrigido de genealogia
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nl_to_sql import NLToSQLPipeline

def test_corrected_system():
    """Testa se o sistema agora gera queries corretas"""
    
    print("🧬 TESTE DO SISTEMA CORRIGIDO")
    print("=" * 50)
    
    # Inicializa o pipeline
    pipeline = NLToSQLPipeline()
    
    # Query de teste
    test_query = "Forneça a genealogia até a terceira geração do animal FSC77898"
    
    print(f"\n📝 Query de teste: '{test_query}'")
    print("\n🔍 Processando...")
    
    # Gera SQL
    success, sql, result_info = pipeline.natural_language_to_sql(test_query)
    
    print(f"\n📊 Resultado:")
    print(f"   ✅ Sucesso: {success}")
    
    if success:
        print(f"\n🔧 SQL Gerado:")
        print(f"   {sql}")
        
        print(f"\n📋 Análise:")
        if isinstance(result_info, dict) and 'analysis' in result_info:
            analysis = result_info['analysis']
            tables = analysis.get('tables_identified', [])
            keywords = analysis.get('keywords_detected', [])
            
            print(f"   📊 Tabelas identificadas: {tables}")
            print(f"   🔍 Palavras-chave: {[kw['keyword'] for kw in keywords]}")
        
        # Verifica se está correto
        sql_lower = sql.lower()
        
        checks = {
            "✅ Usa cubo_genealogia": "cubo_genealogia" in sql_lower,
            "✅ Filtra por animal_codigo": "animal_codigo = 'fsc77898'" in sql_lower,
            "❌ NÃO filtra por sexo": "animal_sexo =" not in sql_lower,
            "❌ NÃO filtra por raça": "animal_raca =" not in sql_lower,
            "✅ Inclui pai_nome": "pai_nome" in sql_lower,
            "✅ Inclui mae_nome": "mae_nome" in sql_lower,
            "❌ NÃO renomeia códigos": "as pai_nome" not in sql_lower and "as mae_nome" not in sql_lower
        }
        
        print(f"\n🔍 Verificações:")
        all_correct = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('✅ ', '').replace('❌ ', '')}")
            if not passed:
                all_correct = False
        
        if all_correct:
            print(f"\n🎉 SISTEMA CORRIGIDO COM SUCESSO!")
        else:
            print(f"\n⚠️ Ainda há problemas na geração do SQL")
            
    else:
        print(f"   ❌ Erro: {result_info}")
        print(f"   🔧 SQL gerado: {sql}")
        
        # Mesmo com erro, vamos verificar o SQL gerado
        if sql:
            sql_lower = sql.lower()
            
            checks = {
                "✅ Usa cubo_genealogia": "cubo_genealogia" in sql_lower,
                "✅ Filtra por animal_codigo": "animal_codigo = 'fsc77898'" in sql_lower,
                "❌ NÃO filtra por sexo": "animal_sexo =" not in sql_lower,
                "❌ NÃO filtra por raça": "animal_raca =" not in sql_lower,
                "✅ Inclui pai_nome": "pai_nome" in sql_lower,
                "✅ Inclui mae_nome": "mae_nome" in sql_lower,
                "❌ NÃO renomeia códigos": "as pai_nome" not in sql_lower and "as mae_nome" not in sql_lower
            }
            
            print(f"\n🔍 Verificações do SQL:")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check.replace('✅ ', '').replace('❌ ', '')}")

if __name__ == "__main__":
    test_corrected_system()