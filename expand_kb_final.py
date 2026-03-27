import json
import os

kb_path = r'c:\idea1\vaidya_slm\backend\engine\knowledge_base.json'

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Vata Deeper Expansion
kb['doshas']['Vata']['secondary_symptoms'].extend([
    "travel sickness", "air travel discomfort", "excessive computing", "smartphone addiction",
    "late night reading", "irregular lunch", "skipping breakfast", "dry eyes from screen",
    "carpal tunnel", "neck stiffness from phone", "anxiety from social media", "light sleep with nightmares",
    "stuttering", "low libido from fatigue", "cold sweats from fear", "trembling hands",
    "prone to fractures", "premature wrinkles", "sensitive to noise", "feeling cold in summer",
    "fast talker", "easily distracted", "difficulty finishing tasks", "shaking legs while sitting",
    "thin and brittle hair", "brownish complexion", "loss of muscle mass", "hyper-flexible joints",
    "variable appetite", "gas after eating beans", "feeling lonely", "existential dread", "phobias"
])
kb['doshas']['Vata']['remedies'].extend([
    "Saraswatarishta for brain nourishment",
    "Yograj Guggulu for joint pains",
    "Consumption of warm Ghee with every meal",
    "Pranayama - Anulom Vilom (Alternate nostril breathing)",
    "Oil pulling with warm sesame oil in morning",
    "Vata-pacifying music (soft, slow, calming)",
    "Avoid dry snacks and crackers",
    "Abhyanga with Dhanwantaram tailam",
    "Nasyam (nasal oiling) with Anu tailam",
    "Regular routine for sleep and waking"
])

# Pitta Deeper Expansion
kb['doshas']['Pitta']['secondary_symptoms'].extend([
    "workaholic tendency", "competitive gaming stress", "angry outbursts at traffic", "deadline pressure",
    "cravings for alcohol", "sensitivity to fried food", "hot flashes at night", "excessive bleeding from wounds",
    "red eyes after swimming", "burning after spicy food", "sour eructations", "bitter taste in mouth",
    "mouth ulcers from heat", "early graying of beard", "perfectionist stress", "judgmental of others",
    "sharp tongue", "excessive body heat in winter", "sweating from small movements", "migraine on right side",
    "hates direct sunlight", "prefers cool drinks over food", "strong digestion", "irritability with hunger"
])
kb['doshas']['Pitta']['remedies'].extend([
    "Shatavari Ghruta (medicated ghee) for cooling",
    "Chandanasava for internal heat reduction",
    "Apply fresh Aloe Vera pulp on burns or rashes",
    "Drink water from a copper vessel kept overnight (moderation)",
    "Consumption of Gulkand (rose petal jam) daily",
    "Bhumyamalaki for liver protection",
    "Triphala Ghruta for eye health",
    "Sip cool coconut water during hot afternoons",
    "Avoid fermented foods like curd and vinegar",
    "Meditation focusing on forgiveness (Metta meditation)"
])

# Kapha Deeper Expansion
kb['doshas']['Kapha']['secondary_symptoms'].extend([
    "sedentary job tiredness", "cravings for chocolates", "sleeping after lunch", "excessive phlegm in morning",
    "difficulty starting projects", "hoarding tendencies", "slow processing of emotions", "stubbornness",
    "feeling heavy in cloudy weather", "swollen feet after long sitting", "sticky sweat with mild odor",
    "greasy hair", "thick skin", "low motivation", "attachment to old habits", "emotional eating",
    "water retention during periods", "slow and deep breathing", "very steady but slow mind",
    "dense and strong teeth", "prefers salty and sweet tastes", "difficulty waking up before 8 AM",
    "prone to chest congestion in winter", "feeling of laziness even after sleep"
])
kb['doshas']['Kapha']['remedies'].extend([
    "Trikatu powder with honey to stimulate digestion",
    "Dry powder massage (Udvartana) with herbal powders",
    "Shilajit for vitality and removing dampness",
    "Arogyavardhini Vati for liver and fat metabolism",
    "Kutaj for intestinal health if sluggish",
    "Hot water with lemon and honey early morning",
    "Intense Surya Namaskar (Sun Salutations) 12 rounds",
    "Avoid cold water, ice cream and heavy dairy",
    "Consume bitter vegetables like Karela (Bitter Gourd)",
    "Triphala at night for regular bowel movement"
])

# Remove duplicates
for dosha in kb['doshas']:
    for category in ['primary_symptoms', 'secondary_symptoms', 'remedies']:
        kb['doshas'][dosha][category] = list(dict.fromkeys(kb['doshas'][dosha][category]))

with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f"Successfully finalized expansion of knowledge base at {kb_path}")
print(f"Total lines estimate: {sum(len(v['primary_symptoms']) + len(v['secondary_symptoms']) for v in kb['doshas'].values())} symptoms.")
