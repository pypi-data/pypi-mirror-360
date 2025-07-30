import json
import requests
from dotenv import load_dotenv
import os

system_input = """

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

Do not put imports in python code - i do not need them. I already have prepared in python code from behave import *

Analyze this feedback and output in JSON format with keys: "code” (python script to use in python application)"""

# Return me a json object, which will have one key: it will be named "code", which will be executable for python with method exec(),
# Please provide me "code" value as simple as possible, parseable by ast module.
# Please find objects by looking first for id of them. Try to find objects by their attributes, class and using xpath, at the final you can use finding by text. 






# Do not treat \n as something special, do not format it for me.
# If you want to get element by text you should use [contains(text(), \"Go to my favorites\")] instead of [text(), \"Go to my favorites\"]
# In first line, do not attach imports to "code" in python meant for execution. Its already taken care of. 
# Initialization of driver for python execution is taken care of (driver = webdriver.Firefox()) so do not worry about it neither.
# Do not use string interpolation in adnotations(@). It may cause some unforseen issues.
# Also please make output in json parseable in python
# Return json without that funny json string after ``` and without ``` at all. Just as normal json in string.
# When you need to upload picture, modify this snippet code: downloads_file_path = os.path.join(os.path.expanduser("~"), "Downloads", "<name_of_file>")
# If feature file ask you to submit a form, find a button element and click it, do not submit a form automatically.
# Do not look for elements by their text content.
# Find them by their id, Find them by css classes using xpath (even by single, unique css classes), by name of inputs, by type of inputs.
# Text content should be at the last place, do not use text content of element.
# PLEASE LOOK CAREFULLY AT THE HTML CODE. DO NOT MAKE STUPID MISTAKES LIKE CLICK SUBMIT BUTTON, WHERE IN HTML CODE THERE IS NONE SUBMIT BUTTON.
# PLEASE DO NOT USE FINDING ELEMENT BY TEXT.
# WHEN YOU MAKE CODE, PLEASE CHECK IF THEY ARE INITIALIZED



# [no prose]

# global_html = """
# <html><head><style type="text/css">.turbo-progress-bar {
#   position: fixed;
#   display: block;
#   top: 0;
#   left: 0;
#   height: 3px;
#   background: #0076ff;
#   z-index: 2147483647;
#   transition:
#     width 300ms ease-out,
#     opacity 150ms 150ms ease-in;
#   transform: translate3d(0, 0, 0);
# }
# </style>
#     <title>WebsiteForScenarioThinker</title>
#     <meta name="viewport" content="width=device-width,initial-scale=1">
#     <meta name="csrf-param" content="authenticity_token">
# <meta name="csrf-token" content="lRYHnc4tz0WvcGqNopvrENOcCS0BcxLXKO9Zkd8pd8yke3zyoMH1OK7KgAKBOfIacIDwqzTFZwXwTJIjjTbXGw">
    

#     <link rel="stylesheet" href="/assets/application-e0cf9d8fcb18bf7f909d8d91a5e78499f82ac29523d475bf3a9ab265d5e2b451.css" data-turbo-track="reload">
#     <script type="importmap" data-turbo-track="reload">{
#   "imports": {
#     "application": "/assets/application-37f365cbecf1fa2810a8303f4b6571676fa1f9c56c248528bc14ddb857531b95.js",
#     "@hotwired/turbo-rails": "/assets/turbo.min-cd3ce4205eaa3eb1f80c30fedaf47bccb15a7668eb53b1cb1a5e0dda16009d4d.js",
#     "@hotwired/stimulus": "/assets/stimulus.min-dd364f16ec9504dfb72672295637a1c8838773b01c0b441bd41008124c407894.js",
#     "@hotwired/stimulus-loading": "/assets/stimulus-loading-3576ce92b149ad5d6959438c6f291e2426c86df3b874c525b30faad51b0d96b3.js",
#     "controllers/application": "/assets/controllers/application-368d98631bccbf2349e0d4f8269afb3fe9625118341966de054759d96ea86c7e.js",
#     "controllers/hello_controller": "/assets/controllers/hello_controller-549135e8e7c683a538c3d6d517339ba470fcfb79d62f738a0a089ba41851a554.js",
#     "controllers": "/assets/controllers/index-31a9bee606cbc5cdb1593881f388bbf4c345bf693ea24e124f84b6d5c98ab648.js"
#   }
# }</script>
# <link rel="modulepreload" href="/assets/application-37f365cbecf1fa2810a8303f4b6571676fa1f9c56c248528bc14ddb857531b95.js">
# <link rel="modulepreload" href="/assets/turbo.min-cd3ce4205eaa3eb1f80c30fedaf47bccb15a7668eb53b1cb1a5e0dda16009d4d.js">
# <link rel="modulepreload" href="/assets/stimulus.min-dd364f16ec9504dfb72672295637a1c8838773b01c0b441bd41008124c407894.js">
# <link rel="modulepreload" href="/assets/stimulus-loading-3576ce92b149ad5d6959438c6f291e2426c86df3b874c525b30faad51b0d96b3.js">
# <link rel="modulepreload" href="/assets/controllers/application-368d98631bccbf2349e0d4f8269afb3fe9625118341966de054759d96ea86c7e.js">
# <link rel="modulepreload" href="/assets/controllers/hello_controller-549135e8e7c683a538c3d6d517339ba470fcfb79d62f738a0a089ba41851a554.js">
# <link rel="modulepreload" href="/assets/controllers/index-31a9bee606cbc5cdb1593881f388bbf4c345bf693ea24e124f84b6d5c98ab648.js">
# <script type="module">import "application"</script>
#     <script src="https://cdn.tailwindcss.com"></script>
#   <style>*, ::before, ::after{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }::backdrop{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }/* ! tailwindcss v3.4.15 | MIT License | https://tailwindcss.com */*,::after,::before{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}::after,::before{--tw-content:''}:host,html{line-height:1.5;-webkit-text-size-adjust:100%;-moz-tab-size:4;tab-size:4;font-family:ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";font-feature-settings:normal;font-variation-settings:normal;-webkit-tap-highlight-color:transparent}body{margin:0;line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,pre,samp{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;font-feature-settings:normal;font-variation-settings:normal;font-size:1em}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}button,input,optgroup,select,textarea{font-family:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-size:100%;font-weight:inherit;line-height:inherit;letter-spacing:inherit;color:inherit;margin:0;padding:0}button,select{text-transform:none}button,input:where([type=button]),input:where([type=reset]),input:where([type=submit]){-webkit-appearance:button;background-color:transparent;background-image:none}:-moz-focusring{outline:auto}:-moz-ui-invalid{box-shadow:none}progress{vertical-align:baseline}::-webkit-inner-spin-button,::-webkit-outer-spin-button{height:auto}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}summary{display:list-item}blockquote,dd,dl,figure,h1,h2,h3,h4,h5,h6,hr,p,pre{margin:0}fieldset{margin:0;padding:0}legend{padding:0}menu,ol,ul{list-style:none;margin:0;padding:0}dialog{padding:0}textarea{resize:vertical}input::placeholder,textarea::placeholder{opacity:1;color:#9ca3af}[role=button],button{cursor:pointer}:disabled{cursor:default}audio,canvas,embed,iframe,img,object,svg,video{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}[hidden]:where(:not([hidden=until-found])){display:none}.mb-4{margin-bottom:1rem}.mt-1{margin-top:0.25rem}.mt-2{margin-top:0.5rem}.mt-6{margin-top:1.5rem}.block{display:block}.flex{display:flex}.min-h-screen{min-height:100vh}.w-full{width:100%}.max-w-md{max-width:28rem}.items-center{align-items:center}.justify-center{justify-content:center}.rounded-lg{border-radius:0.5rem}.rounded-md{border-radius:0.375rem}.border{border-width:1px}.border-gray-300{--tw-border-opacity:1;border-color:rgb(209 213 219 / var(--tw-border-opacity, 1))}.bg-gray-100{--tw-bg-opacity:1;background-color:rgb(243 244 246 / var(--tw-bg-opacity, 1))}.bg-indigo-600{--tw-bg-opacity:1;background-color:rgb(79 70 229 / var(--tw-bg-opacity, 1))}.bg-white{--tw-bg-opacity:1;background-color:rgb(255 255 255 / var(--tw-bg-opacity, 1))}.p-8{padding:2rem}.px-4{padding-left:1rem;padding-right:1rem}.py-2{padding-top:0.5rem;padding-bottom:0.5rem}.text-center{text-align:center}.text-lg{font-size:1.125rem;line-height:1.75rem}.text-sm{font-size:0.875rem;line-height:1.25rem}.font-medium{font-weight:500}.font-semibold{font-weight:600}.text-gray-700{--tw-text-opacity:1;color:rgb(55 65 81 / var(--tw-text-opacity, 1))}.text-gray-900{--tw-text-opacity:1;color:rgb(17 24 39 / var(--tw-text-opacity, 1))}.text-white{--tw-text-opacity:1;color:rgb(255 255 255 / var(--tw-text-opacity, 1))}.shadow-md{--tw-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);--tw-shadow-colored:0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-sm{--tw-shadow:0 1px 2px 0 rgb(0 0 0 / 0.05);--tw-shadow-colored:0 1px 2px 0 var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.hover\:bg-indigo-700:hover{--tw-bg-opacity:1;background-color:rgb(67 56 202 / var(--tw-bg-opacity, 1))}.focus\:border-indigo-500:focus{--tw-border-opacity:1;border-color:rgb(99 102 241 / var(--tw-border-opacity, 1))}.focus\:outline-none:focus{outline:2px solid transparent;outline-offset:2px}.focus\:ring-2:focus{--tw-ring-offset-shadow:var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);--tw-ring-shadow:var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);box-shadow:var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000)}.focus\:ring-indigo-500:focus{--tw-ring-opacity:1;--tw-ring-color:rgb(99 102 241 / var(--tw-ring-opacity, 1))}.focus\:ring-offset-2:focus{--tw-ring-offset-width:2px}@media (min-width: 640px){.sm\:text-sm{font-size:0.875rem;line-height:1.25rem}}</style></head>

#   <body>
#     <div class="flex justify-center items-center min-h-screen bg-gray-100">
#   <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
#     <form action="/select_scenario" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="458MsBTl5B0rN5iLNHZan0TY78FCNsSDXviccDvnZ3b7dqbmys6lweKAAaqXMgMXLeQVfiP0yRfxNtdYOv5Xig" autocomplete="off">
#       <div class="mb-4">
#         <label class="block text-sm font-medium text-gray-700" for="license_plate">License plate for your car:</label>
#         <input class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" type="text" name="license_plate" id="license_plate">
#       </div>

#       <div class="mb-4">
#         <label class="block text-sm font-medium text-gray-700" for="car">Select your car:</label>
#         <select name="car" id="car"><option value="volvo">Volvo</option>
# <option value="saab">Saab</option>
# <option value="opel">Opel</option>
# <option value="audi">Audi</option></select>
#       </div>

#       <div>
#         <input type="submit" name="commit" value="Accept your choice" class="w-full px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" data-disable-with="Accept your choice">
#       </div>
# </form>
#     <!-- Display the license plate and car choice -->
#     <h1 class="mt-6 text-lg font-semibold text-gray-900 text-center">
#       License Plate: 
#     </h1>
#     <h1 class="mt-2 text-lg font-semibold text-gray-900 text-center">
#       Car: 
#     </h1>
#   </div>
# </div>

  

# </body></html>
# """

# global_feature_scenario = """
#  Feature: trying to get select to work
# Scenario: run a simple test
# Given visiting site http://localhost:3000/select_scenario
# When I input into text field "BBI SR88"
# When I select from select menu option "Volvo"
# When I click Submit
# Then I will be redirected into site localhost:3000/select_scenario
# Then i will have on my website written "BBI SR88" and "Volvo" as a text
# """


# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
# model = 'llama3.2:1b' # TODO: update this for whatever model you wish to use
class ClaudeService:
    def __init__(self):
        print("Cladue yeay")
        load_dotenv()
        self.API_KEY = os.getenv("AI_ML_API_VALUE")

    def _get_user_input(self, html, feature_scenario, text_line):
        return f"""
        Provide me execution code for text_line {text_line}.
        HTML_code: 
        {html}
        (if upper line says EMPTY, try to intepret this prompt without html. Probably it will be something easy as visit page)
        Feature file: 
        {feature_scenario}
        """


    def generate(self, html, feature_scenario, text_line):
        user_input = self._get_user_input(html, feature_scenario, text_line)

        print(user_input)
        print(system_input)
        
        whole_input = f"System input: {system_input}, user_input: {user_input}"

        response = requests.post(
            "https://api.aimlapi.com/chat/completions",
            headers={"Content-Type":"application/json", "Authorization": f"Bearer {self.API_KEY}"},
            json={"model":"claude-3-opus-20240229",
            "messages":[
                {"role": "user", "content": "Respond to me in JSON, how are you feeling. Use keys smile and place where would you see yourself now"},
                {"role": "assistant", "content": 'Here is the JSON response with the Python code for the given user input and HTML code:\n{'}
                ]}
        )


        data = response.json()
        print(data)
        return data
    # whole_input = f"System input: {system_input} + user_input{user_input}"

    # print(whole_input)
    # r = requests.post('http://localhost:11434/api/generate',
    #                   json={
    #                       'model': model,
    #                       'prompt': whole_input,
    #                       'context': context,
    #                   },
    #                   stream=True)
    # r.raise_for_status()

    # for line in r.iter_lines():
    #     body = json.loads(line)
    #     response_part = body.get('response', '')
    #     # the response streams one token at a time, print that as we receive it
    #     print(response_part, end='', flush=True)

    #     if 'error' in body:
    #         raise Exception(body['error'])

    #     if body.get('done', False):
    #         return body['context']

# def main():
#     context = [] # the context stores a conversation history, you can use this to make the model more context aware
#     # while True:
#         # user_input = input("Enter a prompt: ")
#         # if not user_input:
#             # exit()
#         # print()
#     context = generate("user_input", context)
#     print()

# if __name__ == "__main__":
#     main()
