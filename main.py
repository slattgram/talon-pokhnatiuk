import os
import pytest_html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

TESTING_URL = "https://electronics.lnu.edu.ua/about/staff/"
EMAIL_FILE_PATH = "/Users/dmytropokhnatiuk/Pokhnatiuk TALON FEIm-14/mail.txt"

# to generate with report pytest main.py --html=report.html --self-contained-html
#f

# Fixture to initialize the WebDriver

@pytest.fixture
def driver() -> webdriver.Chrome:
    # Initialize the WebDriver
    chrome_driver = webdriver.Chrome()
    chrome_driver.get(TESTING_URL)
    return chrome_driver

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        # always add url to report
        extras.append(pytest_html.extras.url("http://www.example.com/"))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extras.append(pytest_html.extras.html("<div>Additional HTML</div>"))
        report.extras = extras


def test_profile_eng(driver: webdriver.Chrome):
    # Wait for all elements to be present on the page
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "*")))

    # Find all staff name elements
    components = driver.find_elements(By.CLASS_NAME, "name")
    default_page_title = driver.title

    # Loop through each staff element and check the behavior
    for component in components:
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
def test_email(driver, capsys):
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "language-switcher")))

    # Click the language switcher if present (Ukrainian)
    div_container = driver.find_element(By.CLASS_NAME, "language-switcher")
    components = div_container.find_elements(By.CSS_SELECTOR, "*")
    if components:
        components[0].click()

    # Read emails from the file
    with open(EMAIL_FILE_PATH, "r") as m_file:
        mails = [line.strip() for line in m_file]

    # Find email elements on the page
    email_elements = driver.find_elements(By.CLASS_NAME, "email")

    # Check each email element against the expected emails
    for index, email_element in enumerate(email_elements, start=1):
        container = email_element.find_elements(By.CSS_SELECTOR, "*")

        # Print information for debugging
        if container:
            print(f"\nChecking email {index}: {container[0].text} against the expected emails.")
            assert container[0].text in mails, f"Email {container[0].text} not found in the expected list"
        else:
            print(f"\nEmail {index} container is empty. Skipping assertion.")

# Run the test





def test_title(driver: webdriver.Chrome):
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


if __name__ == "__main__":
    file_path = os.path.abspath(__file__)
    pytest.main(["-s", file_path, "--html=report.html"])
