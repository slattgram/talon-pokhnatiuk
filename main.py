import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
import pytest
from webdriver_manager.firefox import GeckoDriverManager

TESTING_URL = "https://electronics.lnu.edu.ua/about/staff/"

# to generate with report pytest main.py --html=report.html --self-contained-html -n 2
#f


# Fixture to initialize the WebDriver

@pytest.fixture(autouse=True)
def driver(request) -> webdriver.Chrome:
    # Option setup to run in headless mode (in order to run this in GH Actions)
    options = FirefoxOptions()
    options.add_argument('--width=1600')
    options.add_argument('--height=1600')
    options.add_argument('--headless')
    # Setup
    print(f"\nSetting up: gecko driver")
    gecko_service = Service(GeckoDriverManager().install())
    time.sleep(10)
    driver = webdriver.Firefox(service=gecko_service, options=options)
    driver.implicitly_wait(10)


    driver.get(TESTING_URL)

    # Implicit wait setup for our framework
    yield driver
    # Tear down
    print(f"\nTear down: gecko driver")

    return driver

def test_profile_eng(driver: webdriver.Firefox):
    # Wait for all elements to be present on the page
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))

    # Find all staff name elements
    components = driver.find_elements(By.CLASS_NAME, "name")
    default_page_title = driver.title

    # Loop through each staff element and check the behavior
    for component in components:
        # Re-find the component to avoid stale element reference
        component = driver.find_element(By.CLASS_NAME, "name")
        container = component.find_elements(By.CSS_SELECTOR, "*")

        # Assert that the container is not empty
        assert container

        try:
            # Click on the second element in the container (assuming it's a link)
            container[1].click()

            # Check if the page title changes from the default title
            if driver.title == default_page_title:
                assert False

            # Navigate back to the previous page
            driver.back()

        except Exception:
            # Handle any exceptions that might occur during the interaction
            if not container[1].text:
                continue
            assert False

    # Assert the overall success of the test
    assert True


# Test function to check emails for a given language
def test_email(driver: webdriver.Firefox):
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "language-switcher")))

    mails = []
    # Read emails from the file
    with open(r"./mail.txt", "r") as m_file:
        lines = m_file.readlines()
        for line in lines:
            mails.append(line.replace("\n", ""))

    components = driver.find_elements(By.CLASS_NAME, "email")
    for component in components:
        container = component.find_elements(By.CSS_SELECTOR, "*")
        if container:
            if container[0].text != '':
                assert container[0].text in mails

def test_title(driver: webdriver.Firefox):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "language-switcher")))

    try:
        div_container = driver.find_element(By.CLASS_NAME, "language-switcher")
    except NoSuchElementException:
        pytest.skip("Language switcher not found. Skipping test.")

    # find language switcher components
    components = div_container.find_elements(By.CSS_SELECTOR, "*")
    assert len(components) > 0, "Language switcher components not found."

    # collect english title
    eng_title = driver.title

    # change language
    components[0].click()

    # collect ukrainian title
    ukr_title = driver.title

    assert ukr_title == "Персонал - Факультет електроніки та комп'ютерних технологій" \
           and eng_title == "Staff - Faculty of Electronics and Computer Technologies"
