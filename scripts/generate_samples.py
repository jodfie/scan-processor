#!/usr/bin/env python3
"""
Sample Document Generator for Scan Processor Testing

Generates realistic PDF documents for each document category to validate
the classification and metadata extraction pipeline.

Usage:
    python3 generate_samples.py --all
    python3 generate_samples.py --category personal-medical --count 9
    python3 generate_samples.py --output-dir samples/
"""

import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

fake = Faker()


class SampleDocumentGenerator:
    """Generate realistic PDF samples for different document categories"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self):
        """Generate all sample documents"""
        print("Generating all sample documents...")
        print(f"Output directory: {self.output_dir}")

        # Personal Medical (9 samples)
        self.generate_personal_medical_bills(3)
        self.generate_lab_results(2)
        self.generate_doctor_visit_summaries(2)
        self.generate_prescriptions(2)

        # Personal Expense (9 samples)
        self.generate_restaurant_receipts(3)
        self.generate_amazon_invoices(2)
        self.generate_store_receipts(2)
        self.generate_service_invoices(2)

        # Utility (12 samples)
        self.generate_electric_bills(3)
        self.generate_water_bills(2)
        self.generate_gas_bills(2)
        self.generate_internet_bills(3)
        self.generate_phone_bills(2)

        # Auto Insurance (6 samples)
        self.generate_insurance_policies(2)
        self.generate_declaration_pages(2)
        self.generate_premium_notices(2)

        # Auto Maintenance (6 samples)
        self.generate_oil_change_receipts(2)
        self.generate_tire_service_receipts(2)
        self.generate_general_service_receipts(2)

        # Auto Registration (6 samples)
        self.generate_registration_renewals(3)
        self.generate_inspection_certificates(3)

        print(f"\n✅ Generated 48 sample documents in {self.output_dir}")

    # ========== Personal Medical ==========

    def generate_personal_medical_bills(self, count: int):
        """Generate personal medical bill samples"""
        category_dir = self.output_dir / "personal-medical"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"medical-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, fake.company())
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "MEDICAL BILL")

            # Patient info
            c.setFont("Helvetica", 10)
            date = fake.date_between(start_date='-6m', end_date='today')
            c.drawString(1*inch, height - 2.5*inch, f"Patient: {fake.name()}")
            c.drawString(1*inch, height - 2.7*inch, f"Date of Service: {date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Provider: Dr. {fake.last_name()}")

            # Services
            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Services:")
            y -= 0.3*inch

            services = [
                ("Office Visit - Level 3", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                ("Lab Work - Basic Panel", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
            ]

            c.setFont("Helvetica", 10)
            for service, cost in services:
                c.drawString(1.2*inch, y, f"• {service}")
                c.drawString(5*inch, y, f"${cost}")
                y -= 0.2*inch

            # Total
            total = sum(float(cost) for _, cost in services)
            y -= 0.3*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_lab_results(self, count: int):
        """Generate lab result samples"""
        category_dir = self.output_dir / "personal-medical"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"lab-results-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, f"{fake.company()} Laboratory")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "LABORATORY RESULTS")

            # Patient info
            c.setFont("Helvetica", 10)
            date = fake.date_between(start_date='-3m', end_date='today')
            c.drawString(1*inch, height - 2.5*inch, f"Patient: {fake.name()}")
            c.drawString(1*inch, height - 2.7*inch, f"Test Date: {date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Ordering Physician: Dr. {fake.last_name()}")

            # Test results
            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Test Results:")
            y -= 0.3*inch

            tests = [
                ("Complete Blood Count", "Normal"),
                ("Glucose Level", f"{random.randint(70, 120)} mg/dL"),
                ("Cholesterol Total", f"{random.randint(150, 200)} mg/dL"),
            ]

            c.setFont("Helvetica", 10)
            for test, result in tests:
                c.drawString(1.2*inch, y, f"{test}:")
                c.drawString(4*inch, y, result)
                y -= 0.2*inch

            c.save()
            print(f"Generated: {filepath}")

    def generate_doctor_visit_summaries(self, count: int):
        """Generate doctor visit summary samples"""
        category_dir = self.output_dir / "personal-medical"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"doctor-visit-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, f"Dr. {fake.last_name()} - {fake.job()[:20]}")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "VISIT SUMMARY")

            # Visit info
            c.setFont("Helvetica", 10)
            date = fake.date_between(start_date='-2m', end_date='today')
            c.drawString(1*inch, height - 2.5*inch, f"Patient: {fake.name()}")
            c.drawString(1*inch, height - 2.7*inch, f"Visit Date: {date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Reason: {random.choice(['Annual checkup', 'Follow-up', 'Consultation'])}")

            # Notes
            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Notes:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, "Patient presents for routine examination.")

            c.save()
            print(f"Generated: {filepath}")

    def generate_prescriptions(self, count: int):
        """Generate prescription samples"""
        category_dir = self.output_dir / "personal-medical"
        category_dir.mkdir(exist_ok=True)

        medications = ["Ibuprofen", "Amoxicillin", "Lisinopril", "Metformin", "Atorvastatin"]

        for i in range(count):
            filename = f"prescription-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, f"Dr. {fake.last_name()}")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "PRESCRIPTION")

            # Patient info
            c.setFont("Helvetica", 10)
            date = fake.date_between(start_date='-1m', end_date='today')
            c.drawString(1*inch, height - 2.5*inch, f"Patient: {fake.name()}")
            c.drawString(1*inch, height - 2.7*inch, f"Date: {date.strftime('%Y-%m-%d')}")

            # Medication
            y = height - 3.3*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Medication:")
            y -= 0.3*inch

            medication = random.choice(medications)
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, f"{medication} {random.choice(['10mg', '20mg', '50mg'])}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"Take {random.choice(['1', '2'])} {random.choice(['daily', 'twice daily'])}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"Refills: {random.randint(0, 3)}")

            c.save()
            print(f"Generated: {filepath}")

    # ========== Personal Expense ==========

    def generate_restaurant_receipts(self, count: int):
        """Generate restaurant receipt samples"""
        category_dir = self.output_dir / "personal-expense"
        category_dir.mkdir(exist_ok=True)

        restaurants = ["The Bistro", "Pasta Palace", "Burger Haven", "Sushi Bar", "Taco Fiesta"]

        for i in range(count):
            filename = f"restaurant-receipt-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            restaurant = random.choice(restaurants)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 1*inch, restaurant)
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Receipt details
            date = fake.date_between(start_date='-1m', end_date='today')
            time = fake.time()
            c.drawCentredString(width/2, height - 1.6*inch, f"{date.strftime('%Y-%m-%d')} {time}")

            # Items
            y = height - 2.2*inch
            items = [
                (fake.word().capitalize() + " Plate", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                (fake.word().capitalize() + " Special", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                ("Beverage", fake.pydecimal(left_digits=1, right_digits=2, positive=True)),
            ]

            for item, price in items:
                c.drawString(2*inch, y, item)
                c.drawString(5*inch, y, f"${price}")
                y -= 0.2*inch

            # Total
            subtotal = sum(float(price) for _, price in items)
            tax = subtotal * 0.08
            total = subtotal + tax

            y -= 0.3*inch
            c.drawString(2*inch, y, "Subtotal:")
            c.drawString(5*inch, y, f"${subtotal:.2f}")
            y -= 0.2*inch
            c.drawString(2*inch, y, "Tax:")
            c.drawString(5*inch, y, f"${tax:.2f}")
            y -= 0.2*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_amazon_invoices(self, count: int):
        """Generate Amazon invoice samples"""
        category_dir = self.output_dir / "personal-expense"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"amazon-invoice-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 18)
            c.drawString(1*inch, height - 1*inch, "amazon")

            # Order info
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1.5*inch, "Order Confirmation")

            c.setFont("Helvetica", 10)
            date = fake.date_between(start_date='-2m', end_date='today')
            c.drawString(1*inch, height - 2*inch, f"Order Date: {date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.2*inch, f"Order #: {fake.ean13()}")

            # Items
            y = height - 2.8*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Items:")
            y -= 0.3*inch

            items = [
                (fake.bs().capitalize()[:30], fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                (fake.bs().capitalize()[:30], fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
            ]

            c.setFont("Helvetica", 10)
            for item, price in items:
                c.drawString(1.2*inch, y, item)
                c.drawString(5*inch, y, f"${price}")
                y -= 0.2*inch

            # Total
            total = sum(float(price) for _, price in items)
            y -= 0.3*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_store_receipts(self, count: int):
        """Generate general store receipt samples"""
        category_dir = self.output_dir / "personal-expense"
        category_dir.mkdir(exist_ok=True)

        stores = ["Target", "Walmart", "Best Buy", "Home Depot", "CVS"]

        for i in range(count):
            filename = f"store-receipt-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            store = random.choice(stores)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 1*inch, store)
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, height - 1.3*inch, fake.street_address())

            date = fake.date_between(start_date='-1m', end_date='today')
            time = fake.time()
            c.drawCentredString(width/2, height - 1.6*inch, f"{date.strftime('%Y-%m-%d')} {time}")

            # Items
            y = height - 2.2*inch
            items = [
                (fake.word().capitalize() + " Item", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                (fake.word().capitalize() + " Product", fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
                (fake.word().capitalize() + " Supply", fake.pydecimal(left_digits=1, right_digits=2, positive=True)),
            ]

            for item, price in items:
                c.drawString(2*inch, y, item)
                c.drawString(5*inch, y, f"${price}")
                y -= 0.2*inch

            # Total
            total = sum(float(price) for _, price in items)
            y -= 0.3*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_service_invoices(self, count: int):
        """Generate service invoice samples"""
        category_dir = self.output_dir / "personal-expense"
        category_dir.mkdir(exist_ok=True)

        services = ["Lawn Care", "House Cleaning", "Plumbing Repair", "HVAC Service", "Electrical Work"]

        for i in range(count):
            filename = f"service-invoice-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            service = random.choice(services)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, f"{fake.company()} - {service}")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Invoice details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "INVOICE")

            date = fake.date_between(start_date='-1m', end_date='today')
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.4*inch, f"Date: {date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.6*inch, f"Invoice #: INV-{fake.random_number(digits=5)}")

            # Services
            y = height - 3.2*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Services Provided:")
            y -= 0.3*inch

            c.setFont("Helvetica", 10)
            labor_cost = fake.pydecimal(left_digits=3, right_digits=2, positive=True)
            c.drawString(1.2*inch, y, "Labor (3 hours)")
            c.drawString(5*inch, y, f"${labor_cost}")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Total Due:")
            c.drawString(5*inch, y, f"${labor_cost}")

            c.save()
            print(f"Generated: {filepath}")

    # ========== Utility ==========

    def generate_electric_bills(self, count: int):
        """Generate electric bill samples"""
        category_dir = self.output_dir / "utility"
        category_dir.mkdir(exist_ok=True)

        companies = ["City Power & Light", "Metro Electric", "Regional Energy Co."]

        for i in range(count):
            filename = f"electric-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            company = random.choice(companies)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, company)
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Bill details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "ELECTRIC BILL")

            billing_date = fake.date_between(start_date='-1m', end_date='today')
            due_date = billing_date + timedelta(days=21)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Account #: {fake.random_number(digits=10)}")
            c.drawString(1*inch, height - 2.7*inch, f"Billing Date: {billing_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 3.1*inch, f"Service Address: {fake.address().replace(chr(10), ', ')}")

            # Usage
            kwh = random.randint(500, 1500)
            rate = 0.12
            amount = kwh * rate

            y = height - 3.7*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Usage Summary:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, f"Total kWh Used: {kwh}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"Rate: ${rate}/kWh")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Amount Due:")
            c.drawString(5*inch, y, f"${amount:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_water_bills(self, count: int):
        """Generate water bill samples"""
        category_dir = self.output_dir / "utility"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"water-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "City Water & Sewer")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Bill details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "WATER/SEWER BILL")

            billing_date = fake.date_between(start_date='-1m', end_date='today')
            due_date = billing_date + timedelta(days=21)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Account #: {fake.random_number(digits=8)}")
            c.drawString(1*inch, height - 2.7*inch, f"Billing Date: {billing_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Charges
            water_charge = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
            sewer_charge = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
            total = float(water_charge) + float(sewer_charge)

            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Charges:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, "Water:")
            c.drawString(5*inch, y, f"${water_charge}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, "Sewer:")
            c.drawString(5*inch, y, f"${sewer_charge}")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total Due:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_gas_bills(self, count: int):
        """Generate gas bill samples"""
        category_dir = self.output_dir / "utility"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"gas-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "Metro Gas Company")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Bill details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "NATURAL GAS BILL")

            billing_date = fake.date_between(start_date='-1m', end_date='today')
            due_date = billing_date + timedelta(days=21)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Account #: {fake.random_number(digits=9)}")
            c.drawString(1*inch, height - 2.7*inch, f"Billing Date: {billing_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Usage
            therms = random.randint(20, 150)
            rate = 1.05
            amount = therms * rate

            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Usage:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, f"Therms Used: {therms}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"Rate: ${rate}/therm")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Amount Due:")
            c.drawString(5*inch, y, f"${amount:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_internet_bills(self, count: int):
        """Generate internet bill samples"""
        category_dir = self.output_dir / "utility"
        category_dir.mkdir(exist_ok=True)

        providers = ["Comcast Xfinity", "AT&T Internet", "Spectrum", "Verizon Fios"]

        for i in range(count):
            filename = f"internet-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            provider = random.choice(providers)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, provider)
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Bill details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "INTERNET SERVICE BILL")

            billing_date = fake.date_between(start_date='-1m', end_date='today')
            due_date = billing_date + timedelta(days=21)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Account #: {fake.random_number(digits=12)}")
            c.drawString(1*inch, height - 2.7*inch, f"Billing Date: {billing_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Service
            speeds = ["100 Mbps", "200 Mbps", "500 Mbps", "1 Gbps"]
            speed = random.choice(speeds)
            monthly_charge = random.uniform(50, 120)

            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Service:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, f"Internet Service ({speed})")
            c.drawString(5*inch, y, f"${monthly_charge:.2f}")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total Due:")
            c.drawString(5*inch, y, f"${monthly_charge:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_phone_bills(self, count: int):
        """Generate phone bill samples"""
        category_dir = self.output_dir / "utility"
        category_dir.mkdir(exist_ok=True)

        providers = ["Verizon Wireless", "AT&T Wireless", "T-Mobile", "Sprint"]

        for i in range(count):
            filename = f"phone-bill-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            provider = random.choice(providers)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, provider)
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Bill details
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "WIRELESS BILL")

            billing_date = fake.date_between(start_date='-1m', end_date='today')
            due_date = billing_date + timedelta(days=21)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Account #: {fake.random_number(digits=10)}")
            c.drawString(1*inch, height - 2.7*inch, f"Billing Date: {billing_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Charges
            line_charge = random.uniform(40, 80)
            data_charge = random.uniform(20, 50)
            total = line_charge + data_charge

            y = height - 3.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Charges:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, "Line Access:")
            c.drawString(5*inch, y, f"${line_charge:.2f}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, "Data:")
            c.drawString(5*inch, y, f"${data_charge:.2f}")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total Due:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    # ========== Auto Insurance ==========

    def generate_insurance_policies(self, count: int):
        """Generate auto insurance policy samples"""
        category_dir = self.output_dir / "auto-insurance"
        category_dir.mkdir(exist_ok=True)

        companies = ["State Farm", "Geico", "Progressive", "Allstate"]

        for i in range(count):
            filename = f"insurance-policy-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            company = random.choice(companies)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, company)
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.address().replace('\n', ', '))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "AUTO INSURANCE POLICY")

            # Policy details
            policy_date = fake.date_between(start_date='-1y', end_date='today')
            expiration_date = policy_date + timedelta(days=365)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Policy #: {fake.bothify(text='POL-########')}")
            c.drawString(1*inch, height - 2.7*inch, f"Policy Holder: {fake.name()}")
            c.drawString(1*inch, height - 2.9*inch, f"Effective Date: {policy_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 3.1*inch, f"Expiration Date: {expiration_date.strftime('%Y-%m-%d')}")

            # Vehicle info
            y = height - 3.7*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford", "Chevrolet"])
            model = random.choice(["Accord", "Camry", "F-150", "Malibu"])
            c.drawString(1.2*inch, y, f"{year} {make} {model}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"VIN: {fake.bothify(text='#??########?????')}")

            # Coverage
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Coverage:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y, "Bodily Injury: $250,000/$500,000")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, "Property Damage: $100,000")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, "Collision: $500 deductible")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, "Comprehensive: $500 deductible")

            # Premium
            y -= 0.5*inch
            premium = random.uniform(800, 1500)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Annual Premium:")
            c.drawString(5*inch, y, f"${premium:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_declaration_pages(self, count: int):
        """Generate insurance declaration page samples"""
        category_dir = self.output_dir / "auto-insurance"
        category_dir.mkdir(exist_ok=True)

        companies = ["State Farm", "Geico", "Progressive", "Allstate"]

        for i in range(count):
            filename = f"declaration-page-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            company = random.choice(companies)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, company)

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1.5*inch, "DECLARATION PAGE")

            # Policy info
            policy_date = fake.date_between(start_date='-6m', end_date='today')

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2*inch, f"Policy #: {fake.bothify(text='DEC-########')}")
            c.drawString(1*inch, height - 2.2*inch, f"Policy Date: {policy_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.4*inch, f"Insured: {fake.name()}")

            # Vehicle
            y = height - 3*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Insured Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford", "Chevrolet"])
            model = random.choice(["Civic", "Corolla", "Escape", "Equinox"])
            c.drawString(1.2*inch, y, f"{year} {make} {model}")

            # Coverages
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Coverage Summary:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            coverages = [
                ("Liability", f"${random.randint(50, 100) * 1000}"),
                ("Collision", f"${random.choice([500, 1000])} deductible"),
                ("Comprehensive", f"${random.choice([250, 500, 1000])} deductible"),
            ]
            for coverage, amount in coverages:
                c.drawString(1.2*inch, y, f"{coverage}: {amount}")
                y -= 0.2*inch

            c.save()
            print(f"Generated: {filepath}")

    def generate_premium_notices(self, count: int):
        """Generate insurance premium notice samples"""
        category_dir = self.output_dir / "auto-insurance"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"premium-notice-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, random.choice(["State Farm", "Geico"]))

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1.5*inch, "PREMIUM PAYMENT NOTICE")

            # Notice details
            due_date = fake.date_between(start_date='today', end_date='+1m')

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2*inch, f"Policy #: {fake.bothify(text='PREM-########')}")
            c.drawString(1*inch, height - 2.2*inch, f"Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Amount
            premium = random.uniform(100, 300)
            y = height - 2.8*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Premium Due:")
            c.drawString(5*inch, y, f"${premium:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    # ========== Auto Maintenance ==========

    def generate_oil_change_receipts(self, count: int):
        """Generate oil change receipt samples"""
        category_dir = self.output_dir / "auto-maintenance"
        category_dir.mkdir(exist_ok=True)

        shops = ["Jiffy Lube", "Valvoline", "Take 5 Oil Change", "Pennzoil"]

        for i in range(count):
            filename = f"oil-change-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            shop = random.choice(shops)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, shop)
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.street_address())

            # Receipt details
            service_date = fake.date_between(start_date='-3m', end_date='today')
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "SERVICE RECEIPT")

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.4*inch, f"Date: {service_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.6*inch, f"Invoice #: {fake.random_number(digits=6)}")

            # Vehicle
            y = height - 3.2*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford"])
            model = random.choice(["Accord", "Camry", "F-150"])
            c.drawString(1.2*inch, y, f"{year} {make} {model}")
            y -= 0.2*inch
            mileage = random.randint(20000, 150000)
            c.drawString(1.2*inch, y, f"Mileage: {mileage:,}")

            # Services
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Services:")
            y -= 0.3*inch

            c.setFont("Helvetica", 10)
            oil_change = random.uniform(40, 80)
            c.drawString(1.2*inch, y, "Oil Change (Synthetic)")
            c.drawString(5*inch, y, f"${oil_change:.2f}")
            y -= 0.2*inch
            filter = random.uniform(10, 20)
            c.drawString(1.2*inch, y, "Oil Filter")
            c.drawString(5*inch, y, f"${filter:.2f}")

            # Total
            total = oil_change + filter
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_tire_service_receipts(self, count: int):
        """Generate tire service receipt samples"""
        category_dir = self.output_dir / "auto-maintenance"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"tire-service-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, random.choice(["Discount Tire", "Firestone", "Goodyear"]))
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.street_address())

            # Receipt details
            service_date = fake.date_between(start_date='-6m', end_date='today')
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "TIRE SERVICE RECEIPT")

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.4*inch, f"Date: {service_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.6*inch, f"Invoice #: TIRE-{fake.random_number(digits=5)}")

            # Vehicle
            y = height - 3.2*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford"])
            c.drawString(1.2*inch, y, f"{year} {make} {random.choice(['Civic', 'Camry', 'Escape'])}")

            # Services
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Services:")
            y -= 0.3*inch

            c.setFont("Helvetica", 10)
            service = random.choice([
                ("Tire Rotation", random.uniform(20, 40)),
                ("Tire Replacement (4 tires)", random.uniform(400, 800)),
                ("Tire Balance", random.uniform(40, 60)),
            ])
            c.drawString(1.2*inch, y, service[0])
            c.drawString(5*inch, y, f"${service[1]:.2f}")

            # Total
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total:")
            c.drawString(5*inch, y, f"${service[1]:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_general_service_receipts(self, count: int):
        """Generate general auto service receipt samples"""
        category_dir = self.output_dir / "auto-maintenance"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"general-service-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, f"{fake.last_name()}'s Auto Repair")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.street_address())

            # Receipt details
            service_date = fake.date_between(start_date='-4m', end_date='today')
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "SERVICE INVOICE")

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.4*inch, f"Date: {service_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.6*inch, f"Invoice #: SVC-{fake.random_number(digits=5)}")

            # Vehicle
            y = height - 3.2*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            c.drawString(1.2*inch, y, f"{year} {random.choice(['Honda', 'Toyota', 'Chevrolet'])} {random.choice(['Accord', 'Camry', 'Malibu'])}")

            # Services
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Services:")
            y -= 0.3*inch

            c.setFont("Helvetica", 10)
            services = [
                ("Brake Pad Replacement", random.uniform(150, 300)),
                ("Labor (2 hours)", random.uniform(100, 200)),
            ]

            total = 0
            for service, cost in services:
                c.drawString(1.2*inch, y, service)
                c.drawString(5*inch, y, f"${cost:.2f}")
                total += cost
                y -= 0.2*inch

            # Total
            y -= 0.3*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Total:")
            c.drawString(5*inch, y, f"${total:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    # ========== Auto Registration ==========

    def generate_registration_renewals(self, count: int):
        """Generate registration renewal samples"""
        category_dir = self.output_dir / "auto-registration"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"registration-renewal-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "Department of Motor Vehicles")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.state())

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "VEHICLE REGISTRATION RENEWAL")

            # Registration details
            renewal_date = fake.date_between(start_date='-2m', end_date='today')
            expiration_date = renewal_date + timedelta(days=365)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Registration #: {fake.bothify(text='??#######')}")
            c.drawString(1*inch, height - 2.7*inch, f"Renewal Date: {renewal_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Expires: {expiration_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 3.1*inch, f"Owner: {fake.name()}")

            # Vehicle
            y = height - 3.7*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle Information:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford", "Chevrolet"])
            model = random.choice(["Accord", "Camry", "F-150", "Malibu"])
            c.drawString(1.2*inch, y, f"Year/Make/Model: {year} {make} {model}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"VIN: {fake.bothify(text='#??########?????')}")
            y -= 0.2*inch
            plate = fake.bothify(text='???-####')
            c.drawString(1.2*inch, y, f"License Plate: {plate}")

            # Fee
            y -= 0.5*inch
            fee = random.uniform(50, 150)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y, "Registration Fee:")
            c.drawString(5*inch, y, f"${fee:.2f}")

            c.save()
            print(f"Generated: {filepath}")

    def generate_inspection_certificates(self, count: int):
        """Generate vehicle inspection certificate samples"""
        category_dir = self.output_dir / "auto-registration"
        category_dir.mkdir(exist_ok=True)

        for i in range(count):
            filename = f"inspection-certificate-{i+1:02d}.pdf"
            filepath = category_dir / filename

            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "Official Vehicle Inspection")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, fake.state())

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 2*inch, "SAFETY INSPECTION CERTIFICATE")

            # Inspection details
            inspection_date = fake.date_between(start_date='-3m', end_date='today')
            expiration_date = inspection_date + timedelta(days=365)

            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 2.5*inch, f"Certificate #: {fake.bothify(text='INSP-########')}")
            c.drawString(1*inch, height - 2.7*inch, f"Inspection Date: {inspection_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 2.9*inch, f"Valid Until: {expiration_date.strftime('%Y-%m-%d')}")
            c.drawString(1*inch, height - 3.1*inch, f"Station: {fake.company()}")

            # Vehicle
            y = height - 3.7*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Vehicle:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            year = random.randint(2015, 2024)
            make = random.choice(["Honda", "Toyota", "Ford"])
            model = random.choice(["Civic", "Corolla", "Escape"])
            c.drawString(1.2*inch, y, f"{year} {make} {model}")
            y -= 0.2*inch
            c.drawString(1.2*inch, y, f"VIN: {fake.bothify(text='#??########?????')}")
            y -= 0.2*inch
            odometer = random.randint(20000, 150000)
            c.drawString(1.2*inch, y, f"Odometer: {odometer:,} miles")

            # Result
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "RESULT: PASS ✓")

            c.save()
            print(f"Generated: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Generate sample PDFs for scan-processor testing")
    parser.add_argument('--all', action='store_true', help="Generate all samples")
    parser.add_argument('--category', type=str, help="Generate samples for specific category")
    parser.add_argument('--count', type=int, default=3, help="Number of samples to generate")
    parser.add_argument('--output-dir', type=str, default='samples', help="Output directory")

    args = parser.parse_args()

    generator = SampleDocumentGenerator(output_dir=args.output_dir)

    if args.all:
        generator.generate_all()
    elif args.category:
        category_method_map = {
            'personal-medical': [
                lambda: generator.generate_personal_medical_bills(args.count),
            ],
            'personal-expense': [
                lambda: generator.generate_restaurant_receipts(args.count),
            ],
            'utility': [
                lambda: generator.generate_electric_bills(args.count),
            ],
            'auto-insurance': [
                lambda: generator.generate_insurance_policies(args.count),
            ],
            'auto-maintenance': [
                lambda: generator.generate_oil_change_receipts(args.count),
            ],
            'auto-registration': [
                lambda: generator.generate_registration_renewals(args.count),
            ],
        }

        if args.category in category_method_map:
            for method in category_method_map[args.category]:
                method()
        else:
            print(f"Unknown category: {args.category}")
            print(f"Available categories: {', '.join(category_method_map.keys())}")
    else:
        print("Please specify --all or --category")
        parser.print_help()


if __name__ == '__main__':
    main()
