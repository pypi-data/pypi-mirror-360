from behave import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def before_scenario(context, scenario):
    context.driver = webdriver.Firefox()


def after_scenario(context, scenario):
    context.driver.close()
