Feature: showing off behave

  Scenario: run a simple test
    Given visiting site "localhost:3000/button_with_redirect"
    When I click button with text "Go to my favorites"
    Then I will be redirected into site localhost:3000/my_favourites