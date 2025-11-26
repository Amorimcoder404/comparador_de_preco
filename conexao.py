from flask import Flask, render_template, request
# Importa o módulo asyncio para rodar a função assíncrona
import asyncio 
# Importa a função de busca do nosso módulo de scraping
from index import find_cheapest_products 
import sys
import time
# Nota: Os imports 'subprocess' e 'sys' foram removidos por não serem mais necessários
# para a função principal deste arquivo.

# Configuração básica do Flask
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """Página inicial com busca de produtos e exibição de resultados."""
    # Obtém o termo de busca do parâmetro da URL
    search_term = request.args.get('search_term', '').strip()
    
    products = []
    search_performed = False
    
    if search_term:
        print(f"Iniciando busca para: {search_term}")
        search_performed = True
        try:
            # CORREÇÃO: Usa asyncio.run() para executar a função assíncrona
            # find_cheapest_products e aguardar seu resultado.
            resultado = asyncio.run(find_cheapest_products(search_term))
            products = resultado['products']
            
        except Exception as e:
            # Em caso de erro (ex: problemas de rede ou raspagem), exibe no console.
            print(f"Erro ao buscar produtos: {e}")
            
    # Retorna o template index.html, passando os produtos, o termo de busca e o status da busca.
    return render_template(
        'index.html', 
        products=products, 
        search_term=search_term,
        search_performed=search_performed
    )

# -----------------------------------------------------------------
# Ponto de entrada: Rodar o servidor Flask
# -----------------------------------------------------------------
"""if __name__ == '__main__':
    print("--- Iniciando o servidor Flask de Comparação de Preços ---")
    # Inicia o servidor em modo de desenvolvimento
    app.run(debug=True, host='0.0.0.0', port=5000)"""