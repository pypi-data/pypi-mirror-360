
# from openai import OpenAI
import os
from dotenv import load_dotenv
from services.parse_scenario import parse_feature_file
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import json
import ast
import re
from services.database import Database
from services.bdd_step_file_creator import create_bdd_step_method
import requests


system_input = """
Return me a json object, which will have one key: it will be named "code", which will be executable for python with method exec(),
Please provide me "code" value as simple as possible, parseable by ast module.
Please find objects by looking first for id of them. Try to find objects by their attributes, class and using xpath, at the final you can use finding by text.
Do not put imports in python code - i do not need them. I already have prepared in python code from behave import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By.

Give me one line at a time.

EXAMPLE OF WORKING PROGRAMME:

Feature scenario file:
The BDD scenario is as follows:
    Given visiting site localhost:3000/button_with_redirect
    When I click button with text "Go to my favorites"
    Then I will be redirected into site localhost:3000/my_favourites

Upper scenario should result in this actions for Selenium WebDriver to:
    Navigate to the page localhost:3000/button_with_redirect
    Click on the button with the text "Go to my favorites"
    Verify that the URL is equal to localhost:3000/my_favourites
    
HTML code:
<html>
  <body>
    <div style="display: flex; align-items: center; justify-content: center; width: 100vw; height: 100vh;">
  <a href="/my_favourites">
    <button style="background-color: cyan; border: none; font-size: 30px; cursor: pointer; ">
      Go to my favorites
    </button>
  </a>
</div>
  

</body></html>

So for the line 'Given visiting site localhost:3000/button_with_redirect' it will be: 
{
  "code": "driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()));driver.get('http://localhost:3000/button_with_redirect')",
}
For the line 'When I click button with text "Go to my favorites"', it will be: 
{
  "code": "button = driver.find_element(By.XPATH, '//button[contains(text(), \"Go to my favorites\")]');button.click()",
}
For the line 'Then I will be redirected into site localhost:3000/my_favourites', it will be:
{
  "code": "current_url = driver.current_url;assert current_url == 'http://localhost:3000/my_favourites', f'Expected URL to be http://localhost:3000/my_favourites but got {current_url}'",
}
Do not treat \n as something special, do not format it for me.
If you want to get element by text you should use [contains(text(), \"Go to my favorites\")] instead of [text(), \"Go to my favorites\"]
In first line, do not attach imports to "code" in python meant for execution. Its already taken care of. 
Initialization of driver for python execution is taken care of (driver = webdriver.Firefox()) so do not worry about it neither.
Do not use string interpolation in adnotations(@). It may cause some unforseen issues.
Also please make output in json parseable in python
Return json without that funny json string after ``` and without ``` at all. Just as normal json in string.
When you need to upload picture, modify this snippet code: downloads_file_path = os.path.join(os.path.expanduser("~"), "Downloads", "<name_of_file>")
If feature file ask you to submit a form, find a button element and click it, do not submit a form automatically.
Do not look for elements by their text content.
Find them by their id, Find them by css classes using xpath (even by single, unique css classes), by name of inputs, by type of inputs.
Text content should be at the last place, do not use text content of element.
PLEASE LOOK CAREFULLY AT THE HTML CODE. DO NOT MAKE STUPID MISTAKES LIKE CLICK SUBMIT BUTTON, WHERE IN HTML CODE THERE IS NONE SUBMIT BUTTON.
PLEASE DO NOT USE FINDING ELEMENT BY TEXT.
WHEN YOU MAKE CODE, PLEASE CHECK IF THEY ARE INITIALIZED

[no prose]
"""
from services.claude_service import ClaudeService
from services.llama_service import LlamaService
from services.google_gemma_service import GoogleGemmaService
from services.testing_service import TestingService
from services.llama_turbo_service import LlamaTurboService
from services.chatgpt_35_turbo_service import ChatGPT35TurboService
from services.claude_haiku_service import ClaudeHaikuService
from services.claude_opus_service import ClaudeOpusService
from services.chatgpt_4_service import ChatGPT4Service
from services.chatgpt_4o_service import ChatGPT4OService
from services.grok_service import GrokService
from services.mistral_nemo_service import MistralNemoService

SAVING_TO_DATABASE = True

class ScenarioCreator:
  def __init__(self, model):
    self.database = Database()

    if model == "claude":
      self.model = ClaudeService()
    elif model == "llama":
      self.model = LlamaService()
    elif model == "gemma":
      self.model = GoogleGemmaService()
    elif model == "testing":
      self.model = TestingService()
    elif model == "llama-turbo":
      self.model = LlamaTurboService()
    elif model == "gpt-4":
      self.model = ChatGPT4Service()
    elif model == "gpt-35":
      self.model = ChatGPT35TurboService()
    elif model == "claude-haiku":
      self.model = ClaudeHaikuService()
    elif model == "claude-opus":
      self.model = ClaudeOpusService()
    elif model == "gpt-4o":
      self.model = ChatGPT4OService()
    elif model == "grok":
      self.model = GrokService()
    elif model == "mistral-nemo":
      self.model = MistralNemoService()
    # elif model == "google-gemma-2b":
    #   self.model = GoogleGemmaService()
    
    else:
      self.model = LlamaService()


  def get_user_input(self, html, feature_scenario, text_line):
    return f"""
    Provide me execution code for text_line {text_line}.
    HTML_code: 
    {html}
    (if upper line says EMPTY, try to intepret this prompt without html. Probably it will be something easy as visit page)
    Feature file: 
    {feature_scenario}
    """


  def get_response(self, feature_scenario):
    ready_file = """from behave import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select"""

    driver = webdriver.Firefox()
    html = "EMPTY"
    json_data = parse_feature_file(feature_scenario)
    for scenario_json in json_data["Scenario"]:
      ready_file = ready_file + "\n\n"
      for given_line in scenario_json["Given"]:
        command_in_database = self.database.get_specific_action(given_line)
        # command_in_database = None
        if command_in_database is not None:
          generated_code = { "code": command_in_database[1] }
        else:
          generated_code = self.model.generate(html, feature_scenario, given_line)
        

        print("generated_code: ", generated_code, "\n\n\n\n")

        try:
          exec(generated_code["code"])
        except Exception as e:
          print("zwalilo sie")
          driver.close()
          return [ready_file, "Error in when line: " + given_line + "\n" + "\n" + repr(e)]

        if SAVING_TO_DATABASE:
          self.database.insert_into_table(given_line, generated_code["code"])

        elem = driver.find_element("xpath", "//*")
        html = elem.get_attribute("outerHTML")
        ready_file = ready_file + create_bdd_step_method(given_line, generated_code["code"])
        ready_file = ready_file + "\n"

      for when_line in scenario_json["When"]:
        command_in_database = self.database.get_specific_action(when_line)
        # command_in_database = None

        if command_in_database is not None:
          generated_code = { "code": command_in_database[1] }
        else:
          generated_code = self.model.generate(html, feature_scenario, when_line)
        print("generated_code: ", generated_code, "\n\n\n\n")

        try:
          exec(generated_code["code"])
        except Exception as e:
          print("zwalilo sie")
          driver.close()
          return [ready_file, "Error in when line: " + when_line + "\n" + "\n" + repr(e)]

        if SAVING_TO_DATABASE:
          self.database.insert_into_table(when_line, generated_code["code"])

        elem = driver.find_element("xpath", "//*/body")
        html = elem.get_attribute("outerHTML")
        ready_file = ready_file + create_bdd_step_method(when_line, generated_code["code"])
        ready_file = ready_file + "\n"

      for then_line in scenario_json["Then"]:
        command_in_database = self.database.get_specific_action(then_line)
        # command_in_database = None

        if command_in_database is not None:
          generated_code = { "code": command_in_database[1] }
        else:
          generated_code = self.model.generate(html, feature_scenario, then_line)
        print("generated_code: ", generated_code, "\n\n\n\n")

        try:
          exec(generated_code["code"])
        except Exception as e:
          driver.close()
          return [ready_file, f"Error in when line:  {then_line} \n \n {repr(e)} \n \n AI returned (after formatting to hash): {generated_code['code']}"]

        if SAVING_TO_DATABASE:
          self.database.insert_into_table(then_line, generated_code["code"])

        elem = driver.find_element("xpath", "//*")
        html = elem.get_attribute("outerHTML")
        ready_file = ready_file + create_bdd_step_method(then_line, generated_code["code"])
        ready_file = ready_file + "\n"

    driver.close()
    return [ready_file, ""] 


#   def _single_

