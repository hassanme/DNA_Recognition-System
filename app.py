import os
import pytesseract
from PIL import Image
import base64
import requests
import streamlit as st
from pyngrok import ngrok


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"

def analyze_image_with_groq(image):
    """
    Analyze an image using the Groq API and return the main analysis as JSON.
    """
    try:

        with open(image, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }


        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 1,
            "max_completion_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            response_json = response.json()


            if 'choices' in response_json and len(response_json['choices']) > 0:
                main_analysis = response_json['choices'][0]['message']['content']


                analysis_json = {
                    "main_analysis": main_analysis
                }
                return analysis_json
            else:
                return {"error": "No valid analysis found in the response."}
        else:
            st.error(f"Error from Groq API: {response.status_code} - {response.text}")
            return {"error": f"Failed to analyze image. Status code: {response.status_code}"}
    except Exception as e:
        st.error(f"Error connecting to Groq API: {e}")
        return {"error": f"Exception occurred: {str(e)}"}


st.title("DNA Image Analysis with Groq")


uploaded_file = st.file_uploader("Upload a DNA Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)


    temp_image_path = "/tmp/dna_test_image.jpg"
    image.save(temp_image_path)


    st.write("### Analyzing the image using Groq API:")
    result = analyze_image_with_groq(temp_image_path)
    if "main_analysis" in result:
        st.write("**Main DNA Analysis:**")
        st.json(result)
    else:
        st.warning("Failed to analyze the image with Groq API.")
else:
    st.info("Please upload an image to analyze using Groq.")
