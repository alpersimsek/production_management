from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FireThresholdManager:
    """Manages fire thresholds and warnings"""
    
    DEFAULT_THRESHOLDS = {
        'poset': {
            'level1_percent': 3.0,
            'level1_kg': 15.0,
            'level2_percent': 6.0,
            'level2_kg': 30.0
        },
        'deterjan': {
            'level1_percent': 2.0,
            'level1_kg': 10.0,
            'level2_percent': 4.0,
            'level2_kg': 20.0
        },
        'al-sat': {
            'level1_percent': 1.0,
            'level1_kg': 5.0,
            'level2_percent': 2.0,
            'level2_kg': 10.0
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_thresholds(self, product_type: str) -> Dict[str, float]:
        """Get fire thresholds for a product type"""
        from ..models.settings import Settings
        
        settings = self.db.query(Settings).filter(Settings.key == 'fire_thresholds').first()
        if settings and settings.value:
            thresholds = settings.value.get(product_type, self.DEFAULT_THRESHOLDS.get(product_type, {}))
        else:
            thresholds = self.DEFAULT_THRESHOLDS.get(product_type, {})
        
        return thresholds
    
    def set_thresholds(self, product_type: str, thresholds: Dict[str, float], user_id: int) -> bool:
        """Set fire thresholds for a product type"""
        from ..models.settings import Settings
        
        try:
            settings = self.db.query(Settings).filter(Settings.key == 'fire_thresholds').first()
            if not settings:
                settings = Settings(
                    key='fire_thresholds',
                    value={},
                    updated_by=user_id
                )
                self.db.add(settings)
            
            if not settings.value:
                settings.value = {}
            
            settings.value[product_type] = thresholds
            settings.updated_by = user_id
            settings.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Fire thresholds updated for {product_type}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update fire thresholds: {str(e)}")
            return False
    
    def check_fire_level(self, waste_kg: float, total_kg: float, product_type: str) -> Tuple[int, str]:
        """
        Check fire level based on waste amount
        Returns: (level, message)
        level: 0 = normal, 1 = warning, 2 = critical
        """
        thresholds = self.get_thresholds(product_type)
        
        if total_kg <= 0:
            return 0, "No production data"
        
        waste_percentage = (waste_kg / total_kg) * 100
        
        # Check level 2 (critical) first
        if (waste_percentage >= thresholds.get('level2_percent', 0) or 
            waste_kg >= thresholds.get('level2_kg', 0)):
            return 2, f"Critical fire level: {waste_percentage:.2f}% ({waste_kg:.2f}kg)"
        
        # Check level 1 (warning)
        if (waste_percentage >= thresholds.get('level1_percent', 0) or 
            waste_kg >= thresholds.get('level1_kg', 0)):
            return 1, f"Fire warning: {waste_percentage:.2f}% ({waste_kg:.2f}kg)"
        
        return 0, f"Normal fire level: {waste_percentage:.2f}% ({waste_kg:.2f}kg)"

class FireAnalytics:
    """Fire analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_fire_summary(self, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None,
                        product_type: Optional[str] = None) -> Dict:
        """Get fire summary statistics"""
        from ..models.production import DefectWaste, Lot
        from ..models.product import Product
        
        query = self.db.query(DefectWaste)
        
        if start_date:
            query = query.filter(DefectWaste.created_at >= start_date)
        if end_date:
            query = query.filter(DefectWaste.created_at <= end_date)
        
        fire_records = query.all()
        
        if not fire_records:
            return {
                'total_waste_kg': 0,
                'total_records': 0,
                'level1_count': 0,
                'level2_count': 0,
                'by_product_type': {},
                'by_reason': {},
                'trend': []
            }
        
        # Calculate totals
        total_waste_kg = sum(record.waste_kg for record in fire_records)
        level1_count = sum(1 for record in fire_records if record.level == 1)
        level2_count = sum(1 for record in fire_records if record.level == 2)
        
        # Group by product type
        by_product_type = {}
        for record in fire_records:
            # Get product type from context
            if record.context_type == 'lot':
                lot = self.db.query(Lot).filter(Lot.id == record.context_id).first()
                if lot and lot.production_job and lot.production_job.order_item:
                    product = lot.production_job.order_item.product
                    product_type = product.product_type
                    
                    if product_type not in by_product_type:
                        by_product_type[product_type] = {'count': 0, 'waste_kg': 0}
                    
                    by_product_type[product_type]['count'] += 1
                    by_product_type[product_type]['waste_kg'] += record.waste_kg
        
        # Group by reason
        by_reason = {}
        for record in fire_records:
            reason = record.reason_code or 'Unknown'
            if reason not in by_reason:
                by_reason[reason] = {'count': 0, 'waste_kg': 0}
            
            by_reason[reason]['count'] += 1
            by_reason[reason]['waste_kg'] += record.waste_kg
        
        # Calculate trend (last 30 days)
        trend = self._calculate_fire_trend()
        
        return {
            'total_waste_kg': float(total_waste_kg),
            'total_records': len(fire_records),
            'level1_count': level1_count,
            'level2_count': level2_count,
            'by_product_type': by_product_type,
            'by_reason': by_reason,
            'trend': trend
        }
    
    def _calculate_fire_trend(self) -> List[Dict]:
        """Calculate fire trend for last 30 days"""
        from ..models.production import DefectWaste
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Group by day
        daily_fire = {}
        
        fire_records = self.db.query(DefectWaste).filter(
            DefectWaste.created_at >= start_date,
            DefectWaste.created_at <= end_date
        ).all()
        
        for record in fire_records:
            date_key = record.created_at.date()
            if date_key not in daily_fire:
                daily_fire[date_key] = {'waste_kg': 0, 'count': 0}
            
            daily_fire[date_key]['waste_kg'] += record.waste_kg
            daily_fire[date_key]['count'] += 1
        
        # Convert to list sorted by date
        trend = []
        for date in sorted(daily_fire.keys()):
            trend.append({
                'date': date.isoformat(),
                'waste_kg': float(daily_fire[date]['waste_kg']),
                'count': daily_fire[date]['count']
            })
        
        return trend
    
    def get_operator_fire_performance(self, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[Dict]:
        """Get fire performance by operator"""
        from ..models.production import DefectWaste, Lot
        from ..models.user import User
        
        query = self.db.query(DefectWaste, Lot, User).join(
            Lot, DefectWaste.context_id == Lot.id
        ).join(
            User, Lot.operator_id == User.id
        )
        
        if start_date:
            query = query.filter(DefectWaste.created_at >= start_date)
        if end_date:
            query = query.filter(DefectWaste.created_at <= end_date)
        
        results = query.all()
        
        # Group by operator
        operator_stats = {}
        for fire_record, lot, user in results:
            if user.id not in operator_stats:
                operator_stats[user.id] = {
                    'user_id': user.id,
                    'user_name': user.full_name,
                    'department': user.department,
                    'total_waste_kg': 0,
                    'total_lots': 0,
                    'fire_count': 0,
                    'level1_count': 0,
                    'level2_count': 0
                }
            
            stats = operator_stats[user.id]
            stats['total_waste_kg'] += fire_record.waste_kg
            stats['fire_count'] += 1
            
            if fire_record.level == 1:
                stats['level1_count'] += 1
            elif fire_record.level == 2:
                stats['level2_count'] += 1
        
        # Calculate lot counts
        lot_counts = self.db.query(
            Lot.operator_id,
            func.count(Lot.id).label('lot_count')
        ).group_by(Lot.operator_id).all()
        
        for operator_id, lot_count in lot_counts:
            if operator_id in operator_stats:
                operator_stats[operator_id]['total_lots'] = lot_count
        
        # Convert to list and calculate percentages
        performance_list = []
        for stats in operator_stats.values():
            if stats['total_lots'] > 0:
                stats['fire_percentage'] = (stats['fire_count'] / stats['total_lots']) * 100
                stats['avg_waste_per_lot'] = stats['total_waste_kg'] / stats['total_lots']
            else:
                stats['fire_percentage'] = 0
                stats['avg_waste_per_lot'] = 0
            
            performance_list.append(stats)
        
        # Sort by fire percentage (ascending - lower is better)
        performance_list.sort(key=lambda x: x['fire_percentage'])
        
        return performance_list

class FireNotificationManager:
    """Manages fire notifications and alerts"""
    
    def __init__(self, db: Session):
        self.db = db
        self.threshold_manager = FireThresholdManager(db)
    
    def check_and_send_notifications(self, waste_record_id: int) -> bool:
        """Check fire levels and send notifications if needed"""
        from ..models.production import DefectWaste, Lot
        
        waste_record = self.db.query(DefectWaste).filter(DefectWaste.id == waste_record_id).first()
        if not waste_record:
            return False
        
        # Get lot information
        lot = None
        if waste_record.context_type == 'lot':
            lot = self.db.query(Lot).filter(Lot.id == waste_record.context_id).first()
        
        if not lot:
            return False
        
        # Get product type
        product_type = 'poset'  # default
        if lot.production_job and lot.production_job.order_item:
            product_type = lot.production_job.order_item.product.product_type
        
        # Check fire level
        total_kg = lot.planned_quantity or 0
        level, message = self.threshold_manager.check_fire_level(
            waste_record.waste_kg, total_kg, product_type
        )
        
        # Update waste record level
        waste_record.level = level
        self.db.commit()
        
        # Send notifications based on level
        if level >= 1:
            self._send_fire_notification(waste_record, lot, level, message)
        
        return True
    
    def _send_fire_notification(self, waste_record, lot, level: int, message: str):
        """Send fire notification to relevant users"""
        # This would integrate with notification system
        # For now, just log the notification
        
        notification_data = {
            'level': level,
            'message': message,
            'lot_id': lot.id,
            'lot_number': lot.lot_number,
            'operator': lot.operator.full_name if lot.operator else 'Unknown',
            'waste_kg': waste_record.waste_kg,
            'reason': waste_record.reason_code,
            'timestamp': waste_record.created_at.isoformat()
        }
        
        if level == 1:
            logger.warning(f"Fire Warning: {notification_data}")
        elif level == 2:
            logger.error(f"Fire Critical: {notification_data}")
        
        # TODO: Implement actual notification sending (email, SMS, web push)
        # - Send to admin and managers for level 1
        # - Send to all management for level 2
        # - Include photo if available
