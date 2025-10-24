from schema_mapper import schema_mapper

def test_dictionaries():
    print('🔍 Testando integração de dicionários...')
    print(f'📊 Tabelas nos dicionários: {list(schema_mapper.dicts_data.keys())}')
    print(f'🔑 Total de palavras-chave mapeadas: {len(schema_mapper.keyword_mappings)}')

    # Testa análise de algumas queries
    test_queries = [
        'touros com melhor produção de leite',
        'genealogia de animais',
        'filhas produtivas',
        'primeiro parto das vacas'
    ]
    
    for query in test_queries:
        print(f'\n🎯 Análise: "{query}"')
        analysis = schema_mapper.analyze_query(query)
        print(f'   Tabelas: {list(analysis["tables"])}')
        print(f'   Campos: {list(analysis["fields"])[:3]}')  # Primeiros 3
        keywords = [kw["keyword"] for kw in analysis["detected_keywords"][:3]]
        print(f'   Palavras: {keywords}')

if __name__ == "__main__":
    test_dictionaries()