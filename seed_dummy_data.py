"""
Seed script to generate realistic demonstration and testing data
for the Billing & AI Inventory Management System.

Populates:
1. Realistic retail products across 6 major categories with valid EAN-13 barcodes
2. Transaction history spanning 45 days up to today (activating charts, dashboard cards, and reports)
3. Multi-warehouse inventory allocations with AI stock transfer suggestions
4. Purchase orders across draft, approved, and received statuses
5. AI Agent Activity logs and NLP query history
6. Expiry alerts tracking (fresh, near-expiry, and expired items)
7. Stock adjustment records with anomaly detection triggers
8. Trains the offline Random Forest ML demand forecast model
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import database as db
from ml import train as ml_train

def get_products_data():
    """Returns catalog of realistic retail products with real EAN-13 barcodes."""
    today = datetime.now().date()
    
    return [
        # --- GROCERIES & STAPLES ---
        {
            "name": "Daawat Rozana Gold Basmati Rice (5 kg)",
            "category": "Groceries",
            "sub_category": "Rice & Grains",
            "brand": "Daawat",
            "code_value": "8902080000109",
            "code_type": "EAN13",
            "unit_price": 485.0,
            "cost_price": 375.0,
            "mrp": 550.0,
            "stock_qty": 45.0,
            "reorder_level": 12.0,
            "unit_label": "kg",
            "weight": "5 kg",
            "volume": "",
            "manufacturer": "LT Foods Ltd",
            "country_of_origin": "India",
            "description": "Rich aroma aged long grain basmati rice, perfect for biryanis and daily meals.",
            "ingredients": "100% Pure Aged Basmati Rice",
            "nutritional_info": "Per 100g: Energy 350 kcal, Protein 8.5g, Carbs 78g, Fat 0.5g",
            "expiry_date": (today + timedelta(days=365)).isoformat(),
            "mfg_date": (today - timedelta(days=90)).isoformat(),
            "batch_number": "DWT-2026-B8",
        },
        {
            "name": "Aashirvaad Superior MP Sharbati Atta (10 kg)",
            "category": "Groceries",
            "sub_category": "Flours & Grains",
            "brand": "Aashirvaad",
            "code_value": "8901725181222",
            "code_type": "EAN13",
            "unit_price": 490.0,
            "cost_price": 410.0,
            "mrp": 540.0,
            "stock_qty": 38.0,
            "reorder_level": 10.0,
            "unit_label": "kg",
            "weight": "10 kg",
            "volume": "",
            "manufacturer": "ITC Limited",
            "country_of_origin": "India",
            "description": "100% pure whole wheat flour ground from grains of Madhya Pradesh.",
            "ingredients": "Whole Wheat",
            "nutritional_info": "Per 100g: Energy 365 kcal, Dietary Fiber 11g, Protein 12g",
            "expiry_date": (today + timedelta(days=150)).isoformat(),
            "mfg_date": (today - timedelta(days=30)).isoformat(),
            "batch_number": "ASH-W99-10K",
        },
        {
            "name": "Fortune Sunlite Refined Sunflower Oil (1 L)",
            "category": "Groceries",
            "sub_category": "Edible Oils",
            "brand": "Fortune",
            "code_value": "8906007280014",
            "code_type": "EAN13",
            "unit_price": 145.0,
            "cost_price": 118.0,
            "mrp": 165.0,
            "stock_qty": 55.0,
            "reorder_level": 15.0,
            "unit_label": "ltr",
            "weight": "910g",
            "volume": "1 L",
            "manufacturer": "Adani Wilmar Limited",
            "country_of_origin": "India",
            "description": "Light and healthy refined sunflower cooking oil enriched with Vitamins A & D.",
            "ingredients": "Refined Sunflower Oil, Vitamin A, Vitamin D",
            "nutritional_info": "Per 100g: Energy 900 kcal, Polyunsaturated Fatty Acids 60g",
            "expiry_date": (today + timedelta(days=270)).isoformat(),
            "mfg_date": (today - timedelta(days=45)).isoformat(),
            "batch_number": "FSN-2026-L1",
        },
        {
            "name": "Tata Salt Vacuum Evaporated Iodized (1 kg)",
            "category": "Groceries",
            "sub_category": "Spices & Seasonings",
            "brand": "Tata",
            "code_value": "8901052002344",
            "code_type": "EAN13",
            "unit_price": 28.0,
            "cost_price": 22.0,
            "mrp": 30.0,
            "stock_qty": 80.0,
            "reorder_level": 20.0,
            "unit_label": "pcs",
            "weight": "1 kg",
            "volume": "",
            "manufacturer": "Tata Consumer Products",
            "country_of_origin": "India",
            "description": "Desh Ka Namak - purest vacuum evaporated iodized table salt.",
            "ingredients": "Edible Common Salt, Potassium Iodate",
            "nutritional_info": "Per 100g: Sodium 38.7g, Iodine >15 ppm",
            "expiry_date": (today + timedelta(days=500)).isoformat(),
            "mfg_date": (today - timedelta(days=60)).isoformat(),
            "batch_number": "TS-2026-08",
        },
        {
            "name": "Tata Sampann Unpolished Toor Dal (1 kg)",
            "category": "Groceries",
            "sub_category": "Pulses & Lentils",
            "brand": "Tata",
            "code_value": "8901491102940",
            "code_type": "EAN13",
            "unit_price": 178.0,
            "cost_price": 142.0,
            "mrp": 195.0,
            "stock_qty": 24.0,
            "reorder_level": 8.0,
            "unit_label": "kg",
            "weight": "1 kg",
            "volume": "",
            "manufacturer": "Tata Consumer Products",
            "country_of_origin": "India",
            "description": "Unpolished yellow pigeon peas retaining natural goodness and authentic taste.",
            "ingredients": "Unpolished Toor Dal",
            "nutritional_info": "Per 100g: Protein 22g, Dietary Fiber 8g, Energy 343 kcal",
            "expiry_date": (today + timedelta(days=300)).isoformat(),
            "mfg_date": (today - timedelta(days=40)).isoformat(),
            "batch_number": "TD-SAMP-1K",
        },

        # --- PACKAGED FOODS & SNACKS ---
        {
            "name": "Maggi 2-Minute Masala Instant Noodles (4-Pack, 280g)",
            "category": "Packaged Foods",
            "sub_category": "Noodles & Pasta",
            "brand": "Maggi",
            "code_value": "8901058852370",
            "code_type": "EAN13",
            "unit_price": 56.0,
            "cost_price": 44.0,
            "mrp": 60.0,
            "stock_qty": 65.0,
            "reorder_level": 15.0,
            "unit_label": "pkts",
            "weight": "280g",
            "volume": "",
            "manufacturer": "Nestle India Ltd",
            "country_of_origin": "India",
            "description": "Classic masala instant noodles with authentic roasted spices.",
            "ingredients": "Wheat Flour, Palm Oil, Salt, Mixed Spices (Coriander, Cumin, Turmeric)",
            "nutritional_info": "Per 70g: Energy 312 kcal, Carbohydrate 43g, Protein 6.1g",
            "expiry_date": (today + timedelta(days=180)).isoformat(),
            "mfg_date": (today - timedelta(days=30)).isoformat(),
            "batch_number": "MG-4PK-0926",
        },
        {
            "name": "Britannia Good Day Butter Cookies (120g)",
            "category": "Packaged Foods",
            "sub_category": "Biscuits & Cookies",
            "brand": "Britannia",
            "code_value": "8901063012486",
            "code_type": "EAN13",
            "unit_price": 30.0,
            "cost_price": 23.5,
            "mrp": 35.0,
            "stock_qty": 4.0,  # LOW STOCK trigger
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "120g",
            "volume": "",
            "manufacturer": "Britannia Industries Ltd",
            "country_of_origin": "India",
            "description": "Crisp, buttery and golden-baked delight that spreads smiles.",
            "ingredients": "Refined Wheat Flour, Butter, Sugar, Milk Solids",
            "nutritional_info": "Per 100g: Energy 490 kcal, Fat 22g, Sugar 26g",
            "expiry_date": (today + timedelta(days=18)).isoformat(),  # NEAR EXPIRY trigger
            "mfg_date": (today - timedelta(days=160)).isoformat(),
            "batch_number": "BGD-120-04",
        },
        {
            "name": "Lay's Classic Salted Potato Chips (50g)",
            "category": "Packaged Foods",
            "sub_category": "Chips & Crisps",
            "brand": "Lay's",
            "code_value": "8901491361026",
            "code_type": "EAN13",
            "unit_price": 20.0,
            "cost_price": 15.5,
            "mrp": 20.0,
            "stock_qty": 72.0,
            "reorder_level": 15.0,
            "unit_label": "pcs",
            "weight": "50g",
            "volume": "",
            "manufacturer": "PepsiCo India Holdings",
            "country_of_origin": "India",
            "description": "Crispy thin potato chips seasoned with natural salt.",
            "ingredients": "Potatoes, Edible Vegetable Oil, Salt",
            "nutritional_info": "Per 50g: Energy 275 kcal, Fat 17g, Carbs 26g",
            "expiry_date": (today + timedelta(days=90)).isoformat(),
            "mfg_date": (today - timedelta(days=20)).isoformat(),
            "batch_number": "LAYS-CS-50",
        },
        {
            "name": "Cadbury Dairy Milk Silk Chocolate Bar (150g)",
            "category": "Packaged Foods",
            "sub_category": "Chocolates & Confectionery",
            "brand": "Cadbury",
            "code_value": "8901233024523",
            "code_type": "EAN13",
            "unit_price": 175.0,
            "cost_price": 140.0,
            "mrp": 190.0,
            "stock_qty": 3.0,  # LOW STOCK trigger
            "reorder_level": 8.0,
            "unit_label": "pcs",
            "weight": "150g",
            "volume": "",
            "manufacturer": "Mondelez India Foods",
            "country_of_origin": "India",
            "description": "Velvety smooth milk chocolate bar crafted with pure cocoa and fresh milk.",
            "ingredients": "Sugar, Milk Solids, Cocoa Butter, Cocoa Mass",
            "nutritional_info": "Per 100g: Energy 532 kcal, Protein 7.8g, Fat 31g",
            "expiry_date": (today + timedelta(days=210)).isoformat(),
            "mfg_date": (today - timedelta(days=50)).isoformat(),
            "batch_number": "CDM-SILK-150",
        },
        {
            "name": "Kellogg's Corn Flakes Original (475g)",
            "category": "Packaged Foods",
            "sub_category": "Breakfast Cereals",
            "brand": "Kellogg's",
            "code_value": "8901079010155",
            "code_type": "EAN13",
            "unit_price": 195.0,
            "cost_price": 155.0,
            "mrp": 215.0,
            "stock_qty": 28.0,
            "reorder_level": 8.0,
            "unit_label": "pcs",
            "weight": "475g",
            "volume": "",
            "manufacturer": "Kellogg India Pvt Ltd",
            "country_of_origin": "India",
            "description": "Crispy golden corn flakes enriched with iron and 8 essential vitamins.",
            "ingredients": "Milled Corn, Sugar, Barley Malt Extract, Salt",
            "nutritional_info": "Per 30g: Energy 114 kcal, Protein 2.1g, Iron 4.2mg",
            "expiry_date": (today + timedelta(days=240)).isoformat(),
            "mfg_date": (today - timedelta(days=40)).isoformat(),
            "batch_number": "KEL-CF-475",
        },
        {
            "name": "Haldiram's Nagpur Bhujia Sev (400g)",
            "category": "Packaged Foods",
            "sub_category": "Namkeen & Snacks",
            "brand": "Haldiram's",
            "code_value": "8904063200118",
            "code_type": "EAN13",
            "unit_price": 115.0,
            "cost_price": 90.0,
            "mrp": 125.0,
            "stock_qty": 42.0,
            "reorder_level": 12.0,
            "unit_label": "pcs",
            "weight": "400g",
            "volume": "",
            "manufacturer": "Haldiram Snacks Pvt Ltd",
            "country_of_origin": "India",
            "description": "Traditional spicy crisp chickpea noodle snack with authentic spices.",
            "ingredients": "Tepary Beans Flour, Gram Pulse Flour, Edible Vegetable Oil, Salt, Red Chilli",
            "nutritional_info": "Per 100g: Energy 578 kcal, Protein 12g, Fat 42g",
            "expiry_date": (today + timedelta(days=120)).isoformat(),
            "mfg_date": (today - timedelta(days=35)).isoformat(),
            "batch_number": "HLD-BHUJ-400",
        },

        # --- BEVERAGES ---
        {
            "name": "Tata Tea Gold Leaf Tea (500g)",
            "category": "Beverages",
            "sub_category": "Tea",
            "brand": "Tata",
            "code_value": "8901491101837",
            "code_type": "EAN13",
            "unit_price": 315.0,
            "cost_price": 255.0,
            "mrp": 350.0,
            "stock_qty": 36.0,
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "500g",
            "volume": "",
            "manufacturer": "Tata Consumer Products",
            "country_of_origin": "India",
            "description": "Exquisite blend of fine Assam CTC tea leaves with gently rolled long leaves.",
            "ingredients": "100% Black Tea",
            "nutritional_info": "Negligible calories, rich in tea antioxidants and flavonoids.",
            "expiry_date": (today + timedelta(days=360)).isoformat(),
            "mfg_date": (today - timedelta(days=45)).isoformat(),
            "batch_number": "TTG-500-09",
        },
        {
            "name": "Nescafe Classic 100% Pure Instant Coffee Jar (100g)",
            "category": "Beverages",
            "sub_category": "Coffee",
            "brand": "Nescafe",
            "code_value": "8901058859010",
            "code_type": "EAN13",
            "unit_price": 340.0,
            "cost_price": 270.0,
            "mrp": 380.0,
            "stock_qty": 20.0,
            "reorder_level": 6.0,
            "unit_label": "pcs",
            "weight": "100g",
            "volume": "",
            "manufacturer": "Nestle India Ltd",
            "country_of_origin": "India",
            "description": "Signature robust coffee blend with unmistakable aroma and bold roast flavor.",
            "ingredients": "100% Pure Coffee Beans Blend",
            "nutritional_info": "Per serving (2g): Energy 2 kcal, Caffeine 60mg",
            "expiry_date": (today + timedelta(days=26)).isoformat(),  # NEAR EXPIRY trigger
            "mfg_date": (today - timedelta(days=340)).isoformat(),
            "batch_number": "NES-CLS-100",
        },
        {
            "name": "Coca-Cola Original Taste Sparkling Soft Drink (750ml)",
            "category": "Beverages",
            "sub_category": "Cold Drinks & Soda",
            "brand": "Coca-Cola",
            "code_value": "8901764012228",
            "code_type": "EAN13",
            "unit_price": 40.0,
            "cost_price": 31.0,
            "mrp": 45.0,
            "stock_qty": 85.0,
            "reorder_level": 20.0,
            "unit_label": "pcs",
            "weight": "790g",
            "volume": "750 ml",
            "manufacturer": "Hindustan Coca-Cola Beverages",
            "country_of_origin": "India",
            "description": "Crisp, delicious, and refreshing carbonated beverage served chilled.",
            "ingredients": "Carbonated Water, Sugar, Acidity Regulator (338), Caffeine",
            "nutritional_info": "Per 100ml: Energy 44 kcal, Carbohydrates 10.9g",
            "expiry_date": (today + timedelta(days=120)).isoformat(),
            "mfg_date": (today - timedelta(days=30)).isoformat(),
            "batch_number": "COKE-750-B",
        },
        {
            "name": "Tropicana 100% Pure Real Orange Juice (1 L)",
            "category": "Beverages",
            "sub_category": "Fruit Juices",
            "brand": "Tropicana",
            "code_value": "8901888000452",
            "code_type": "EAN13",
            "unit_price": 130.0,
            "cost_price": 102.0,
            "mrp": 145.0,
            "stock_qty": 2.0,  # CRITICAL LOW STOCK trigger
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "1.05 kg",
            "volume": "1 L",
            "manufacturer": "PepsiCo India Holdings",
            "country_of_origin": "India",
            "description": "100% pure orange juice with no added sugar or preservatives.",
            "ingredients": "Water, Concentrated Orange Juice, Vitamin C",
            "nutritional_info": "Per 200ml: Energy 96 kcal, Vitamin C 30mg, Potassium 320mg",
            "expiry_date": (today + timedelta(days=60)).isoformat(),
            "mfg_date": (today - timedelta(days=60)).isoformat(),
            "batch_number": "TROP-OR-1L",
        },
        {
            "name": "Bisleri Packaged Drinking Mineral Water (1 L)",
            "category": "Beverages",
            "sub_category": "Packaged Water",
            "brand": "Bisleri",
            "code_value": "8906014410015",
            "code_type": "EAN13",
            "unit_price": 20.0,
            "cost_price": 13.0,
            "mrp": 20.0,
            "stock_qty": 110.0,
            "reorder_level": 25.0,
            "unit_label": "pcs",
            "weight": "1 kg",
            "volume": "1 L",
            "manufacturer": "Bisleri International Pvt Ltd",
            "country_of_origin": "India",
            "description": "Ozonated and mineral-enriched pure bottled drinking water.",
            "ingredients": "Purified Water, Minerals (Magnesium Sulphate, Potassium Bicarbonate)",
            "nutritional_info": "Essential electrolytes: Mg 0.2mg, K 0.1mg per 100ml",
            "expiry_date": (today + timedelta(days=180)).isoformat(),
            "mfg_date": (today - timedelta(days=10)).isoformat(),
            "batch_number": "BIS-1L-09",
        },

        # --- DAIRY & COLD STORAGE ---
        {
            "name": "Amul Pasteurised Salted Butter (500g)",
            "category": "Dairy",
            "sub_category": "Butter & Cheese",
            "brand": "Amul",
            "code_value": "8901262010054",
            "code_type": "EAN13",
            "unit_price": 275.0,
            "cost_price": 235.0,
            "mrp": 285.0,
            "stock_qty": 35.0,
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "500g",
            "volume": "",
            "manufacturer": "GCMMF Ltd (Amul)",
            "country_of_origin": "India",
            "description": "Utterly butterly delicious creamy table butter made from fresh cow and buffalo milk.",
            "ingredients": "Butter (Milk Fat 80%), Common Salt, Annatto color",
            "nutritional_info": "Per 100g: Energy 722 kcal, Milk Fat 80g, Vitamin A 650 mcg",
            "expiry_date": (today + timedelta(days=90)).isoformat(),
            "mfg_date": (today - timedelta(days=20)).isoformat(),
            "batch_number": "AML-BUT-500",
        },
        {
            "name": "Amul Taaza Homogenised Toned Milk (1 L Tetra Pak)",
            "category": "Dairy",
            "sub_category": "Fresh Milk",
            "brand": "Amul",
            "code_value": "8901262150026",
            "code_type": "EAN13",
            "unit_price": 72.0,
            "cost_price": 61.0,
            "mrp": 75.0,
            "stock_qty": 18.0,
            "reorder_level": 12.0,
            "unit_label": "ltr",
            "weight": "1.03 kg",
            "volume": "1 L",
            "manufacturer": "GCMMF Ltd (Amul)",
            "country_of_origin": "India",
            "description": "Long-life UHT treated toned milk with minimum 3.0% fat and 8.5% SNF.",
            "ingredients": "Toned Milk, Vitamin A, Vitamin D2",
            "nutritional_info": "Per 100ml: Energy 58 kcal, Calcium 120mg, Protein 3.2g",
            "expiry_date": (today - timedelta(days=12)).isoformat(),  # EXPIRED trigger
            "mfg_date": (today - timedelta(days=120)).isoformat(),
            "batch_number": "AML-TZ-EXP",
        },
        {
            "name": "Mother Dairy Classic Malai Paneer (200g)",
            "category": "Dairy",
            "sub_category": "Paneer & Cheese",
            "brand": "Mother Dairy",
            "code_value": "8901262020084",
            "code_type": "EAN13",
            "unit_price": 92.0,
            "cost_price": 76.0,
            "mrp": 98.0,
            "stock_qty": 14.0,
            "reorder_level": 8.0,
            "unit_label": "pcs",
            "weight": "200g",
            "volume": "",
            "manufacturer": "Mother Dairy Fruit & Vegetable Pvt Ltd",
            "country_of_origin": "India",
            "description": "Soft, succulent cottage cheese blocks crafted from pure pasteurised milk.",
            "ingredients": "Standardised Milk, Citric Acid",
            "nutritional_info": "Per 100g: Energy 289 kcal, Protein 18g, Calcium 480mg",
            "expiry_date": (today + timedelta(days=6)).isoformat(),  # NEAR EXPIRY trigger (6 days left!)
            "mfg_date": (today - timedelta(days=24)).isoformat(),
            "batch_number": "MD-PAN-200",
        },
        {
            "name": "Epigamia Greek Yogurt Natural (100g)",
            "category": "Dairy",
            "sub_category": "Yogurt",
            "brand": "Epigamia",
            "code_value": "8908007281001",
            "code_type": "EAN13",
            "unit_price": 50.0,
            "cost_price": 38.0,
            "mrp": 55.0,
            "stock_qty": 6.0,
            "reorder_level": 8.0,
            "unit_label": "pcs",
            "weight": "100g",
            "volume": "",
            "manufacturer": "Drums Food International",
            "country_of_origin": "India",
            "description": "High-protein artisanal strained Greek yogurt with zero preservatives.",
            "ingredients": "Pasteurized Double Toned Milk, Active Live Cultures",
            "nutritional_info": "Per 100g: Protein 8.0g, Energy 82 kcal, Fat 3.0g",
            "expiry_date": (today - timedelta(days=8)).isoformat(),  # EXPIRED trigger
            "mfg_date": (today - timedelta(days=35)).isoformat(),
            "batch_number": "EPI-GY-EXP",
        },

        # --- PERSONAL CARE & HYGIENE ---
        {
            "name": "Dettol Original Antiseptic Bathing Soap (125g x 3)",
            "category": "Personal Care",
            "sub_category": "Soaps & Body Wash",
            "brand": "Dettol",
            "code_value": "8901030735516",
            "code_type": "EAN13",
            "unit_price": 145.0,
            "cost_price": 115.0,
            "mrp": 160.0,
            "stock_qty": 40.0,
            "reorder_level": 10.0,
            "unit_label": "pkts",
            "weight": "375g",
            "volume": "",
            "manufacturer": "Reckitt Benckiser India",
            "country_of_origin": "India",
            "description": "Protects against 100 illness-causing germs with trusted germ defense.",
            "ingredients": "Sodium Palmate, Sodium Palm Kernelate, Chloroxylenol, Fragrance",
            "nutritional_info": "Grade 1 Toilet Soap TFM 76%",
            "expiry_date": (today + timedelta(days=400)).isoformat(),
            "mfg_date": (today - timedelta(days=45)).isoformat(),
            "batch_number": "DTL-SP-3PK",
        },
        {
            "name": "Colgate Strong Teeth Anticavity Toothpaste (150g)",
            "category": "Personal Care",
            "sub_category": "Oral Care",
            "brand": "Colgate",
            "code_value": "8901030005480",
            "code_type": "EAN13",
            "unit_price": 95.0,
            "cost_price": 74.0,
            "mrp": 105.0,
            "stock_qty": 48.0,
            "reorder_level": 12.0,
            "unit_label": "pcs",
            "weight": "150g",
            "volume": "",
            "manufacturer": "Colgate-Palmolive India",
            "country_of_origin": "India",
            "description": "Amino Shakti formula that provides 2x stronger teeth and cavity defense.",
            "ingredients": "Calcium Carbonate, Sodium Monofluorophosphate, Arginine",
            "nutritional_info": "Contains 1000 ppm available fluoride",
            "expiry_date": (today + timedelta(days=365)).isoformat(),
            "mfg_date": (today - timedelta(days=30)).isoformat(),
            "batch_number": "COL-ST-150",
        },
        {
            "name": "Head & Shoulders Cool Menthol Anti-Dandruff Shampoo (340ml)",
            "category": "Personal Care",
            "sub_category": "Hair Care",
            "brand": "Head & Shoulders",
            "code_value": "8901030800115",
            "code_type": "EAN13",
            "unit_price": 310.0,
            "cost_price": 242.0,
            "mrp": 350.0,
            "stock_qty": 3.0,  # LOW STOCK trigger
            "reorder_level": 8.0,
            "unit_label": "pcs",
            "weight": "360g",
            "volume": "340 ml",
            "manufacturer": "Procter & Gamble Hygiene",
            "country_of_origin": "India",
            "description": "Menthol blast gives intense cooling sensation while eliminating visible flakes.",
            "ingredients": "Zinc Pyrithione, Menthol, Sodium Laureth Sulfate",
            "nutritional_info": "Clinically proven dandruff control",
            "expiry_date": (today + timedelta(days=500)).isoformat(),
            "mfg_date": (today - timedelta(days=60)).isoformat(),
            "batch_number": "HS-CM-340",
        },
        {
            "name": "Nivea Soft Light Moisturizer Face & Body Cream (200ml)",
            "category": "Personal Care",
            "sub_category": "Skin Care",
            "brand": "Nivea",
            "code_value": "8901030600104",
            "code_type": "EAN13",
            "unit_price": 280.0,
            "cost_price": 218.0,
            "mrp": 320.0,
            "stock_qty": 22.0,
            "reorder_level": 6.0,
            "unit_label": "pcs",
            "weight": "220g",
            "volume": "200 ml",
            "manufacturer": "Nivea India Pvt Ltd",
            "country_of_origin": "India",
            "description": "Quick-absorbing moisturizing cream infused with Jojoba Oil & Vitamin E.",
            "ingredients": "Aqua, Jojoba Oil, Tocopheryl Acetate (Vitamin E), Glycerin",
            "nutritional_info": "Dermatologically tested for all skin types",
            "expiry_date": (today + timedelta(days=450)).isoformat(),
            "mfg_date": (today - timedelta(days=50)).isoformat(),
            "batch_number": "NIV-SFT-200",
        },

        # --- HOUSEHOLD & CLEANING ---
        {
            "name": "Surf Excel Easy Wash Detergent Powder (1 kg)",
            "category": "Household",
            "sub_category": "Laundry Detergent",
            "brand": "Surf Excel",
            "code_value": "8901030383427",
            "code_type": "EAN13",
            "unit_price": 140.0,
            "cost_price": 112.0,
            "mrp": 155.0,
            "stock_qty": 60.0,
            "reorder_level": 15.0,
            "unit_label": "kg",
            "weight": "1 kg",
            "volume": "",
            "manufacturer": "Hindustan Unilever Limited",
            "country_of_origin": "India",
            "description": "Fast-acting stain removal technology dissolves tough grease and dirt in minutes.",
            "ingredients": "Linear Alkyl Benzene Sulphonate, Soda Ash, Optical Brighteners",
            "nutritional_info": "Non-food household product",
            "expiry_date": (today + timedelta(days=600)).isoformat(),
            "mfg_date": (today - timedelta(days=40)).isoformat(),
            "batch_number": "SX-EW-1K",
        },
        {
            "name": "Vim Dishwash Liquid Gel Lemon (750ml)",
            "category": "Household",
            "sub_category": "Dishwashing",
            "brand": "Vim",
            "code_value": "8901030300127",
            "code_type": "EAN13",
            "unit_price": 165.0,
            "cost_price": 130.0,
            "mrp": 180.0,
            "stock_qty": 34.0,
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "800g",
            "volume": "750 ml",
            "manufacturer": "Hindustan Unilever Limited",
            "country_of_origin": "India",
            "description": "Infused with power of 100 lemons, cleans oily utensils with single drop.",
            "ingredients": "Anionic Surfactants, Lemon Extracts, Color, Preservatives",
            "nutritional_info": "pH balanced dishwashing liquid",
            "expiry_date": (today + timedelta(days=550)).isoformat(),
            "mfg_date": (today - timedelta(days=50)).isoformat(),
            "batch_number": "VIM-GEL-750",
        },
        {
            "name": "Lizol Disinfectant Surface Cleaner Citrus (1 L)",
            "category": "Household",
            "sub_category": "Floor Cleaners",
            "brand": "Lizol",
            "code_value": "8901396123450",
            "code_type": "EAN13",
            "unit_price": 190.0,
            "cost_price": 150.0,
            "mrp": 210.0,
            "stock_qty": 29.0,
            "reorder_level": 8.0,
            "unit_label": "ltr",
            "weight": "1.05 kg",
            "volume": "1 L",
            "manufacturer": "Reckitt Benckiser India",
            "country_of_origin": "India",
            "description": "Kills 99.9% germs, removes 100 types of stains with refreshing citrus aroma.",
            "ingredients": "Benzalkonium Chloride solution, Non-ionic surfactant, Citrus Perfume",
            "nutritional_info": "Triple action floor disinfectant",
            "expiry_date": (today + timedelta(days=500)).isoformat(),
            "mfg_date": (today - timedelta(days=45)).isoformat(),
            "batch_number": "LZL-CIT-1L",
        },
        {
            "name": "Harpic Power Plus Toilet Cleaner Original (500ml)",
            "category": "Household",
            "sub_category": "Toilet Cleaners",
            "brand": "Harpic",
            "code_value": "8901396543210",
            "code_type": "EAN13",
            "unit_price": 95.0,
            "cost_price": 75.0,
            "mrp": 105.0,
            "stock_qty": 40.0,
            "reorder_level": 10.0,
            "unit_label": "pcs",
            "weight": "550g",
            "volume": "500 ml",
            "manufacturer": "Reckitt Benckiser India",
            "country_of_origin": "India",
            "description": "10x better stain cleaner with thick formula that clings to surfaces.",
            "ingredients": "Hydrochloric Acid 10.5%, Cationic Surfactant, Acid Blue 80",
            "nutritional_info": "Disinfectant toilet cleaner",
            "expiry_date": (today + timedelta(days=600)).isoformat(),
            "mfg_date": (today - timedelta(days=30)).isoformat(),
            "batch_number": "HRP-PWR-500",
        },

        # --- SPECIALTY: DEAD STOCK & SLOW MOVING DEMO ITEMS ---
        {
            "name": "Specialty Quinoa Gourmet Superfood Grain (500g)",
            "category": "Groceries",
            "sub_category": "Specialty Foods",
            "brand": "Gourmet Garden",
            "code_value": "8909999000012",
            "code_type": "EAN13",
            "unit_price": 380.0,
            "cost_price": 290.0,
            "mrp": 425.0,
            "stock_qty": 32.0,  # ZERO SALES over 60 days -> DEAD STOCK DEMO
            "reorder_level": 6.0,
            "unit_label": "pcs",
            "weight": "500g",
            "volume": "",
            "manufacturer": "Organic Andes Imports",
            "country_of_origin": "Peru",
            "description": "Imported organic white royal quinoa rich in complete plant protein and amino acids.",
            "ingredients": "100% Organic White Quinoa Seeds",
            "nutritional_info": "Per 100g: Protein 14g, Fiber 7g, Energy 368 kcal",
            "expiry_date": (today + timedelta(days=300)).isoformat(),
            "mfg_date": (today - timedelta(days=90)).isoformat(),
            "batch_number": "QNA-SPEC-01",
        },
        {
            "name": "Organic Chamomile Pure Herbal Tea Bags (25 count)",
            "category": "Beverages",
            "sub_category": "Herbal Tea",
            "brand": "Gourmet Garden",
            "code_value": "8909999000029",
            "code_type": "EAN13",
            "unit_price": 260.0,
            "cost_price": 195.0,
            "mrp": 299.0,
            "stock_qty": 24.0,  # VERY FEW SALES (<0.3 units/day) -> SLOW MOVING DEMO
            "reorder_level": 5.0,
            "unit_label": "pcs",
            "weight": "50g",
            "volume": "",
            "manufacturer": "Himalayan Herbal Teas Ltd",
            "country_of_origin": "India",
            "description": "Naturally caffeine-free golden chamomile blossom herbal infusion for calm evenings.",
            "ingredients": "100% Pure Chamomile Flowers",
            "nutritional_info": "Zero calories, soothing apigenin flavonoids",
            "expiry_date": (today + timedelta(days=280)).isoformat(),
            "mfg_date": (today - timedelta(days=60)).isoformat(),
            "batch_number": "CHAM-TB-25",
        },
    ]


def ensure_products_schema(conn):
    """Ensures products table supports multi-tenancy with per-user unique barcodes instead of obsolete global unique."""
    try:
        sql_row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'").fetchone()
        if not sql_row or not sql_row[0]:
            return
        sql = sql_row[0]
        # Check if code_value has a global UNIQUE constraint
        if "code_value      TEXT UNIQUE" in sql or "code_value TEXT UNIQUE" in sql:
            print("Upgrading products table schema to support multi-tenant barcodes...")
            conn.execute("PRAGMA foreign_keys = OFF")
            cols = [r[1] for r in conn.execute("PRAGMA table_info(products)").fetchall()]
            col_str = ", ".join(cols)
            conn.executescript(f"""
                CREATE TABLE IF NOT EXISTS products_new (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id         INTEGER NOT NULL DEFAULT 1,
                    name            TEXT NOT NULL,
                    category        TEXT DEFAULT 'General',
                    code_value      TEXT,
                    code_type       TEXT DEFAULT 'CODE128',
                    unit_price      REAL NOT NULL DEFAULT 0,
                    cost_price      REAL NOT NULL DEFAULT 0,
                    stock_qty       REAL NOT NULL DEFAULT 0,
                    unit_label      TEXT DEFAULT 'pcs',
                    reorder_level   REAL NOT NULL DEFAULT 5,
                    created_at      TEXT NOT NULL,
                    updated_at      TEXT NOT NULL,
                    brand           TEXT DEFAULT '',
                    sub_category    TEXT DEFAULT '',
                    description     TEXT DEFAULT '',
                    image_url       TEXT DEFAULT '',
                    expiry_date     TEXT DEFAULT '',
                    mfg_date        TEXT DEFAULT '',
                    batch_number    TEXT DEFAULT '',
                    serial_number   TEXT DEFAULT '',
                    weight          TEXT DEFAULT '',
                    volume          TEXT DEFAULT '',
                    mrp             REAL DEFAULT 0,
                    manufacturer    TEXT DEFAULT '',
                    country_of_origin TEXT DEFAULT '',
                    ingredients     TEXT DEFAULT '',
                    nutritional_info TEXT DEFAULT '',
                    dimensions      TEXT DEFAULT '',
                    color           TEXT DEFAULT '',
                    size_label      TEXT DEFAULT '',
                    warranty_info   TEXT DEFAULT '',
                    supplier_details TEXT DEFAULT '',
                    barcode_raw     TEXT DEFAULT '',
                    source_db       TEXT DEFAULT '',
                    UNIQUE(user_id, code_value)
                );
                INSERT INTO products_new ({col_str}) SELECT {col_str} FROM products;
                DROP TABLE products;
                ALTER TABLE products_new RENAME TO products;
                CREATE INDEX IF NOT EXISTS idx_products_user ON products(user_id);
            """)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            print("Products schema successfully upgraded!")
    except Exception as e:
        print(f"Notice during schema check: {e}")


def seed_data_for_user(conn, user_id, clean=False):
    """Seed comprehensive test & demo data for a specific user_id."""
    print(f"\n--- Seeding demonstration data for User ID: {user_id} ---")
    
    if clean:
        print(f"Cleaning existing transaction, inventory, and warehouse data for user {user_id}...")
        conn.execute("DELETE FROM expiry_alerts WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM warehouse_transfers WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM purchase_order_items WHERE po_id IN (SELECT id FROM purchase_orders WHERE user_id = ?)", (user_id,))
        conn.execute("DELETE FROM purchase_orders WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM stock_adjustments WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM ai_agent_log WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM transaction_items WHERE transaction_id IN (SELECT id FROM transactions WHERE user_id = ?)", (user_id,))
        conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM product_warehouse WHERE warehouse_id IN (SELECT id FROM warehouses WHERE user_id = ?)", (user_id,))
        conn.execute("DELETE FROM warehouses WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM products WHERE user_id = ?", (user_id,))
        conn.commit()

    # 1. Ensure realistic store settings
    store_settings = {
        "business_name": "Apex AI Supermarket",
        "business_address": "Plot 42, Tech City Road, Knowledge Park, New Delhi 110001",
        "business_phone": "+91 98765 43210",
        "currency_symbol": "₹",
        "default_tax_rate": "5",
        "low_stock_default": "8",
        "preferred_code_type": "EAN13",
        "invoice_prefix": "INV",
        "invoice_counter": "2000",
        "lead_time_days": "3",
        "safety_stock_multiplier": "1.5",
        "dead_stock_days": "60",
        "slow_moving_days": "30",
        "po_prefix": "PO",
        "po_counter": "100",
    }
    for k, v in store_settings.items():
        conn.execute(
            """INSERT INTO settings (key, value, user_id) VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value, user_id = excluded.user_id""",
            (k, v, user_id)
        )
    conn.commit()

    # 2. Insert Products
    print("Inserting 28 retail products...")
    raw_products = get_products_data()
    inserted_products = []
    
    for p in raw_products:
        # Check if already exists for this user by barcode
        existing = conn.execute(
            "SELECT id FROM products WHERE user_id = ? AND code_value = ?",
            (user_id, p["code_value"])
        ).fetchone()
        
        now = db.now_iso()
        if existing:
            pid = existing["id"]
            conn.execute(
                """UPDATE products SET name=?, category=?, sub_category=?, brand=?,
                   unit_price=?, cost_price=?, mrp=?, stock_qty=?, reorder_level=?,
                   unit_label=?, weight=?, volume=?, manufacturer=?, country_of_origin=?,
                   description=?, ingredients=?, nutritional_info=?, expiry_date=?,
                   mfg_date=?, batch_number=?, updated_at=?
                   WHERE id = ?""",
                (p["name"], p["category"], p["sub_category"], p["brand"],
                 p["unit_price"], p["cost_price"], p["mrp"], p["stock_qty"], p["reorder_level"],
                 p["unit_label"], p["weight"], p["volume"], p["manufacturer"], p["country_of_origin"],
                 p["description"], p["ingredients"], p["nutritional_info"], p["expiry_date"],
                 p["mfg_date"], p["batch_number"], now, pid)
            )
        else:
            cur = conn.execute(
                """INSERT INTO products (
                    user_id, name, category, sub_category, brand, code_value, code_type,
                    unit_price, cost_price, mrp, stock_qty, reorder_level, unit_label,
                    weight, volume, manufacturer, country_of_origin, description,
                    ingredients, nutritional_info, expiry_date, mfg_date, batch_number,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, p["name"], p["category"], p["sub_category"], p["brand"],
                 p["code_value"], p["code_type"], p["unit_price"], p["cost_price"], p["mrp"],
                 p["stock_qty"], p["reorder_level"], p["unit_label"], p["weight"], p["volume"],
                 p["manufacturer"], p["country_of_origin"], p["description"], p["ingredients"],
                 p["nutritional_info"], p["expiry_date"], p["mfg_date"], p["batch_number"],
                 now, now)
            )
            pid = cur.lastrowid
            
        p_dict = dict(p)
        p_dict["id"] = pid
        inserted_products.append(p_dict)
        
        # Populate expiry alerts table
        exp_status, days_rem = db.get_expiry_status(p["expiry_date"])
        if exp_status:
            conn.execute("DELETE FROM expiry_alerts WHERE user_id = ? AND product_id = ?", (user_id, pid))
            conn.execute(
                """INSERT INTO expiry_alerts (user_id, product_id, expiry_date, status, notified, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, pid, p["expiry_date"], exp_status, 1 if exp_status == "expired" else 0, now)
            )
            
        # Seed barcode_cache for offline fast scan
        cache_data = {
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "sub_category": p["sub_category"],
            "unit_price": p["unit_price"],
            "mrp": p["mrp"],
            "weight": p["weight"],
            "volume": p["volume"],
            "manufacturer": p["manufacturer"],
            "country_of_origin": p["country_of_origin"],
            "ingredients": p["ingredients"],
            "nutritional_info": p["nutritional_info"],
            "barcode": p["code_value"],
        }
        conn.execute(
            """INSERT INTO barcode_cache (barcode, data, source, cached_at)
               VALUES (?, ?, 'seeded_catalog', ?)
               ON CONFLICT(barcode) DO UPDATE SET data=excluded.data, cached_at=excluded.cached_at""",
            (p["code_value"], json.dumps(cache_data), now)
        )

    conn.commit()

    # 3. Insert Multi-Warehouse Architecture
    print("Setting up 3 multi-warehouses and stock distributions...")
    wh_suffix = f" (Unit {user_id})" if user_id > 1 else ""
    wh_defs = [
        {"name": f"Central Distribution Hub{wh_suffix}", "location": "Sector 62 Logistics Park, Noida", "is_default": 1},
        {"name": f"Downtown Retail Storefront{wh_suffix}", "location": "Connaught Place, Block B, New Delhi", "is_default": 0},
        {"name": f"West Regional Depot{wh_suffix}", "location": "Ring Road Freight Complex, Gurgaon", "is_default": 0},
    ]
    
    warehouses = []
    for wd in wh_defs:
        wh_row = conn.execute(
            "SELECT id FROM warehouses WHERE user_id = ? AND name = ?",
            (user_id, wd["name"])
        ).fetchone()
        if not wh_row:
            cur = conn.execute(
                "INSERT INTO warehouses (user_id, name, location, is_default, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, wd["name"], wd["location"], wd["is_default"], db.now_iso())
            )
            wh_id = cur.lastrowid
        else:
            wh_id = wh_row["id"]
        warehouses.append({"id": wh_id, **wd})
    conn.commit()

    wh_central = warehouses[0]["id"]
    wh_retail = warehouses[1]["id"]
    wh_west = warehouses[2]["id"]

    # Distribute product stock across warehouses
    # Specific setup to trigger AI Multi-Warehouse Optimizer:
    # Overstocked in Central Hub, understocked (< reorder_level) in Retail Storefront
    for idx, p in enumerate(inserted_products):
        pid = p["id"]
        total_stock = p["stock_qty"]
        reorder = p["reorder_level"]
        
        if idx % 3 == 0:
            # Overstock in Central (75%), Understock in Retail (5%), Rest in West (20%)
            c_qty = round(total_stock * 0.75, 1)
            r_qty = round(min(total_stock * 0.05, reorder * 0.3), 1)  # Trigger understocked transfer!
            w_qty = round(total_stock - c_qty - r_qty, 1)
        elif idx % 3 == 1:
            # Balanced distribution
            c_qty = round(total_stock * 0.50, 1)
            r_qty = round(total_stock * 0.35, 1)
            w_qty = round(total_stock - c_qty - r_qty, 1)
        else:
            # Retail store prioritized
            c_qty = round(total_stock * 0.30, 1)
            r_qty = round(total_stock * 0.55, 1)
            w_qty = round(total_stock - c_qty - r_qty, 1)

        for w_id, s_qty in [(wh_central, max(0.0, c_qty)), (wh_retail, max(0.0, r_qty)), (wh_west, max(0.0, w_qty))]:
            conn.execute(
                """INSERT INTO product_warehouse (product_id, warehouse_id, stock_qty)
                   VALUES (?, ?, ?)
                   ON CONFLICT(product_id, warehouse_id) DO UPDATE SET stock_qty = excluded.stock_qty""",
                (pid, w_id, s_qty)
            )
    
    # Add historical warehouse transfers
    transfers = [
        {"pid": inserted_products[0]["id"], "from_wh": wh_central, "to_wh": wh_retail, "qty": 15, "reason": "Weekly storefront inventory replenishment", "days_ago": 7},
        {"pid": inserted_products[5]["id"], "from_wh": wh_central, "to_wh": wh_retail, "qty": 20, "reason": "AI-optimized transfer to avoid stockout", "days_ago": 4},
        {"pid": inserted_products[11]["id"], "from_wh": wh_west, "to_wh": wh_central, "qty": 10, "reason": "Regional stock consolidation", "days_ago": 2},
    ]
    for tr in transfers:
        created = (datetime.now() - timedelta(days=tr["days_ago"], hours=3)).isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO warehouse_transfers (user_id, product_id, from_warehouse, to_warehouse, quantity, reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, tr["pid"], tr["from_wh"], tr["to_wh"], tr["qty"], tr["reason"], created)
        )
    conn.commit()

    # 4. Generate 85+ Realistic Invoices over the past 45 days
    print("Generating 85+ realistic transactions across the past 45 days (including today)...")
    
    customers = [
        "Rahul Sharma", "Priya Patel", "Amit Verma", "Sneha Rao", "Vikram Singh",
        "Deepak Gupta", "Pooja Malhotra", "Ananya Deshmukh", "Rajesh Iyer", "Sunita Nair",
        "Karan Mehra", "Meera Joshi", "Arjun Kapoor", "Walk-in Customer", "Walk-in Customer"
    ]
    pay_methods = ["UPI", "UPI", "UPI", "Cash", "Cash", "Card"]
    
    # Products eligible for regular sales (excluding dead stock item, and minimal sales for slow item)
    active_products = [p for p in inserted_products if "Quinoa" not in p["name"]]
    dead_stock_prod = [p for p in inserted_products if "Quinoa" in p["name"]][0]
    slow_prod = [p for p in inserted_products if "Chamomile" in p["name"]][0]

    invoice_counter = 1000 * user_id + 1
    now_dt = datetime.now()

    # Distribute transactions across days: 45 days ago up to Day 0 (today)
    # Day 0 (Today): 5 transactions
    # Day 1 (Yesterday): 4 transactions
    # Days 2 to 13: 2 to 4 transactions per day (guarantees a full 14-day trend line)
    # Days 14 to 45: 1 to 3 transactions per day
    for day_offset in range(45, -1, -1):
        target_date = now_dt.date() - timedelta(days=day_offset)
        
        if day_offset == 0:
            tx_count_for_day = 5  # Today has 5 transactions
        elif day_offset == 1:
            tx_count_for_day = 4  # Yesterday has 4
        elif day_offset <= 13:
            tx_count_for_day = random.randint(2, 4)
        else:
            tx_count_for_day = random.randint(1, 3)

        for t_idx in range(tx_count_for_day):
            # Spread transactions between 9 AM and 8 PM
            hour = 9 + int((11 / max(1, tx_count_for_day)) * t_idx) + random.randint(0, 1)
            minute = random.randint(5, 55)
            second = random.randint(10, 50)
            
            # If today, don't generate in the future
            if day_offset == 0 and hour >= now_dt.hour:
                hour = max(8, now_dt.hour - 1 - (4 - t_idx))
                
            tx_time = datetime(target_date.year, target_date.month, target_date.day, hour % 24, minute, second)
            created_iso = tx_time.isoformat(timespec="seconds")
            
            invoice_no = f"INV-{invoice_counter}"
            invoice_counter += 1
            customer = random.choice(customers)
            pay_method = random.choice(pay_methods)
            
            # Pick 1 to 4 items for this invoice
            num_items = random.choices([1, 2, 3, 4], weights=[35, 40, 18, 7])[0]
            sampled_items = random.sample(active_products, num_items)
            
            # Add one slow-moving item on only 2 occasions across the entire 45 days
            if day_offset in [10, 25] and t_idx == 0:
                sampled_items.append(slow_prod)
                
            subtotal = 0.0
            line_items = []
            
            for item in sampled_items:
                # Quantities: usually 1 to 3 units
                qty = float(random.choices([1, 2, 3], weights=[70, 22, 8])[0])
                price = float(item["unit_price"])
                line_tot = round(qty * price, 2)
                subtotal += line_tot
                line_items.append((item["id"], item["name"], qty, price, line_tot))

            # Discount logic: normally 0, occasionally small, one anomaly discount
            discount = 0.0
            if day_offset == 3 and t_idx == 0:
                # Anomaly discount: 35% off on a big bill (triggers AI discount anomaly)
                discount = round(subtotal * 0.35, 2)
            elif random.random() < 0.15:
                discount = round(subtotal * 0.05, 2)

            tax = round((subtotal - discount) * 0.05, 2)
            total = round(subtotal - discount + tax, 2)

            cur = conn.execute(
                """INSERT INTO transactions (user_id, invoice_no, created_at, subtotal, discount, tax, total, payment_method, customer_name)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, invoice_no, created_iso, subtotal, discount, tax, total, pay_method, customer)
            )
            tx_id = cur.lastrowid

            for pid, pname, qty, uprice, ltot in line_items:
                conn.execute(
                    """INSERT INTO transaction_items (transaction_id, product_id, product_name, quantity, unit_price, line_total)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (tx_id, pid, pname, qty, uprice, ltot)
                )

    conn.commit()

    # 5. Insert Stock Adjustments (including 1 shrinkage anomaly)
    print("Recording inventory adjustments and audit reconciliation...")
    adjustments = [
        {"pid": inserted_products[1]["id"], "qty": -3.0, "reason": "Damaged in transit / packaging dent", "days_ago": 15},
        {"pid": inserted_products[6]["id"], "qty": 10.0, "reason": "Physical stock count reconciliation audit", "days_ago": 8},
        {"pid": inserted_products[3]["id"], "qty": -18.0, "reason": "Water pipe leak damage in backroom shelf B", "days_ago": 4},  # Anomaly shrinkage
    ]
    for sa in adjustments:
        adj_time = (now_dt - timedelta(days=sa["days_ago"], hours=2)).isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO stock_adjustments (user_id, product_id, change_qty, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, sa["pid"], sa["qty"], sa["reason"], adj_time)
        )
    conn.commit()

    # 6. Purchase Orders
    print("Creating purchase orders across draft, approved, and received statuses...")
    pos = [
        {
            "number": f"PO-{user_id:02d}01",
            "status": "received",
            "supplier": "Amul Dairy & Provisions Wholesale",
            "total": 14250.0,
            "notes": "Monthly recurring dairy and butter procurement",
            "days_ago": 18,
            "items": [
                {"pid": inserted_products[15]["id"], "name": inserted_products[15]["name"], "qty": 30, "cost": 235.0},
                {"pid": inserted_products[17]["id"], "name": inserted_products[17]["name"], "qty": 40, "cost": 76.0},
                {"pid": inserted_products[16]["id"], "name": inserted_products[16]["name"], "qty": 50, "cost": 61.0},
            ]
        },
        {
            "number": f"PO-{user_id:02d}02",
            "status": "approved",
            "supplier": "Nestle & Britannia Regional Distributor",
            "total": 18600.0,
            "notes": "Fast-moving packaged snacks replenishment order",
            "days_ago": 5,
            "items": [
                {"pid": inserted_products[5]["id"], "name": inserted_products[5]["name"], "qty": 100, "cost": 44.0},
                {"pid": inserted_products[11]["id"], "name": inserted_products[11]["name"], "qty": 35, "cost": 270.0},
                {"pid": inserted_products[6]["id"], "name": inserted_products[6]["name"], "qty": 80, "cost": 23.5},
            ]
        },
        {
            "number": f"PO-{user_id:02d}03",
            "status": "draft",
            "supplier": "Tata FMCG Wholesale Hub",
            "total": 12850.0,
            "notes": "AI-generated restock recommendation draft for low-stock staples",
            "days_ago": 1,
            "items": [
                {"pid": inserted_products[10]["id"], "name": inserted_products[10]["name"], "qty": 30, "cost": 255.0},
                {"pid": inserted_products[4]["id"], "name": inserted_products[4]["name"], "qty": 35, "cost": 142.0},
            ]
        },
    ]

    for po in pos:
        po_created = (now_dt - timedelta(days=po["days_ago"], hours=4)).isoformat(timespec="seconds")
        cur = conn.execute(
            """INSERT INTO purchase_orders (user_id, po_number, status, supplier_name, total_cost, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, po["number"], po["status"], po["supplier"], po["total"], po["notes"], po_created, po_created)
        )
        poid = cur.lastrowid
        for itm in po["items"]:
            lt = round(itm["qty"] * itm["cost"], 2)
            conn.execute(
                """INSERT INTO purchase_order_items (po_id, product_id, product_name, quantity, unit_cost, line_total)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (poid, itm["pid"], itm["name"], itm["qty"], itm["cost"], lt)
            )
    conn.commit()

    # 7. Seed AI Agent Action Log
    print("Populating AI agent action history...")
    ai_logs = [
        {"action": "nlp", "summary": "NLP: show low stock", "details": 'Found 4 product(s) at or below reorder level.', "hours_ago": 2},
        {"action": "nlp", "summary": "NLP: sales today", "details": 'Calculated live revenue for today.', "hours_ago": 4},
        {"action": "po", "summary": "Generated 2 purchase orders", "details": 'Auto-drafted purchase orders for Dairy and Staples categories.', "hours_ago": 24},
        {"action": "transfer", "summary": "Transferred 15 units", "details": 'Balanced stock between Central Hub and Downtown Store.', "hours_ago": 48},
        {"action": "nlp", "summary": "NLP: demand forecast", "details": 'Calculated 30-day demand predictions using trained ML model.', "hours_ago": 72},
        {"action": "nlp", "summary": "NLP: check health", "details": 'Inventory health check: 2 critical, 3 warning, 23 safe.', "hours_ago": 96},
    ]
    for log in ai_logs:
        log_time = (now_dt - timedelta(hours=log["hours_ago"])).isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO ai_agent_log (user_id, action_type, summary, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, log["action"], log["summary"], log["details"], log_time)
        )
    conn.commit()
    print(f"Successfully seeded demonstration data for User {user_id}!")


def main():
    parser = argparse.ArgumentParser(description="Seed realistic dummy content for billing & AI inventory software.")
    parser.add_argument("--user", type=int, default=None, help="Target specific user_id (default: seeds user 1 and user 2)")
    parser.add_argument("--clean", action="store_true", help="Wipe existing inventory & transaction records for the targeted user before seeding")
    parser.add_argument("--no-ml", action="store_true", help="Skip machine learning model training")
    args = parser.parse_args()

    conn = db.get_connection()
    
    # Target users
    if args.user:
        target_users = [args.user]
    else:
        # Check users in database
        existing_users = [row["id"] for row in conn.execute("SELECT id FROM users ORDER BY id ASC").fetchall()]
        if not existing_users:
            db.init_db()
            existing_users = [1]
        # Seed user 1 (admin) and user 2 (if present)
        target_users = [uid for uid in [1, 2] if uid in existing_users]
        if not target_users:
            target_users = [existing_users[0]]

    # Ensure schema supports per-user barcodes
    ensure_products_schema(conn)

    for uid in target_users:
        seed_data_for_user(conn, uid, clean=args.clean)

    # 8. Train Machine Learning Demand Forecasting Model
    if not args.no_ml:
        print("\n--- Training Offline Random Forest Demand Forecasting Model ---")
        try:
            train_res = ml_train.train_model(conn)
            print("ML Training Status:", train_res.get("status"))
            if train_res.get("status") == "trained":
                print(f"  Rows Trained: {train_res.get('rows_available')}")
                print(f"  Distinct Days: {train_res.get('distinct_days')}")
                print(f"  Mean Absolute Error (MAE): {train_res.get('mean_absolute_error')}")
                print(f"  Products Covered: {train_res.get('products_covered')}")
            else:
                print("  Notice:", train_res.get("reason"))
        except Exception as e:
            print("ML Training Warning:", e)

    conn.close()
    print("\n[SUCCESS] Dummy data seeding and ML training complete! The system is now ready for testing and demonstration.")


if __name__ == "__main__":
    main()
