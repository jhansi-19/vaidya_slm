# Vaidya SLM Demo Script for Judges

The goal of this demo is to prove that the Vaidya SLM project completely solves the problem outlined: access to affordable, culturally relevant healthcare on low connectivity infrastructure without hallucination.

### Intro Hook (30s)
"Rural India lacks basic continuous health monitoring. Solutions like ChatGPT don't work natively offline, don't prioritize classical Indian knowledge like Ayurveda, and are prohibitively expensive on data. Vaidya SLM runs offline, acts as an Ayurvedic consultant, and combines high accuracy reasoning with voice technology."

### The Stack (45s)
"Over 10 datasets, including the Charaka and Sushruta Samhitas, were processed locally. The QLoRA training scripts in our `scripts/training` folder map this directly into a conversational model. To prevent the SLM from hallucinating on medicine, we combine it with a deterministic Hybrid logic module which grounds responses directly to Ayurveda texts, outputting exact Dosha values (Vata, Pitta, Kapha) directly in FastAPI."

### Live Frontend Demo (2 mins)
1. *Open the Flutter Android App. Call attention to the "Offline Ready" marker.*
2. Press the Microphone Button. 
3. *Simulate an english query:* "I have acidity and a slight headache."
    - Point to the app interface as the Pitta meter activates.
    - Show the AI text: "Detected acidity which corresponds to Pitta imbalance... Drink coriander seed water."
4. *Simulate an Indic query:* "Mujhe pet mein jalan ho rahi hai."
    - Demonstrate how the backend normalizes the language using our ASR integration to route correctly into the Dosha pipeline.
5. Emphasize that everything occurred safely locally, matching the core hackathon objective exactly.

### Future Roadmap
- Expanding to localized hardware (Raspberry Pi for rural clinics).
- Securing certification frameworks aligned with the National Digital Health Mission.
