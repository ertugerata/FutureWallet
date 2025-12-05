import google.generativeai as genai

# API anahtarınızı buraya girin
genai.configure(api_key="BURAYA_API_ANAHTARINIZI_YAZIN")

print("Kullanılabilir Modeller:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
