
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By


# class DummyChatGptService:
#   def create_single_request(self, html, feature_scenario, input_line=1):
#     if input_line == 1:
#       return {
#         "code": "driver.get('http://localhost:3000/button_with_redirect')",
#         "bdd": "@given('visiting site \"{url}\"')\ndef step_visit_site(context, url):\n    context.driver.get(url)"
#       }
#     elif input_line == 2:
#       return {
#         "code": "button = driver.find_element(By.XPATH, '//button[contains(text(), \"Go to my favorites\")]')\nbutton.click()",
#         "bdd": "@when('I click button with text \"Go to my favorites\"')\ndef step_click_button(context):\n    button = context.driver.find_element(By.XPATH, '//button[contains(text(), \"Go to my favorites\")]')\n    button.click()"
#       }
#     elif input_line == 3:      
#       return {
#         "code": "current_url = driver.current_url\nassert current_url == 'http://localhost:3000/my_favourites', 'Expected URL to be http://localhost:3000/my_favourites but got {current_url}'",
#         "bdd": "@then('I will be redirected into site localhost:3000/my_favourites')\ndef step_verify_redirection(context):\n    current_url = context.driver.current_url\n    assert current_url == 'http://localhost:3000/my_favourites', 'Expected URL to be http://localhost:3000/my_favourites but got different"
#       }


#   def get_user_input(self, html, feature_scenario, input_line):
#     return None

#   def get_response(self, feature_scenario):
#     ready_file = """from behave import *
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By"""
#     driver = webdriver.Firefox()

#     html = "EMPTY"
#     for i in range(1, 4):
#       request = self.create_single_request(html, feature_scenario, input_line=i)
#       exec(request["code"])
#       ready_file = ready_file + "\n\n\n"
#       ready_file = ready_file + request["bdd"]
#       elem = driver.find_element("xpath", "//*")
#       html = elem.get_attribute("outerHTML")
#     driver.close()
#     return ready_file
#       # ready_file = ""
# # dummy_class = DummyChatGptService()
# # open("games.py", "w")
#   # for input_line in range(1, 3):
#     # print(f"HTML: {html}")
#     # request = dummy_class.create_request(html, scenario, input_line)
#     # print(request["code"])
#     # exec(request["code"])
#     # with open("games.py", "a") as text_file:
# #     if input_line == 1:
# #         ready_file = ready_file + """from behave import *
# # from selenium import webdriver
# # from selenium.webdriver.common.keys import Keys
# # from selenium.webdriver.common.by import By"""

#     # ready_file = ready_file + "\n\n\n"
#     # ready_file = ready_file + request["bdd"]
#     # print("ready file", ready_file)


# # with open("games.py", "a") as text_file:
#         # text_file.write(ready_file)