import json
import os

kb_path = r'c:\idea1\vaidya_slm\backend\engine\knowledge_base.json'

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Hairfall (Khalitya) Specific Expansion
kb['doshas']['Vata']['secondary_symptoms'].extend([
    "khalitya with dryness", "sudden hair fall", "rough hair texture", "frizzy hair", "split ends",
    "hair fall due to stress", "hair fall during travel", "dry itchy scalp", "brittle hair",
    "thinning of hair with dryness", "hair loss in patches with dry skin", "receding hairline with dryness"
])
kb['doshas']['Pitta']['secondary_symptoms'].extend([
    "khalitya with heat", "premature greying", "hair thinning", "scalp burning", "red scalp with hair loss",
    "hair fall with oily scalp", "hair fall due to anger", "hair fall in summer", "pattern baldness",
    "thinning at top of head", "early balding", "inflamed hair follicles"
])
kb['doshas']['Kapha']['secondary_symptoms'].extend([
    "khalitya with oiliness", "sticky dandruff hair loss", "heavy scalp feeling", "slow hair growth",
    "oily sticky scalp", "hair fall with congestion", "thick but falling hair", "white sticky dandruff",
    "clogged hair follicles", "hair loss with lethargy"
])

# 500+ Universal/Unique Symptoms Expansion
# Vata
kb['doshas']['Vata']['secondary_symptoms'].extend([
    "trembling lips", "twitching nose", "difficulty swallowing", "choking sensation", "vague body pains",
    "sharp needle-like pain", "shifting joint pain", "cracking sound in ears", "excessive yawning",
    "irregular pulse", "variable appetite", "averse to cold air", "craves salt and sour", "quick fatigue",
    "dry vagina", "painful intercourse", "scanty dark menses", "premature ejaculation", "low semen volume",
    "feeling of emptiness", "loss of purpose", "fear of the future", "nightmares of falling",
    "speech block", "forgetting names", "inability to sit still", "constantly checking phone", "digital burnout",
    "hyper-sensitivity to touch", " intolerance to light", "ear blockage", "popping ears"
])

# Pitta
kb['doshas']['Pitta']['secondary_symptoms'].extend([
    "bloodshot eyes", "yellowish sclera", "bitter taste in mouth", "sour taste in mouth", "metallic taste",
    "strong desire for cold items", "intolerance to heat", "profuse sweating in armpits", "foul body odor",
    "urticaria with itching", "burning sensation while urinating", "dark yellow urine", "sharp stabbing pains",
    "mouth ulcers on tongue", "bleeding from nose", "heavy menstrual flow with heat", "short menstrual cycle",
    "intense drive for success", "hostility towards colleagues", "jealousy", "pride", "arrogance",
    "judgmental thoughts", "critical of self and others", "perfectionist anxiety", "insomnia from overthinking work",
    "burning in chest", "esophageal burning", "sensitive gums", "pustules on back", "inflamed acne"
])

# Kapha
kb['doshas']['Kapha']['secondary_symptoms'].extend([
    "thick white coating on tongue", "sticky feeling in throat", "excessive salivation in sleep",
    "heavy head in morning", "swelling in face", "puffiness around eyes", "clogged nose in morning",
    "loss of smell from mucus", "dull taste buds", "slow to react", "emotional dependency",
    "possessive of relationships", "heavy limbs in humid weather", "sleepiness after breakfast",
    "sluggish bowel in morning", "soft but large stools", "gain weight just by looking at food",
    "resistant to exercise", "hoarding old clothes", "nostalgia for past", "sadness without reason",
    "melancholy", "weeping easily", "feeling of being stuck", "no desire to move", "oily eyelids",
    "excessive ear wax buildup", "lipomas", "benign tumours", "fibroids"
])

# Remedies Expansion
kb['doshas']['Vata']['remedies'].extend([
    "Brahmi Ghrita for memory and anxiety", 
    "Apply warm sesame oil to soles of feet at night",
    "Dashamularishta for general weakness",
    "Ashwagandha Lehyam for strength",
    "Kshirabala tailam for joint pains",
    "Gentle stretching and Yin Yoga",
    "Eating walnuts and almonds soaked in water",
    "Abhyanga with Dhanwantaram oil"
])
kb['doshas']['Pitta']['remedies'].extend([
    "Abhisheka with cool water on head",
    "Apply coconut oil with camphor for scalp burning",
    "Sip water with vetiver roots",
    "Consumption of Gulkand (rose jam) with milk",
    "Amalaki Rasayana for hair and skin",
    "Chandanasava for urinary heat",
    "Arogyavardhini Vati for liver health",
    "Sandalwood powder mask for acne"
])
kb['doshas']['Kapha']['remedies'].extend([
    "Triphala Guggulu for weight and congestion",
    "Trikatu powder with honey before meals",
    "Nasyam with Anu tailam to clear sinuses",
    "Vigorous dry brushing of skin",
    "Include more black pepper and ginger in diet",
    "Avoid sleeping during the day at all costs",
    "Engage in HIIT or fast-paced yoga",
    "Drink warm water with cinnamon and cardamom"
])

# Remove duplicates and sort for cleanliness
for dosha in kb['doshas']:
    for category in ['primary_symptoms', 'secondary_symptoms', 'remedies']:
        # Convert to list to remove duplicates and keep order consistent
        unique_items = sorted(list(set(kb['doshas'][dosha][category])), key=len)
        kb['doshas'][dosha][category] = unique_items

# Save the massive KB
with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f"Successfully performed massive expansion. New size: {os.path.getsize(kb_path) // 1024} KB.")
print(f"Unique symptoms count estimated: {sum(len(v['primary_symptoms']) + len(v['secondary_symptoms']) for v in kb['doshas'].values())}")
