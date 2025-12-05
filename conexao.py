from flask import Flask, render_template, request
import asyncio
from index import find_cheapest_products

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    search_term = request.args.get("search_term", "").strip()
    products = []
    search_performed = False

    if search_term:
        search_performed = True
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resultado = loop.run_until_complete(find_cheapest_products(search_term))
            products = resultado["products"]
        except Exception as e:
            print("Erro:", e)

    return render_template("index.html",
                           products=products,
                           search_term=search_term,
                           search_performed=search_performed)
