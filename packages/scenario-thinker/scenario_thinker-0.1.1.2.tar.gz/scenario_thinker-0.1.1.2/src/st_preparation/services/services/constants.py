original_system_input = """
EXAMPLE OF WORKING PROGRAMME:

Feature scenario file:
The BDD scenario is as follows:
Feature: showing off behave
Scenario: run a simple test
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
"code": "driver.get('http://localhost:3000/button_with_redirect')"
}
For the line 'When I click button with text "Go to my favorites"', it will be: 
{
"code": "button = driver.find_element(By.XPATH, '//button[contains(text(), \\"Go to my favorites\\")]');button.click()"
}
For the line 'Then I will be redirected into site localhost:3000/my_favourites', it will be:
{
"code": "current_url = driver.current_url;assert current_url == 'http://localhost:3000/my_favourites', f'Expected URL to be http://localhost:3000/my_favourites but got {current_url}'"
}
Do not put imports in python code - i do not need them. I already have prepared in python code from behave import *
Analyze this feedback and output in JSON format with keys: "code” (python script to use in python application)
If html is empty, just be resourceful and try to find by context of given line what python script you need to execute.
All of these commands are incredible important.

Do not put context before driver, make it normal python script compatible.
Please do not leave ``` at the end of your input :D
Find elements by id or by xpath. Do not use find element by text content.
If you use something with XPATH, for example:
'{ "code": "select = driver.find_element(By.ID, \'car\'); select.click(); select.find_element(By.XPATH, \'//option[contains(text(), \\"Volvo\\")]\').click()"}'
use double backslashes
When you need to assert that url is correct, just use contain, in python is 'in'
When the script ask you to find text something on site, just use universal tag and with contains
Make assert as separate lines of code please
So the line 'i will have on my website written "Maciek" and "Wioletta" as a text'
Will be two different assert, but in one code
Do not forget about starting brackets
THIS IS VERY IMPORTANT:
Keep your response only for one line. THIS IS VERY IMPORTANT
Focus only on given line, do not try to find something for site, do not fill anything not asked for
If you use any additional libraries, please add import to it. For example Select: from selenium.webdriver.support.select import Select.
Please if possible, take elements by id, xpath, attributes, let the finding element by text will be the latest you will do.
Please look at the given html code in user input and make assumptions on it.
Please assume that the code in feature scenario is nearly perfect, look at the html and make necessary fixes, for example some big letters if you're using contains text()
THIS IS VERY IMPORTANT, REMEMBER

You should return me json with
code: 'python code'

"""

experiment_system_input = """
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

So for the LINE OF FEATURE SCENARIO 'Given visiting site localhost:3000/button_with_redirect' it will be:
{
"code": "driver.get('http://localhost:3000/button_with_redirect')"
}

For the LINE OF FEATURE SCENARIO 'When I click button with text "Go to my favorites"', it will be: 
{
"code": "button = driver.find_element(By.XPATH, '//button[contains(text(), "Go to my favorites")]');button.click()"
}

For the LINE OF FEATURE SCENARIO 'Then I will be redirected into site localhost:3000/my_favourites', it will be:
{
"code": "current_url = driver.current_url;assert 'http://localhost:3000/my_favourites' in current_url, f'Expected URL to be http://localhost:3000/my_favourites but got {current_url}'"
}

Keep your response only for one LINE OF FEATURE SCENARIO.
Return me only JSON, no additional comments.
If you use something with XPATH, for example:
'{ "code": "driver.find_element(By.XPATH, \'//a[contains(text(), \\"najlepsze kremowki z wadowic\\")]\').click()"}'
use double backslashes as shown. This is very important, please. The " matters, ' not that much.
Change letter cases if needed. For example if asked in scenario for clicking button with text "See my doggies", pay attention to given HTML code and properly change it, for example "See My Doggies".
Pay attention to html. Do not take my commands too straightforward. They are always true, but find elements and do actions on your own.
This is very important.
Please see if given in scenario lines are truly correct. Compare them with HTML and get value from HTML for sure.
Directly find elements in HTML, do not use relative XPATH HTML trees, because they are complicating things and usually are not correct.
If you have Then keyword in LINE OF FEATURE SCENARIO, use assert.
"""
# Pay attention to details in html and create xpath carefully.
# Pay attention to html. Do not take my commands to straightforward. They have always true, but find elements and do actions on your own.
# This is very important.



# If you use something with XPATH, for example:
# '{ "code": "driver.find_element(By.XPATH, \'//a[contains(text(), \\"najlepsze kremowki z wadowic\\")]\').click()"}'
# use double backslashes as shown.