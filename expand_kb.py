import json
import os

kb_path = r'c:\idea1\vaidya_slm\backend\engine\knowledge_base.json'

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Vata Expansion
kb['doshas']['Vata']['primary_symptoms'].extend([
    "sciatica", "tinnitus", "restless legs", "speech difficulty", "tremors", "dehydration",
    "muscle wasting", "unexplained weight loss", "hearing loss", "dizziness", "vertigo"
])
kb['doshas']['Vata']['secondary_symptoms'].extend([
    "brittle nails", "cracking joints", "lower back ache", "twitching eyelids", "nerve pain",
    "sharp shooting pains", "sensitivity to cold wind", "prefers hot environment",
    "irregular pulse", "anxious heartbeat", "difficulty falling asleep", "vivid dreams",
    "fear of heights", "social withdrawal from anxiety", "dry throat", "hoarse voice",
    "scanty sweat", "rough skin texture", "cold extremities", "mental scatteredness"
])
kb['doshas']['Vata']['remedies'].extend([
    "Dashamula decoction for nerve strengthening",
    "Narayana oil for joint massage",
    "Warm milk with pinch of nutmeg before bed",
    "Mahanarayan oil application on painful joints",
    "Haritaki powder with warm water at night",
    "Avoid air-conditioned rooms",
    "Practice grounding meditation in nature",
    "Consume cooked beets and carrots with ghee",
    "Shatavari kalpa for nourishing tissues",
    "Brahmi Vati for mental calmness"
])

# Pitta Expansion
kb['doshas']['Pitta']['primary_symptoms'].extend([
    "acid reflux", "gerd", "stomach ulser", "hyperacidity", "liver congestion", 
    "hypertension", "photophobia", "burning eyes", "urticaria", "hives", "migraine"
])
kb['doshas']['Pitta']['secondary_symptoms'].extend([
    "yellowish urine", "sharp hunger pains", "intolerance to missed meals", "strong body odor",
    "excessive thirst", "craves cold drinks", "easily frustrated", "judgmental attitude",
    "redness in face", "sensitive to chemicals", "pustular acne", "burning soles of feet",
    "hot flashes", "profuse sweating", "sharp intellect but critical", "inflammation in gums"
])
kb['doshas']['Pitta']['remedies'].extend([
    "Gulvel (Guduchi) satva for cooling the blood",
    "Kamadhuda ras for acidity control",
    "Avipattikar churna before meals",
    "Praval pisti or Mukta pisti for heat reduction",
    "Chandanasava or Usheerasava for cooling",
    "Apply sandalwood paste on forehead for migraines",
    "Sip rose water mixed with normal water",
    "Avoid midday sun exposure",
    "Eat sweet pomegranate and grapes",
    "Coconut oil application on scalp for cooling"
])

# Kapha Expansion
kb['doshas']['Kapha']['primary_symptoms'].extend([
    "obesity", "hypothyroidism", "diabetes", "type 2 diabetes", "oedema", "water retention",
    "chronic sinusitis", "nasal polyps", "depression", "metabolic syndrome", "high cholesterol"
])
kb['doshas']['Kapha']['secondary_symptoms'].extend([
    "wakes up feeling unrefreshed", "sticky coating on tongue in morning", "sluggish bowel movement",
    "heavy limbs", "difficulty losing weight despite low intake", "cravings for sweets and salt",
    "frequent colds and flu", "excessive ear wax", "thick skin", "oily complexion",
    "attached to possessions", "procrastination", "mental fog after eating", "swollen ankles",
    "low body temperature", "slow pulse rate", "excessive salivation"
])
kb['doshas']['Kapha']['remedies'].extend([
    "Trikatu churna (Ginger, Black Pepper, Long Pepper) for metabolism",
    "Guggul preparations for cholesterol and joints",
    "Shilajit for vitality and removing kapha blockages",
    "Varanadi kashayam for obesity control",
    "Kanchanar guggulu for thyroid issues",
    "Honey with warm water and lemon in morning",
    "Punarnava for reducing water retention",
    "Chitrakadi vati for digestion stimulation",
    "Sunthi (Dry Ginger) powder in all meals",
    "Engage in loud singing or active dancing to stimulate energy"
])

# Remove duplicates if any
for dosha in kb['doshas']:
    for category in ['primary_symptoms', 'secondary_symptoms', 'remedies']:
        kb['doshas'][dosha][category] = list(dict.fromkeys(kb['doshas'][dosha][category]))

with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f"Successfully expanded knowledge base at {kb_path}")
