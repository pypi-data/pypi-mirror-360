#@title Generador de personaje
import os
import google.generativeai as genai

# Mapeo de modelos Gemini compatibles
modelo_ids = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Flash Lite Previe": "gemini-2.5-flash-lite-preview-06-17",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.0 Flash Thinking": "gemini-2.0-flash-thinking-exp-01-21",
    "Gemini 1.5 Pro": "gemini-1.5-pro",
    "Gemini 1.5 Flash-8B": "gemini-1.5-flash-8b"
}

def generate_char(prompt, modelo_select, system_prompt):

        api_key = os.environ.get("GEN_API_KEY")
        model_selected = modelo_ids.get(modelo_select)
        
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Error configuring Gemini API: {e}")


        model = genai.GenerativeModel(model_selected, system_instruction=system_prompt) # Pass system_instruction here
        full_prompt = prompt

        try:
            response = model.generate_content(
                full_prompt,
                # Remove generation_config here
            )
        except Exception as e:
            raise ValueError(f"Error during Gemini content generation: {e}")

        # Validación robusta del contenido
        try:
            generated_prompt = response.candidates[0].content.parts[0].text
        except (IndexError, AttributeError):
            generated_prompt = "No valid prompt was generated."
        return generated_prompt



