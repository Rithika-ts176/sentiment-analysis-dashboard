from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import random

app = Flask(__name__)

# -------------------------------
# LOAD DATASET
# -------------------------------
df = pd.read_csv("reviews.csv")

# Unique products
all_products = df["product_name"].unique()

# -------------------------------
# GENERATE RANDOM PRICES
# -------------------------------
def generate_prices():
    price_data = {}
    for product in all_products:
        amazon_price = random.randint(30000, 80000)
        flipkart_price = random.randint(30000, 80000)

        price_data[product] = {
            "amazon": amazon_price,
            "flipkart": flipkart_price
        }
    return price_data

price_data = generate_prices()

# -------------------------------
# PLATFORM-WISE SENTIMENT
# -------------------------------
def generate_sentiment(selected_product):

    data = df[df["product_name"] == selected_product].copy()

    def get_sentiment(text):
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"

    data["Sentiment"] = data["review"].apply(get_sentiment)

    amazon_data = data[data["platform"] == "Amazon"]
    flipkart_data = data[data["platform"] == "Flipkart"]

    amazon_counts = amazon_data["Sentiment"].value_counts()
    flipkart_counts = flipkart_data["Sentiment"].value_counts()

    amazon_positive = amazon_counts.get("Positive", 0)
    amazon_negative = amazon_counts.get("Negative", 0)
    amazon_neutral = amazon_counts.get("Neutral", 0)

    flipkart_positive = flipkart_counts.get("Positive", 0)
    flipkart_negative = flipkart_counts.get("Negative", 0)
    flipkart_neutral = flipkart_counts.get("Neutral", 0)

    # Chart
    labels = ["Positive", "Negative", "Neutral"]
    amazon_values = [amazon_positive, amazon_negative, amazon_neutral]
    flipkart_values = [flipkart_positive, flipkart_negative, flipkart_neutral]

    x = range(len(labels))

    plt.figure(figsize=(7,5))
    plt.bar(x, amazon_values, width=0.4, label="Amazon")
    plt.bar([p + 0.4 for p in x], flipkart_values, width=0.4, label="Flipkart")

    plt.xticks([p + 0.2 for p in x], labels)
    plt.title(f"Platform-wise Sentiment for {selected_product}")
    plt.legend()
    plt.savefig("static/graphics.png")
    plt.close()

    # Totals
    amazon_total = len(amazon_data)
    flipkart_total = len(flipkart_data)

    def calculate_percentage(part, total):
        if total == 0:
            return 0
        return round((part / total) * 100, 2)

    amazon_positive_pct = calculate_percentage(amazon_positive, amazon_total)
    flipkart_positive_pct = calculate_percentage(flipkart_positive, flipkart_total)

    if amazon_positive_pct > flipkart_positive_pct:
        better_platform = "Amazon"
    elif flipkart_positive_pct > amazon_positive_pct:
        better_platform = "Flipkart"
    else:
        better_platform = "Both platforms show similar satisfaction levels"

    insight = f"{better_platform} demonstrates comparatively stronger positive customer sentiment for this product."

    return {
        "amazon_total": amazon_total,
        "flipkart_total": flipkart_total,
        "amazon_positive_pct": amazon_positive_pct,
        "flipkart_positive_pct": flipkart_positive_pct,
        "insight": insight
    }

# -------------------------------
# HOME PAGE
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# COMPARE PAGE
# -------------------------------
@app.route("/compare", methods=["GET", "POST"])
def compare():

    selected_product = None
    result = None
    sentiment_data = None

    if request.method == "POST":
        selected_product = request.form["product"]

        amazon_price = price_data[selected_product]["amazon"]
        flipkart_price = price_data[selected_product]["flipkart"]

        if amazon_price < flipkart_price:
            cheaper = "Amazon"
        elif flipkart_price < amazon_price:
            cheaper = "Flipkart"
        else:
            cheaper = "Both are same price"

        result = {
            "name": selected_product,
            "amazon": amazon_price,
            "flipkart": flipkart_price,
            "cheaper": cheaper
        }

        sentiment_data = generate_sentiment(selected_product)

    return render_template(
        "compare.html",
        products=all_products,
        result=result,
        selected_product=selected_product,
        sentiment_data=sentiment_data
    )

if __name__ == "__main__":
    app.run(debug=False)
