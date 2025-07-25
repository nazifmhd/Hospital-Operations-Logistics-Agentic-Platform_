#!/usr/bin/env python3
"""
Comprehensive Hospital Data Seeder for Multi-Agent System
Seeds the database with realistic hospital data for frontend testing
"""
import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the multi_agent_system directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "multi_agent_system"))

from database.config import db_manager
from database.models import (
    Base, Department, StaffMember, StaffRole, StaffStatus, ShiftType,
    Bed, BedType, BedStatus, MedicalEquipment, EquipmentType, EquipmentStatus,
    SupplyItem, SupplyCategory, SupplyStatus, InventoryLocation,
    Patient, PatientAcuity, Supplier
)
from sqlalchemy import text

class ProfessionalHospitalSeeder:
    """Professional hospital data seeder for the multi-agent system"""
    
    def __init__(self):
        self.departments = []
        self.staff_members = []
        self.beds = []
        self.equipment = []
        self.supplies = []
        self.suppliers = []
        self.patients = []
        print("🏥 Hospital Data Seeder Initialized")
    
    async def seed_comprehensive_data(self):
        """Seed comprehensive hospital data"""
        print("🚀 Starting Comprehensive Hospital Data Seeding...")
        print("=" * 60)
        
        # Initialize database
        db_manager.initialize()
        
        async with db_manager.get_async_session() as session:
            try:
                # Check existing data first
                should_seed = await self._clear_existing_data(session)
                
                if not should_seed:
                    print("\n" + "=" * 60)
                    print("✅ Hospital Database Already Contains Data!")
                    await self._print_existing_summary(session)
                    return
                
                # Seed data in dependency order
                await self._seed_departments(session)
                await self._seed_suppliers(session)
                await self._seed_staff_members(session)
                await self._seed_beds(session)
                await self._seed_equipment(session)
                await self._seed_supplies(session)
                await self._seed_patients(session)
                
                await session.commit()
                print("\n" + "=" * 60)
                print("✅ Comprehensive Hospital Data Seeding Complete!")
                await self._print_summary()
                
            except Exception as e:
                print(f"❌ Error during seeding: {e}")
                await session.rollback()
                raise
    
    async def _clear_existing_data(self, session):
        """Clear existing data to avoid conflicts"""
        print("🧹 Checking for existing data...")
        
        try:
            # Check if departments exist
            result = await session.execute(text("SELECT COUNT(*) FROM departments"))
            dept_count = result.scalar()
            
            if dept_count > 0:
                print(f"Found {dept_count} existing departments. Skipping seeding to avoid conflicts.")
                print("✅ Database already contains data - using existing data")
                return False  # Indicate that we should skip seeding
            else:
                print("✅ Database is empty - proceeding with seeding")
                return True  # Indicate that we can proceed with seeding
            
        except Exception as e:
            print(f"⚠️ Error checking existing data: {e}")
            return True  # Proceed anyway
    
    async def _seed_departments(self, session):
        """Seed hospital departments"""
        print("\n🏢 Seeding Departments...")
        
        departments_data = [
            {"id": "dept_icu", "name": "Intensive Care Unit", "code": "ICU", "floor": 4, "capacity": 40},
            {"id": "dept_ccu", "name": "Cardiac Care Unit", "code": "CCU", "floor": 4, "capacity": 20},
            {"id": "dept_emergency", "name": "Emergency Department", "code": "ED", "floor": 1, "capacity": 50},
            {"id": "dept_surgery", "name": "Surgical Department", "code": "SURG", "floor": 3, "capacity": 15},
            {"id": "dept_medical", "name": "Medical Ward", "code": "MED", "floor": 2, "capacity": 80},
            {"id": "dept_pediatric", "name": "Pediatric Ward", "code": "PEDS", "floor": 5, "capacity": 30},
            {"id": "dept_maternity", "name": "Maternity Ward", "code": "MAT", "floor": 6, "capacity": 25},
            {"id": "dept_neurology", "name": "Neurology Ward", "code": "NEURO", "floor": 4, "capacity": 22},
        ]
        
        for dept_data in departments_data:
            department = Department(
                id=dept_data["id"],
                name=dept_data["name"],
                code=dept_data["code"],
                floor=dept_data["floor"],
                building="Main Hospital",
                capacity=dept_data["capacity"],
                is_active=True,
                specialties=[dept_data["name"].split()[0].lower()],
                created_at=datetime.now()
            )
            session.add(department)
            self.departments.append(department)
            print(f"  ✓ Added {dept_data['name']}")
        
        await session.flush()
        print(f"✅ Seeded {len(self.departments)} departments")
    
    async def _seed_suppliers(self, session):
        """Seed suppliers"""
        print("\n🏭 Seeding Suppliers...")
        
        suppliers_data = [
            {"name": "MedSupply Corp", "contact": "John Smith", "email": "john@medsupply.com", "phone": "555-0101"},
            {"name": "Pharma Plus", "contact": "Sarah Johnson", "email": "sarah@pharmaplus.com", "phone": "555-0102"},
            {"name": "Surgical Solutions", "contact": "Mike Wilson", "email": "mike@surgsol.com", "phone": "555-0103"},
            {"name": "EquipMed Technologies", "contact": "Lisa Brown", "email": "lisa@equipmed.com", "phone": "555-0104"},
        ]
        
        for i, supplier_data in enumerate(suppliers_data):
            supplier = Supplier(
                id=f"supplier_{i+1:03d}",
                name=supplier_data["name"],
                contact_name=supplier_data["contact"],
                email=supplier_data["email"],
                phone=supplier_data["phone"],
                address={
                    "street": f"{random.randint(100, 9999)} Medical Plaza",
                    "city": "Healthcare City",
                    "state": "HC",
                    "zip": f"{random.randint(10000, 99999)}"
                },
                payment_terms="Net 30",
                lead_time_days=random.randint(3, 14),
                preferred_supplier=i < 2,  # First 2 are preferred
                quality_rating=round(random.uniform(4.0, 5.0), 1),
                delivery_rating=round(random.uniform(4.0, 5.0), 1),
                price_rating=round(random.uniform(3.5, 5.0), 1),
                is_active=True
            )
            session.add(supplier)
            self.suppliers.append(supplier)
            print(f"  ✓ Added {supplier_data['name']}")
        
        await session.flush()
        print(f"✅ Seeded {len(self.suppliers)} suppliers")
    
    async def _seed_staff_members(self, session):
        """Seed staff members"""
        print("\n👥 Seeding Staff Members...")
        
        # ICU Staff
        icu_staff = [
            ("Dr. Sarah Martinez", StaffRole.DOCTOR, "Intensivist"),
            ("Dr. James Chen", StaffRole.DOCTOR, "Critical Care"),
            ("Nurse Emily Rodriguez", StaffRole.NURSE, "ICU RN"),
            ("Nurse Michael Thompson", StaffRole.NURSE, "ICU RN"),
            ("Nurse Lisa Parker", StaffRole.NURSE, "ICU RN"),
            ("Nurse David Kim", StaffRole.NURSE, "ICU RN"),
            ("Nurse Amanda Wilson", StaffRole.NURSE, "ICU RN"),
            ("Nurse Robert Garcia", StaffRole.NURSE, "ICU RN"),
            ("Tech John Davis", StaffRole.TECHNICIAN, "Respiratory"),
            ("Tech Maria Lopez", StaffRole.TECHNICIAN, "Biomedical"),
        ]
        
        # Emergency Department Staff
        ed_staff = [
            ("Dr. Jennifer Adams", StaffRole.DOCTOR, "Emergency Medicine"),
            ("Dr. Mark Thompson", StaffRole.DOCTOR, "Emergency Medicine"),
            ("Dr. Ashley Brown", StaffRole.DOCTOR, "Emergency Medicine"),
            ("Nurse Kelly Johnson", StaffRole.NURSE, "ED RN"),
            ("Nurse Brian Wilson", StaffRole.NURSE, "ED RN"),
            ("Nurse Rachel Lee", StaffRole.NURSE, "ED RN"),
            ("Nurse Christopher Moore", StaffRole.NURSE, "ED RN"),
            ("Nurse Jessica Taylor", StaffRole.NURSE, "ED RN"),
            ("Nurse Anthony Martinez", StaffRole.NURSE, "ED RN"),
            ("Nurse Stephanie Davis", StaffRole.NURSE, "ED RN"),
            ("Nurse Kevin Rodriguez", StaffRole.NURSE, "ED RN"),
            ("Nurse Nicole Anderson", StaffRole.NURSE, "ED RN"),
            ("Tech Alex Johnson", StaffRole.TECHNICIAN, "Radiology"),
            ("Tech Samantha White", StaffRole.TECHNICIAN, "Lab"),
        ]
        
        # Medical Ward Staff
        medical_staff = [
            ("Dr. William Johnson", StaffRole.DOCTOR, "Internal Medicine"),
            ("Dr. Patricia Lee", StaffRole.DOCTOR, "Internal Medicine"),
            ("Dr. Thomas Wilson", StaffRole.DOCTOR, "Hospitalist"),
            ("Nurse Jennifer Martinez", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Daniel Garcia", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Michelle Brown", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Timothy Davis", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Laura Rodriguez", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Jonathan Miller", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Rebecca Wilson", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Joshua Anderson", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Amy Thompson", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Matthew Taylor", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Elizabeth Moore", StaffRole.NURSE, "Med-Surg RN"),
            ("Nurse Andrew Jackson", StaffRole.NURSE, "Med-Surg RN"),
        ]
        
        # Surgical Staff
        surgical_staff = [
            ("Dr. Richard Martinez", StaffRole.DOCTOR, "General Surgery"),
            ("Dr. Catherine Wilson", StaffRole.DOCTOR, "Orthopedic Surgery"),
            ("Dr. Steven Garcia", StaffRole.DOCTOR, "Neurosurgery"),
            ("Nurse Operating Room", StaffRole.NURSE, "OR RN"),
            ("Nurse Surgery Center", StaffRole.NURSE, "OR RN"),
            ("Tech Surgical", StaffRole.TECHNICIAN, "Surgical Tech"),
        ]
        
        # Other departments
        other_staff = [
            ("Dr. Mary Johnson", StaffRole.DOCTOR, "Pediatrics"),
            ("Dr. Joseph Brown", StaffRole.DOCTOR, "Cardiology"),
            ("Dr. Linda Davis", StaffRole.DOCTOR, "Neurology"),
            ("Dr. Helen Rodriguez", StaffRole.DOCTOR, "OB/GYN"),
            ("Nurse Pediatric", StaffRole.NURSE, "Pediatric RN"),
            ("Nurse Cardiac", StaffRole.NURSE, "Cardiac RN"),
            ("Nurse Maternity", StaffRole.NURSE, "L&D RN"),
            ("Nurse Neurology", StaffRole.NURSE, "Neuro RN"),
        ]
        
        all_staff = icu_staff + ed_staff + medical_staff + surgical_staff + other_staff
        
        for i, (name, role, specialty) in enumerate(all_staff):
            # Assign to appropriate department
            if "ICU" in specialty or "Critical Care" in specialty or "Intensivist" in specialty:
                dept_id = "dept_icu"
            elif "Emergency" in specialty or "ED" in specialty:
                dept_id = "dept_emergency"
            elif "Surgery" in specialty or "OR" in specialty:
                dept_id = "dept_surgery"
            elif "Pediatric" in specialty:
                dept_id = "dept_pediatric"
            elif "Cardiac" in specialty or "CCU" in specialty:
                dept_id = "dept_ccu"
            elif "Neurology" in specialty or "Neuro" in specialty:
                dept_id = "dept_neurology"
            elif "OB/GYN" in specialty or "L&D" in specialty or "Maternity" in specialty:
                dept_id = "dept_maternity"
            else:
                dept_id = "dept_medical"
            
            staff = StaffMember(
                id=f"staff_{i+1:03d}",
                employee_id=f"EMP{i+1:05d}",
                name=name,
                role=role,
                department_id=dept_id,
                specialties=[specialty],
                skill_level=random.randint(2, 5),
                status=random.choice([StaffStatus.AVAILABLE, StaffStatus.ON_DUTY]),
                email=f"{name.lower().replace(' ', '.').replace('dr.', '').replace('nurse', '').replace('tech', '').strip('.')}@hospital.com",
                phone=f"555-{random.randint(1000, 9999)}",
                hire_date=datetime.now() - timedelta(days=random.randint(30, 1825)),
                is_active=True,
                certifications=[specialty, "BLS", "ACLS"] if role == StaffRole.DOCTOR else [specialty, "BLS"],
                max_patients=random.randint(4, 8) if role == StaffRole.NURSE else random.randint(8, 15)
            )
            session.add(staff)
            self.staff_members.append(staff)
        
        await session.flush()
        print(f"✅ Seeded {len(self.staff_members)} staff members")
    
    async def _seed_beds(self, session):
        """Seed hospital beds"""
        print("\n🛏️ Seeding Beds...")
        
        bed_configs = [
            ("dept_icu", BedType.ICU, 40, True, True),
            ("dept_ccu", BedType.ICU, 20, True, True),
            ("dept_emergency", BedType.STANDARD, 50, False, False),
            ("dept_surgery", BedType.STANDARD, 15, False, False),
            ("dept_medical", BedType.STANDARD, 80, False, False),
            ("dept_pediatric", BedType.PEDIATRIC, 30, True, False),
            ("dept_maternity", BedType.MATERNITY, 25, True, False),
            ("dept_neurology", BedType.TELEMETRY, 22, False, True),
        ]
        
        bed_counter = 1
        for dept_id, bed_type, count, isolation_capable, has_telemetry in bed_configs:
            dept_name = next(d.name for d in self.departments if d.id == dept_id)
            
            for i in range(count):
                room_num = f"{bed_counter // 10 + 1:02d}{(bed_counter % 10) + 1:02d}"
                bed_num = f"{bed_counter:03d}"
                
                # Some beds are occupied, some available
                status = random.choices(
                    [BedStatus.AVAILABLE, BedStatus.OCCUPIED, BedStatus.CLEANING],
                    weights=[60, 30, 10]
                )[0]
                
                bed = Bed(
                    id=f"bed_{bed_num}",
                    number=bed_num,
                    department_id=dept_id,
                    room_number=room_num,
                    bed_type=bed_type,
                    status=status,
                    is_isolation_capable=isolation_capable,
                    is_bariatric=random.random() < 0.1,  # 10% bariatric capable
                    has_telemetry=has_telemetry,
                    last_cleaned=datetime.now() - timedelta(hours=random.randint(1, 24)),
                    last_maintenance=datetime.now() - timedelta(days=random.randint(1, 30)),
                    notes="Standard hospital bed" if random.random() > 0.3 else None
                )
                session.add(bed)
                self.beds.append(bed)
                bed_counter += 1
            
            print(f"  ✓ Added {count} beds to {dept_name}")
        
        await session.flush()
        print(f"✅ Seeded {len(self.beds)} beds")
    
    async def _seed_equipment(self, session):
        """Seed medical equipment"""
        print("\n🔧 Seeding Medical Equipment...")
        
        equipment_types = [
            (EquipmentType.VENTILATOR, "dept_icu", 25),
            (EquipmentType.IV_PUMP, "dept_icu", 40),
            (EquipmentType.MONITOR, "dept_icu", 40),
            (EquipmentType.DEFIBRILLATOR, "dept_emergency", 8),
            (EquipmentType.WHEELCHAIR, "dept_medical", 30),
            (EquipmentType.TRANSPORT_BED, "dept_emergency", 15),
            (EquipmentType.DIALYSIS, "dept_icu", 5),
            (EquipmentType.ULTRASOUND, "dept_emergency", 3),
        ]
        
        equipment_counter = 1
        for equipment_type, dept_id, count in equipment_types:
            dept_name = next(d.name for d in self.departments if d.id == dept_id)
            
            for i in range(count):
                status = random.choices(
                    [EquipmentStatus.AVAILABLE, EquipmentStatus.IN_USE, EquipmentStatus.MAINTENANCE],
                    weights=[70, 25, 5]
                )[0]
                
                equipment = MedicalEquipment(
                    id=f"equip_{equipment_counter:03d}",
                    asset_tag=f"ASSET{equipment_counter:05d}",
                    name=f"{equipment_type.value.replace('_', ' ').title()} #{equipment_counter}",
                    equipment_type=equipment_type,
                    manufacturer=random.choice(["Philips", "GE Healthcare", "Medtronic", "Siemens"]),
                    model=f"MODEL-{random.randint(1000, 9999)}",
                    serial_number=f"SN{random.randint(100000, 999999)}",
                    department_id=dept_id,
                    status=status,
                    location_type="department",
                    current_location_id=dept_id,
                    purchase_date=datetime.now() - timedelta(days=random.randint(30, 1825)),
                    last_maintenance=datetime.now() - timedelta(days=random.randint(1, 90)),
                    next_maintenance=datetime.now() + timedelta(days=random.randint(30, 180)),
                    maintenance_interval_days=random.randint(90, 365),
                    cost=random.randint(5000, 150000),
                    is_portable=equipment_type in [EquipmentType.WHEELCHAIR, EquipmentType.IV_PUMP],
                    requires_certification=equipment_type in [EquipmentType.VENTILATOR, EquipmentType.DEFIBRILLATOR],
                    notes="Standard hospital equipment" if random.random() > 0.3 else None
                )
                session.add(equipment)
                self.equipment.append(equipment)
                equipment_counter += 1
            
            print(f"  ✓ Added {count} {equipment_type.value.replace('_', ' ')} to {dept_name}")
        
        await session.flush()
        print(f"✅ Seeded {len(self.equipment)} equipment items")
    
    async def _seed_supplies(self, session):
        """Seed supply inventory"""
        print("\n📦 Seeding Supply Inventory...")
        
        supplies_data = [
            # PPE
            {"name": "Surgical Gloves (S)", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 50, "max": 500},
            {"name": "Surgical Gloves (M)", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 50, "max": 500},
            {"name": "Surgical Gloves (L)", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 50, "max": 500},
            {"name": "N95 Masks", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 20, "max": 200},
            {"name": "Surgical Masks", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 100, "max": 1000},
            {"name": "Face Shields", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "box", "reorder": 15, "max": 150},
            {"name": "Isolation Gowns", "category": SupplyCategory.PERSONAL_PROTECTIVE_EQUIPMENT, "unit": "pack", "reorder": 25, "max": 250},
            
            # Pharmaceuticals
            {"name": "Saline Solution 0.9%", "category": SupplyCategory.PHARMACEUTICALS, "unit": "bag", "reorder": 100, "max": 1000},
            {"name": "Morphine 10mg/ml", "category": SupplyCategory.PHARMACEUTICALS, "unit": "vial", "reorder": 10, "max": 100},
            {"name": "Epinephrine 1mg/ml", "category": SupplyCategory.PHARMACEUTICALS, "unit": "vial", "reorder": 15, "max": 150},
            {"name": "Lidocaine 2%", "category": SupplyCategory.PHARMACEUTICALS, "unit": "vial", "reorder": 12, "max": 120},
            {"name": "Propofol 10mg/ml", "category": SupplyCategory.PHARMACEUTICALS, "unit": "vial", "reorder": 15, "max": 150},
            {"name": "Insulin Regular", "category": SupplyCategory.PHARMACEUTICALS, "unit": "vial", "reorder": 20, "max": 200},
            
            # Medical Supplies
            {"name": "Disposable Syringes 5ml", "category": SupplyCategory.MEDICAL_SUPPLIES, "unit": "pack", "reorder": 50, "max": 500},
            {"name": "IV Catheters 20G", "category": SupplyCategory.MEDICAL_SUPPLIES, "unit": "pack", "reorder": 30, "max": 300},
            {"name": "Gauze Pads 4x4", "category": SupplyCategory.MEDICAL_SUPPLIES, "unit": "pack", "reorder": 40, "max": 400},
            {"name": "Medical Tape", "category": SupplyCategory.MEDICAL_SUPPLIES, "unit": "roll", "reorder": 30, "max": 300},
            
            # Surgical Instruments
            {"name": "Surgical Drapes", "category": SupplyCategory.SURGICAL_INSTRUMENTS, "unit": "pack", "reorder": 20, "max": 200},
            {"name": "Scalpel Blades #10", "category": SupplyCategory.SURGICAL_INSTRUMENTS, "unit": "pack", "reorder": 15, "max": 150},
            {"name": "Suture Materials 3-0", "category": SupplyCategory.SURGICAL_INSTRUMENTS, "unit": "pack", "reorder": 15, "max": 150},
            
            # Laboratory Supplies
            {"name": "Blood Collection Tubes", "category": SupplyCategory.LABORATORY_SUPPLIES, "unit": "pack", "reorder": 100, "max": 1000},
            {"name": "Specimen Containers", "category": SupplyCategory.LABORATORY_SUPPLIES, "unit": "pack", "reorder": 30, "max": 300},
            
            # Cleaning Supplies
            {"name": "Alcohol Prep Pads", "category": SupplyCategory.CLEANING_SUPPLIES, "unit": "box", "reorder": 50, "max": 500},
            {"name": "Hand Sanitizer", "category": SupplyCategory.CLEANING_SUPPLIES, "unit": "bottle", "reorder": 40, "max": 400},
        ]
        
        for i, supply_data in enumerate(supplies_data):
            current_quantity = random.randint(supply_data["reorder"], supply_data["max"])
            
            # 30% chance of low stock to trigger alerts
            if random.random() < 0.3:
                current_quantity = random.randint(0, supply_data["reorder"] - 1)
            
            supply = SupplyItem(
                id=f"supply_{i+1:03d}",
                name=supply_data["name"],
                description=f"High-quality {supply_data['name'].lower()}",
                category=supply_data["category"],
                sku=f"SKU{i+1:06d}",
                manufacturer=random.choice(["MedSupply Corp", "Pharma Plus", "Surgical Solutions", "EquipMed Technologies"]),
                model_number=f"MDL{random.randint(100, 999)}",
                unit_of_measure=supply_data["unit"],
                unit_cost=round(random.uniform(5.0, 150.0), 2),
                reorder_point=supply_data["reorder"],
                max_stock_level=supply_data["max"],
                expiration_required=supply_data["category"] == SupplyCategory.PHARMACEUTICALS,
                controlled_substance=supply_data["name"] in ["Morphine 10mg/ml", "Propofol 10mg/ml"],
                storage_requirements={"temperature": "room_temp", "humidity": "normal"}
            )
            session.add(supply)
            self.supplies.append(supply)
            
            # Create inventory location
            location = InventoryLocation(
                id=f"inv_{supply.id}",
                supply_item_id=supply.id,
                location_name=f"Main {supply_data['category'].value.replace('_', ' ').title()} Storage",
                department_id="dept_medical",  # Central storage
                current_quantity=current_quantity,
                available_quantity=current_quantity,
                lot_number=f"LOT{random.randint(100000, 999999)}",
                expiration_date=datetime.now() + timedelta(days=random.randint(30, 730)) if supply.expiration_required else None,
                received_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                status=SupplyStatus.LOW_STOCK if current_quantity < supply.reorder_point else SupplyStatus.IN_STOCK,
                last_counted=datetime.now() - timedelta(days=random.randint(1, 7)),
                storage_location=f"Shelf {random.choice(['A', 'B', 'C'])}-{random.randint(1, 20)}"
            )
            session.add(location)
        
        await session.flush()
        print(f"✅ Seeded {len(self.supplies)} supply items with inventory locations")
    
    async def _seed_patients(self, session):
        """Seed patients"""
        print("\n🏥 Seeding Patients...")
        
        # Sample patient data
        patient_names = [
            "John Smith", "Mary Johnson", "Robert Brown", "Patricia Davis",
            "Michael Wilson", "Jennifer Garcia", "William Martinez", "Elizabeth Rodriguez",
            "David Anderson", "Susan Thompson", "Richard Taylor", "Jessica Moore",
            "Charles Jackson", "Sarah Lee", "Thomas White", "Nancy Harris",
            "Christopher Martin", "Betty Thompson", "Matthew Garcia", "Helen Martinez"
        ]
        
        diagnoses = [
            "Pneumonia", "Myocardial Infarction", "Stroke", "Sepsis",
            "Chronic Obstructive Pulmonary Disease", "Congestive Heart Failure",
            "Diabetes Mellitus", "Hypertension", "Acute Renal Failure",
            "Post-operative Care", "Chest Pain", "Respiratory Failure"
        ]
        
        for i, name in enumerate(patient_names):
            # Assign to occupied beds
            available_beds = [b for b in self.beds if b.status == BedStatus.OCCUPIED]
            if not available_beds:
                break
            
            bed = random.choice(available_beds)
            available_beds.remove(bed)
            
            acuity = PatientAcuity.CRITICAL if bed.bed_type == BedType.ICU else random.choice(list(PatientAcuity))
            
            patient = Patient(
                id=f"patient_{i+1:03d}",
                mrn=f"MRN{i+1:07d}",
                name=name,
                date_of_birth=datetime.now() - timedelta(days=random.randint(365*18, 365*85)),
                gender=random.choice(["Male", "Female"]),
                acuity_level=acuity,
                admission_date=datetime.now() - timedelta(days=random.randint(0, 14)),
                primary_diagnosis=random.choice(diagnoses),
                isolation_required=random.random() < 0.15,  # 15% need isolation
                isolation_type="contact" if random.random() < 0.5 else "droplet",
                allergies=["Penicillin"] if random.random() < 0.3 else [],
                special_needs=[],
                emergency_contact={
                    "name": f"Emergency Contact for {name}",
                    "phone": f"555-{random.randint(1000, 9999)}",
                    "relationship": random.choice(["Spouse", "Child", "Parent", "Sibling"])
                }
            )
            session.add(patient)
            self.patients.append(patient)
            
            # Update bed with patient
            bed.current_patient_id = patient.id
        
        await session.flush()
        print(f"✅ Seeded {len(self.patients)} patients")
    
    async def _print_existing_summary(self, session):
        """Print summary of existing data"""
        try:
            # Count existing records
            dept_result = await session.execute(text("SELECT COUNT(*) FROM departments"))
            staff_result = await session.execute(text("SELECT COUNT(*) FROM staff_members"))
            bed_result = await session.execute(text("SELECT COUNT(*) FROM beds"))
            equip_result = await session.execute(text("SELECT COUNT(*) FROM medical_equipment"))
            supply_result = await session.execute(text("SELECT COUNT(*) FROM supply_items"))
            patient_result = await session.execute(text("SELECT COUNT(*) FROM patients"))
            
            dept_count = dept_result.scalar()
            staff_count = staff_result.scalar()
            bed_count = bed_result.scalar()
            equip_count = equip_result.scalar()
            supply_count = supply_result.scalar()
            patient_count = patient_result.scalar()
            
            print("\n📊 Existing Data Summary:")
            print(f"  🏢 Departments: {dept_count}")
            print(f"  👥 Staff Members: {staff_count}")
            print(f"  🛏️ Beds: {bed_count}")
            print(f"  🔧 Equipment: {equip_count}")
            print(f"  📦 Supply Items: {supply_count}")
            print(f"  🏥 Patients: {patient_count}")
            print(f"\n🎯 Total Records: {dept_count + staff_count + bed_count + equip_count + supply_count + patient_count}")
            print("🚀 Multi-Agent System is ready with comprehensive hospital data!")
            
        except Exception as e:
            print(f"Could not retrieve existing data summary: {e}")
    
    async def _print_summary(self):
        """Print seeding summary"""
        print("\n📊 Data Seeding Summary:")
        print(f"  🏢 Departments: {len(self.departments)}")
        print(f"  🏭 Suppliers: {len(self.suppliers)}")
        print(f"  👥 Staff Members: {len(self.staff_members)}")
        print(f"  🛏️ Beds: {len(self.beds)}")
        print(f"  🔧 Equipment: {len(self.equipment)}")
        print(f"  📦 Supply Items: {len(self.supplies)}")
        print(f"  🏥 Patients: {len(self.patients)}")
        print(f"\n🎯 Total Records: {len(self.departments) + len(self.suppliers) + len(self.staff_members) + len(self.beds) + len(self.equipment) + len(self.supplies) + len(self.patients)}")

async def main():
    """Main seeding function"""
    seeder = ProfessionalHospitalSeeder()
    await seeder.seed_comprehensive_data()

if __name__ == "__main__":
    asyncio.run(main())
