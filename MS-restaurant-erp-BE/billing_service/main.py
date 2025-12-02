from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from routes.billing import BillList, BillDetail, BillStats, MonthlyRevenue

app = Flask(__name__)
CORS(app)
api = Api(app)

# Health check
@app.route('/')
def health():
    return {"status": "ok", "service": "billing_service"}

# Routes
api.add_resource(BillList, '/billing/bills')
api.add_resource(BillDetail, '/billing/bills/<string:bill_id>')
api.add_resource(BillStats, '/billing/bills/stats')
api.add_resource(MonthlyRevenue, '/billing/bills/monthly-revenue')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)