#!/usr/bin/env python3
"""
Script para testar queries corretas de genealogia
"""

import psycopg2
from config import Config

def connect_to_db():
    """Conecta ao PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def test_queries():
    """Testa diferentes queries de genealogia"""
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("🧬 TESTANDO QUERIES DE GENEALOGIA")
    print("=" * 50)
    
    # Query 1: Animal específico FSC77898
    print("\n1️⃣ Query Original (INCORRETA):")
    query1 = """
    SELECT
        animal_codigo,
        animal_nome,
        pai_codigo AS pai_nome,
        mae_codigo AS mae_nome,
        avo_paterno_codigo AS avo_paterno_nome
    FROM
        cubo_genealogia
    WHERE
        animal_sexo = 'M' AND
        animal_raca = 'Bovino'
    ORDER BY
        animal_codigo;
    """
    print(f"   SQL: {query1.strip()}")
    
    cursor.execute(query1)
    results = cursor.fetchall()
    print(f"   📊 Resultados: {len(results)} registros")
    
    # Query 2: Animal específico FSC77898 (CORRETA)
    print("\n2️⃣ Query Corrigida para FSC77898:")
    query2 = """
    SELECT
        animal_codigo,
        animal_nome,
        animal_sexo,
        animal_raca,
        pai_codigo,
        pai_nome,
        mae_codigo,
        mae_nome,
        avo_paterno_codigo,
        avo_paterno_nome,
        avo_materno_codigo,
        avo_materno_nome
    FROM
        cubo_genealogia
    WHERE
        animal_codigo = 'FSC77898';
    """
    print(f"   SQL: {query2.strip()}")
    
    cursor.execute(query2)
    results = cursor.fetchall()
    print(f"   📊 Resultados: {len(results)} registros")
    
    if results:
        result = results[0]
        print(f"   ✅ Animal encontrado:")
        print(f"      🐄 Código: {result[0]}")
        print(f"      📝 Nome: {result[1]}")
        print(f"      ⚧ Sexo: {result[2]}")
        print(f"      🧬 Raça: {result[3]}")
        print(f"      👨 Pai: {result[4]} - {result[5]}")
        print(f"      👩 Mãe: {result[6]} - {result[7]}")
        print(f"      👴 Avô paterno: {result[8]} - {result[9]}")
        print(f"      👴 Avô materno: {result[10]} - {result[11]}")
    
    # Query 3: Genealogia até 3ª geração (CORRETA)
    print("\n3️⃣ Genealogia completa de FSC77898:")
    query3 = """
    -- Animal base e seus pais
    SELECT 
        'Animal base' as tipo,
        animal_codigo,
        animal_nome,
        animal_sexo,
        pai_codigo,
        pai_nome,
        mae_codigo,
        mae_nome
    FROM cubo_genealogia 
    WHERE animal_codigo = 'FSC77898'
    
    UNION ALL
    
    -- Pais do animal
    SELECT 
        'Pai' as tipo,
        animal_codigo,
        animal_nome,
        animal_sexo,
        pai_codigo,
        pai_nome,
        mae_codigo,
        mae_nome
    FROM cubo_genealogia 
    WHERE animal_codigo IN (
        SELECT pai_codigo FROM cubo_genealogia WHERE animal_codigo = 'FSC77898' AND pai_codigo IS NOT NULL
    )
    
    UNION ALL
    
    -- Mãe do animal
    SELECT 
        'Mae' as tipo,
        animal_codigo,
        animal_nome,
        animal_sexo,
        pai_codigo,
        pai_nome,
        mae_codigo,
        mae_nome
    FROM cubo_genealogia 
    WHERE animal_codigo IN (
        SELECT mae_codigo FROM cubo_genealogia WHERE animal_codigo = 'FSC77898' AND mae_codigo IS NOT NULL
    )
    
    ORDER BY tipo, animal_codigo;
    """
    print(f"   SQL: Genealogia simples com pais")
    
    cursor.execute(query3)
    results = cursor.fetchall()
    print(f"   📊 Resultados: {len(results)} registros")
    
    for result in results:
        tipo = result[0]
        codigo = result[1]
        nome = result[2]
        sexo = result[3]
        pai_codigo = result[4]
        pai_nome = result[5]
        mae_codigo = result[6]
        mae_nome = result[7]
        
        print(f"   📊 {tipo}: {codigo} ({nome}) - Sexo: {sexo}")
        if pai_codigo:
            print(f"      👨 Pai: {pai_codigo} ({pai_nome})")
        if mae_codigo:
            print(f"      👩 Mãe: {mae_codigo} ({mae_nome})")
        print()
    
    # Query 4: Query simples para genealogia (RECOMENDADA)
    print("\n4️⃣ Query Simples e Correta:")
    query4 = """
    SELECT
        animal_codigo,
        animal_nome,
        animal_sexo,
        pai_codigo,
        pai_nome,
        mae_codigo,
        mae_nome
    FROM
        cubo_genealogia
    WHERE
        animal_codigo = 'FSC77898';
    """
    print(f"   SQL: {query4.strip()}")
    
    cursor.execute(query4)
    results = cursor.fetchall()
    
    if results:
        result = results[0]
        print(f"   ✅ Genealogia de {result[0]}:")
        print(f"      🐄 Animal: {result[0]} - {result[1]} ({result[2]})")
        print(f"      👨 Pai: {result[3]} - {result[4]}")
        print(f"      👩 Mãe: {result[5]} - {result[6]}")
    
    conn.close()

if __name__ == "__main__":
    test_queries()