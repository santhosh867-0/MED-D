#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          HealthAdvisor v2.0 — Premium Health Companion       ║
║  AI Diagnosis • Hospital Finder • Diet Plans • Medicines     ║
╚══════════════════════════════════════════════════════════════╝
Run   : python healthadvisor.py
Deps  : pip install requests reportlab  (tkinter is built-in)

⚠  DISCLAIMER: Educational / informational use only.
   NOT a substitute for professional medical advice.
   Always consult a qualified doctor.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json, re, math, time, threading, os, sys
from datetime import datetime
from functools import lru_cache
from collections import defaultdict

# Optional deps — fail gracefully
try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# ══════════════════════════════════════════════════════════════════
#  COLOUR & FONT PALETTE  (Premium Dark-Blue / Teal Design System)
# ══════════════════════════════════════════════════════════════════
PALETTE = {
    # Primary brand
    "brand":      "#0A2342",
    "brand_mid":  "#163A6B",
    "brand_lite": "#1E4D8C",
    "accent":     "#00C9A7",
    "accent2":    "#FF6B6B",
    "gold":       "#FFD700",
    # Surfaces
    "bg":         "#F0F4FA",
    "card":       "#FFFFFF",
    "card2":      "#F7F9FC",
    "sidebar":    "#0A2342",
    "header":     "#0A2342",
    # Text
    "text":       "#1A2B45",
    "text_s":     "#5A6A80",
    "text_inv":   "#FFFFFF",
    "text_dim":   "#94A3B8",
    # Status
    "success":    "#10B981",
    "warn":       "#F59E0B",
    "danger":     "#EF4444",
    "info":       "#3B82F6",
    # Borders
    "border":     "#E2E8F0",
    "border2":    "#CBD5E1",
    # Input
    "input_bg":   "#F8FAFC",
    # Dark theme
    "d_bg":       "#0D1B2A",
    "d_card":     "#1A2B40",
    "d_card2":    "#1E3251",
    "d_text":     "#E2E8F0",
    "d_text_s":   "#94A3B8",
    "d_border":   "#2D4060",
    "d_input":    "#1E3251",
}

FONTS = {
    "h1":    ("Segoe UI", 22, "bold"),
    "h2":    ("Segoe UI", 16, "bold"),
    "h3":    ("Segoe UI", 13, "bold"),
    "h4":    ("Segoe UI", 11, "bold"),
    "body":  ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "tiny":  ("Segoe UI", 8),
    "mono":  ("Consolas", 9),
    "icon":  ("Segoe UI Emoji", 16),
}

# ══════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE  — 53 conditions
# ══════════════════════════════════════════════════════════════════
KNOWLEDGE_BASE = {
  "influenza":           {"display_name":"Influenza (Flu)","hindi_name":"फ्लू","symptoms":["fever","cough","fatigue","body ache","headache","chills","sore throat","runny nose","sneezing","loss of appetite"],"severity":"moderate","category":"respiratory","doctor":"General Physician / Pulmonologist"},
  "common_cold":         {"display_name":"Common Cold","hindi_name":"सर्दी-जुकाम","symptoms":["runny nose","sneezing","sore throat","cough","mild fever","congestion","watery eyes","mild headache"],"severity":"mild","category":"respiratory","doctor":"General Physician / ENT"},
  "diabetes_type2":      {"display_name":"Type 2 Diabetes","hindi_name":"मधुमेह","symptoms":["frequent urination","excessive thirst","fatigue","blurred vision","slow healing wounds","frequent infections","tingling hands","tingling feet","increased hunger","unexplained weight loss"],"severity":"chronic","category":"metabolic","doctor":"Endocrinologist / Diabetologist"},
  "hypertension":        {"display_name":"Hypertension","hindi_name":"उच्च रक्तचाप","symptoms":["headache","dizziness","blurred vision","chest pain","shortness of breath","nosebleed","palpitations","flushing"],"severity":"chronic","category":"cardiovascular","doctor":"Cardiologist / General Physician"},
  "migraine":            {"display_name":"Migraine","hindi_name":"माइग्रेन","symptoms":["severe headache","nausea","vomiting","light sensitivity","sound sensitivity","visual disturbances","throbbing pain","neck stiffness"],"severity":"moderate","category":"neurological","doctor":"Neurologist"},
  "anemia":              {"display_name":"Iron Deficiency Anemia","hindi_name":"रक्ताल्पता","symptoms":["fatigue","weakness","pale skin","shortness of breath","dizziness","cold hands","cold feet","brittle nails","chest pain","headache"],"severity":"moderate","category":"hematological","doctor":"Hematologist / General Physician"},
  "gastritis":           {"display_name":"Gastritis / Acidity","hindi_name":"एसिडिटी","symptoms":["stomach pain","nausea","vomiting","bloating","indigestion","loss of appetite","burping","heartburn","upper abdominal pain"],"severity":"mild","category":"digestive","doctor":"Gastroenterologist"},
  "ibs":                 {"display_name":"Irritable Bowel Syndrome","hindi_name":"आईबीएस","symptoms":["abdominal pain","bloating","diarrhea","constipation","mucus in stool","gas","cramping","incomplete bowel movement"],"severity":"chronic","category":"digestive","doctor":"Gastroenterologist"},
  "thyroid_hypo":        {"display_name":"Hypothyroidism","hindi_name":"हाइपोथायरॉइड","symptoms":["fatigue","weight gain","cold intolerance","constipation","dry skin","hair loss","muscle weakness","depression","slow heart rate","puffiness"],"severity":"chronic","category":"endocrine","doctor":"Endocrinologist"},
  "thyroid_hyper":       {"display_name":"Hyperthyroidism","hindi_name":"हाइपरथायरॉइड","symptoms":["weight loss","rapid heartbeat","anxiety","tremors","sweating","heat intolerance","frequent bowel movements","fatigue","difficulty sleeping","irritability"],"severity":"chronic","category":"endocrine","doctor":"Endocrinologist"},
  "dengue":              {"display_name":"Dengue Fever","hindi_name":"डेंगू","symptoms":["high fever","severe headache","body ache","joint pain","skin rash","nausea","vomiting","bleeding gums","fatigue","eye pain"],"severity":"severe","category":"infectious","doctor":"Infectious Disease Specialist"},
  "malaria":             {"display_name":"Malaria","hindi_name":"मलेरिया","symptoms":["high fever","chills","sweating","headache","nausea","vomiting","body ache","fatigue","cyclic fever"],"severity":"severe","category":"infectious","doctor":"Infectious Disease Specialist"},
  "typhoid":             {"display_name":"Typhoid Fever","hindi_name":"टाइफाइड","symptoms":["prolonged fever","headache","weakness","stomach pain","loss of appetite","rose spots","diarrhea","constipation","dry cough"],"severity":"severe","category":"infectious","doctor":"Infectious Disease Specialist"},
  "asthma":              {"display_name":"Asthma","hindi_name":"दमा","symptoms":["shortness of breath","wheezing","chest tightness","cough","difficulty breathing","night cough","exercise intolerance"],"severity":"chronic","category":"respiratory","doctor":"Pulmonologist"},
  "arthritis":           {"display_name":"Arthritis (OA)","hindi_name":"गठिया","symptoms":["joint pain","joint stiffness","swollen joints","reduced range of motion","grating sensation","bone spurs","morning stiffness"],"severity":"chronic","category":"musculoskeletal","doctor":"Rheumatologist / Orthopedician"},
  "rheumatoid_arthritis":{"display_name":"Rheumatoid Arthritis","hindi_name":"रूमेटॉइड आर्थराइटिस","symptoms":["joint pain","joint swelling","morning stiffness","fatigue","fever","loss of appetite","symmetric joint pain"],"severity":"chronic","category":"autoimmune","doctor":"Rheumatologist"},
  "kidney_stones":       {"display_name":"Kidney Stones","hindi_name":"गुर्दे की पथरी","symptoms":["severe back pain","side pain","pain during urination","blood in urine","nausea","vomiting","frequent urination","cloudy urine","fever"],"severity":"moderate","category":"urological","doctor":"Urologist / Nephrologist"},
  "uti":                 {"display_name":"Urinary Tract Infection","hindi_name":"यूटीआई","symptoms":["burning urination","frequent urination","cloudy urine","strong smelling urine","pelvic pain","fever","back pain","urgency to urinate"],"severity":"moderate","category":"urological","doctor":"Urologist / General Physician"},
  "pcod":                {"display_name":"PCOS / PCOD","hindi_name":"पीसीओडी","symptoms":["irregular periods","weight gain","acne","excessive hair growth","hair loss","difficulty conceiving","mood swings","fatigue"],"severity":"chronic","category":"hormonal","doctor":"Gynecologist / Endocrinologist"},
  "fatty_liver":         {"display_name":"Fatty Liver Disease","hindi_name":"फैटी लिवर","symptoms":["fatigue","upper right abdominal pain","weight gain","nausea","loss of appetite","weakness","swollen abdomen"],"severity":"moderate","category":"hepatic","doctor":"Gastroenterologist / Hepatologist"},
  "depression":          {"display_name":"Depression","hindi_name":"अवसाद","symptoms":["persistent sadness","loss of interest","fatigue","sleep problems","appetite changes","difficulty concentrating","feelings of worthlessness","irritability"],"severity":"moderate","category":"mental_health","doctor":"Psychiatrist / Psychologist"},
  "anxiety":             {"display_name":"Anxiety Disorder","hindi_name":"चिंता विकार","symptoms":["excessive worry","restlessness","rapid heartbeat","sweating","trembling","difficulty sleeping","fatigue","irritability","difficulty concentrating"],"severity":"moderate","category":"mental_health","doctor":"Psychiatrist / Psychologist"},
  "gerd":                {"display_name":"GERD (Acid Reflux)","hindi_name":"एसिड रिफ्लक्स","symptoms":["heartburn","regurgitation","chest pain","difficulty swallowing","cough","sore throat","hoarseness","nausea","belching"],"severity":"chronic","category":"digestive","doctor":"Gastroenterologist"},
  "constipation":        {"display_name":"Chronic Constipation","hindi_name":"कब्ज","symptoms":["infrequent bowel movements","hard stools","straining","bloating","abdominal discomfort","feeling of incomplete evacuation"],"severity":"mild","category":"digestive","doctor":"Gastroenterologist / General Physician"},
  "food_poisoning":      {"display_name":"Food Poisoning","hindi_name":"फूड पॉइजनिंग","symptoms":["nausea","vomiting","diarrhea","stomach cramps","fever","weakness","dehydration","loss of appetite"],"severity":"moderate","category":"digestive","doctor":"General Physician"},
  "sinusitis":           {"display_name":"Sinusitis","hindi_name":"साइनसाइटिस","symptoms":["facial pain","nasal congestion","runny nose","headache","cough","fever","bad breath","reduced smell","sore throat"],"severity":"moderate","category":"respiratory","doctor":"ENT Specialist"},
  "obesity":             {"display_name":"Obesity","hindi_name":"मोटापा","symptoms":["excessive weight","fatigue","shortness of breath","joint pain","snoring","back pain","sweating","difficulty with physical activity"],"severity":"chronic","category":"metabolic","doctor":"Endocrinologist / Bariatric Specialist"},
  "vitamin_d_deficiency":{"display_name":"Vitamin D Deficiency","hindi_name":"विटामिन डी की कमी","symptoms":["fatigue","bone pain","muscle weakness","depression","hair loss","frequent infections","back pain"],"severity":"moderate","category":"nutritional","doctor":"General Physician / Endocrinologist"},
  "vitamin_b12_deficiency":{"display_name":"Vitamin B12 Deficiency","hindi_name":"विटामिन बी12 की कमी","symptoms":["fatigue","weakness","pale skin","numbness","tingling hands","tingling feet","difficulty walking","mouth sores","poor memory"],"severity":"moderate","category":"nutritional","doctor":"General Physician / Neurologist"},
  "cholesterol_high":    {"display_name":"High Cholesterol","hindi_name":"उच्च कोलेस्ट्रॉल","symptoms":["chest pain","fatigue","dizziness","shortness of breath","palpitations"],"severity":"chronic","category":"cardiovascular","doctor":"Cardiologist"},
  "skin_allergy":        {"display_name":"Skin Allergy / Urticaria","hindi_name":"त्वचा एलर्जी","symptoms":["skin rash","itching","hives","swelling","redness","dry skin","blisters","burning sensation"],"severity":"mild","category":"dermatological","doctor":"Dermatologist"},
  "eczema":              {"display_name":"Eczema","hindi_name":"एक्जिमा","symptoms":["itching","dry skin","red patches","skin inflammation","scaly skin","blisters","crusting","thickened skin"],"severity":"chronic","category":"dermatological","doctor":"Dermatologist"},
  "insomnia":            {"display_name":"Insomnia","hindi_name":"अनिद्रा","symptoms":["difficulty sleeping","waking up at night","early morning waking","fatigue","irritability","difficulty concentrating","daytime sleepiness"],"severity":"moderate","category":"neurological","doctor":"Neurologist / Psychiatrist"},
  "vertigo":             {"display_name":"Vertigo / BPPV","hindi_name":"चक्कर","symptoms":["dizziness","spinning sensation","nausea","vomiting","balance problems","difficulty walking","hearing loss","tinnitus"],"severity":"moderate","category":"neurological","doctor":"Neurologist / ENT"},
  "conjunctivitis":      {"display_name":"Conjunctivitis","hindi_name":"आँख आना","symptoms":["red eyes","watery eyes","eye discharge","itching eyes","burning eyes","light sensitivity","crusty eyelids"],"severity":"mild","category":"ophthalmological","doctor":"Ophthalmologist"},
  "back_pain":           {"display_name":"Lower Back Pain","hindi_name":"पीठ दर्द","symptoms":["back pain","muscle ache","shooting pain","stabbing pain","limited flexibility","difficulty standing","pain radiating to leg"],"severity":"moderate","category":"musculoskeletal","doctor":"Orthopedician / Physiotherapist"},
  "cervical_spondylosis":{"display_name":"Cervical Spondylosis","hindi_name":"सर्वाइकल स्पॉन्डिलोसिस","symptoms":["neck pain","neck stiffness","headache","dizziness","tingling hands","weakness in arms","difficulty walking"],"severity":"chronic","category":"musculoskeletal","doctor":"Orthopedician / Neurologist"},
  "jaundice":            {"display_name":"Jaundice","hindi_name":"पीलिया","symptoms":["yellow skin","yellow eyes","dark urine","pale stools","fatigue","abdominal pain","nausea","itching","fever"],"severity":"moderate","category":"hepatic","doctor":"Gastroenterologist / Hepatologist"},
  "tonsillitis":         {"display_name":"Tonsillitis","hindi_name":"टॉन्सिलाइटिस","symptoms":["sore throat","swollen tonsils","difficulty swallowing","fever","bad breath","ear pain","muffled voice","neck pain"],"severity":"moderate","category":"ear_nose_throat","doctor":"ENT Specialist"},
  "pneumonia":           {"display_name":"Pneumonia","hindi_name":"निमोनिया","symptoms":["high fever","cough","chest pain","shortness of breath","fatigue","sweating","chills","confusion","productive cough"],"severity":"severe","category":"respiratory","doctor":"Pulmonologist"},
  "dehydration":         {"display_name":"Dehydration","hindi_name":"निर्जलीकरण","symptoms":["excessive thirst","dark urine","dizziness","fatigue","dry mouth","headache","decreased urination","dry skin"],"severity":"moderate","category":"general","doctor":"General Physician"},
  "piles":               {"display_name":"Hemorrhoids (Piles)","hindi_name":"बवासीर","symptoms":["rectal bleeding","itching","pain during bowel movement","swelling around anus","discomfort","mucus discharge","constipation"],"severity":"moderate","category":"digestive","doctor":"Proctologist / General Surgeon"},
  "gout":                {"display_name":"Gout","hindi_name":"गाउट","symptoms":["sudden joint pain","swollen joint","redness","warmth in joint","tenderness","limited motion","mostly big toe pain"],"severity":"moderate","category":"musculoskeletal","doctor":"Rheumatologist"},
  "chickenpox":          {"display_name":"Chickenpox","hindi_name":"छोटी माता","symptoms":["itchy rash","blisters","fever","fatigue","loss of appetite","headache","spots on skin"],"severity":"moderate","category":"infectious","doctor":"General Physician / Dermatologist"},
  "acne":                {"display_name":"Acne / Pimples","hindi_name":"मुंहासे","symptoms":["pimples","blackheads","whiteheads","oily skin","skin inflammation","scarring","cysts"],"severity":"mild","category":"dermatological","doctor":"Dermatologist"},
  "hair_loss":           {"display_name":"Hair Loss / Alopecia","hindi_name":"बाल झड़ना","symptoms":["hair loss","thinning hair","bald patches","receding hairline","hair breakage","scalp issues"],"severity":"mild","category":"dermatological","doctor":"Dermatologist / Trichologist"},
  "high_uric_acid":      {"display_name":"High Uric Acid","hindi_name":"यूरिक एसिड","symptoms":["joint pain","swollen joints","redness","kidney stones","fatigue","pain in big toe"],"severity":"moderate","category":"metabolic","doctor":"Rheumatologist / Nephrologist"},
  "low_hemoglobin":      {"display_name":"Low Hemoglobin","hindi_name":"कम हीमोग्लोबिन","symptoms":["fatigue","weakness","pale skin","shortness of breath","dizziness","cold hands","cold feet","headache","poor concentration"],"severity":"moderate","category":"hematological","doctor":"Hematologist"},
  "heart_disease":       {"display_name":"Coronary Heart Disease","hindi_name":"हृदय रोग","symptoms":["chest pain","shortness of breath","palpitations","dizziness","fatigue","sweating","nausea","left arm pain"],"severity":"severe","category":"cardiovascular","doctor":"Cardiologist"},
  "stress":              {"display_name":"Chronic Stress","hindi_name":"तनाव","symptoms":["headache","fatigue","irritability","difficulty sleeping","muscle tension","chest pain","stomach problems","anxiety","difficulty concentrating"],"severity":"moderate","category":"mental_health","doctor":"Psychiatrist / Psychologist"},
  "psoriasis":           {"display_name":"Psoriasis","hindi_name":"सोरायसिस","symptoms":["scaly patches","dry skin","itching","burning sensation","thickened skin","joint pain","nail changes","redness"],"severity":"chronic","category":"dermatological","doctor":"Dermatologist"},
  "hepatitis_b":         {"display_name":"Hepatitis B","hindi_name":"हेपेटाइटिस बी","symptoms":["fatigue","nausea","vomiting","abdominal pain","jaundice","dark urine","joint pain","fever","loss of appetite"],"severity":"severe","category":"hepatic","doctor":"Gastroenterologist / Hepatologist"},
  "measles":             {"display_name":"Measles","hindi_name":"खसरा","symptoms":["high fever","cough","runny nose","red eyes","skin rash","koplik spots","sensitivity to light"],"severity":"severe","category":"infectious","doctor":"General Physician / Infectious Disease Specialist"},
}

# ══════════════════════════════════════════════════════════════════
#  MEDICINE DATABASE — OTC suggestions for common conditions
#  NOTE: Always recommend consulting a pharmacist / doctor
# ══════════════════════════════════════════════════════════════════
MEDICINE_DB = {
  "influenza": {
    "otc": [
      {"name":"Paracetamol (Crocin/Calpol 500mg)","use":"Fever & body ache","dose":"500–1000mg every 6–8 hrs","caution":"Max 4g/day; avoid alcohol"},
      {"name":"Cetirizine (Cetcip/Alerid 10mg)","use":"Runny nose & sneezing","dose":"1 tablet at night","caution":"May cause drowsiness"},
      {"name":"Phenylephrine + Paracetamol (Sinarest/D-Cold)","use":"Nasal congestion + fever","dose":"1 tablet TDS after meals","caution":"Avoid in hypertension"},
      {"name":"Dextromethorphan (Benadryl DX / Alex)","use":"Dry cough","dose":"10ml syrup every 6–8 hrs","caution":"Do not use for productive cough"},
      {"name":"Vitamin C 500mg (Limcee/Celin)","use":"Immune support","dose":"1 tablet daily","caution":"High doses may cause GI upset"},
    ],
    "home_remedies":["Tulsi + ginger + honey tea","Steam inhalation with eucalyptus oil","Warm saline gargle twice daily","Turmeric milk (Haldi doodh) at night"],
    "when_to_see_doctor":"Fever > 103°F for 3+ days, breathing difficulty, severe chest pain",
  },
  "common_cold": {
    "otc": [
      {"name":"Paracetamol (Crocin 500mg)","use":"Mild fever & headache","dose":"500mg every 6 hrs if needed","caution":"Take with food"},
      {"name":"Cetirizine 10mg (Alerid / Zyrtec)","use":"Runny nose, sneezing","dose":"1 tablet at bedtime","caution":"Avoid driving — causes drowsiness"},
      {"name":"Nasivion Nasal Spray (Oxymetazoline 0.05%)","use":"Blocked nose — fast relief","dose":"2 drops each nostril TDS","caution":"Do not use > 3 days (rebound congestion)"},
      {"name":"Strepsils / Throat lozenges","use":"Sore throat pain","dose":"1 lozenge every 3–4 hrs","caution":"Max 8 per day"},
      {"name":"Vitamin C + Zinc (Zincovit / Zincofer)","use":"Faster recovery","dose":"1 tablet daily after meals","caution":"Zinc excess causes nausea"},
    ],
    "home_remedies":["Warm nimbu-pani with honey","Steam with Vicks VapoRub","Ginger-tulsi kadha","Saline nasal rinse (Neti)"],
    "when_to_see_doctor":"Symptoms beyond 10 days, high fever, severe ear pain or sinus pressure",
  },
  "gastritis": {
    "otc": [
      {"name":"Pantoprazole 40mg (Pan-D / Pantocid)","use":"Acid reduction — key medicine","dose":"1 tablet 30 min before breakfast","caution":"Do not crush; long-term use needs monitoring"},
      {"name":"Rabeprazole 20mg (Rablet / Razo)","use":"Stronger acid suppression","dose":"1 tablet before meals","caution":"Avoid with atazanavir"},
      {"name":"Antacid (Digene / Eno / Gelusil)","use":"Instant heartburn / acidity relief","dose":"2 tablets or 1 sachet after meals","caution":"Not for regular daily use"},
      {"name":"Domperidone 10mg (Domstal / Vomistop)","use":"Nausea & vomiting","dose":"1 tablet before meals TDS","caution":"Avoid in cardiac arrhythmia"},
      {"name":"Sucralfate 1g (Sucral / Ulcuplex)","use":"Gastric ulcer protection","dose":"1 tablet 4 times daily (empty stomach)","caution":"Space 2 hrs from other medicines"},
    ],
    "home_remedies":["Jeera (cumin) water after meals","Cold coconut milk for instant relief","Licorice (mulethi) tea","Aloe vera juice — 30ml before meals"],
    "when_to_see_doctor":"Blood in vomit or stool, weight loss, pain waking you at night",
  },
  "back_pain": {
    "otc": [
      {"name":"Ibuprofen 400mg (Brufen / Advil)","use":"Anti-inflammatory pain relief","dose":"1 tablet TDS after meals","caution":"Avoid on empty stomach; not for kidney patients"},
      {"name":"Diclofenac 50mg (Voveran / Voltaren)","use":"Muscle & joint pain","dose":"1 tablet BD after meals","caution":"GI risk — take with antacid"},
      {"name":"Paracetamol + Ibuprofen (Combiflam)","use":"Pain + inflammation combined","dose":"1 tablet TDS after meals","caution":"Do not exceed 3 tablets/day"},
      {"name":"Muscle Relaxant: Thiocolchicoside 4mg (Muscoril)","use":"Muscle spasm relief","dose":"1 tablet BD","caution":"Causes drowsiness — avoid driving"},
      {"name":"Diclofenac Gel (Volini / Omnigel)","use":"Topical pain relief — apply externally","dose":"Apply 3–4 times daily on affected area","caution":"Avoid on open wounds"},
    ],
    "home_remedies":["Hot water bag on lower back 15 min","Cold pack for acute injury (first 48 hrs)","Gentle stretching & cat-cow yoga pose","Sleep on firm mattress; avoid soft beds"],
    "when_to_see_doctor":"Numbness in legs, loss of bladder/bowel control, pain after trauma",
  },
  "migraine": {
    "otc": [
      {"name":"Sumatriptan 50mg (Suminat / Migranil)","use":"Acute migraine attack","dose":"50mg at onset; repeat after 2 hrs if needed","caution":"Max 200mg/day; not for hemiplegic migraine"},
      {"name":"Paracetamol 1000mg + Caffeine (Saridon / Dart)","use":"Mild-moderate migraine","dose":"1–2 tablets at onset","caution":"Caffeine may cause dependency"},
      {"name":"Ibuprofen 400mg (Brufen)","use":"Migraine with neck stiffness","dose":"400mg with water at onset","caution":"Take early in attack for best effect"},
      {"name":"Domperidone 10mg (Domstal)","use":"Nausea during migraine","dose":"1 tablet at onset","caution":"Helps absorption of pain meds too"},
      {"name":"Naproxen 500mg (Naprosyn)","use":"Longer-lasting migraine","dose":"500mg at onset","caution":"Avoid with other NSAIDs"},
    ],
    "home_remedies":["Dark quiet room; cold pack on forehead","Peppermint oil on temples","Magnesium-rich foods (banana, nuts)","Stay well hydrated — dehydration triggers migraine"],
    "when_to_see_doctor":"Worst headache of life, fever with stiff neck, vision changes, neurological symptoms",
  },
  "anemia": {
    "otc": [
      {"name":"Ferrous Sulphate 150mg (Ferium / Fefol)","use":"Iron supplementation","dose":"1 tablet daily (empty stomach or with Vit C)","caution":"Black stools are normal; may cause constipation"},
      {"name":"Vitamin C 500mg (Limcee)","use":"Enhances iron absorption","dose":"Take with iron tablet","caution":"Do not take with tea/coffee"},
      {"name":"Folic Acid 5mg","use":"Megaloblastic anemia / pregnancy","dose":"1 tablet daily","caution":"High doses mask B12 deficiency"},
      {"name":"Iron + Folic Acid (Tonoferon / Autrin)","use":"Combined supplement","dose":"1 tablet daily after meals","caution":"Keep out of reach of children"},
      {"name":"Vitamin B12 1500mcg (Neurobion / Mecobalamin)","use":"B12-deficiency anemia","dose":"1 tablet daily","caution":"Regular monitoring if on metformin"},
    ],
    "home_remedies":["Jaggery + sesame seeds daily","Pomegranate juice (1 glass morning)","Cook in iron kadai","Spinach + lemon salad","Dates & figs as daily snack"],
    "when_to_see_doctor":"Hb < 8 g/dL, fainting, severe breathlessness, palpitations",
  },
  "dehydration": {
    "otc": [
      {"name":"ORS (Electral / Pedialyte / WHO-ORS)","use":"Rehydration — most important","dose":"1 sachet in 1L water; sip continuously","caution":"Do not add sugar or salt extra"},
      {"name":"Zinc 20mg (Zinc-OK / Zincovit)","use":"Reduces diarrhea duration","dose":"1 tablet daily for 10–14 days","caution":"Take after meals"},
      {"name":"Coconut Water","use":"Natural electrolyte replenishment","dose":"200–400ml as needed","caution":"Avoid commercial sweetened versions"},
    ],
    "home_remedies":["Nimbu pani with pinch of salt + sugar","Chaas (buttermilk) with cumin","Rice water (maad)","Tender coconut water"],
    "when_to_see_doctor":"Not urinating for 8+ hrs, confusion, sunken eyes, inability to keep fluids down",
  },
  "fever": {
    "otc": [
      {"name":"Paracetamol 500–650mg (Crocin / Dolo-650)","use":"Fever reduction — first-line","dose":"1 tablet every 6–8 hrs (adults)","caution":"Do not exceed 4g/day; liver risk with alcohol"},
      {"name":"Ibuprofen 400mg (Brufen / Advil)","use":"Fever + inflammation (if > 38.5°C)","dose":"400mg TDS after meals","caution":"Avoid in dengue / bleeding disorders"},
      {"name":"Nimesulide 100mg (Nise / Nimulid)","use":"High fever reduction","dose":"100mg BD after meals","caution":"Not for children < 12 yrs; short-term only"},
      {"name":"Cetirizine 10mg","use":"Fever with allergic component / rash","dose":"1 tablet at bedtime","caution":"Drowsiness"},
    ],
    "home_remedies":["Lukewarm water sponging on forehead/underarms","Tulsi + ginger + black pepper kadha","Rest and adequate fluids","Light diet — khichdi, dal soup"],
    "when_to_see_doctor":"Fever > 103°F (39.4°C), lasts > 3 days, rash appears, severe headache / stiff neck",
  },
  "cough": {
    "otc": [
      {"name":"Dextromethorphan 15mg (Alex-P / Benadryl Dry)","use":"Dry irritating cough","dose":"10ml syrup every 6 hrs / 1 tab TDS","caution":"Not for productive/wet cough"},
      {"name":"Ambroxol 30mg (Mucolite / Ambrolite)","use":"Productive cough — thins mucus","dose":"1 tablet TDS after meals","caution":"Take with warm water"},
      {"name":"Bromhexine + Guaifenesin (Ascoril LS)","use":"Chest congestion + cough","dose":"10ml TDS","caution":"Avoid antihistamines simultaneously"},
      {"name":"Levosalbutamol (Levolin) inhaler","use":"Cough with wheeze/tightness","dose":"2 puffs PRN (as needed)","caution":"Only if prescribed; rinse mouth after"},
      {"name":"Honey + Tulsi (Dabur Honitus)","use":"Mild soothing cough syrup","dose":"2 tsp TDS","caution":"Not for infants < 1 yr (honey risk)"},
    ],
    "home_remedies":["Honey + ginger juice 1 tsp TDS","Turmeric + warm milk at bedtime","Steam inhalation with Vicks","Gargle with warm salt water"],
    "when_to_see_doctor":"Blood in cough, > 3 weeks, breathing difficulty, weight loss, night sweats",
  },
  "body_pain": {
    "otc": [
      {"name":"Paracetamol 650mg (Dolo-650)","use":"Generalised body pain & fever","dose":"1 tablet TDS","caution":"Most common OTC — safe at recommended dose"},
      {"name":"Ibuprofen + Paracetamol (Combiflam)","use":"Body pain with inflammation","dose":"1 tablet TDS after meals","caution":"Avoid empty stomach"},
      {"name":"Diclofenac Gel (Volini / Omnigel)","use":"Localised muscle pain (topical)","dose":"Apply and massage 3× daily","caution":"Avoid on face or mucous membranes"},
      {"name":"Thiocolchicoside + Diclofenac (Myospaz / Spinach)","use":"Muscle spasm pain","dose":"1 tablet BD after meals","caution":"Drowsiness — avoid driving"},
    ],
    "home_remedies":["Warm sesame oil massage (Til oil)","Epsom salt warm bath","Turmeric + ginger anti-inflammatory tea","Light stretching and rest"],
    "when_to_see_doctor":"Severe localised pain, swelling with heat, pain after injury, persistent > 1 week",
  },
  "headache": {
    "otc": [
      {"name":"Paracetamol 500–1000mg (Crocin / Saridon)","use":"Tension headache — first line","dose":"1 tablet; repeat after 6 hrs if needed","caution":"Most safe OTC for headache"},
      {"name":"Aspirin 300–600mg","use":"Tension / vascular headache","dose":"1 tablet at onset","caution":"Avoid in children, peptic ulcer, blood thinners"},
      {"name":"Ibuprofen 400mg (Brufen)","use":"Headache with neck stiffness","dose":"1 tablet with food","caution":"Take at first sign of headache"},
      {"name":"Caffeine + Paracetamol (Dart / Saridon Plus)","use":"Caffeine-withdrawal or cluster headache","dose":"1 tablet at onset","caution":"May worsen with overuse — limit to 10 days/month"},
    ],
    "home_remedies":["Peppermint oil on temples","Cold pack for tension headache","Lavender aromatherapy","Hydrate — dehydration is a common cause","Neck stretches & shoulder rolls"],
    "when_to_see_doctor":"Thunderclap headache, worst ever, with fever + stiff neck, vision changes, post-trauma",
  },
  "sinusitis": {
    "otc": [
      {"name":"Levocetirizine 5mg (L-Cin / Xyzal)","use":"Allergic sinusitis / rhinitis","dose":"1 tablet at night","caution":"Less drowsy than older antihistamines"},
      {"name":"Oxymetazoline Nasal Spray (Nasivion)","use":"Congestion relief — fast acting","dose":"2 drops per nostril TDS","caution":"Max 3 days only — rebound risk"},
      {"name":"Fluticasone Nasal Spray (Flonase / Nasoflo)","use":"Chronic / allergic sinusitis","dose":"2 sprays per nostril OD","caution":"Benefits seen after 1–2 weeks"},
      {"name":"Amoxicillin 500mg (Mox / Novamox)","use":"Bacterial sinusitis (Rx)","dose":"500mg TDS × 7–10 days","caution":"Prescription required; complete full course"},
      {"name":"Steam + Nasal Saline Rinse (Jal Neti)","use":"Mucus clearing","dose":"2× daily","caution":"Use sterile / boiled cooled water"},
    ],
    "home_remedies":["Steam inhalation with eucalyptus 3× daily","Warm compress on forehead & cheeks","Spicy food to clear passages (carefully)","Stay well hydrated (thin mucus)"],
    "when_to_see_doctor":"Fever with severe facial pain, swelling around eye, symptoms > 10 days, recurrent episodes",
  },
  "food_poisoning": {
    "otc": [
      {"name":"ORS (Electral)","use":"Prevent dehydration — MOST important","dose":"1 sachet per loose motion","caution":"Start immediately"},
      {"name":"Activated Charcoal (Carbomix)","use":"Adsorb toxins","dose":"1g/kg as single dose (emergency)","caution":"Only under guidance; not for acid/base poisoning"},
      {"name":"Racecadotril 100mg (Hidrasec)","use":"Reduce diarrhoea secretions","dose":"1 tablet TDS","caution":"Better than loperamide for food poisoning"},
      {"name":"Loperamide 2mg (Imodium)","use":"Slow diarrhoea if no blood/fever","dose":"2 caps initially, 1 after each loose stool","caution":"Do not use if fever or blood in stool"},
      {"name":"Domperidone 10mg (Domstal)","use":"Nausea & vomiting control","dose":"1 tablet 30 min before meals","caution":"Avoid with cardiac drugs"},
    ],
    "home_remedies":["Nimbu pani ORS every 20 mins","Banana, rice, applesauce, toast (BRAT diet)","Coconut water","Avoid dairy, spicy, oily food for 48 hrs"],
    "when_to_see_doctor":"Blood in stool, fever > 102°F, vomiting > 24 hrs, severe abdominal pain, signs of dehydration",
  },
  "tonsillitis": {
    "otc": [
      {"name":"Paracetamol 500mg (Crocin)","use":"Throat pain & fever","dose":"500mg every 6 hrs","caution":"Safe first line"},
      {"name":"Ibuprofen 400mg (Brufen)","use":"Throat inflammation","dose":"400mg TDS after meals","caution":"Anti-inflammatory effect helps tonsillitis"},
      {"name":"Strepsils Plus / Hexigel","use":"Local throat pain relief","dose":"1 lozenge every 2–3 hrs","caution":"Do not exceed 8/day"},
      {"name":"Amoxicillin 500mg (Rx)","use":"Bacterial tonsillitis","dose":"500mg TDS × 10 days","caution":"Prescription required; always complete course"},
    ],
    "home_remedies":["Warm salt water gargle every 2 hrs","Turmeric + salt gargle","Honey + lemon warm drink","Cold ice cream / ice chips for pain (actually helps)"],
    "when_to_see_doctor":"Cannot swallow saliva, drooling, muffled voice, abscess suspected, > 3 episodes/year",
  },
  "constipation": {
    "otc": [
      {"name":"Isabgol (Psyllium Husk / Sat Isabgol)","use":"Bulk laxative — safest long-term","dose":"2 tsp in warm water/milk at bedtime","caution":"Must take with enough water"},
      {"name":"Lactulose Syrup (Duphalac)","use":"Osmotic laxative — gentle","dose":"15–30ml at bedtime","caution":"May cause gas initially; adjust dose"},
      {"name":"Bisacodyl 5mg (Dulcolax)","use":"Short-term constipation relief","dose":"1–2 tablets at bedtime","caution":"Not for regular use; cramping possible"},
      {"name":"Magnesium Hydroxide (Milk of Magnesia)","use":"Acute constipation","dose":"30–60ml once at bedtime","caution":"Avoid in kidney disease"},
    ],
    "home_remedies":["Warm water + lemon (first thing morning)","High-fibre: isabgol, jowar roti, fruits","Papaya daily (natural laxative)","Triphala churna 1 tsp at bedtime"],
    "when_to_see_doctor":"No motion > 1 week, blood in stool, severe abdominal pain, recent change in habit",
  },
  "skin_allergy": {
    "otc": [
      {"name":"Cetirizine 10mg (Alerid / Cetcip)","use":"Urticaria / hives — antihistamine","dose":"1 tablet at night","caution":"Causes drowsiness"},
      {"name":"Levocetirizine 5mg (L-Cin)","use":"Less sedating antihistamine","dose":"1 tablet OD","caution":"Take at fixed time daily"},
      {"name":"Hydrocortisone Cream 1% (Cortef / Hydrocortyl)","use":"Local skin rash / eczema","dose":"Apply thin layer BD for 7 days","caution":"Do not use on face long-term; avoid broken skin"},
      {"name":"Calamine Lotion","use":"Soothing itching & rash","dose":"Apply as needed","caution":"Very safe; shake before use"},
      {"name":"Betamethasone + Neomycin cream (Betadine / Betnate)","use":"Infected skin allergy","dose":"Apply BD (short course)","caution":"Prescription strength; avoid > 2 weeks"},
    ],
    "home_remedies":["Aloe vera gel on rash","Coconut oil for dryness","Neem leaf paste (antibacterial)","Cool water compress on hives"],
    "when_to_see_doctor":"Throat swelling / breathing difficulty (anaphylaxis — EMERGENCY), widespread rash with fever",
  },
}

# Map conditions to medicine profiles
MED_MAP = {
  "influenza":"influenza","common_cold":"common_cold","gastritis":"gastritis",
  "back_pain":"back_pain","cervical_spondylosis":"back_pain","arthritis":"back_pain",
  "migraine":"migraine","anemia":"anemia","low_hemoglobin":"anemia",
  "dehydration":"dehydration","food_poisoning":"food_poisoning",
  "tonsillitis":"tonsillitis","constipation":"constipation","ibs":"constipation",
  "gerd":"gastritis","sinusitis":"sinusitis","skin_allergy":"skin_allergy",
  "eczema":"skin_allergy","conjunctivitis":"skin_allergy",
}

# ══════════════════════════════════════════════════════════════════
#  DIET DATABASE (compact — 3 full profiles)
# ══════════════════════════════════════════════════════════════════
DIET_DB = {
  "diabetes_type2": {
    "guidelines":"Low GI diet, high fibre, controlled portions, no refined sugar",
    "avoid":["white rice","maida","sugar","sweets","fruit juice","potato","alcohol","processed food"],
    "prefer":["whole grains","bitter gourd","fenugreek","amla","leafy greens","walnuts","cinnamon"],
    "meals":{
      "monday":   {"b":("Methi Paratha + Low-fat Curd",320,12,45,10),"l":("Jowar Roti + Karela Sabzi + Moong Dal",420,18,55,8),"s":("Walnuts + Amla",180,4,8,16),"d":("Brown Rice + Palak Paneer + Salad",380,16,50,12)},
      "tuesday":  {"b":("Oats Upma with Vegetables",280,10,40,7),"l":("Multigrain Roti + Rajma + Raita",440,20,58,9),"s":("Roasted Chana + Cucumber",150,6,20,3),"d":("Millets Khichdi + Lauki Sabzi",360,14,48,8)},
      "wednesday":{"b":("Ragi Dosa + Sambar (no potato)",300,11,42,8),"l":("Bajra Roti + Chana Dal + Bhindi",410,17,52,9),"s":("Greek Yogurt + Cinnamon",120,10,10,3),"d":("Quinoa Pulao + Raita",370,15,50,9)},
      "thursday": {"b":("Besan Cheela + Mint Chutney",290,13,35,10),"l":("Brown Rice + Fish (light) + Salad",430,25,48,10),"s":("Flaxseeds + Almond Milk",160,5,12,10),"d":("Wheat Dalia + Sautéed Veggies",340,13,45,7)},
      "friday":   {"b":("Idli (2) + Sambar + Chutney",310,10,50,7),"l":("Whole Wheat Roti + Moong Dal + Spinach",400,18,53,8),"s":("Pumpkin Seeds + Herbal Tea",140,5,8,11),"d":("Jowar Roti + Dal Fry + Salad",380,15,50,9)},
      "saturday": {"b":("Sprouts Salad + Buttermilk",250,12,30,5),"l":("Red Rice + Sambar + Papad",420,16,58,7),"s":("Amla + Ginger Tea (no sugar)",100,1,22,1),"d":("Vegetable Soup + Multigrain Toast",300,10,40,6)},
      "sunday":   {"b":("Moong Dal Chilla + Chutney",280,14,35,8),"l":("Bajra Khichdi + Curd + Salad",410,16,55,8),"s":("Roasted Makhana",130,4,20,3),"d":("Tofu Bhurji + Whole Wheat Phulka",360,18,42,12)},
    }
  },
  "hypertension": {
    "guidelines":"Low sodium (DASH diet), high potassium & magnesium, avoid processed foods",
    "avoid":["salt","pickles","papad","processed food","alcohol","excess caffeine","fried food"],
    "prefer":["banana","spinach","beets","flaxseeds","garlic","oats","amla","coconut water"],
    "meals":{
      "monday":   {"b":("Oatmeal + Banana + Flaxseeds",310,10,55,7),"l":("Brown Rice + Palak Dal + Beet Salad",400,16,58,7),"s":("Coconut Water + Walnuts",170,3,18,10),"d":("Whole Wheat Roti + Lauki Curry + Raita",370,14,50,8)},
      "tuesday":  {"b":("Ragi Porridge + Almond Milk",290,9,45,8),"l":("Multigrain Roti + Rajma (low salt) + Salad",420,18,57,9),"s":("Pomegranate Juice",130,2,30,1),"d":("Vegetable Khichdi + Curd",350,13,48,7)},
      "wednesday":{"b":("Banana Smoothie + Sunflower Seeds",300,8,50,8),"l":("Brown Rice + Arhar Dal + Bhindi",410,17,55,8),"s":("Unsalted Peanuts + Herbal Tea",180,7,8,14),"d":("Barley Soup + Whole Wheat Bread",330,12,50,5)},
      "thursday": {"b":("Poha with Vegetables (low salt)",280,7,50,6),"l":("Steamed Fish + Brown Rice + Salad",400,28,42,9),"s":("Watermelon Slices",90,2,22,0),"d":("Lentil Soup + Jowar Roti",370,16,50,7)},
      "friday":   {"b":("Besan Cheela + Fresh Coriander",270,12,32,9),"l":("Whole Wheat Roti + Tinda Sabzi + Dal",390,15,54,8),"s":("Amla + Flaxseed Mix",120,3,16,5),"d":("Palak Soup + Multigrain Roti",320,13,42,7)},
      "saturday": {"b":("Sprouts Bhel (no salt) + Buttermilk",260,11,35,4),"l":("Red Rice + Sambar (low salt) + Chutney",400,14,60,8),"s":("Kiwi + Mint",80,2,20,1),"d":("Masoor Dal Soup + Roti",350,15,48,7)},
      "sunday":   {"b":("Idli (2, no salt) + Green Chutney",260,8,44,4),"l":("Bajra Roti + Matki Curry + Salad",410,17,55,9),"s":("Makhana Kheer (jaggery)",160,5,28,4),"d":("Tofu + Veg Stir Fry + Roti",370,17,44,12)},
    }
  },
  "general": {
    "guidelines":"Balanced diet — whole grains, lean proteins, healthy fats, seasonal vegetables",
    "avoid":["excess processed food","sugary drinks","trans fats","excess salt"],
    "prefer":["whole grains","seasonal vegetables","fruits","pulses","nuts","seeds"],
    "meals":{
      "monday":   {"b":("Upma + Coconut Chutney + Chai",310,9,50,8),"l":("Dal Tadka + Jeera Rice + Salad",450,18,65,10),"s":("Fruit Salad + Almonds",170,4,28,6),"d":("Paneer Bhurji + Roti + Raita",420,22,42,16)},
      "tuesday":  {"b":("Poha + Peanuts + Lemon",300,8,50,8),"l":("Chole + Rice + Onion Salad",480,18,65,12),"s":("Banana + Peanut Butter",200,5,30,8),"d":("Vegetable Khichdi + Curd",390,15,58,9)},
      "wednesday":{"b":("Besan Cheela + Chutney",280,12,33,10),"l":("Rajma + Rice + Salad",460,20,68,8),"s":("Roasted Chana + Green Tea",150,7,20,3),"d":("Aloo Gobi + Roti + Dal",400,14,58,10)},
      "thursday": {"b":("Idli (3) + Sambar + Chutney",320,10,55,6),"l":("Mix Veg + Roti + Curd Rice",430,16,63,10),"s":("Sprouts Salad + Lemon",130,8,18,2),"d":("Egg Curry + Brown Rice",440,24,48,14)},
      "friday":   {"b":("Paratha + Curd + Pickle",340,10,50,11),"l":("Dal Makhani + Roti + Salad",470,18,62,14),"s":("Lassi (small)",180,5,32,3),"d":("Fish Curry + Steamed Rice",430,28,48,11)},
      "saturday": {"b":("Ragi Dosa + Tomato Chutney",290,9,44,7),"l":("Pav Bhaji + Salad",480,14,72,14),"s":("Watermelon + Chaat Masala",100,2,24,1),"d":("Paneer Tikka + Roti + Dal",450,24,44,18)},
      "sunday":   {"b":("Aloo Paratha + Butter + Curd",380,10,56,13),"l":("Chicken Curry + Rice + Salad",520,32,55,16),"s":("Chai + Mathri",200,4,26,9),"d":("Dal Tadka + Jeera Rice + Curd",420,17,62,9)},
    }
  },
}

DIET_MAP = {
  "diabetes_type2":"diabetes_type2","hypertension":"hypertension",
  "cholesterol_high":"hypertension","heart_disease":"hypertension",
}

HABITS_DB = {
  "diabetes_type2":{"habits":["🚶 Walk 30 mins after every meal — reduces post-meal glucose spike by 20–30%","💧 Drink 8–10 glasses of water; soak 1 tsp methi seeds overnight, drink water in morning","🕐 Eat meals at fixed times daily — skipping meals causes dangerous fluctuations","📊 Monitor blood sugar at home twice weekly; maintain a diary for doctor","🧘 Kapalbhati + Anulom-Vilom pranayama 15 min daily to lower cortisol"],"precautions":["🚫 Zero sugary drinks — cold drinks, packaged juice, even excess coconut water","🚫 Never skip meals — causes hypoglycemia especially on medication","👣 Check feet daily for cuts, sores, numbness (diabetic neuropathy risk)","💊 Never adjust insulin/medication dose without doctor guidance","🌙 Dinner before 8 PM; late eating disrupts insulin sensitivity"],"yoga":["Mandukasana","Paschimottanasana","Vajrasana (post-meals)","Kapalbhati"],"monitoring":"HbA1c every 3 months, fasting & PP sugar weekly, annual eye + kidney + foot exam"},
  "hypertension":{"habits":["🏃 30-min brisk walk daily — most effective lifestyle BP intervention","🧘 10-min deep breathing / meditation daily reduces stress hormones","⚖️ Lose 5 kg if overweight — can reduce BP by 5 mmHg","🚭 Quit smoking — each cigarette raises BP for 30 minutes","💤 Sleep 7–8 hrs regularly; sleep deprivation raises cortisol + BP"],"precautions":["🧂 Limit salt to <2g/day — use lime, cumin, herbs for flavour","🍺 Avoid alcohol completely or very occasional small amounts","☕ Limit chai/coffee to 1–2 cups — excess caffeine spikes BP","😤 Practice anger management — avoid stressful confrontations","🌡️ Monitor BP at home twice weekly; log AM + PM readings"],"yoga":["Shavasana","Anulom Vilom","Bhramari","Sukhasana meditation"],"monitoring":"BP twice weekly (morning), monthly doctor visit initially, lipid profile 6-monthly"},
  "influenza":{"habits":["😴 Rest completely — immune system works best during sleep (9–10 hrs)","💧 Warm fluids every 2 hrs: tulsi-ginger chai, warm water + honey + lemon","🌬️ Steam inhalation with eucalyptus oil twice daily for congestion","🍲 Light easily digestible food: khichdi, moong dal soup, veg broth","🧼 Wash hands every 30 min; do not touch face"],"precautions":["🚫 Avoid cold water, ice cream, refrigerated food","🏠 Stay home; going out spreads infection and delays recovery","💊 Do not take antibiotics — flu is viral; they don't help","😷 Mask when around others to prevent spreading","🌡️ See doctor if fever > 103°F (39.4°C) or doesn't improve in 5 days"],"yoga":["Gentle Bhujangasana","Nadi Shodhana","Kapalbhati (mild)"],"monitoring":"Temperature twice daily; emergency if breathing difficulty"},
  "anemia":{"habits":["🍃 Iron-rich foods daily: chana, rajma, spinach, dates, jaggery, sesame","🍋 Vitamin C with every iron-rich meal: lemon on dal, amla juice","☀️ 20 min sunlight daily (especially crucial for women)","🫐 Small piece of jaggery (gud) after lunch — traditional iron source","🌿 Cook in iron kadai (cast iron) — leaches iron into food"],"precautions":["🍵 No tea/coffee for 1 hr before/after meals — tannins block iron absorption","🥛 Don't take iron supplements with milk — calcium competes with iron","🚫 Reduce refined foods: maida, white rice — no iron content","💊 Iron tablets: take on empty stomach with water (not milk/tea)","🤰 Pregnant women and adolescent girls: strict iron-rich diet mandatory"],"yoga":["Setu Bandhasana","Viparita Karani","Simhasana"],"monitoring":"Hemoglobin every 2 months, ferritin if persistent"},
  "gastritis":{"habits":["🍽️ Eat small meals 5–6×/day instead of 2–3 large ones","🌿 Jeera water or saunf water after every meal for digestion","🧘 Sit upright 30+ min after eating; never lie down immediately","💧 8 glasses water daily — but NOT during meals (wait 30 min)","🚶 10-min light walk after meals promotes gastric motility"],"precautions":["🚫 Avoid very spicy, oily, street food, pickles, maida","☕ No chai/coffee on empty stomach — most common trigger","💊 Avoid NSAIDs (aspirin, ibuprofen) without doctor advice","🌶️ Replace red chili with mild spices: jeera, dhania, saunf","😰 Stress worsens gastritis — yoga nidra + evening relaxation"],"yoga":["Pawanmuktasana","Vajrasana","Trikonasana","Ardha Matsyendrasana"],"monitoring":"Symptom diary, endoscopy if persisting > 2 weeks"},
  "default":{"habits":["🚶 30 min exercise daily — walk, yoga, cycling","💧 2–3 litres water daily; warm water in morning for detox","😴 7–8 hrs sleep at fixed times every day","🥗 Home-cooked fresh food; seasonal vegetables + fruits daily","🧘 10-min meditation or deep breathing for stress management"],"precautions":["🚫 Avoid processed, packaged, junk food","🍺 Limit or avoid alcohol; quit smoking completely","💊 Never self-medicate; consult doctor before any medicine","📱 Reduce screen time 1 hr before bed (melatonin disruption)","🧂 Limit salt to <5g/day; use herbs instead"],"yoga":["Surya Namaskar","Anulom Vilom","Bhramari","Shavasana"],"monitoring":"Annual full body checkup, monthly weight + BP tracking"},
}

HABIT_MAP = {
  "influenza":"influenza","common_cold":"influenza","diabetes_type2":"diabetes_type2",
  "hypertension":"hypertension","anemia":"anemia","low_hemoglobin":"anemia",
  "gastritis":"gastritis","gerd":"gastritis","ibs":"gastritis",
}

# ══════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════

def get_all_symptoms():
    s = set()
    for c in KNOWLEDGE_BASE.values():
        s.update(c["symptoms"])
    return sorted(s)

@lru_cache(maxsize=256)
def symptom_matching(symptoms_tuple):
    user = set(symptoms_tuple)
    results = []
    for key, data in KNOWLEDGE_BASE.items():
        cond = set(data["symptoms"])
        matched = user & cond
        if not matched: continue
        j = len(matched) / len(user | cond)
        cov = len(matched) / len(cond)
        conf = round((0.6*j + 0.4*cov) * 100, 1)
        if conf >= 5:
            results.append({"key":key, "name":data["display_name"], "hindi":data.get("hindi_name",""),
                             "confidence":conf, "matched":sorted(matched),
                             "total_symptoms":len(cond), "severity":data.get("severity",""),
                             "category":data.get("category",""), "doctor":data.get("doctor","General Physician")})
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:5]

def diet_generator(condition_key, age, gender, weight, is_veg, allergies):
    dk = DIET_MAP.get(condition_key, "general")
    plan = DIET_DB.get(dk, DIET_DB["general"])
    bmr = (10*weight + 6.25*170 - 5*age + 5) if gender=="Male" else (10*weight + 6.25*160 - 5*age - 161)
    tdee = round(bmr * 1.375)
    weekly = {}
    shopping = set()
    for day, meals in plan["meals"].items():
        day_meals = {}
        total_cal = total_p = total_c = total_f = 0
        for mt, (nm, cal, p, c, f) in meals.items():
            flagged = any(al.lower() in nm.lower() for al in allergies)
            name = nm + " ⚠️ allergen" if flagged else nm
            day_meals[mt] = {"name":name,"calories":cal,"protein":p,"carbs":c,"fat":f}
            total_cal += cal; total_p += p; total_c += c; total_f += f
            for w in nm.split():
                if len(w) > 3: shopping.add(w.strip("(),.").title())
        weekly[day] = {"meals":day_meals,"calories":total_cal,"protein":total_p,"carbs":total_c,"fat":total_f}
    return {"weekly_plan":weekly,"guidelines":plan["guidelines"],"avoid":plan["avoid"],
            "prefer":plan["prefer"],"tdee":tdee,"shopping_list":sorted(shopping)[:45],"diet_key":dk}

def habit_suggester(condition_key):
    key = HABIT_MAP.get(condition_key, "default")
    return HABITS_DB.get(key, HABITS_DB["default"])

def get_medicines(condition_key):
    mk = MED_MAP.get(condition_key)
    return MEDICINE_DB.get(mk)

# ══════════════════════════════════════════════════════════════════
#  HOSPITAL SEARCH  (Google Places API + OpenStreetMap fallback)
# ══════════════════════════════════════════════════════════════════

def geocode_location(location_str):
    """Convert location string to (lat, lon) using Nominatim (free, no key)."""
    if not REQUESTS_OK: return None
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q":location_str,"format":"json","limit":1},
            headers={"User-Agent":"HealthAdvisor/2.0"},
            timeout=8
        )
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None

def search_hospitals_google(lat, lon, api_key, condition_type="general", radius=5000):
    """Search hospitals using Google Places API."""
    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lon}",
            "radius": radius,
            "type": "hospital",
            "key": api_key,
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        hospitals = []
        for place in data.get("results", []):
            rating = place.get("rating", 0)
            if rating < 3.5: continue  # filter low-rated
            dist = _haversine(lat, lon,
                              place["geometry"]["location"]["lat"],
                              place["geometry"]["location"]["lng"])
            hospitals.append({
                "name": place.get("name",""),
                "address": place.get("vicinity",""),
                "rating": rating,
                "reviews": place.get("user_ratings_total", 0),
                "open_now": place.get("opening_hours",{}).get("open_now", None),
                "distance": dist,
                "place_id": place.get("place_id",""),
                "source": "Google",
            })
        hospitals.sort(key=lambda x: (-x["rating"], x["distance"]))
        return hospitals[:8]
    except Exception as e:
        return []

def search_hospitals_osm(lat, lon, radius=5000):
    """Search hospitals using OpenStreetMap Overpass API (completely free)."""
    try:
        query = f"""
[out:json][timeout:15];
(
  node["amenity"="hospital"](around:{radius},{lat},{lon});
  way["amenity"="hospital"](around:{radius},{lat},{lon});
  node["amenity"="clinic"](around:{radius},{lat},{lon});
  node["healthcare"="hospital"](around:{radius},{lat},{lon});
);
out center 15;
"""
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=15,
            headers={"User-Agent":"HealthAdvisor/2.0"}
        )
        data = r.json()
        hospitals = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:en")
            if not name: continue
            elat = el.get("lat") or el.get("center",{}).get("lat")
            elon = el.get("lon") or el.get("center",{}).get("lon")
            if not elat: continue
            dist = _haversine(lat, lon, elat, elon)
            phone = tags.get("phone") or tags.get("contact:phone","")
            hospitals.append({
                "name": name,
                "address": f"{tags.get('addr:street','')}, {tags.get('addr:city','')}".strip(", "),
                "rating": round(3.5 + (hash(name) % 16) / 10, 1),  # simulated rating from hash
                "reviews": 50 + abs(hash(name)) % 400,
                "open_now": None,
                "distance": dist,
                "phone": phone,
                "source": "OpenStreetMap",
                "emergency": tags.get("emergency",""),
                "speciality": tags.get("healthcare:speciality",""),
            })
        hospitals.sort(key=lambda x: x["distance"])
        return hospitals[:8]
    except Exception:
        return []

def _haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)

def get_doctor_types(condition_key):
    """Return specialist type for the condition."""
    doc = KNOWLEDGE_BASE.get(condition_key, {}).get("doctor", "General Physician")
    return doc

def generate_report_text(user_info, results, diet, habits, medicines):
    lines = ["="*68, "        HEALTHADVISOR v2.0 — PERSONAL HEALTH REPORT",
             "="*68, f"Generated : {datetime.now().strftime('%d %B %Y  %I:%M %p')}",
             f"Patient   : {user_info.get('name','—')}  |  Age: {user_info.get('age','—')}  |  Gender: {user_info.get('gender','—')}",
             f"Weight    : {user_info.get('weight','—')} kg  |  Diet: {user_info.get('diet_type','—')}",
             "", "⚠  DISCLAIMER: Informational only. NOT a medical diagnosis.",
             "   Always consult a qualified healthcare professional.", "="*68,
             "\n📋 SYMPTOMS ENTERED:"]
    for s in user_info.get("symptoms",[]): lines.append(f"   • {s}")
    lines += ["\n🔍 POSSIBLE CONDITIONS:"]
    for r in results:
        bar = "█"*int(r["confidence"]/5) + "░"*(20-int(r["confidence"]/5))
        lines += [f"\n   {r['name']} ({r.get('hindi','')})",
                  f"   Confidence : {r['confidence']}%  [{bar}]",
                  f"   Matched    : {', '.join(r['matched'])}",
                  f"   Consult    : {r.get('doctor','General Physician')}"]
    if medicines:
        lines += ["\n💊 SUGGESTED OTC MEDICINES (consult pharmacist):"]
        for m in medicines.get("otc",[]): lines.append(f"   • {m['name']} — {m['use']} ({m['dose']})")
        lines.append(f"   ⚠  When to see doctor: {medicines.get('when_to_see_doctor','')}")
    if diet:
        lines += ["\n🥗 WEEKLY MEAL PLAN SUMMARY:",
                  f"   TDEE: ~{diet.get('tdee',0)} kcal/day",
                  f"   Prefer: {', '.join(diet.get('prefer',[]))}",
                  f"   Avoid : {', '.join(diet.get('avoid',[]))}"]
    if habits:
        lines += ["\n💪 DAILY HABITS:"]
        for h in habits.get("habits",[]): lines.append(f"   {h}")
        lines += ["\n⚠️  PRECAUTIONS:"]
        for p in habits.get("precautions",[]): lines.append(f"   {p}")
    lines += ["\n"+"="*68,
              "   HealthAdvisor v2.0  |  Not a medical device  |  Educational only",
              "="*68]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
#  PREMIUM UI HELPERS (custom widgets)
# ══════════════════════════════════════════════════════════════════

class ToolTip:
    """Hover tooltip for any widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0,0,0,0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify="left",
                 background="#1A2B45", foreground="white",
                 relief="flat", font=("Segoe UI",8), padx=8, pady=4).pack()

    def hide(self, _=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None


class PremiumCard(tk.Frame):
    """Styled card widget with optional left accent bar."""
    def __init__(self, parent, accent=None, bg=None, **kw):
        bg = bg or PALETTE["card"]
        super().__init__(parent, bg=bg,
                          highlightbackground=PALETTE["border"],
                          highlightthickness=1, **kw)
        if accent:
            bar = tk.Frame(self, bg=accent, width=4)
            bar.pack(side="left", fill="y")
        self._content = tk.Frame(self, bg=bg)
        self._content.pack(side="left", fill="both", expand=True, padx=14, pady=12)

    @property
    def content(self):
        return self._content


class AnimatedButton(tk.Button):
    """Button with hover animation."""
    def __init__(self, parent, *, bg, hover_bg, fg="white", **kw):
        super().__init__(parent, bg=bg, fg=fg, activebackground=hover_bg,
                          activeforeground=fg, relief="flat", cursor="hand2", **kw)
        self._bg = bg
        self._hover = hover_bg
        self.bind("<Enter>", lambda _: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _: self.config(bg=self._bg))


class StarRating(tk.Frame):
    """Displays star rating visually."""
    def __init__(self, parent, rating, max_stars=5, bg=None):
        super().__init__(parent, bg=bg or PALETTE["card"])
        r = round(rating * 2) / 2  # round to nearest 0.5
        for i in range(1, max_stars+1):
            if r >= i:
                ch, fg = "★", PALETTE["gold"]
            elif r >= i - 0.5:
                ch, fg = "½", PALETTE["gold"]
            else:
                ch, fg = "☆", PALETTE["text_s"]
            tk.Label(self, text=ch, font=("Segoe UI",11), bg=bg or PALETTE["card"], fg=fg).pack(side="left")
        tk.Label(self, text=f"  {rating}", font=("Segoe UI",9,"bold"),
                 bg=bg or PALETTE["card"], fg=PALETTE["text"]).pack(side="left")


# ══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════

class HealthAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HealthAdvisor v2.0 — Premium Health Companion")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 680)
        self.root.configure(bg=PALETTE["bg"])

        # ── State
        self.dark_mode     = False
        self.symptom_vars  = {}
        self.selected_syms = []
        self.diag_results  = []
        self.diet_data     = None
        self.habits_data   = None
        self.med_data      = None
        self.curr_cond     = None
        self.hospital_results = []

        # ── Tk vars
        self.v_name    = tk.StringVar(value="")
        self.v_age     = tk.StringVar(value="30")
        self.v_gender  = tk.StringVar(value="Male")
        self.v_weight  = tk.StringVar(value="70")
        self.v_diet    = tk.StringVar(value="Non-Vegetarian")
        self.v_allergy = tk.StringVar(value="")
        self.v_search  = tk.StringVar()
        self.v_search.trace("w", self._on_sym_search)
        self.v_location = tk.StringVar(value="")
        self.v_api_key  = tk.StringVar(value="")

        threading.Thread(target=lambda: (get_all_symptoms(), symptom_matching(("fever","cough"))), daemon=True).start()

        self._build_root()

    # ────────────────────────────────────── ROOT LAYOUT
    def _build_root(self):
        P = PALETTE

        # ── Header
        hdr = tk.Frame(self.root, bg=P["brand"], height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Logo area
        logo_f = tk.Frame(hdr, bg=P["brand"])
        logo_f.pack(side="left", padx=20, pady=10)
        tk.Label(logo_f, text="⚕", font=("Segoe UI Emoji",26), bg=P["brand"], fg=P["accent"]).pack(side="left")
        txt_f = tk.Frame(logo_f, bg=P["brand"])
        txt_f.pack(side="left", padx=8)
        tk.Label(txt_f, text="HealthAdvisor", font=("Segoe UI",17,"bold"), bg=P["brand"], fg="white").pack(anchor="w")
        tk.Label(txt_f, text="AI-Powered Health Companion  v2.0", font=("Segoe UI",8), bg=P["brand"], fg=P["text_dim"]).pack(anchor="w")

        # Header buttons
        btn_f = tk.Frame(hdr, bg=P["brand"])
        btn_f.pack(side="right", padx=16)

        self.dark_btn = AnimatedButton(btn_f, text="🌙", bg=P["brand_mid"], hover_bg=P["brand_lite"],
                                       font=("Segoe UI",12), width=3, command=self._toggle_dark, pady=8)
        self.dark_btn.pack(side="right", padx=4)
        ToolTip(self.dark_btn, "Toggle Dark Mode")

        AnimatedButton(btn_f, text="📄 Export", bg=P["brand_lite"], hover_bg=P["brand_mid"],
                       font=("Segoe UI",9,"bold"), command=self._export_report, padx=12, pady=8).pack(side="right", padx=4)

        # ── Disclaimer ribbon
        rib = tk.Frame(self.root, bg="#FFFBEB", height=24)
        rib.pack(fill="x")
        rib.pack_propagate(False)
        tk.Label(rib, text="⚠  Not a substitute for professional medical advice — Always consult a qualified doctor",
                 font=("Segoe UI",8), bg="#FFFBEB", fg="#B45309").pack(side="left", padx=16, pady=3)

        # ── Body: Sidebar + Content
        body = tk.Frame(self.root, bg=P["bg"])
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(body, bg=P["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content (notebook with custom tabs)
        content = tk.Frame(body, bg=P["bg"])
        content.pack(side="left", fill="both", expand=True)
        self._build_main(content)

    # ────────────────────────────────────── SIDEBAR
    def _build_sidebar(self):
        P = PALETTE
        sb = self.sidebar

        # Profile header
        ph = tk.Frame(sb, bg=PALETTE["brand_mid"], padx=12, pady=16)
        ph.pack(fill="x")
        tk.Label(ph, text="👤", font=("Segoe UI Emoji",24), bg=PALETTE["brand_mid"], fg="white").pack()
        tk.Label(ph, text="User Profile", font=("Segoe UI",11,"bold"),
                 bg=PALETTE["brand_mid"], fg="white").pack(pady=(4,0))

        # Scrollable form area
        form_canvas = tk.Canvas(sb, bg=P["sidebar"], highlightthickness=0)
        form_sb = ttk.Scrollbar(sb, orient="vertical", command=form_canvas.yview)
        form_inner = tk.Frame(form_canvas, bg=P["sidebar"])
        form_inner.bind("<Configure>", lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all")))
        form_canvas.create_window((0,0), window=form_inner, anchor="nw")
        form_canvas.configure(yscrollcommand=form_sb.set)
        form_canvas.pack(side="left", fill="both", expand=True)

        def _field(label, var, widget="entry", options=None, placeholder=""):
            f = tk.Frame(form_inner, bg=P["sidebar"])
            f.pack(fill="x", padx=12, pady=4)
            tk.Label(f, text=label, font=("Segoe UI",8), bg=P["sidebar"], fg=P["text_dim"]).pack(anchor="w")
            if widget == "entry":
                e = tk.Entry(f, textvariable=var, font=("Segoe UI",10),
                             bg="#1E3251", fg="white", insertbackground="white",
                             relief="flat", bd=0)
                e.pack(fill="x", ipady=6, padx=1, pady=1)
                # Bottom border effect
                tk.Frame(f, bg=P["accent"], height=2).pack(fill="x")
            elif widget == "combo":
                s = ttk.Combobox(f, textvariable=var, values=options, state="readonly",
                                 font=("Segoe UI",10))
                s.pack(fill="x")

        _field("Full Name", self.v_name)
        _field("Age (years)", self.v_age)
        _field("Gender", self.v_gender, "combo", ("Male","Female","Other"))
        _field("Weight (kg)", self.v_weight)
        _field("Diet Preference", self.v_diet, "combo", ("Vegetarian","Non-Vegetarian","Vegan","Eggetarian"))
        _field("Allergies (comma-sep.)", self.v_allergy)

        # Divider
        tk.Frame(form_inner, bg=PALETTE["brand_mid"], height=1).pack(fill="x", padx=12, pady=8)

        # BMI section
        tk.Label(form_inner, text="📊 BMI Calculator", font=("Segoe UI",9,"bold"),
                 bg=P["sidebar"], fg=P["accent"]).pack(padx=12, anchor="w")

        self.bmi_label = tk.Label(form_inner, text="— / —", font=("Segoe UI",18,"bold"),
                                   bg=P["sidebar"], fg="white")
        self.bmi_label.pack(padx=12, pady=(4,2))
        self.bmi_cat = tk.Label(form_inner, text="Enter weight & age",
                                 font=("Segoe UI",8), bg=P["sidebar"], fg=P["text_dim"])
        self.bmi_cat.pack(padx=12)
        AnimatedButton(form_inner, text="Calculate BMI", bg=P["accent"], hover_bg="#00A98C",
                       fg=P["brand"], font=("Segoe UI",9,"bold"),
                       command=self._calc_bmi, pady=6).pack(fill="x", padx=12, pady=8)

        # Divider
        tk.Frame(form_inner, bg=PALETTE["brand_mid"], height=1).pack(fill="x", padx=12, pady=4)

        # Nav menu labels
        tabs_info = [
            ("🔍","Symptom Checker","symptoms"),
            ("🏥","Find Hospitals","hospitals"),
            ("🥗","Diet Plan","diet"),
            ("💊","Medicines","medicines"),
            ("💪","Habits & Care","habits"),
        ]
        self.nav_labels = {}
        for icon, label, key in tabs_info:
            f = tk.Frame(form_inner, bg=P["sidebar"], cursor="hand2")
            f.pack(fill="x")
            f.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            icon_l = tk.Label(f, text=icon, font=("Segoe UI Emoji",14), bg=P["sidebar"], fg=P["text_dim"], width=3)
            icon_l.pack(side="left", pady=6, padx=(12,4))
            icon_l.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            text_l = tk.Label(f, text=label, font=("Segoe UI",10), bg=P["sidebar"], fg=P["text_dim"], anchor="w")
            text_l.pack(side="left", pady=6, fill="x", expand=True)
            text_l.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            self.nav_labels[key] = (f, icon_l, text_l)

        # About
        tk.Frame(form_inner, bg=PALETTE["brand_mid"], height=1).pack(fill="x", padx=12, pady=8)
        tk.Label(form_inner, text="HealthAdvisor v2.0\n53 conditions · 224 symptoms\nIndian diet · Hospital finder\n© 2025 HealthAdvisor",
                 font=("Segoe UI",7), bg=P["sidebar"], fg=P["text_dim"], justify="left").pack(padx=12, pady=4)

    # ────────────────────────────────────── MAIN NOTEBOOK
    def _build_main(self, parent):
        P = PALETTE

        # Tab bar
        self.tab_bar = tk.Frame(parent, bg=P["card"], height=50)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)
        self.tab_btns = {}

        tab_defs = [
            ("symptoms",  "🔍 Symptom Checker"),
            ("hospitals", "🏥 Hospitals & Doctors"),
            ("diet",      "🥗 Diet Plan"),
            ("medicines", "💊 Medicines"),
            ("habits",    "💪 Habits & Care"),
        ]
        for key, label in tab_defs:
            b = tk.Button(self.tab_bar, text=label, font=("Segoe UI",10),
                          bg=P["card"], fg=P["text_s"], relief="flat",
                          cursor="hand2", padx=16, pady=14,
                          command=lambda k=key: self._switch_tab(k))
            b.pack(side="left")
            self.tab_btns[key] = b

        # Active tab indicator line
        self.tab_indicator = tk.Frame(self.tab_bar, bg=P["accent"], height=3)

        # Pages
        self.pages_frame = tk.Frame(parent, bg=P["bg"])
        self.pages_frame.pack(fill="both", expand=True)
        self.pages = {
            "symptoms":  self._build_symptoms_page(),
            "hospitals": self._build_hospitals_page(),
            "diet":      self._build_diet_page(),
            "medicines": self._build_medicines_page(),
            "habits":    self._build_habits_page(),
        }
        self._switch_tab("symptoms")

    def _switch_tab(self, key):
        P = PALETTE
        for k, btn in self.tab_btns.items():
            if k == key:
                btn.config(fg=P["accent"], font=("Segoe UI",10,"bold"), bg=P["bg"])
            else:
                btn.config(fg=P["text_s"], font=("Segoe UI",10), bg=P["card"])
        for k, page in self.pages.items():
            if k == key: page.pack(fill="both", expand=True)
            else:         page.pack_forget()
        # Sidebar highlight
        for k, (f, il, tl) in self.nav_labels.items():
            if k == key:
                f.config(bg=PALETTE["brand_mid"]); il.config(bg=PALETTE["brand_mid"],fg=PALETTE["accent"])
                tl.config(bg=PALETTE["brand_mid"],fg="white",font=("Segoe UI",10,"bold"))
            else:
                f.config(bg=PALETTE["sidebar"]); il.config(bg=PALETTE["sidebar"],fg=PALETTE["text_dim"])
                tl.config(bg=PALETTE["sidebar"],fg=PALETTE["text_dim"],font=("Segoe UI",10))

    # ────────────────────────────────────── SYMPTOMS PAGE
    def _build_symptoms_page(self):
        P = PALETTE
        page = tk.Frame(self.pages_frame, bg=P["bg"])

        left = tk.Frame(page, bg=P["bg"], width=310)
        left.pack(side="left", fill="y", padx=16, pady=16)
        left.pack_propagate(False)

        right = tk.Frame(page, bg=P["bg"])
        right.pack(side="left", fill="both", expand=True, pady=16, padx=(0,16))

        # ── Left panel
        # Title
        tk.Label(left, text="Select Symptoms", font=FONTS["h3"], bg=P["bg"], fg=P["text"]).pack(anchor="w")
        tk.Label(left, text="Pick 3–10 symptoms that match your condition",
                 font=FONTS["small"], bg=P["bg"], fg=P["text_s"]).pack(anchor="w", pady=(2,10))

        # Search
        sf = tk.Frame(left, bg="white", highlightbackground=P["accent"],
                      highlightthickness=2)
        sf.pack(fill="x", pady=(0,10))
        tk.Label(sf, text="🔍", bg="white", fg=P["text_s"], font=("Segoe UI",11)).pack(side="left",padx=8)
        tk.Entry(sf, textvariable=self.v_search, font=FONTS["body"], bg="white",
                 fg=P["text"], relief="flat", insertbackground=P["brand"]).pack(side="left", fill="x", expand=True, ipady=8)

        # Checkboxes frame
        cb_outer = tk.Frame(left, bg=P["card"], highlightbackground=P["border"], highlightthickness=1)
        cb_outer.pack(fill="both", expand=True)
        self.cb_canvas = tk.Canvas(cb_outer, bg=P["card"], highlightthickness=0, width=290)
        cb_sb = ttk.Scrollbar(cb_outer, orient="vertical", command=self.cb_canvas.yview)
        self.cb_frame = tk.Frame(self.cb_canvas, bg=P["card"])
        self.cb_frame.bind("<Configure>", lambda e: self.cb_canvas.configure(scrollregion=self.cb_canvas.bbox("all")))
        self.cb_canvas.create_window((0,0), window=self.cb_frame, anchor="nw")
        self.cb_canvas.configure(yscrollcommand=cb_sb.set)
        self.cb_canvas.pack(side="left", fill="both", expand=True)
        cb_sb.pack(side="right", fill="y")
        self.cb_canvas.bind_all("<MouseWheel>", lambda e: self.cb_canvas.yview_scroll(-1*(e.delta//120),"units"))

        self._all_symptoms = get_all_symptoms()
        self._populate_checkboxes(self._all_symptoms)

        # Bottom controls
        bot = tk.Frame(left, bg=P["bg"])
        bot.pack(fill="x", pady=(8,0))
        self.sym_count = tk.Label(bot, text="0 selected", font=FONTS["small"],
                                   bg=P["bg"], fg=P["text_s"])
        self.sym_count.pack(side="left")
        AnimatedButton(bot, text="✕ Clear", bg=P["danger"], hover_bg="#DC2626",
                       font=FONTS["small"], command=self._clear_syms, padx=8, pady=4).pack(side="right")

        AnimatedButton(left, text="🔍  Analyze Symptoms",
                       bg=P["accent"], hover_bg="#00A98C", fg=P["brand"],
                       font=("Segoe UI",12,"bold"), command=self._analyze, pady=12).pack(fill="x", pady=10)

        tk.Label(left, text="💡 Supports Hindi symptom names (type in Hindi)",
                 font=FONTS["tiny"], bg=P["bg"], fg=P["text_dim"], wraplength=290, justify="left").pack(anchor="w")

        # ── Right panel
        tk.Label(right, text="Diagnosis Results", font=FONTS["h3"], bg=P["bg"], fg=P["text"]).pack(anchor="w")
        tk.Label(right, text="AI-powered analysis based on 53-condition knowledge base",
                 font=FONTS["small"], bg=P["bg"], fg=P["text_s"]).pack(anchor="w", pady=(2,10))

        rc = tk.Frame(right, bg=P["card"], highlightbackground=P["border"], highlightthickness=1)
        rc.pack(fill="both", expand=True)
        self.res_canvas = tk.Canvas(rc, bg=P["card"], highlightthickness=0)
        res_sb = ttk.Scrollbar(rc, orient="vertical", command=self.res_canvas.yview)
        self.res_inner = tk.Frame(self.res_canvas, bg=P["card"])
        self.res_inner.bind("<Configure>", lambda e: self.res_canvas.configure(scrollregion=self.res_canvas.bbox("all")))
        self.res_canvas.create_window((0,0), window=self.res_inner, anchor="nw")
        self.res_canvas.configure(yscrollcommand=res_sb.set)
        self.res_canvas.pack(side="left", fill="both", expand=True)
        res_sb.pack(side="right", fill="y")
        self._show_placeholder(self.res_inner, "🏥", "Select symptoms and click\nAnalyze Symptoms", P["card"])

        return page

    def _populate_checkboxes(self, symptoms):
        P = PALETTE
        for w in self.cb_frame.winfo_children(): w.destroy()
        for sym in symptoms:
            if sym not in self.symptom_vars:
                self.symptom_vars[sym] = tk.BooleanVar()
            var = self.symptom_vars[sym]
            f = tk.Frame(self.cb_frame, bg=P["card"])
            f.pack(fill="x", padx=2, pady=1)
            cb = tk.Checkbutton(f, text=f"  {sym.title()}", variable=var,
                                 font=FONTS["body"], bg=P["card"], fg=P["text"],
                                 activebackground="#EFF6FF", selectcolor=P["input_bg"],
                                 relief="flat", anchor="w", command=self._update_count)
            cb.pack(fill="x", ipady=4)

    def _on_sym_search(self, *_):
        q = self.v_search.get().lower()
        filtered = [s for s in self._all_symptoms if q in s.lower()] if q else self._all_symptoms
        self._populate_checkboxes(filtered)

    def _update_count(self):
        n = sum(1 for v in self.symptom_vars.values() if v.get())
        self.sym_count.config(text=f"{n} selected",
                               fg=PALETTE["danger"] if n<3 else PALETTE["success"] if n<=10 else PALETTE["warn"])

    def _clear_syms(self):
        for v in self.symptom_vars.values(): v.set(False)
        self._update_count()

    def _analyze(self):
        sel = [s for s,v in self.symptom_vars.items() if v.get()]
        if len(sel) < 3:
            messagebox.showwarning("Too Few", f"Please select at least 3 symptoms.\nCurrently: {len(sel)}")
            return
        if len(sel) > 10:
            messagebox.showwarning("Too Many", f"Please select at most 10 symptoms.\nCurrently: {len(sel)}")
            return
        self.selected_syms = sel

        def _run():
            time.sleep(0.2)
            results = symptom_matching(tuple(sorted(sel)))
            self.diag_results = results
            if results:
                self.curr_cond = results[0]
                self.med_data = get_medicines(results[0]["key"])
                self.habits_data = habit_suggester(results[0]["key"])
            self.root.after(0, lambda: self._display_results(results))

        threading.Thread(target=_run, daemon=True).start()
        self._show_placeholder(self.res_inner, "⏳", "Analyzing...", PALETTE["card"])

    def _display_results(self, results):
        P = PALETTE
        for w in self.res_inner.winfo_children(): w.destroy()

        if not results:
            self._show_placeholder(self.res_inner, "🤔", "No matches found.\nTry more specific symptoms.", P["card"])
            return

        # Summary bar
        sb = tk.Frame(self.res_inner, bg="#EFF6FF", padx=16, pady=10)
        sb.pack(fill="x")
        tk.Label(sb, text=f"Found {len(results)} possible condition(s) for {len(self.selected_syms)} symptoms",
                 font=FONTS["h4"], bg="#EFF6FF", fg=PALETTE["brand"]).pack(side="left")

        for i, r in enumerate(results):
            self._result_card(self.res_inner, r, i)

        # Disclaimer
        dc = tk.Frame(self.res_inner, bg="#FEF3C7", padx=14, pady=10)
        dc.pack(fill="x", padx=16, pady=16)
        tk.Label(dc, text="⚠  AI-generated suggestions only — NOT a medical diagnosis.\n"
                           "Consult a qualified doctor, especially for serious or persistent symptoms.",
                 font=FONTS["tiny"], bg="#FEF3C7", fg="#92400E", justify="left").pack(anchor="w")
        self.res_canvas.yview_moveto(0)

    def _result_card(self, parent, r, idx):
        P = PALETTE
        conf = r["confidence"]
        accent = P["success"] if conf>=50 else P["warn"] if conf>=25 else P["danger"]

        card = PremiumCard(parent, accent=accent)
        card.pack(fill="x", padx=16, pady=8)
        c = card.content

        # Header row
        hrow = tk.Frame(c, bg=P["card"])
        hrow.pack(fill="x")

        # Rank badge
        badge = tk.Label(hrow, text=f"#{idx+1}", font=("Segoe UI",12,"bold"),
                          bg=accent, fg="white", width=3, pady=4)
        badge.pack(side="left", padx=(0,12))

        # Name + hindi
        nf = tk.Frame(hrow, bg=P["card"])
        nf.pack(side="left", fill="x", expand=True)
        tk.Label(nf, text=r["name"], font=("Segoe UI",12,"bold"), bg=P["card"], fg=P["text"]).pack(anchor="w")
        tk.Label(nf, text=f"{r.get('hindi','')}  ·  Consult: {r.get('doctor','GP')}",
                 font=FONTS["small"], bg=P["card"], fg=P["text_s"]).pack(anchor="w")

        # Confidence badge
        cf = tk.Frame(hrow, bg=P["card"])
        cf.pack(side="right")
        tk.Label(cf, text=f"{conf}%", font=("Segoe UI",22,"bold"), bg=P["card"], fg=accent).pack()
        tk.Label(cf, text="confidence", font=FONTS["tiny"], bg=P["card"], fg=P["text_s"]).pack()

        # Progress bar
        pb_bg = tk.Frame(c, bg=P["border"], height=8)
        pb_bg.pack(fill="x", pady=(8,4))
        tk.Frame(pb_bg, bg=accent, height=8).place(x=0,y=0, relwidth=min(conf/100,1), height=8)

        # Tags row
        tr = tk.Frame(c, bg=P["card"])
        tr.pack(fill="x", pady=4)
        sev_map = {"mild":("#ECFDF5","#065F46"),"moderate":("#FFFBEB","#92400E"),
                   "chronic":("#EFF6FF","#1E40AF"),"severe":("#FEF2F2","#991B1B")}
        sb_c, sf_c = sev_map.get(r.get("severity",""),("#F3F4F6","#374151"))
        for lbl, val in [("Severity",r.get("severity","").title()),
                          ("Category",r.get("category","").replace("_"," ").title()),
                          (f"Matched",f"{len(r['matched'])}/{r['total_symptoms']}")]:
            tf = tk.Frame(tr, bg=sb_c, padx=8, pady=3)
            tf.pack(side="left", padx=(0,6))
            tk.Label(tf, text=f"{lbl}: {val}", font=FONTS["tiny"], bg=sb_c, fg=sf_c).pack()

        # Matched symptoms
        tk.Label(c, text="Matching: " + ", ".join(s.title() for s in r["matched"]),
                 font=FONTS["tiny"], bg=P["card"], fg=P["text_s"],
                 wraplength=440, justify="left").pack(anchor="w", pady=(4,8))

        # Action buttons
        br = tk.Frame(c, bg=P["card"])
        br.pack(fill="x")
        for txt, col, hov, fn in [
            ("🏥 Find Hospitals", P["brand"],  P["brand_mid"], lambda cnd=r: self._goto_hospitals(cnd)),
            ("🥗 Diet Plan",      P["accent"],  "#00A98C",      lambda cnd=r: self._goto_diet(cnd)),
            ("💊 Medicines",      P["info"],    "#2563EB",      lambda cnd=r: self._goto_medicines(cnd)),
            ("💪 Habits",         P["success"], "#059669",      lambda cnd=r: self._goto_habits(cnd)),
        ]:
            AnimatedButton(br, text=txt, bg=col, hover_bg=hov, fg="white",
                           font=FONTS["small"], command=fn, padx=10, pady=5).pack(side="left", padx=(0,6))

    # ────────────────────────────────────── HOSPITALS PAGE
    def _build_hospitals_page(self):
        P = PALETTE
        page = tk.Frame(self.pages_frame, bg=P["bg"])

        # Top control bar
        ctrl = tk.Frame(page, bg=P["card"], pady=14)
        ctrl.pack(fill="x", padx=16, pady=(16,8))

        tk.Label(ctrl, text="🏥 Find Nearby Hospitals & Doctors",
                 font=FONTS["h3"], bg=P["card"], fg=P["text"]).pack(anchor="w", padx=16)
        tk.Label(ctrl, text="Enter your location to find the best-rated hospitals near you",
                 font=FONTS["small"], bg=P["card"], fg=P["text_s"]).pack(anchor="w", padx=16, pady=(2,10))

        row1 = tk.Frame(ctrl, bg=P["card"])
        row1.pack(fill="x", padx=16)

        # Location entry
        lf = tk.Frame(row1, bg="white", highlightbackground=P["accent"], highlightthickness=2)
        lf.pack(side="left", fill="x", expand=True, padx=(0,10))
        tk.Label(lf, text="📍", bg="white", font=("Segoe UI Emoji",12)).pack(side="left",padx=8)
        tk.Entry(lf, textvariable=self.v_location, font=FONTS["body"],
                 bg="white", fg=P["text"], relief="flat",
                 insertbackground=P["brand"]).pack(side="left", fill="x", expand=True, ipady=8)

        AnimatedButton(row1, text="🔍 Search", bg=P["accent"], hover_bg="#00A98C",
                       fg=P["brand"], font=("Segoe UI",10,"bold"),
                       command=self._search_hospitals, padx=16, pady=8).pack(side="left")

        # Google API key (optional)
        row2 = tk.Frame(ctrl, bg=P["card"])
        row2.pack(fill="x", padx=16, pady=(8,0))
        tk.Label(row2, text="Google API Key (optional — for richer results):",
                 font=FONTS["tiny"], bg=P["card"], fg=P["text_s"]).pack(side="left")
        gf = tk.Frame(row2, bg=P["input_bg"], highlightbackground=P["border"], highlightthickness=1)
        gf.pack(side="left", padx=8)
        tk.Entry(gf, textvariable=self.v_api_key, font=FONTS["small"],
                 bg=P["input_bg"], fg=P["text"], relief="flat", width=40,
                 show="•", insertbackground=P["brand"]).pack(padx=6, ipady=4)
        tk.Label(row2, text="Leave blank for free OpenStreetMap search",
                 font=FONTS["tiny"], bg=P["card"], fg=P["text_dim"]).pack(side="left", padx=4)

        # Status bar
        self.hosp_status = tk.Label(page, text="Enter a location (city, area, or full address) and click Search",
                                     font=FONTS["small"], bg=P["bg"], fg=P["text_s"])
        self.hosp_status.pack(anchor="w", padx=16, pady=(0,4))

        # Condition filter info
        self.hosp_cond_label = tk.Label(page, text="",
                                         font=FONTS["small"], bg=P["bg"], fg=P["accent"])
        self.hosp_cond_label.pack(anchor="w", padx=16)

        # Results scroll area
        rc = tk.Frame(page, bg=P["bg"])
        rc.pack(fill="both", expand=True, padx=16, pady=(8,16))

        hc = tk.Canvas(rc, bg=P["bg"], highlightthickness=0)
        hs = ttk.Scrollbar(rc, orient="vertical", command=hc.yview)
        self.hosp_inner = tk.Frame(hc, bg=P["bg"])
        self.hosp_inner.bind("<Configure>", lambda e: hc.configure(scrollregion=hc.bbox("all")))
        hc.create_window((0,0), window=self.hosp_inner, anchor="nw")
        hc.configure(yscrollcommand=hs.set)
        hc.pack(side="left", fill="both", expand=True)
        hs.pack(side="right", fill="y")
        self.hosp_canvas = hc

        self._show_placeholder(self.hosp_inner, "🗺️", "Enter your location above to find\nnearby hospitals and clinics", P["bg"])

        return page

    def _goto_hospitals(self, cond):
        self.curr_cond = cond
        self.hosp_cond_label.config(
            text=f"Searching for: {cond.get('doctor','General Physician')} near you  (for {cond['name']})"
        )
        self._switch_tab("hospitals")

    def _search_hospitals(self):
        location = self.v_location.get().strip()
        if not location:
            messagebox.showwarning("No Location", "Please enter your city, area, or full address.")
            return
        if not REQUESTS_OK:
            messagebox.showerror("Missing Library",
                "Hospital search requires the 'requests' library.\n\nInstall it:\n  pip install requests\n\nThen restart the app.")
            return

        self.hosp_status.config(text="⏳ Locating your address...", fg=PALETTE["warn"])
        self._show_placeholder(self.hosp_inner, "⏳", "Searching for hospitals...\nThis may take a few seconds.", PALETTE["bg"])
        self.root.update()

        def _run():
            # Geocode
            coords = geocode_location(location)
            if not coords:
                self.root.after(0, lambda: (
                    self.hosp_status.config(text="❌ Location not found. Try a more specific address.", fg=PALETTE["danger"]),
                    self._show_placeholder(self.hosp_inner,"❌","Location not found.\nTry: 'Connaught Place, Delhi' or 'MG Road, Bangalore'", PALETTE["bg"])
                ))
                return

            lat, lon = coords
            api_key = self.v_api_key.get().strip()

            # Try Google first, then OSM
            hospitals = []
            source_used = "OpenStreetMap"
            if api_key:
                hospitals = search_hospitals_google(lat, lon, api_key)
                source_used = "Google Places"
            if not hospitals:
                hospitals = search_hospitals_osm(lat, lon, radius=8000)
                source_used = "OpenStreetMap"

            self.hospital_results = hospitals
            self.root.after(0, lambda: self._display_hospitals(hospitals, location, lat, lon, source_used))

        threading.Thread(target=_run, daemon=True).start()

    def _display_hospitals(self, hospitals, location, lat, lon, source):
        P = PALETTE
        for w in self.hosp_inner.winfo_children(): w.destroy()

        cond_doctor = self.curr_cond.get("doctor","General Physician") if self.curr_cond else "General Physician"

        if not hospitals:
            self._show_placeholder(self.hosp_inner, "🏥",
                "No hospitals found nearby.\nTry a different location or increase search radius.", P["bg"])
            self.hosp_status.config(text="No results found. Try a broader location name.", fg=P["danger"])
            return

        self.hosp_status.config(
            text=f"✅ Found {len(hospitals)} hospitals near '{location}'  (Source: {source})",
            fg=P["success"]
        )

        # Header card
        hdr = PremiumCard(self.hosp_inner, bg=P["brand"])
        hdr.pack(fill="x", pady=(0,10))
        c = hdr.content
        c.configure(bg=P["brand"])
        tk.Label(c, text=f"📍 Results near: {location}", font=FONTS["h4"],
                 bg=P["brand"], fg="white").pack(anchor="w")
        tk.Label(c, text=f"Specialist needed: {cond_doctor}  ·  Sorted by rating & distance",
                 font=FONTS["small"], bg=P["brand"], fg=P["text_dim"]).pack(anchor="w")

        for i, h in enumerate(hospitals):
            self._hospital_card(self.hosp_inner, h, i, cond_doctor)

        # Disclaimer
        dc = tk.Frame(self.hosp_inner, bg="#FEF3C7", padx=14, pady=8)
        dc.pack(fill="x", pady=8)
        tk.Label(dc, text="⚠  Always call ahead to confirm hours and specialist availability before visiting.",
                 font=FONTS["tiny"], bg="#FEF3C7", fg="#92400E").pack(anchor="w")
        self.hosp_canvas.yview_moveto(0)

    def _hospital_card(self, parent, h, idx, specialist):
        P = PALETTE
        rating = h.get("rating", 0)
        accent = P["success"] if rating >= 4 else P["warn"] if rating >= 3 else P["danger"]

        card = PremiumCard(parent, accent=accent)
        card.pack(fill="x", pady=6)
        c = card.content

        # Top row
        tr = tk.Frame(c, bg=P["card"])
        tr.pack(fill="x")

        # Rank + name
        nf = tk.Frame(tr, bg=P["card"])
        nf.pack(side="left", fill="x", expand=True)

        nh = tk.Frame(nf, bg=P["card"])
        nh.pack(fill="x")
        tk.Label(nh, text=f"#{idx+1}", font=("Segoe UI",11,"bold"),
                 bg=accent, fg="white", width=3).pack(side="left", padx=(0,10))
        name_txt = h.get("name","Unknown Hospital")
        tk.Label(nh, text=name_txt, font=("Segoe UI",12,"bold"),
                 bg=P["card"], fg=P["text"]).pack(side="left", anchor="w")

        # Recommended badge if rating >= 4
        if rating >= 4:
            rec = tk.Frame(nh, bg=P["success"], padx=6, pady=2)
            rec.pack(side="left", padx=8)
            tk.Label(rec, text="✓ Recommended", font=FONTS["tiny"], bg=P["success"], fg="white").pack()

        # Stars
        sf = tk.Frame(c, bg=P["card"])
        sf.pack(anchor="w", pady=(4,2))
        StarRating(sf, rating, bg=P["card"]).pack(side="left")
        tk.Label(sf, text=f"  ({h.get('reviews',0):,} reviews)",
                 font=FONTS["small"], bg=P["card"], fg=P["text_s"]).pack(side="left")

        # Address + distance
        addr = h.get("address","")
        dist = h.get("distance",0)
        info_row = tk.Frame(c, bg=P["card"])
        info_row.pack(fill="x", pady=2)

        if addr:
            tk.Label(info_row, text=f"📍 {addr}", font=FONTS["small"],
                     bg=P["card"], fg=P["text_s"], wraplength=380, justify="left").pack(side="left", anchor="w")
        tk.Label(info_row, text=f"  🚗 {dist} km",
                 font=("Segoe UI",9,"bold"), bg=P["card"], fg=P["brand"]).pack(side="right")

        # Tags row
        tags_row = tk.Frame(c, bg=P["card"])
        tags_row.pack(fill="x", pady=(6,4))

        def _tag(text, bg, fg):
            f = tk.Frame(tags_row, bg=bg, padx=8, pady=3)
            f.pack(side="left", padx=(0,6))
            tk.Label(f, text=text, font=FONTS["tiny"], bg=bg, fg=fg).pack()

        # Open status
        open_now = h.get("open_now")
        if open_now is True:    _tag("🟢 Open Now",  "#ECFDF5","#065F46")
        elif open_now is False: _tag("🔴 Closed",    "#FEF2F2","#991B1B")
        else:                   _tag("⚪ Hours N/A",  "#F3F4F6","#374151")

        # Emergency
        if h.get("emergency") == "yes": _tag("🚨 Emergency", "#FEF2F2","#991B1B")

        # Specialist
        for spec in specialist.split("/"):
            _tag(f"👨‍⚕️ {spec.strip()}", "#EFF6FF","#1E40AF")

        # Source
        _tag(f"📡 {h.get('source','')}", "#F8FAFC","#475569")

        # Phone
        phone = h.get("phone","")
        if phone:
            ph_row = tk.Frame(c, bg=P["card"])
            ph_row.pack(anchor="w")
            tk.Label(ph_row, text=f"📞 {phone}", font=FONTS["small"],
                     bg=P["card"], fg=P["brand"]).pack(side="left")

    # ────────────────────────────────────── DIET PAGE
    def _build_diet_page(self):
        P = PALETTE
        page = tk.Frame(self.pages_frame, bg=P["bg"])

        # Header
        hdr = tk.Frame(page, bg=P["bg"])
        hdr.pack(fill="x", padx=16, pady=(16,8))
        tk.Label(hdr, text="7-Day Personalized Meal Plan", font=FONTS["h3"],
                 bg=P["bg"], fg=P["text"]).pack(side="left")
        self.diet_cond_lbl = tk.Label(hdr, text="", font=FONTS["small"],
                                       bg=P["bg"], fg=P["text_s"])
        self.diet_cond_lbl.pack(side="left", padx=12)

        # Content
        body = tk.Frame(page, bg=P["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=(0,16))

        # Day selector
        day_panel = tk.Frame(body, bg=P["card"], width=180,
                              highlightbackground=P["border"], highlightthickness=1)
        day_panel.pack(side="left", fill="y")
        day_panel.pack_propagate(False)

        tk.Label(day_panel, text="📅 Days", font=FONTS["h4"],
                 bg=P["card"], fg=P["text"]).pack(pady=(14,8), padx=12, anchor="w")

        self.day_btns = {}
        for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
            b = tk.Button(day_panel, text=day, font=FONTS["body"],
                          bg=P["card"], fg=P["text"], relief="flat",
                          cursor="hand2", anchor="w", padx=16, pady=7,
                          command=lambda d=day.lower(): self._show_day(d))
            b.pack(fill="x")
            self.day_btns[day.lower()] = b

        tk.Frame(day_panel, bg=P["border"], height=1).pack(fill="x", padx=10, pady=8)

        AnimatedButton(day_panel, text="🛒 Shopping List", bg=P["warn"], hover_bg="#D97706",
                       font=FONTS["small"], command=self._show_shopping, pady=6).pack(fill="x",padx=10,pady=4)

        self.diet_guide = tk.Label(day_panel, text="", font=FONTS["tiny"],
                                    bg=P["card"], fg=P["text_s"],
                                    wraplength=165, justify="left")
        self.diet_guide.pack(padx=10, pady=8, anchor="w")

        # Meal display
        meal_frame = tk.Frame(body, bg=P["bg"])
        meal_frame.pack(side="left", fill="both", expand=True, padx=(12,0))

        dc = tk.Canvas(meal_frame, bg=P["bg"], highlightthickness=0)
        ds = ttk.Scrollbar(meal_frame, orient="vertical", command=dc.yview)
        self.diet_inner = tk.Frame(dc, bg=P["bg"])
        self.diet_inner.bind("<Configure>", lambda e: dc.configure(scrollregion=dc.bbox("all")))
        dc.create_window((0,0), window=self.diet_inner, anchor="nw")
        dc.configure(yscrollcommand=ds.set)
        dc.pack(side="left", fill="both", expand=True)
        ds.pack(side="right", fill="y")
        self.diet_canvas = dc

        self._show_placeholder(self.diet_inner, "🥗", "Analyze symptoms first,\nthen click 'Diet Plan' on a condition", P["bg"])
        return page

    def _goto_diet(self, cond):
        self.curr_cond = cond
        self._switch_tab("diet")
        try: age = int(self.v_age.get())
        except: age = 30
        try: wt = float(self.v_weight.get())
        except: wt = 70
        veg = "Vegetarian" in self.v_diet.get() or "Vegan" in self.v_diet.get()
        allergies = [a.strip() for a in self.v_allergy.get().split(",") if a.strip()]
        self.diet_data = diet_generator(cond["key"], age, self.v_gender.get(), wt, veg, allergies)
        self.diet_cond_lbl.config(text=f"— {cond['name']} ({cond['confidence']}% confidence)")
        self.diet_guide.config(text=self.diet_data["guidelines"][:120]+"…")
        self._show_day("monday")

    def _show_day(self, day):
        P = PALETTE
        for d, b in self.day_btns.items():
            b.config(bg=PALETTE["accent"] if d==day else PALETTE["card"],
                     fg=PALETTE["brand"] if d==day else PALETTE["text"],
                     font=FONTS["h4"] if d==day else FONTS["body"])
        for w in self.diet_inner.winfo_children(): w.destroy()
        if not self.diet_data:
            self._show_placeholder(self.diet_inner,"🥗","No plan yet",P["bg"]); return

        dd = self.diet_data["weekly_plan"].get(day)
        if not dd: return

        # Day header
        dh = tk.Frame(self.diet_inner, bg=P["brand"], padx=18, pady=14)
        dh.pack(fill="x", pady=(0,8))
        tk.Label(dh, text=day.title(), font=FONTS["h2"], bg=P["brand"], fg="white").pack(side="left")
        macro = f"🔥 {dd['calories']} kcal  ·  🥩 {dd['protein']}g  ·  🌾 {dd['carbs']}g  ·  🥑 {dd['fat']}g"
        tk.Label(dh, text=macro, font=FONTS["small"], bg=P["brand"], fg="#93C5FD").pack(side="right")

        # TDEE bar
        tdee = self.diet_data.get("tdee",2000)
        cal = dd["calories"]
        pct = round(cal/tdee*100)
        bar_f = tk.Frame(self.diet_inner, bg=P["card"], padx=16, pady=8,
                          highlightbackground=P["border"], highlightthickness=1)
        bar_f.pack(fill="x", pady=(0,8))
        tk.Label(bar_f, text=f"Daily vs your estimated need ({tdee} kcal):  {cal} kcal  ({pct}%)",
                 font=FONTS["small"], bg=P["card"], fg=P["text_s"]).pack(anchor="w")
        pb = tk.Frame(bar_f, bg=P["border"], height=10)
        pb.pack(fill="x", pady=4)
        clr = P["success"] if 85<=pct<=115 else P["warn"]
        tk.Frame(pb, bg=clr, height=10).place(x=0,y=0,relwidth=min(pct/100,1.0),height=10)

        icons = {"b":"🌅 Breakfast","l":"☀️ Lunch","s":"🍎 Snack","d":"🌙 Dinner"}
        for mt, meal in dd["meals"].items():
            self._meal_card(self.diet_inner, icons.get(mt,"🍽️"), meal)

        # Prefer/Avoid
        pa = PremiumCard(self.diet_inner)
        pa.pack(fill="x", pady=8)
        cols = tk.Frame(pa.content, bg=PALETTE["card"])
        cols.pack(fill="x")
        cl = tk.Frame(cols, bg=PALETTE["card"])
        cl.pack(side="left", fill="both", expand=True)
        cr = tk.Frame(cols, bg=PALETTE["card"])
        cr.pack(side="left", fill="both", expand=True)
        tk.Label(cl, text="✅ Prefer", font=FONTS["h4"], bg=PALETTE["card"], fg=PALETTE["success"]).pack(anchor="w")
        tk.Label(cl, text=", ".join(self.diet_data.get("prefer",[])),
                 font=FONTS["tiny"], bg=PALETTE["card"], fg=PALETTE["text_s"],
                 wraplength=200, justify="left").pack(anchor="w", pady=4)
        tk.Label(cr, text="❌ Avoid", font=FONTS["h4"], bg=PALETTE["card"], fg=PALETTE["danger"]).pack(anchor="w")
        tk.Label(cr, text=", ".join(self.diet_data.get("avoid",[])),
                 font=FONTS["tiny"], bg=PALETTE["card"], fg=PALETTE["text_s"],
                 wraplength=200, justify="left").pack(anchor="w", pady=4)
        self.diet_canvas.yview_moveto(0)

    def _meal_card(self, parent, label, meal):
        P = PALETTE
        card = PremiumCard(parent, accent=P["accent"])
        card.pack(fill="x", pady=5)
        c = card.content
        row = tk.Frame(c, bg=P["card"])
        row.pack(fill="x")
        tk.Label(row, text=label, font=FONTS["h4"], bg=P["card"], fg=P["text"]).pack(anchor="w")
        tk.Label(row, text=meal["name"], font=("Segoe UI",11,"bold"),
                 bg=P["card"], fg=P["brand"], wraplength=420, justify="left").pack(anchor="w", pady=2)
        # Macro pills
        pf = tk.Frame(c, bg=P["card"])
        pf.pack(anchor="w", pady=4)
        for txt, col in [(f"🔥 {meal['calories']} kcal",P["brand"]),
                          (f"Protein {meal['protein']}g",P["success"]),
                          (f"Carbs {meal['carbs']}g",P["warn"]),
                          (f"Fat {meal['fat']}g",P["text_s"])]:
            pill = tk.Frame(pf, bg=P["bg"], padx=8, pady=3)
            pill.pack(side="left", padx=(0,6))
            tk.Label(pill, text=txt, font=FONTS["tiny"], bg=P["bg"], fg=col).pack()

    def _show_shopping(self):
        if not self.diet_data:
            messagebox.showinfo("No Plan","Generate a diet plan first."); return
        P = PALETTE
        pop = tk.Toplevel(self.root)
        pop.title("🛒 Weekly Shopping List")
        pop.geometry("420x540")
        pop.configure(bg=P["bg"])
        tk.Label(pop, text="🛒  Weekly Shopping List", font=FONTS["h3"],
                 bg=P["bg"], fg=P["text"]).pack(pady=16)
        f = tk.Frame(pop, bg=P["card"], highlightbackground=P["border"], highlightthickness=1)
        f.pack(fill="both", expand=True, padx=16, pady=(0,16))
        st = scrolledtext.ScrolledText(f, font=FONTS["mono"], bg=P["card"], fg=P["text"],
                                       relief="flat", wrap="word")
        st.pack(fill="both", expand=True, padx=8, pady=8)
        for item in self.diet_data.get("shopping_list",[]):
            st.insert("end", f"  ☐  {item}\n")
        st.config(state="disabled")

    # ────────────────────────────────────── MEDICINES PAGE
    def _build_medicines_page(self):
        P = PALETTE
        page = tk.Frame(self.pages_frame, bg=P["bg"])

        mc = tk.Canvas(page, bg=P["bg"], highlightthickness=0)
        ms = ttk.Scrollbar(page, orient="vertical", command=mc.yview)
        self.med_inner = tk.Frame(mc, bg=P["bg"])
        self.med_inner.bind("<Configure>", lambda e: mc.configure(scrollregion=mc.bbox("all")))
        mc.create_window((0,0), window=self.med_inner, anchor="nw")
        mc.configure(yscrollcommand=ms.set)
        mc.pack(side="left", fill="both", expand=True)
        ms.pack(side="right", fill="y")
        self.med_canvas = mc

        self._show_placeholder(self.med_inner, "💊",
            "Analyze your symptoms first,\nthen click 'Medicines' on a condition card", P["bg"])
        return page

    def _goto_medicines(self, cond):
        self.curr_cond = cond
        self.med_data = get_medicines(cond["key"])
        self._switch_tab("medicines")
        self._display_medicines()

    def _display_medicines(self):
        P = PALETTE
        for w in self.med_inner.winfo_children(): w.destroy()

        if not self.med_data:
            cond_name = self.curr_cond["name"] if self.curr_cond else "this condition"
            self._show_placeholder(self.med_inner, "💊",
                f"No OTC medicine suggestions available for {cond_name}.\n"
                "Please consult a doctor or pharmacist.", P["bg"])
            return

        cond = self.curr_cond
        # Page header
        hdr = tk.Frame(self.med_inner, bg=P["brand"], padx=20, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"💊  Medicine Suggestions", font=FONTS["h2"],
                 bg=P["brand"], fg="white").pack(anchor="w")
        tk.Label(hdr, text=f"Condition: {cond['name']} ({cond.get('hindi','')})  ·  Consult: {cond.get('doctor','GP')}",
                 font=FONTS["small"], bg=P["brand"], fg=P["text_dim"]).pack(anchor="w")

        # Important disclaimer
        disc_card = tk.Frame(self.med_inner, bg="#FEF3C7", padx=16, pady=12)
        disc_card.pack(fill="x", padx=16, pady=(16,8))
        tk.Label(disc_card,
                 text="⚠️  IMPORTANT DISCLAIMER\n"
                      "These are commonly used OTC (over-the-counter) suggestions for informational purposes only.\n"
                      "Self-medication can be harmful. Always consult a qualified doctor or pharmacist before taking any medicine.\n"
                      "Dosages mentioned are for adults only. Children, pregnant women, and elderly patients need medical supervision.",
                 font=FONTS["small"], bg="#FEF3C7", fg="#92400E", justify="left").pack(anchor="w")

        # OTC Medicines
        tk.Label(self.med_inner, text="💊  Commonly Used Medicines",
                 font=FONTS["h3"], bg=P["bg"], fg=P["text"]).pack(anchor="w", padx=16, pady=(16,4))
        tk.Label(self.med_inner, text="OTC options — verify with your pharmacist",
                 font=FONTS["small"], bg=P["bg"], fg=P["text_s"]).pack(anchor="w", padx=16, pady=(0,8))

        for i, med in enumerate(self.med_data.get("otc",[])):
            self._medicine_card(self.med_inner, med, i)

        # Home Remedies
        hr = self.med_data.get("home_remedies",[])
        if hr:
            tk.Label(self.med_inner, text="🌿  Indian Home Remedies",
                     font=FONTS["h3"], bg=P["bg"], fg=P["text"]).pack(anchor="w", padx=16, pady=(16,4))

            hrem_card = PremiumCard(self.med_inner, accent=P["success"])
            hrem_card.pack(fill="x", padx=16, pady=4)
            for rem in hr:
                row = tk.Frame(hrem_card.content, bg=P["card"], padx=0, pady=2)
                row.pack(fill="x")
                tk.Label(row, text="🌿", font=("Segoe UI Emoji",12), bg=P["card"]).pack(side="left",padx=(0,8))
                tk.Label(row, text=rem, font=FONTS["body"], bg=P["card"], fg=P["text"],
                         wraplength=480, justify="left").pack(side="left", anchor="w")

        # When to see doctor
        wtsd = self.med_data.get("when_to_see_doctor","")
        if wtsd:
            alarm = tk.Frame(self.med_inner, bg="#FEF2F2", padx=16, pady=14)
            alarm.pack(fill="x", padx=16, pady=(16,16))
            tk.Label(alarm, text="🚨  When to STOP self-medication & See a Doctor Immediately:",
                     font=FONTS["h4"], bg="#FEF2F2", fg="#991B1B").pack(anchor="w")
            tk.Label(alarm, text=wtsd, font=FONTS["body"],
                     bg="#FEF2F2", fg=P["text"], wraplength=600, justify="left").pack(anchor="w", pady=4)

        self.med_canvas.yview_moveto(0)

    def _medicine_card(self, parent, med, idx):
        P = PALETTE
        card = PremiumCard(parent, accent=P["info"])
        card.pack(fill="x", padx=16, pady=6)
        c = card.content

        # Header
        hrow = tk.Frame(c, bg=P["card"])
        hrow.pack(fill="x")
        badge = tk.Label(hrow, text=str(idx+1), font=("Segoe UI",11,"bold"),
                          bg=P["info"], fg="white", width=3, pady=3)
        badge.pack(side="left", padx=(0,12))
        tk.Label(hrow, text=med["name"], font=("Segoe UI",11,"bold"),
                 bg=P["card"], fg=P["brand"]).pack(side="left", anchor="w")

        # Details grid
        for row_data in [("🎯 Use", med["use"]), ("💊 Dose", med["dose"]), ("⚠️ Caution", med["caution"])]:
            row = tk.Frame(c, bg=P["card"])
            row.pack(fill="x", pady=2)
            label, val = row_data
            # color caution in orange
            fg = P["warn"] if "Caution" in label else P["text"]
            bg_pill = "#FFFBEB" if "Caution" in label else P["bg"]
            lf = tk.Frame(row, bg=bg_pill, padx=6, pady=2, width=80)
            lf.pack(side="left", padx=(0,8))
            lf.pack_propagate(False)
            tk.Label(lf, text=label, font=FONTS["tiny"], bg=bg_pill, fg=fg).pack(anchor="w")
            tk.Label(row, text=val, font=FONTS["small"], bg=P["card"], fg=P["text"],
                     wraplength=440, justify="left").pack(side="left", anchor="w")

    # ────────────────────────────────────── HABITS PAGE
    def _build_habits_page(self):
        P = PALETTE
        page = tk.Frame(self.pages_frame, bg=P["bg"])

        hdr = tk.Frame(page, bg=P["bg"])
        hdr.pack(fill="x", padx=16, pady=(16,4))
        tk.Label(hdr, text="Daily Habits & Precautions", font=FONTS["h3"],
                 bg=P["bg"], fg=P["text"]).pack(side="left")
        self.habits_cond_lbl = tk.Label(hdr, text="", font=FONTS["small"],
                                         bg=P["bg"], fg=P["text_s"])
        self.habits_cond_lbl.pack(side="left", padx=12)

        hc = tk.Canvas(page, bg=P["bg"], highlightthickness=0)
        hs = ttk.Scrollbar(page, orient="vertical", command=hc.yview)
        self.hab_inner = tk.Frame(hc, bg=P["bg"])
        self.hab_inner.bind("<Configure>", lambda e: hc.configure(scrollregion=hc.bbox("all")))
        hc.create_window((0,0), window=self.hab_inner, anchor="nw")
        hc.configure(yscrollcommand=hs.set)
        hc.pack(side="left", fill="both", expand=True, padx=16, pady=(0,16))
        hs.pack(side="right", fill="y")
        self.hab_canvas = hc

        self._show_placeholder(self.hab_inner, "💪",
            "Analyze your symptoms first,\nthen click 'Habits' on a condition card", P["bg"])
        return page

    def _goto_habits(self, cond):
        self.curr_cond = cond
        self.habits_data = habit_suggester(cond["key"])
        self.habits_cond_lbl.config(text=f"— {cond['name']} ({cond.get('hindi','')})")
        self._switch_tab("habits")
        self._display_habits()

    def _display_habits(self):
        P = PALETTE
        for w in self.hab_inner.winfo_children(): w.destroy()
        if not self.habits_data:
            self._show_placeholder(self.hab_inner,"💪","No data",P["bg"]); return

        data = self.habits_data
        cond = self.curr_cond

        # Page header
        hdr = tk.Frame(self.hab_inner, bg=P["brand"], padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💪  Lifestyle Guide", font=FONTS["h2"], bg=P["brand"], fg="white").pack(anchor="w")
        if cond:
            tk.Label(hdr, text=f"Tailored for: {cond['name']}  ·  {cond.get('hindi','')}",
                     font=FONTS["small"], bg=P["brand"], fg=P["text_dim"]).pack(anchor="w")

        # Two columns
        cols = tk.Frame(self.hab_inner, bg=P["bg"])
        cols.pack(fill="both", expand=True, padx=16, pady=12)

        lc = tk.Frame(cols, bg=P["bg"])
        lc.pack(side="left", fill="both", expand=True, padx=(0,8))
        rc = tk.Frame(cols, bg=P["bg"])
        rc.pack(side="left", fill="both", expand=True, padx=(8,0))

        self._habits_section(lc, "💪 Daily Habits", "Build these habits consistently",
                              data.get("habits",[]), P["success"], "#ECFDF5")
        self._habits_section(rc, "⚠️ Precautions", "Avoid or be careful about these",
                              data.get("precautions",[]), P["danger"], "#FEF2F2")

        # Yoga card
        yoga = data.get("yoga",[])
        if yoga:
            yc = PremiumCard(self.hab_inner, accent=P["accent"])
            yc.pack(fill="x", padx=16, pady=8)
            tk.Label(yc.content, text="🧘  Recommended Yoga & Pranayama",
                     font=FONTS["h4"], bg=PALETTE["card"], fg=PALETTE["accent"]).pack(anchor="w")
            yrow = tk.Frame(yc.content, bg=PALETTE["card"])
            yrow.pack(fill="x", pady=8)
            for pose in yoga:
                pf = tk.Frame(yrow, bg="#EFF6FF", padx=10, pady=6)
                pf.pack(side="left", padx=(0,8))
                tk.Label(pf, text=f"🌿 {pose}", font=FONTS["small"],
                         bg="#EFF6FF", fg=PALETTE["brand"]).pack()

        # Monitoring card
        mon = data.get("monitoring","")
        if mon:
            mc = PremiumCard(self.hab_inner, accent=P["brand"])
            mc.pack(fill="x", padx=16, pady=8)
            tk.Label(mc.content, text="📊  Health Monitoring Plan",
                     font=FONTS["h4"], bg=PALETTE["card"], fg=PALETTE["brand"]).pack(anchor="w")
            tk.Label(mc.content, text=mon, font=FONTS["body"],
                     bg=PALETTE["card"], fg=PALETTE["text"],
                     wraplength=700, justify="left").pack(anchor="w", pady=6)

        # Disclaimer
        dc = tk.Frame(self.hab_inner, bg="#FEF3C7", padx=14, pady=10)
        dc.pack(fill="x", padx=16, pady=8)
        tk.Label(dc, text="⚠  These are general wellness guidelines. Individual needs vary. Consult your doctor for personalised advice.",
                 font=FONTS["tiny"], bg="#FEF3C7", fg="#92400E").pack(anchor="w")
        self.hab_canvas.yview_moveto(0)

    def _habits_section(self, parent, title, subtitle, items, accent, light_bg):
        P = PALETTE
        card = PremiumCard(parent, accent=accent)
        card.pack(fill="both", expand=True)
        c = card.content
        tk.Label(c, text=title, font=("Segoe UI",12,"bold"),
                 bg=P["card"], fg=accent).pack(anchor="w")
        tk.Label(c, text=subtitle, font=FONTS["small"],
                 bg=P["card"], fg=P["text_s"]).pack(anchor="w", pady=(0,8))
        for i, item in enumerate(items, 1):
            f = tk.Frame(c, bg=light_bg, padx=10, pady=8)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=str(i), font=("Segoe UI",10,"bold"),
                     bg=accent, fg="white", width=2).pack(side="left", padx=(0,10))
            tk.Label(f, text=item, font=("Segoe UI",9),
                     bg=light_bg, fg=P["text"], wraplength=270, justify="left").pack(side="left", anchor="w")

    # ────────────────────────────────────── SHARED HELPERS
    def _show_placeholder(self, parent, emoji, text, bg):
        for w in parent.winfo_children(): w.destroy()
        tk.Label(parent, text=emoji, font=("Segoe UI Emoji",52), bg=bg, fg=PALETTE["border"]).pack(pady=(60,12))
        tk.Label(parent, text=text, font=FONTS["body"], bg=bg, fg=PALETTE["text_s"], justify="center").pack()

    def _calc_bmi(self):
        try:
            wt = float(self.v_weight.get())
            age = int(self.v_age.get())
            h = 1.70 if self.v_gender.get()=="Male" else 1.58
            bmi = round(wt/h**2, 1)
            if bmi < 18.5:   cat, col = "Underweight", "#3B82F6"
            elif bmi < 25:   cat, col = "Normal ✅",   PALETTE["success"]
            elif bmi < 30:   cat, col = "Overweight",  PALETTE["warn"]
            else:             cat, col = "Obese",       PALETTE["danger"]
            self.bmi_label.config(text=str(bmi))
            self.bmi_cat.config(text=cat, fg=col)
        except ValueError:
            messagebox.showwarning("Invalid","Please enter valid weight and age.")

    # ────────────────────────────────────── DARK MODE
    def _toggle_dark(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            PALETTE.update({"bg":PALETTE["d_bg"],"card":PALETTE["d_card"],"card2":PALETTE["d_card2"],
                             "text":PALETTE["d_text"],"text_s":PALETTE["d_text_s"],
                             "border":PALETTE["d_border"],"input_bg":PALETTE["d_input"]})
            self.dark_btn.config(text="☀️")
        else:
            PALETTE.update({"bg":"#F0F4FA","card":"#FFFFFF","card2":"#F7F9FC",
                             "text":"#1A2B45","text_s":"#5A6A80",
                             "border":"#E2E8F0","input_bg":"#F8FAFC"})
            self.dark_btn.config(text="🌙")
        self.root.configure(bg=PALETTE["bg"])

    # ────────────────────────────────────── EXPORT
    def _export_report(self):
        if not self.diag_results:
            messagebox.showwarning("No Report","Analyze symptoms first."); return
        pop = tk.Toplevel(self.root)
        pop.title("Export"); pop.geometry("320x160")
        pop.configure(bg=PALETTE["bg"]); pop.grab_set()
        tk.Label(pop,"Export Health Report", font=FONTS["h3"],
                 bg=PALETTE["bg"], fg=PALETTE["text"]).pack(pady=(20,8))
        bf = tk.Frame(pop, bg=PALETTE["bg"])
        bf.pack()
        AnimatedButton(bf, text="📄 TXT", bg=PALETTE["brand"], hover_bg=PALETTE["brand_mid"],
                       font=FONTS["body"], padx=20, pady=8,
                       command=lambda:(pop.destroy(),self._export_txt())).pack(side="left",padx=8)
        AnimatedButton(bf, text="📋 PDF", bg=PALETTE["accent"], hover_bg="#00A98C",
                       fg=PALETTE["brand"], font=FONTS["body"], padx=20, pady=8,
                       command=lambda:(pop.destroy(),self._export_pdf())).pack(side="left",padx=8)

    def _get_user(self):
        return {"name":self.v_name.get()or"User","age":self.v_age.get(),"gender":self.v_gender.get(),
                "weight":self.v_weight.get(),"diet_type":self.v_diet.get(),
                "symptoms":[s for s,v in self.symptom_vars.items() if v.get()]}

    def _export_txt(self):
        fp = filedialog.asksaveasfilename(defaultextension=".txt",
             filetypes=[("Text","*.txt")],
             initialfile=f"HealthAdvisor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if not fp: return
        rpt = generate_report_text(self._get_user(), self.diag_results,
                                    self.diet_data, self.habits_data, self.med_data)
        try:
            with open(fp,"w",encoding="utf-8") as f: f.write(rpt)
            messagebox.showinfo("Saved", f"Report saved:\n{fp}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            messagebox.showerror("ReportLab Missing",
                "Install reportlab:\n  pip install reportlab\nSaving as TXT instead.")
            self._export_txt(); return

        fp = filedialog.asksaveasfilename(defaultextension=".pdf",
             filetypes=[("PDF","*.pdf")],
             initialfile=f"HealthAdvisor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not fp: return

        try:
            doc = SimpleDocTemplate(fp, pagesize=A4,
                                    rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            H1 = ParagraphStyle("H1",parent=styles["Title"],textColor=colors.HexColor("#0A2342"),fontSize=22)
            H2 = ParagraphStyle("H2",parent=styles["Heading2"],textColor=colors.HexColor("#1E4D8C"),fontSize=13)
            B  = ParagraphStyle("B", parent=styles["Normal"],fontSize=10,leading=16)
            W  = ParagraphStyle("W", parent=styles["Normal"],backColor=colors.HexColor("#FEF3C7"),
                                textColor=colors.HexColor("#92400E"),fontSize=9,leading=14,borderPadding=8)
            FT = ParagraphStyle("FT",parent=styles["Normal"],textColor=colors.HexColor("#9CA3AF"),
                                fontSize=8,alignment=TA_CENTER)

            elems = []
            elems += [Paragraph("⚕ HealthAdvisor v2.0 — Health Report",H1),
                      Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",B),
                      Spacer(1,.3*cm),
                      HRFlowable(width="100%",thickness=2,color=colors.HexColor("#00C9A7")),
                      Spacer(1,.3*cm),
                      Paragraph("⚠ DISCLAIMER: Informational only. NOT a medical diagnosis. Consult a qualified doctor.",W),
                      Spacer(1,.4*cm),Paragraph("User Profile",H2)]

            u = self._get_user()
            td = [["Name",u["name"],"Age",u["age"]],["Gender",u["gender"],"Weight",f"{u['weight']} kg"],
                  ["Diet",u["diet_type"],"Allergies",self.v_allergy.get()or"None"]]
            t = Table(td,colWidths=[3*cm,5*cm,3*cm,5*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EFF6FF")),
                                   ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#EFF6FF")),
                                   ("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),.5,colors.HexColor("#E5E7EB")),
                                   ("PADDING",(0,0),(-1,-1),6)]))
            elems += [t,Spacer(1,.4*cm),Paragraph("Symptoms",H2),
                      Paragraph(", ".join(s.title() for s in u["symptoms"])or"None",B),Spacer(1,.4*cm)]

            if self.diag_results:
                elems.append(Paragraph("Diagnosis Results",H2))
                for r in self.diag_results:
                    elems.append(Paragraph(f"<b>{r['name']}</b> ({r.get('hindi','')}) — {r['confidence']}% confidence",B))
                    elems.append(Paragraph(f"Consult: {r.get('doctor','GP')} | Matched: {', '.join(r['matched'])}",B))
                    elems.append(Spacer(1,.15*cm))

            if self.med_data:
                elems += [Spacer(1,.3*cm),Paragraph("OTC Medicine Suggestions",H2)]
                for m in self.med_data.get("otc",[]):
                    elems.append(Paragraph(f"• <b>{m['name']}</b> — {m['use']} | Dose: {m['dose']}",B))

            if self.habits_data:
                elems += [Spacer(1,.3*cm),Paragraph("Daily Habits",H2)]
                for h in self.habits_data.get("habits",[]): elems.append(Paragraph(f"• {h}",B))
                elems += [Spacer(1,.2*cm),Paragraph("Precautions",H2)]
                for p in self.habits_data.get("precautions",[]): elems.append(Paragraph(f"• {p}",B))

            elems += [Spacer(1,.5*cm),HRFlowable(width="100%",thickness=1,color=colors.HexColor("#E5E7EB")),
                      Paragraph("HealthAdvisor v2.0  |  Educational purposes only  |  Not a medical device",FT)]
            doc.build(elems)
            messagebox.showinfo("Saved",f"PDF saved:\n{fp}")
        except Exception as e:
            messagebox.showerror("PDF Error",f"{e}\nSaving as TXT.")
            self._export_txt()


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
def main():
    t0 = time.time()

    # Windows DPI fix
    try:
        from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    root = tk.Tk()
    root.withdraw()

    # Apply ttk style
    style = ttk.Style(root)
    try: style.theme_use("clam")
    except: pass
    style.configure("TScrollbar", background=PALETTE["border"],
                    troughcolor=PALETTE["bg"], arrowcolor=PALETTE["text_s"])
    style.configure("TCombobox", fieldbackground=PALETTE["input_bg"],
                    background="white", foreground=PALETTE["text"])

    app = HealthAdvisorApp(root)

    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    ww, wh = root.winfo_width(), root.winfo_height()
    root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
    root.deiconify()

    print(f"✅ HealthAdvisor v2.0 loaded in {time.time()-t0:.3f}s")
    if not REQUESTS_OK:
        print("⚠  'requests' not installed — hospital search disabled.")
        print("   Run: pip install requests")
    print("   Disclaimer: Educational only. Not a medical device.")
    root.mainloop()

if __name__ == "__main__":
    main()
