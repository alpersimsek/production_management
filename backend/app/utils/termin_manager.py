from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

logger = logging.getLogger(__name__)

class TerminColorManager:
    """Manages termin color coding for orders"""
    
    COLOR_CODES = {
        'critical': '🔴',      # < 7 days
        'warning': '🟠',       # 8-15 days
        'normal': '🟡',        # 16-30 days
        'ready': '🔵',         # Ready for delivery
        'delivered': '🟢'      # Delivered
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_order_color_code(self, order) -> Tuple[str, str, str]:
        """
        Get color code for an order based on due date and status
        Returns: (color_code, description, days_remaining)
        """
        today = date.today()
        due_date = order.due_date
        
        # Calculate days remaining
        days_remaining = (due_date - today).days
        
        # Check delivery status first (highest priority)
        if order.status == 'teslim_edildi':
            return self.COLOR_CODES['delivered'], 'Teslim Edildi', days_remaining
        
        if order.status in ['sevkiyat_planlandi', 'teslimde']:
            return self.COLOR_CODES['ready'], 'Teslim Edilmek Üzere Hazır', days_remaining
        
        # Color based on days remaining
        if days_remaining < 0:
            return self.COLOR_CODES['critical'], f'{abs(days_remaining)} gün gecikme', days_remaining
        elif days_remaining <= 7:
            return self.COLOR_CODES['critical'], f'{days_remaining} gün kala', days_remaining
        elif days_remaining <= 15:
            return self.COLOR_CODES['warning'], f'{days_remaining} gün kala', days_remaining
        elif days_remaining <= 30:
            return self.COLOR_CODES['normal'], f'{days_remaining} gün kala', days_remaining
        else:
            return self.COLOR_CODES['normal'], f'{days_remaining} gün kala', days_remaining
    
    def get_orders_by_color(self, color_code: str, start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> List[Dict]:
        """Get orders filtered by color code"""
        from ..models.order import Order
        
        query = self.db.query(Order)
        
        if start_date:
            query = query.filter(Order.due_date >= start_date)
        if end_date:
            query = query.filter(Order.due_date <= end_date)
        
        orders = query.all()
        
        filtered_orders = []
        for order in orders:
            order_color, _, _ = self.get_order_color_code(order)
            if order_color == color_code:
                filtered_orders.append({
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': order.customer.name if order.customer else 'Unknown',
                    'due_date': order.due_date.isoformat(),
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'days_remaining': (order.due_date - date.today()).days
                })
        
        return filtered_orders
    
    def get_critical_orders(self) -> List[Dict]:
        """Get orders that are critical (overdue or < 7 days)"""
        return self.get_orders_by_color(self.COLOR_CODES['critical'])
    
    def get_warning_orders(self) -> List[Dict]:
        """Get orders that are in warning state (8-15 days)"""
        return self.get_orders_by_color(self.COLOR_CODES['warning'])
    
    def get_termin_dashboard_data(self) -> Dict:
        """Get termin dashboard data with counts and statistics"""
        from ..models.order import Order
        
        today = date.today()
        
        # Get all orders
        orders = self.db.query(Order).all()
        
        # Count by color
        color_counts = {
            'critical': 0,
            'warning': 0,
            'normal': 0,
            'ready': 0,
            'delivered': 0
        }
        
        overdue_count = 0
        total_value = 0
        
        for order in orders:
            color_code, _, days_remaining = self.get_order_color_code(order)
            
            if color_code == self.COLOR_CODES['critical']:
                color_counts['critical'] += 1
                if days_remaining < 0:
                    overdue_count += 1
            elif color_code == self.COLOR_CODES['warning']:
                color_counts['warning'] += 1
            elif color_code == self.COLOR_CODES['normal']:
                color_counts['normal'] += 1
            elif color_code == self.COLOR_CODES['ready']:
                color_counts['ready'] += 1
            elif color_code == self.COLOR_CODES['delivered']:
                color_counts['delivered'] += 1
            
            if order.total_amount:
                total_value += float(order.total_amount)
        
        # Calculate statistics
        total_orders = len(orders)
        on_time_percentage = 0
        if total_orders > 0:
            on_time_orders = color_counts['delivered'] + color_counts['ready']
            on_time_percentage = (on_time_orders / total_orders) * 100
        
        return {
            'total_orders': total_orders,
            'total_value': total_value,
            'overdue_count': overdue_count,
            'on_time_percentage': round(on_time_percentage, 2),
            'color_counts': color_counts,
            'critical_orders': self.get_critical_orders(),
            'warning_orders': self.get_warning_orders()
        }

class TerminAnalytics:
    """Termin analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
        self.color_manager = TerminColorManager(db)
    
    def get_termin_performance(self, start_date: Optional[date] = None, 
                              end_date: Optional[date] = None) -> Dict:
        """Get termin performance statistics"""
        from ..models.order import Order
        
        query = self.db.query(Order)
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        
        orders = query.all()
        
        if not orders:
            return {
                'total_orders': 0,
                'on_time_delivery': 0,
                'late_delivery': 0,
                'on_time_percentage': 0,
                'average_delay_days': 0,
                'by_month': [],
                'by_customer': []
            }
        
        # Calculate performance metrics
        on_time_count = 0
        late_count = 0
        total_delay_days = 0
        
        for order in orders:
            if order.status == 'teslim_edildi':
                if order.due_date >= order.updated_at.date():
                    on_time_count += 1
                else:
                    late_count += 1
                    delay_days = (order.updated_at.date() - order.due_date).days
                    total_delay_days += delay_days
        
        total_delivered = on_time_count + late_count
        on_time_percentage = (on_time_count / total_delivered * 100) if total_delivered > 0 else 0
        average_delay_days = (total_delay_days / late_count) if late_count > 0 else 0
        
        # Group by month
        by_month = self._get_monthly_performance(orders)
        
        # Group by customer
        by_customer = self._get_customer_performance(orders)
        
        return {
            'total_orders': len(orders),
            'on_time_delivery': on_time_count,
            'late_delivery': late_count,
            'on_time_percentage': round(on_time_percentage, 2),
            'average_delay_days': round(average_delay_days, 2),
            'by_month': by_month,
            'by_customer': by_customer
        }
    
    def _get_monthly_performance(self, orders: List) -> List[Dict]:
        """Get monthly performance data"""
        monthly_data = {}
        
        for order in orders:
            if order.status == 'teslim_edildi':
                month_key = order.updated_at.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'total_orders': 0,
                        'on_time': 0,
                        'late': 0
                    }
                
                monthly_data[month_key]['total_orders'] += 1
                
                if order.due_date >= order.updated_at.date():
                    monthly_data[month_key]['on_time'] += 1
                else:
                    monthly_data[month_key]['late'] += 1
        
        # Convert to list and calculate percentages
        result = []
        for data in monthly_data.values():
            if data['total_orders'] > 0:
                data['on_time_percentage'] = (data['on_time'] / data['total_orders']) * 100
            else:
                data['on_time_percentage'] = 0
            
            result.append(data)
        
        return sorted(result, key=lambda x: x['month'])
    
    def _get_customer_performance(self, orders: List) -> List[Dict]:
        """Get customer performance data"""
        customer_data = {}
        
        for order in orders:
            if order.status == 'teslim_edildi' and order.customer:
                customer_id = order.customer.id
                customer_name = order.customer.name
                
                if customer_id not in customer_data:
                    customer_data[customer_id] = {
                        'customer_id': customer_id,
                        'customer_name': customer_name,
                        'total_orders': 0,
                        'on_time': 0,
                        'late': 0,
                        'total_value': 0
                    }
                
                customer_data[customer_id]['total_orders'] += 1
                customer_data[customer_id]['total_value'] += float(order.total_amount or 0)
                
                if order.due_date >= order.updated_at.date():
                    customer_data[customer_id]['on_time'] += 1
                else:
                    customer_data[customer_id]['late'] += 1
        
        # Convert to list and calculate percentages
        result = []
        for data in customer_data.values():
            if data['total_orders'] > 0:
                data['on_time_percentage'] = (data['on_time'] / data['total_orders']) * 100
            else:
                data['on_time_percentage'] = 0
            
            result.append(data)
        
        # Sort by on-time percentage (descending)
        return sorted(result, key=lambda x: x['on_time_percentage'], reverse=True)
    
    def get_salesperson_performance(self, start_date: Optional[date] = None, 
                                   end_date: Optional[date] = None) -> List[Dict]:
        """Get salesperson (plasiyer) performance data"""
        from ..models.order import Order
        from ..models.user import User
        
        query = self.db.query(Order, User).join(
            User, Order.salesperson_id == User.id
        )
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        
        results = query.all()
        
        salesperson_data = {}
        
        for order, user in results:
            if user.id not in salesperson_data:
                salesperson_data[user.id] = {
                    'user_id': user.id,
                    'user_name': user.full_name,
                    'total_orders': 0,
                    'total_value': 0,
                    'on_time_delivery': 0,
                    'late_delivery': 0
                }
            
            data = salesperson_data[user.id]
            data['total_orders'] += 1
            data['total_value'] += float(order.total_amount or 0)
            
            if order.status == 'teslim_edildi':
                if order.due_date >= order.updated_at.date():
                    data['on_time_delivery'] += 1
                else:
                    data['late_delivery'] += 1
        
        # Convert to list and calculate percentages
        result = []
        for data in salesperson_data.values():
            total_delivered = data['on_time_delivery'] + data['late_delivery']
            if total_delivered > 0:
                data['on_time_percentage'] = (data['on_time_delivery'] / total_delivered) * 100
            else:
                data['on_time_percentage'] = 0
            
            result.append(data)
        
        # Sort by total value (descending)
        return sorted(result, key=lambda x: x['total_value'], reverse=True)
