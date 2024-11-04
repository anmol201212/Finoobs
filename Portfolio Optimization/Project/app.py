from flask import Flask, render_template, jsonify, request
from portfolio_optimizer import optimize_portfolio  # Import the optimizer function
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_list', methods=['GET'])
def get_list():
    # Read the CSV file containing stock names
    try:
        # df = pd.read_csv('E:\Projects\Finoobs\Portfolio Optimization\Project\companies.csv')  # Replace with the actual path to your CSV file
        df = pd.read_csv('E:\Projects\Finoobs\Portfolio Optimization\Project\indian_stock_listings.csv')
        stock_list = df['NAME OF COMPANY'].dropna().tolist()  # Retrieve the list and remove any NaN values
        return jsonify(stock_list)
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    investment_amount = data.get('amount')
    selected_items = data.get('selectedItems')

    # Log the incoming data
    print(f"Received amount: {investment_amount}, selected items: {selected_items}")
    
    try:
        recommendations, expected_return, volatility, total_invested = optimize_portfolio(investment_amount, selected_items)
        print("hehehe",expected_return)
        return jsonify({
            "recommendations": recommendations,
            "expected_return": expected_return,
            "volatility": volatility,
            "total_invested": total_invested
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
