from schema_mapper import schema_mapper

print('🧪 Testando carregamento do schema...')

print(f'📊 Schema carregado via backup: {schema_mapper.use_backup}')
print(f'🔗 Mapeamentos de palavras: {len(schema_mapper.keyword_mappings)}')

# Testa algumas palavras-chave
test_words = ['bovino', 'genealogia', 'producao', 'touro', 'vaca']
for word in test_words:
    if word in schema_mapper.keyword_mappings:
        mappings = schema_mapper.keyword_mappings[word]
        print(f'🔍 "{word}": {len(mappings)} mapeamentos encontrados')
        # Mostra primeiro mapeamento
        if mappings:
            first = mappings[0]
            print(f'   → {first["type"]}: {first["target"]}')
    else:
        print(f'❌ "{word}": não encontrado')

# Mostra primeiras 10 palavras-chave
print(f'\n📋 Primeiras 10 palavras-chave mapeadas:')
for i, word in enumerate(list(schema_mapper.keyword_mappings.keys())[:10]):
    mappings = schema_mapper.keyword_mappings[word]
    print(f'{i+1}. "{word}" → {len(mappings)} mapeamentos')