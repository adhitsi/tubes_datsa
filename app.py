from utils.feature_engineering import FeatureEngineer
from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib

app = Flask(__name__)

model = joblib.load('model/model_rf.pkl')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        
        data = request.get_json()
        if data['age'] <= 0:
            return jsonify({'error': 'Umur harus > 0'}), 400
        if data['bmi'] <= 0:
            return jsonify({'error': 'BMI harus > 0'}), 400
        if data['bmi'] < 10 or data['bmi'] > 60:
            return jsonify({'error': 'BMI tidak realistis (10 - 60)'}), 400

        df = pd.DataFrame([data])

        pred = model.predict(df)[0]

        return jsonify({
            'prediction': float(pred),
            'range': {
                'lower': float(pred * 0.8),
                'upper': float(pred * 1.2)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)