from flask import Flask, request, jsonify
from nl_to_sql import nl_to_sql_pipeline
from schema_mapper import schema_mapper
from config import Config
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)





@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NL to SQL - Mapeamento Inteligente</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .info-panel { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
            textarea { width: 100%; height: 80px; padding: 15px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; margin: 15px 0; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .result { margin: 25px 0; padding: 20px; border-radius: 5px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; }
            .loading { background: #fff3cd; border: 1px solid #ffeaa7; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .analysis { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 NL to SQL - Mapeamento Inteligente</h1>
            
            <div class="info-panel">
                <h3>📊 Sistema Baseado em Schema JSON</h3>
                <p><strong>Funcionamento:</strong> Analisa palavras-chave e mapeia para tabelas e campos específicos</p>
                <p><strong>Exemplos:</strong> "touros reprodutores", "animais com pais", "filhos do animal FSC00370"</p>
            </div>
            
            <p>Digite sua pergunta sobre genealogia bovina:</p>
            
            <textarea id="queryInput" placeholder="Ex: Mostre todos os touros reprodutores"></textarea>
            <br>
            <button onclick="processQuery()">🎯 Gerar SQL Inteligente</button>
            
            <div id="results"></div>
        </div>

        <script>
            function processQuery() {
                const query = document.getElementById('queryInput').value;
                const resultsDiv = document.getElementById('results');
                
                if (!query) {
                    alert('Por favor, digite uma pergunta!');
                    return;
                }
                
                resultsDiv.innerHTML = '<div class="result loading">⏳ Analisando palavras-chave e gerando SQL...</div>';
                
                fetch('/api/nl-to-sql', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                })
                .then(r => r.json())
                .then(data => {
                    let html = '<div class="result ' + (data.success ? 'success' : 'error') + '">';
                    html += '<h3>📊 SQL Gerado:</h3><pre>' + data.sql + '</pre>';
                    
                    if (data.success) {
                        // Mostra análise de palavras-chave
                        if (data.results.analysis) {
                            html += '<div class="analysis">';
                            html += '<h4>🔍 Análise de Palavras-Chave:</h4>';
                            html += '<p><strong>Tabelas identificadas:</strong> ' + (data.results.analysis.tables_identified.join(', ') || 'Nenhuma') + '</p>';
                            html += '<p><strong>Campos identificados:</strong> ' + (data.results.analysis.fields_identified.join(', ') || 'Nenhum') + '</p>';
                            if (data.results.analysis.keywords_detected && data.results.analysis.keywords_detected.length > 0) {
                                html += '<p><strong>Palavras detectadas:</strong> ';
                                data.results.analysis.keywords_detected.forEach(kw => {
                                    html += `"${kw.keyword}" → ${kw.target} | `;
                                });
                                html += '</p>';
                            }
                            html += '</div>';
                        }
                        
                        // 🆕 Mostra dados retornados do PostgreSQL
                        if (data.results.data && data.results.data.length > 0) {
                            html += '<h3>📋 Dados Retornados:</h3>';
                            html += '<div style="overflow-x: auto;">';
                            html += '<table border="1" style="border-collapse: collapse; width: 100%;">';
                            
                            // Cabeçalho da tabela
                            html += '<thead><tr style="background: #f0f0f0;">';
                            Object.keys(data.results.data[0]).forEach(key => {
                                html += '<th style="padding: 8px; text-align: left;">' + key + '</th>';
                            });
                            html += '</tr></thead>';
                            
                            // Dados da tabela (máximo 10 linhas)
                            html += '<tbody>';
                            data.results.data.slice(0, 10).forEach(row => {
                                html += '<tr>';
                                Object.values(row).forEach(value => {
                                    html += '<td style="padding: 8px;">' + (value || '') + '</td>';
                                });
                                html += '</tr>';
                            });
                            html += '</tbody></table>';
                            
                            if (data.results.data.length > 10) {
                                html += '<p><em>Mostrando 10 de ' + data.results.data.length + ' registros</em></p>';
                            }
                            html += '</div>';
                        }
                        
                        html += '<h3>✅ Status:</h3>';
                        html += '<p>' + (data.results.message || 'SQL executado com sucesso') + '</p>';
                    } else {
                        html += '<h3>❌ Erro:</h3><p>' + data.error + '</p>';
                    }
                    html += '</div>';
                    resultsDiv.innerHTML = html;
                })
                .catch(error => {
                    resultsDiv.innerHTML = '<div class="result error">❌ Erro de conexão: ' + error + '</div>';
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/nl-to-sql', methods=['POST'])
def nl_to_sql():
    """Endpoint principal com análise de palavras-chave"""
    data = request.get_json()
    natural_language_query = data.get('query', '').strip()
    
    if not natural_language_query:
        return jsonify({
            'success': False,
            'error': 'Query vazia'
        })
    
    # Executa o pipeline inteligente
    success, sql_query, results = nl_to_sql_pipeline.natural_language_to_sql(natural_language_query)
    
    response_data = {
        'success': success,
        'sql': sql_query,
        'results': results if success else None,
        'error': None if success else results
    }
    
    return jsonify(response_data)

@app.route('/api/schema-info')
def get_schema_info():
    """Retorna informações do schema carregado"""
    tables = [table.get("tabela") for table in schema_mapper.schema_data]
    return jsonify({
        'tables': tables,
        'total_tables': len(tables),
        'keyword_mappings_count': len(schema_mapper.keyword_mappings)
    })

@app.route('/api/database-status')
def get_database_status():
    """Testa conexão com PostgreSQL"""
    from database_executor import db_executor
    
    success, message = db_executor.test_connection()
    
    if success:
        # Obtém informações da tabela cubo_genealogia
        table_info = db_executor.get_table_info("cubo_genealogia")
        return jsonify({
            'connected': True,
            'message': message,
            'table_info': table_info
        })
    else:
        return jsonify({
            'connected': False,
            'message': message
        })

if __name__ == '__main__':
    print("🚀 Iniciando NL to SQL com Mapeamento Inteligente...")
    print("📊 Schema: schema_descriptions.json")
    print("🔗 Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)