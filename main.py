from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium import webdriver

import time
import logging
import openai
import requests
from webdriver_confi import webdriver_config
from dotenv import load_dotenv
import os
import pyperclip

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY", "default_openai_api_key")

class LoomRequest(BaseModel):
    video_url: str
    # prompt: str

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# GPT RESPONSE
# def summarize_text(text, prompt=None):
#     default_prompt = "summarize and make proposal from this text and it should look professional"
#     prompt_to_use = prompt if prompt else default_prompt
    
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {openai.api_key}"
#     }
#     data = {
#         "model": "gpt-3.5-turbo",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt_to_use + "\n" + text}
#         ]
#     }
#     response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
   
#     # Check if the request was successful
#     if response.status_code == 200:
#         return response.json()["choices"][0]["message"]["content"]
#     else:
#         logging.error("OpenAI API Error: %s", response.text)
#         return None

# Rest of your imports and code...

@app.post("/download_caption/")
async def download_caption(request: LoomRequest):
    data = []
    
    # Initialize the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    
    wait = WebDriverWait(driver, 20)
    
    driver.get(request.video_url)
    logging.debug(f'Navigating to video URL: {request.video_url}')

    try:
        transcript_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="sidebar-tab-Transcript"]')))
        tanscript_location = transcript_button.location
        x_coordinate = tanscript_location['x']
        y_coordinate = tanscript_location['y']
        logging.debug(f'Element coordinates<<<<<<------->>>>>>: x={x_coordinate}, y={y_coordinate}')
        transcript_button.click()
    
        logging.debug("Clicked on the Transcript button")
    except TimeoutException:
        logging.error("Timeout: Transcript button not found or not clickable.")
        driver.quit()
        return {"error": "Transcript button not found or not clickable."}

    try:
        copy_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="activity-sidebar-container"]/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]/button')))
        copy_button.click()
        logging.debug("Clicked on the copy Transcript button")
    except TimeoutException:
        logging.error("Timeout: copy Transcript button not found or not clickable.")
        driver.quit()
        return {"error": "Copy Transcript button not found or not clickable."}

    try:
        # Wait for a moment to allow the transcript to be copied
        time.sleep(1)
        
        # Extract text directly from the transcript section
        transcript_elements = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'transcript-list_transcript_1tw')))
        for element in transcript_elements:
            data.append(element.text)
    except TimeoutException:
        logging.error("Timeout: Transcript elements not found.")
        driver.quit()
        return {"error": "Transcript elements not found."}

    driver.quit()
    loom_transcript = "\n".join(data)
    return {"loom_transcript": loom_transcript}
    
    # # Wait for the caption elements to be visible within the transcript section
    # try:
    #     captions = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'css-y326tu')))
    #     logging.debug("Captions found")
    # except TimeoutException:
    #     logging.error("Timeout: Captions not found.")
    #     driver.quit()
    #     return {"error": "Captions not found."}
    
    # # Scroll into view for each caption element
    # for caption in captions:
    #     try:
    #         driver.execute_script("arguments[0].scrollIntoView();", caption)
    #     except StaleElementReferenceException:
    #         continue
             
    # # time.sleep(5)
    
    # captions = driver.find_elements(By.CLASS_NAME, 'css-y326tu')
    # for caption in captions:
    #     try:
    #         data.append(caption.text)
    #     except StaleElementReferenceException:
    #         continue
    
    # driver.quit()
    # loom_transcript= copied_text
    # # logging.debug(f'Captions found: {data}')
    # # loom_summary = "\n".join(data)
    # # chatgpt_response = summarize_text(loom_summary, request.prompt)
    # # logging.debug(f'proposal made: {chatgpt_response}')
    
    # # return {"loom_summary": loom_summary, "chatgpt_response": chatgpt_response}
    # # return {"loom_Transcript": loom_summary}
    # return {"loom_transcript": loom_transcript}
