from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateMachine:
    """Generic state machine implementation"""
    
    def __init__(self, states: List[str], transitions: Dict[str, List[str]]):
        self.states = states
        self.transitions = transitions
    
    def can_transition(self, current_state: str, target_state: str) -> bool:
        """Check if transition from current_state to target_state is allowed"""
        if current_state not in self.states or target_state not in self.states:
            return False
        
        allowed_transitions = self.transitions.get(current_state, [])
        return target_state in allowed_transitions
    
    def get_next_states(self, current_state: str) -> List[str]:
        """Get all possible next states from current state"""
        return self.transitions.get(current_state, [])

class OrderStateMachine(StateMachine):
    """Order state machine implementation"""
    
    def __init__(self):
        states = [
            'taslak', 'onayli', 'uretim_emri_verildi', 'uretimde', 
            'paketlemede', 'depoda', 'sevkiyata_hazir', 'sevkiyat_planlandi', 
            'teslim_edildi', 'kapatildi'
        ]
        
        transitions = {
            'taslak': ['onayli', 'kapatildi'],
            'onayli': ['uretim_emri_verildi', 'taslak'],
            'uretim_emri_verildi': ['uretimde', 'onayli'],
            'uretimde': ['paketlemede', 'uretim_emri_verildi'],
            'paketlemede': ['depoda', 'uretimde'],
            'depoda': ['sevkiyata_hazir', 'paketlemede'],
            'sevkiyata_hazir': ['sevkiyat_planlandi', 'depoda'],
            'sevkiyat_planlandi': ['teslim_edildi', 'sevkiyata_hazir'],
            'teslim_edildi': ['kapatildi'],
            'kapatildi': []
        }
        
        super().__init__(states, transitions)

class LotStateMachine(StateMachine):
    """Lot state machine implementation"""
    
    def __init__(self):
        states = [
            'olusturuldu', 'uretimde', 'uretim_bitti', 'paketlemede', 
            'depoda', 'sevkiyata_hazir'
        ]
        
        transitions = {
            'olusturuldu': ['uretimde'],
            'uretimde': ['uretim_bitti', 'olusturuldu'],
            'uretim_bitti': ['paketlemede'],
            'paketlemede': ['depoda', 'uretim_bitti'],
            'depoda': ['sevkiyata_hazir', 'paketlemede'],
            'sevkiyata_hazir': []
        }
        
        super().__init__(states, transitions)

class PackageStateMachine(StateMachine):
    """Package state machine implementation"""
    
    def __init__(self):
        states = [
            'olusturuldu', 'depo_kabul_bekliyor', 'depoya_alindi', 'sevkiyata_hazir'
        ]
        
        transitions = {
            'olusturuldu': ['depo_kabul_bekliyor'],
            'depo_kabul_bekliyor': ['depoya_alindi', 'olusturuldu'],
            'depoya_alindi': ['sevkiyata_hazir'],
            'sevkiyata_hazir': []
        }
        
        super().__init__(states, transitions)

class ShipmentStateMachine(StateMachine):
    """Shipment state machine implementation"""
    
    def __init__(self):
        states = [
            'planlandi', 'yuklendi', 'teslimde', 'teslim_edildi'
        ]
        
        transitions = {
            'planlandi': ['yuklendi'],
            'yuklendi': ['teslimde', 'planlandi'],
            'teslimde': ['teslim_edildi', 'yuklendi'],
            'teslim_edildi': []
        }
        
        super().__init__(states, transitions)

class StateTransitionManager:
    """Manages state transitions with logging and validation"""
    
    def __init__(self):
        self.order_sm = OrderStateMachine()
        self.lot_sm = LotStateMachine()
        self.package_sm = PackageStateMachine()
        self.shipment_sm = ShipmentStateMachine()
    
    def transition_order(self, db: Session, order_id: int, new_status: str, 
                        user_id: int, notes: Optional[str] = None, 
                        ip_address: Optional[str] = None) -> bool:
        """Transition order to new status"""
        from ..models.order import Order
        from ..models.audit_log import AuditLog
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return False
        
        if not self.order_sm.can_transition(order.status, new_status):
            logger.error(f"Invalid transition from {order.status} to {new_status}")
            return False
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Log the transition
        audit_log = AuditLog(
            user_id=user_id,
            module='orders',
            action='status_change',
            old_values={'status': old_status},
            new_values={'status': new_status},
            ip_address=ip_address
        )
        db.add(audit_log)
        
        try:
            db.commit()
            logger.info(f"Order {order_id} transitioned from {old_status} to {new_status}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to transition order {order_id}: {str(e)}")
            return False
    
    def transition_lot(self, db: Session, lot_id: int, new_status: str, 
                      user_id: int, notes: Optional[str] = None, 
                      photo_ref: Optional[str] = None, 
                      ip_address: Optional[str] = None) -> bool:
        """Transition lot to new status"""
        from ..models.production import Lot, LotLog
        
        lot = db.query(Lot).filter(Lot.id == lot_id).first()
        if not lot:
            logger.error(f"Lot {lot_id} not found")
            return False
        
        if not self.lot_sm.can_transition(lot.status, new_status):
            logger.error(f"Invalid transition from {lot.status} to {new_status}")
            return False
        
        old_status = lot.status
        lot.status = new_status
        lot.updated_at = datetime.utcnow()
        
        # Log the transition
        lot_log = LotLog(
            lot_id=lot_id,
            event_type='status_change',
            user_id=user_id,
            description=f"Status changed from {old_status} to {new_status}",
            photo_ref=photo_ref,
            meta_data={'old_status': old_status, 'new_status': new_status},
            ip_address=ip_address
        )
        db.add(lot_log)
        
        try:
            db.commit()
            logger.info(f"Lot {lot_id} transitioned from {old_status} to {new_status}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to transition lot {lot_id}: {str(e)}")
            return False
    
    def transition_package(self, db: Session, package_id: int, new_status: str, 
                          user_id: int, notes: Optional[str] = None, 
                          photo_ref: Optional[str] = None, 
                          ip_address: Optional[str] = None) -> bool:
        """Transition package to new status"""
        from ..models.production import Packaging
        from ..models.audit_log import AuditLog
        
        package = db.query(Packaging).filter(Packaging.id == package_id).first()
        if not package:
            logger.error(f"Package {package_id} not found")
            return False
        
        if not self.package_sm.can_transition(package.status, new_status):
            logger.error(f"Invalid transition from {package.status} to {new_status}")
            return False
        
        old_status = package.status
        package.status = new_status
        
        # Log the transition
        audit_log = AuditLog(
            user_id=user_id,
            module='packaging',
            action='status_change',
            old_values={'status': old_status},
            new_values={'status': new_status},
            ip_address=ip_address
        )
        db.add(audit_log)
        
        try:
            db.commit()
            logger.info(f"Package {package_id} transitioned from {old_status} to {new_status}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to transition package {package_id}: {str(e)}")
            return False
    
    def transition_shipment(self, db: Session, shipment_id: int, new_status: str, 
                           user_id: int, notes: Optional[str] = None, 
                           ip_address: Optional[str] = None) -> bool:
        """Transition shipment to new status"""
        from ..models.shipment import Shipment
        from ..models.audit_log import AuditLog
        
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            logger.error(f"Shipment {shipment_id} not found")
            return False
        
        if not self.shipment_sm.can_transition(shipment.status, new_status):
            logger.error(f"Invalid transition from {shipment.status} to {new_status}")
            return False
        
        old_status = shipment.status
        shipment.status = new_status
        shipment.updated_at = datetime.utcnow()
        
        # Log the transition
        audit_log = AuditLog(
            user_id=user_id,
            module='shipments',
            action='status_change',
            old_values={'status': old_status},
            new_values={'status': new_status},
            ip_address=ip_address
        )
        db.add(audit_log)
        
        try:
            db.commit()
            logger.info(f"Shipment {shipment_id} transitioned from {old_status} to {new_status}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to transition shipment {shipment_id}: {str(e)}")
            return False

# Global state transition manager instance
state_manager = StateTransitionManager()
