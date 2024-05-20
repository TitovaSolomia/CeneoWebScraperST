import os
import pandas as pd
import numpy as np
from app import app
import requests
from bs4 import BeautifulSoup
from flask import render_template, request, redirect, url_for
from app import utils
import json

@app.route('/')
def index():
    return render_template("index.html.jinja")


@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        url = f'https://www.ceneo.pl/{product_id}'
        response = requests.get(url)
        if response.status_code == requests.codes['ok']:
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions_count = utils.extract(page_dom, "a.product-review__link > span")
            if opinions_count:
                url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
                #proces ekstrakcji
                all_opinions = []
                while (url):
                    response = requests.get(url)
                    response.status_code
                    page_dom = BeautifulSoup(response.text, "html.parser")
                    opinions = page_dom.select("div.js_product-review")

                    for opinion in opinions:
                            single_opinion = {
                                key: utils.extract(opinion, *value)
                                    for key, value in utils.selector.items()
                            }
                            all_opinions.append(single_opinion)      
                    try:
                        url = "https://www.ceneo.pl"+utils.extract(page_dom, "a.pagination__next", "href") 
                    except TypeError:
                        url = None 
                    if not os.path.exists("app/data"):
                        os.mkdir("app/data")
                    if not os.path.exists("app/data/opinions"):
                        os.mkdir("app/data/opinions")
                    with open(f"app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jsonfile:    
                        json.dump(all_opinions, jsonfile, indent = 4, ensure_ascii=False)
                    opinions = pd.DataFrame.from_dict(all_opinions)    

                return redirect(url_for('product', product_id = product_id)) 
            return render_template("extract.html.jinja", error="Product o podanym kodzie nie ma opinii")
        return render_template("extract.html.jinja", error="Product o podanym kodzie nie istnieje")
    return render_template("extract.html.jinja")


@app.route('/products')
def products():
    products = [filename.split(".")[0] for filename in os.listdir("app/data/opinions")]
    return render_template("products.html.jinja")


@app.route('/author')
def author():
    return render_template("author.html.jinja")


@app.route('/product/<product_id>')
def product(product_id):
    return render_template("product.html.jinja", product_id = product_id)



@app.route('/hello')
@app.route('/hello/<name>')
def hello(name = "World"):
    return f"Hello, {name}!"