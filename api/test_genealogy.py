from schema_mapper import schema_mapper

def test_genealogy_mapping():
    print('🧬 Testando mapeamento de genealogia...')
    
    test_queries = [
        'Forneça a genealogia até a terceira geração do animal FSC77898',
        'genealogia do animal FSC12345',
        'linhagem do FSC77898',
        'descendentes de FSC77898',
        'pai e mãe do animal FSC77898'
    ]
    
    for query in test_queries:
        print(f'\n🎯 Query: "{query}"')
        analysis = schema_mapper.analyze_query(query)
        
        print(f'   📊 Tabelas identificadas: {list(analysis["tables"])}')
        print(f'   🔑 Tabelas prioritárias: {list(analysis.get("priority_tables", set()))}')
        
        # Mostra palavras-chave detectadas
        keywords = [kw["keyword"] for kw in analysis["detected_keywords"][:5]]
        print(f'   💬 Palavras-chave: {keywords}')

if __name__ == "__main__":
    test_genealogy_mapping()