import httpx
import asyncio
from bs4 import BeautifulSoup
import urllib.parse
import re
import json
from playwright.async_api import async_playwright


# ============================================================
# HEADERS
# ============================================================
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}


# ============================================================
# UTIL – LIMPAR PREÇO
# ============================================================
def limpar_preco(preco_str):
    if not isinstance(preco_str, str):
        return 0.0

    preco_str = preco_str.replace("R$", "").strip()
    preco_str = preco_str.replace(".", "")
    preco_str = preco_str.replace(",", ".")

    match = re.search(r"(\d+\.\d{2}|\d+)", preco_str)
    if match:
        preco_str = match.group(1)
    else:
        return 0.0

    try:
        return float(preco_str)
    except:
        return 0.0


# ============================================================
# 1 — SUPER SÃO JUDAS
# ============================================================
async def scrape_super_saojudas(client, termo_pesquisa):
    base_url = "https://compreonline.supersaojudas.com.br/loja6/busca/?q="
    url = base_url + urllib.parse.quote(termo_pesquisa)
    produtos = []

    try:
        r = await client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        nomes = soup.find_all("span", class_="nome ellipsis-2")
        precos = soup.find_all("span", class_="preco-final")
        imagens = soup.find_all("img", class_="owl-lazy img-responsive lozad")

        n = min(len(nomes), len(precos))

        for i in range(n):
            nome = nomes[i].text.strip()
            preco_str = precos[i].text.strip()
            preco = limpar_preco(preco_str)

            img = "N/A"
            if i < len(imagens):
                img = imagens[i].get("data-src") or imagens[i].get("src")

            produtos.append({
                "supermercado": "Super São Judas",
                "nome": nome,
                "preco_str": preco_str,
                "preco": preco,
                "image_url": img,
                "url": url
            })

    except Exception as e:
        print(f"[ERRO SÃO JUDAS] {e}")

    return produtos


# ============================================================
# 2 — AMIGÃO USANDO A ROTA QUE VOCÊ PEDIU
#    /s/?q=xxxx (extração via JSON __STATE__)
# ============================================================
async def scrape_amigao(client, termo_pesquisa):
    url = f"https://www.amigao.com/s/?q={termo_pesquisa}&sort=score_desc&page=0"
    produtos = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("Acessando página...")
            await page.goto(url, timeout=60000)

            await page.wait_for_selector("ul.product-grid li", timeout=60000)

            itens = await page.query_selector_all("ul.product-grid li")

            print(f"\nForam encontrados {len(itens)} produtos:\n")

            for item in itens:
                nome_el = await item.query_selector("div.product-card-section-name")
                preco_el = await item.query_selector("div.product-card-price")
                img_el = await item.query_selector("div.product-card-image-container img")
                
                nome = await nome_el.inner_text() if nome_el else "NOME NÃO ENCONTRADO"
                preco = await preco_el.inner_text() if preco_el else "PREÇO NÃO ENCONTRADO"
                imagem = await img_el.get_attribute("src") if img_el else "IMAGEM NÃO ENCONTRADA"
                
                produtos.append({
                    "supermercado": "Amigão",
                    "nome": nome.strip(),
                    "preco_str": preco.strip(),
                    "preco": limpar_preco(preco),
                    "image_url": imagem,
                    "url": url
                })

            await browser.close()

    except Exception as e:
        print(f"[ERRO AMIGÃO] {e}")

    return produtos



# ============================================================
# 3 — ATACADÃO
# ============================================================
async def scrape_atacadao(client, termo_pesquisa):
    url = f"https://www.atacadao.com.br/s?q={termo_pesquisa}&sort=score_desc&page=0"
    produtos = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("\n=== ACESSANDO ATACADÃO ===")
            await page.goto(url, timeout=60000)

            # Esperar os cards carregarem
            await page.wait_for_selector("div.flex.flex-col.h-full.p-2", timeout=60000)

            itens = await page.query_selector_all("div.flex.flex-col.h-full.p-2")
            print(f"\nForam encontrados {len(itens)} produtos no ATACADÃO:\n")

            for item in itens:

                # Nome
                nome_el = await item.query_selector("h3.overflow-hidden")
                nome = await nome_el.inner_text() if nome_el else "NOME NÃO ENCONTRADO"

                # Preço
                preco_el = await item.query_selector("p.text-sm.text-neutral-500.font-bold")
                preco = await preco_el.inner_text() if preco_el else "PREÇO NÃO ENCONTRADO"

                # Imagem
                img_el = await item.query_selector("div.relative")
                imagem = await img_el.get_attribute("srcset") if img_el else "IMAGEM NÃO ENCONTRADA"

                produtos.append({
                    "supermercado": "Atacadão",
                    "nome": nome.strip(),
                    "preco_str": preco.strip(),
                    "preco": limpar_preco(preco),
                    "image_url": imagem,
                    "url": url
                })

            await browser.close()

    except Exception as e:
        print(f"[ERRO ATACADÃO] {e}")

    return produtos



# ============================================================
# FUNÇÃO FINAL – EXECUÇÃO ASSÍNCRONA
# ============================================================
async def find_cheapest_products(termo_pesquisa):
    produtos = []

    async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as client:
        results = await asyncio.gather(
            scrape_super_saojudas(client, termo_pesquisa),
            scrape_amigao(client, termo_pesquisa),
            scrape_atacadao(client, termo_pesquisa)
        )

    for lista in results:
        produtos.extend(lista)

    produtos_validos = [p for p in produtos if p["preco"] > 0]
    produtos_validos.sort(key=lambda x: x["preco"])

    return {
        "search_term": termo_pesquisa,
        "products": produtos_validos
    }


# ============================================================
# TESTE LOCAL
# ============================================================
if __name__ == "__main__":
    termo = "leite integral"
    print(f"Buscando preços para: {termo} ...")

    resultado = asyncio.run(find_cheapest_products(termo))

    print("\nRESULTADOS:\n")
    for p in resultado["products"]:
        print(f"[{p['supermercado']}] {p['nome']} → {p['preco_str']}  (float: {p['preco']})")
