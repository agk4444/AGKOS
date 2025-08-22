from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    try:
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        result = num1 + num2
        return jsonify({'result': result, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'AGK Web App is running!'})

if __name__ == '__main__':
    print("🚀 Starting AGK Web Application...")
    print("📱 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)