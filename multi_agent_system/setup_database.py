"""
Database Setup and Initialization Script for Multi-Agent Hospital System
Creates tables and populates with realistic hospital data
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, time
from typing import List
import random

from database.config import db_manager, init_database
from database.models import (
    Department, Bed, Patient, StaffMember, MedicalEquipment, 
    BedStatus, BedType, PatientAcuity, StaffRole, StaffStatus,
    EquipmentType, EquipmentStatus, ShiftType
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HospitalDataInitializer:
    """Initialize hospital database with realistic data"""
    
    def __init__(self):
        self.departments = []
        self.beds = []
        self.patients = []
        self.staff = []
        self.equipment = []
    
    async def initialize_complete_system(self):
        """Initialize the complete hospital system"""
        logger.info("🏥 Initializing Multi-Agent Hospital System Database...")
        
        # Initialize database
        await init_database()
        
        # Create sample data
        await self.create_departments()
        await self.create_beds()
        await self.create_patients()
        await self.create_staff()
        await self.create_equipment()
        
        logger.info("✅ Multi-Agent Hospital System Database initialized successfully!")
    
    async def create_departments(self):
        """Create hospital departments"""
        logger.info("🏢 Creating departments...")
        
        departments_data = [
            {"name": "Emergency Department", "code": "ED", "floor": 1, "capacity": 20},
            {"name": "Intensive Care Unit", "code": "ICU", "floor": 3, "capacity": 12},
            {"name": "General Medicine", "code": "MED", "floor": 2, "capacity": 30},
            {"name": "Surgery", "code": "SURG", "floor": 4, "capacity": 8},
            {"name": "Pediatrics", "code": "PEDS", "floor": 2, "capacity": 15},
            {"name": "Maternity", "code": "MAT", "floor": 5, "capacity": 10},
            {"name": "Cardiology", "code": "CARD", "floor": 3, "capacity": 12},
            {"name": "Oncology", "code": "ONCO", "floor": 6, "capacity": 20}
        ]
        
        async with db_manager.get_async_session() as session:
            for dept_data in departments_data:
                department = Department(
                    id=str(uuid.uuid4()),
                    name=dept_data["name"],
                    code=dept_data["code"],
                    floor=dept_data["floor"],
                    capacity=dept_data["capacity"],
                    specialties=[]
                )
                session.add(department)
                self.departments.append(department)
            
            await session.commit()
        
        logger.info(f"✅ Created {len(departments_data)} departments")
    
    async def create_beds(self):
        """Create hospital beds across departments"""
        logger.info("🛏️ Creating beds...")
        
        bed_types_by_dept = {
            "ED": [BedType.STANDARD] * 15 + [BedType.ISOLATION] * 5,
            "ICU": [BedType.ICU] * 10 + [BedType.ISOLATION] * 2,
            "MED": [BedType.STANDARD] * 25 + [BedType.ISOLATION] * 5,
            "SURG": [BedType.STANDARD] * 6 + [BedType.ICU] * 2,
            "PEDS": [BedType.PEDIATRIC] * 12 + [BedType.ISOLATION] * 3,
            "MAT": [BedType.MATERNITY] * 8 + [BedType.STANDARD] * 2,
            "CARD": [BedType.TELEMETRY] * 8 + [BedType.ICU] * 4,
            "ONCO": [BedType.STANDARD] * 15 + [BedType.ISOLATION] * 5
        }
        
        async with db_manager.get_async_session() as session:
            for department in self.departments:
                bed_types = bed_types_by_dept.get(department.code, [BedType.STANDARD] * 10)
                
                for i, bed_type in enumerate(bed_types, 1):
                    # Realistic bed status distribution
                    status_weights = [
                        (BedStatus.AVAILABLE, 0.3),
                        (BedStatus.OCCUPIED, 0.6),
                        (BedStatus.CLEANING, 0.05),
                        (BedStatus.MAINTENANCE, 0.03),
                        (BedStatus.BLOCKED, 0.02)
                    ]
                    status = random.choices(
                        [s[0] for s in status_weights],
                        weights=[s[1] for s in status_weights]
                    )[0]
                    
                    bed = Bed(
                        id=str(uuid.uuid4()),
                        number=f"{department.code}-{i:03d}",
                        department_id=department.id,
                        room_number=f"{department.floor}{i:02d}",
                        bed_type=bed_type,
                        status=status,
                        is_isolation_capable=(bed_type == BedType.ISOLATION),
                        is_bariatric=(bed_type == BedType.BARIATRIC),
                        has_telemetry=(bed_type in [BedType.TELEMETRY, BedType.ICU]),
                        last_cleaned=datetime.now() - timedelta(hours=random.randint(1, 24)),
                        last_maintenance=datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    session.add(bed)
                    self.beds.append(bed)
            
            await session.commit()
        
        logger.info(f"✅ Created {len(self.beds)} beds across departments")
    
    async def create_patients(self):
        """Create patient records"""
        logger.info("👥 Creating patients...")
        
        patient_names = [
            "John Smith", "Mary Johnson", "Robert Brown", "Patricia Davis",
            "Michael Wilson", "Linda Moore", "William Taylor", "Elizabeth Anderson",
            "David Thomas", "Barbara Jackson", "Richard White", "Susan Harris",
            "Joseph Martin", "Jessica Thompson", "Thomas Garcia", "Sarah Martinez"
        ]
        
        diagnoses = [
            "Acute myocardial infarction", "Pneumonia", "Diabetes mellitus",
            "Hypertension", "Heart failure", "COPD", "Stroke", "Sepsis",
            "Post-operative monitoring", "Chest pain", "Abdominal pain",
            "Respiratory failure", "Chronic kidney disease", "Cancer treatment"
        ]
        
        async with db_manager.get_async_session() as session:
            # Create patients for occupied beds
            occupied_beds = [bed for bed in self.beds if bed.status == BedStatus.OCCUPIED]
            
            for i, bed in enumerate(occupied_beds[:len(patient_names)]):
                patient = Patient(
                    id=str(uuid.uuid4()),
                    mrn=f"MRN{1000000 + i}",
                    name=patient_names[i],
                    date_of_birth=datetime.now() - timedelta(days=random.randint(18*365, 85*365)),
                    gender=random.choice(["Male", "Female"]),
                    acuity_level=random.choice(list(PatientAcuity)),
                    admission_date=datetime.now() - timedelta(days=random.randint(0, 7)),
                    primary_diagnosis=random.choice(diagnoses),
                    isolation_required=random.choice([True, False]) if random.random() < 0.1 else False,
                    allergies=["NKDA"] if random.random() < 0.7 else ["Penicillin", "Latex"],
                    special_needs=[]
                )
                session.add(patient)
                self.patients.append(patient)
                
                # Link patient to bed
                bed.current_patient_id = patient.id
            
            # Create some patients without beds (waiting for admission)
            for i in range(5):
                patient = Patient(
                    id=str(uuid.uuid4()),
                    mrn=f"MRN{2000000 + i}",
                    name=f"Waiting Patient {i+1}",
                    date_of_birth=datetime.now() - timedelta(days=random.randint(18*365, 85*365)),
                    gender=random.choice(["Male", "Female"]),
                    acuity_level=random.choice(list(PatientAcuity)),
                    admission_date=datetime.now(),
                    primary_diagnosis=random.choice(diagnoses),
                    isolation_required=False
                )
                session.add(patient)
                self.patients.append(patient)
            
            await session.commit()
        
        logger.info(f"✅ Created {len(self.patients)} patients")
    
    async def create_staff(self):
        """Create staff members"""
        logger.info("👨‍⚕️ Creating staff members...")
        
        staff_names = [
            "Dr. Sarah Connor", "Nurse John Doe", "Dr. Emily White", "Tech Mike Brown",
            "Nurse Lisa Garcia", "Dr. James Wilson", "Nurse Anna Martinez", "Tech David Lee",
            "Dr. Maria Rodriguez", "Nurse Kevin Johnson", "Dr. Robert Kim", "Nurse Amy Taylor",
            "Tech Jennifer Davis", "Dr. Steven Chang", "Nurse Michelle Thompson", "Tech Brian Anderson"
        ]
        
        roles_by_name = {
            "Dr.": StaffRole.DOCTOR,
            "Nurse": StaffRole.NURSE,
            "Tech": StaffRole.TECHNICIAN
        }
        
        async with db_manager.get_async_session() as session:
            for i, name in enumerate(staff_names):
                role_prefix = name.split()[0]
                role = roles_by_name.get(role_prefix, StaffRole.NURSE)
                
                # Assign to departments
                department = random.choice(self.departments)
                
                # Realistic staff status
                status_weights = [
                    (StaffStatus.ON_DUTY, 0.6),
                    (StaffStatus.AVAILABLE, 0.2),
                    (StaffStatus.BREAK, 0.1),
                    (StaffStatus.OFF_DUTY, 0.1)
                ]
                status = random.choices(
                    [s[0] for s in status_weights],
                    weights=[s[1] for s in status_weights]
                )[0]
                
                staff = StaffMember(
                    id=str(uuid.uuid4()),
                    employee_id=f"EMP{10000 + i}",
                    name=name,
                    email=f"{name.lower().replace(' ', '.').replace('dr.', '')}@hospital.com",
                    role=role,
                    department_id=department.id,
                    specialties=[] if role != StaffRole.DOCTOR else [department.name],
                    skill_level=random.randint(1, 5),
                    certifications=["BLS", "ACLS"] if role == StaffRole.NURSE else [],
                    license_number=f"LIC{20000 + i}" if role == StaffRole.DOCTOR else None,
                    license_expiry=datetime.now() + timedelta(days=365) if role == StaffRole.DOCTOR else None,
                    hire_date=datetime.now() - timedelta(days=random.randint(30, 1095)),
                    status=status,
                    max_patients=6 if role == StaffRole.NURSE else 12 if role == StaffRole.DOCTOR else 0,
                    phone=f"555-{random.randint(1000, 9999)}"
                )
                session.add(staff)
                self.staff.append(staff)
            
            await session.commit()
        
        logger.info(f"✅ Created {len(self.staff)} staff members")
    
    async def create_equipment(self):
        """Create medical equipment"""
        logger.info("🏥 Creating medical equipment...")
        
        equipment_data = [
            {"name": "Ventilator", "type": EquipmentType.VENTILATOR, "count": 15},
            {"name": "IV Pump", "type": EquipmentType.IV_PUMP, "count": 50},
            {"name": "Patient Monitor", "type": EquipmentType.MONITOR, "count": 80},
            {"name": "Defibrillator", "type": EquipmentType.DEFIBRILLATOR, "count": 12},
            {"name": "Wheelchair", "type": EquipmentType.WHEELCHAIR, "count": 30},
            {"name": "Transport Bed", "type": EquipmentType.TRANSPORT_BED, "count": 20},
            {"name": "Dialysis Machine", "type": EquipmentType.DIALYSIS, "count": 8},
            {"name": "Ultrasound", "type": EquipmentType.ULTRASOUND, "count": 6}
        ]
        
        async with db_manager.get_async_session() as session:
            for eq_data in equipment_data:
                for i in range(eq_data["count"]):
                    # Realistic equipment status
                    status_weights = [
                        (EquipmentStatus.AVAILABLE, 0.4),
                        (EquipmentStatus.IN_USE, 0.45),
                        (EquipmentStatus.MAINTENANCE, 0.05),
                        (EquipmentStatus.BROKEN, 0.03),
                        (EquipmentStatus.CLEANING, 0.07)
                    ]
                    status = random.choices(
                        [s[0] for s in status_weights],
                        weights=[s[1] for s in status_weights]
                    )[0]
                    
                    # Assign to random department
                    department = random.choice(self.departments)
                    
                    equipment = MedicalEquipment(
                        id=str(uuid.uuid4()),
                        asset_tag=f"{eq_data['type'].value.upper()}{1000 + i:03d}",
                        name=f"{eq_data['name']} #{i+1}",
                        equipment_type=eq_data["type"],
                        manufacturer=random.choice(["Philips", "GE Healthcare", "Siemens", "Medtronic"]),
                        model=f"Model-{random.randint(100, 999)}",
                        serial_number=f"SN{random.randint(100000, 999999)}",
                        status=status,
                        location_type="department",
                        current_location_id=department.id,
                        department_id=department.id,
                        purchase_date=datetime.now() - timedelta(days=random.randint(365, 2555)),
                        last_maintenance=datetime.now() - timedelta(days=random.randint(1, 90)),
                        next_maintenance=datetime.now() + timedelta(days=random.randint(30, 365)),
                        maintenance_interval_days=365,
                        warranty_expiry=datetime.now() + timedelta(days=random.randint(30, 730)),
                        is_portable=eq_data["type"] in [EquipmentType.IV_PUMP, EquipmentType.WHEELCHAIR, EquipmentType.TRANSPORT_BED],
                        requires_certification=eq_data["type"] in [EquipmentType.VENTILATOR, EquipmentType.DIALYSIS],
                        cost=random.randint(1000, 50000)
                    )
                    session.add(equipment)
                    self.equipment.append(equipment)
            
            await session.commit()
        
        logger.info(f"✅ Created {len(self.equipment)} pieces of medical equipment")
    
    async def print_system_summary(self):
        """Print summary of created system"""
        logger.info("\n" + "="*60)
        logger.info("🏥 MULTI-AGENT HOSPITAL SYSTEM SUMMARY")
        logger.info("="*60)
        logger.info(f"📊 Departments: {len(self.departments)}")
        logger.info(f"🛏️ Beds: {len(self.beds)}")
        logger.info(f"👥 Patients: {len(self.patients)}")
        logger.info(f"👨‍⚕️ Staff: {len(self.staff)}")
        logger.info(f"🏥 Equipment: {len(self.equipment)}")
        logger.info("="*60)
        
        # Bed status summary
        bed_status_counts = {}
        for bed in self.beds:
            status = bed.status.value
            bed_status_counts[status] = bed_status_counts.get(status, 0) + 1
        
        logger.info("🛏️ BED STATUS DISTRIBUTION:")
        for status, count in bed_status_counts.items():
            logger.info(f"   {status}: {count}")
        
        # Equipment status summary
        equipment_status_counts = {}
        for eq in self.equipment:
            status = eq.status.value
            equipment_status_counts[status] = equipment_status_counts.get(status, 0) + 1
        
        logger.info("🏥 EQUIPMENT STATUS DISTRIBUTION:")
        for status, count in equipment_status_counts.items():
            logger.info(f"   {status}: {count}")
        
        logger.info("="*60)
        logger.info("✅ System ready for multi-agent operations!")
        logger.info("="*60)

async def main():
    """Main initialization function"""
    initializer = HospitalDataInitializer()
    await initializer.initialize_complete_system()
    await initializer.print_system_summary()

if __name__ == "__main__":
    asyncio.run(main())
