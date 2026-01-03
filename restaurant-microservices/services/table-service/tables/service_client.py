import requests
import os
from datetime import date


class BillingServiceClient:
    """Client to communicate with billing-service"""
    
    def __init__(self):
        self.base_url = os.getenv('BILLING_SERVICE_URL', 'http://billing-service:8000')
    
    def create_bill_from_order(self, table_order, customer_info=None):
        """Create a bill from table order"""
        try:
            # Prepare bill data
            items = []
            total = 0
            for item in table_order.items.all():
                subtotal = float(item.price) * item.quantity
                total += subtotal
                items.append({
                    'menu_item_id': item.menu_item_id,
                    'item_name': item.name,
                    'quantity': item.quantity,
                    'price': int(item.price)  # Convert to integer to avoid decimal issues
                })
            
            # Get points info from customer_info
            points_used = int(customer_info.get('points_used', 0)) if customer_info else 0
            points_discount = int(customer_info.get('points_discount', 0)) if customer_info else 0
            final_total = max(0, int(total) - points_discount)
            
            bill_data = {
                'date': date.today().isoformat(),
                'total': final_total,
                'original_total': int(total),
                'items': items,
                'notes': f'Bàn: {table_order.table.name}. {table_order.notes or ""}'.strip(),
                'customer': customer_info.get('customer', '') if customer_info else '',
                'phone': customer_info.get('phone', '') if customer_info else '',
                'customer_id': customer_info.get('customer_id') if customer_info else None,
                'points_used': points_used,
                'points_discount': points_discount,
            }
            
            print(f"Creating bill with data: {bill_data}")
            
            # Call billing service
            response = requests.post(
                f'{self.base_url}/api/billing/bills/',
                json=bill_data,
                timeout=10
            )
            
            print(f"Billing response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'bill': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': response.text
                }
        except Exception as e:
            print(f"Error creating bill: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
