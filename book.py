import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

def go_to_right_day(driver, wait):
    given_date = datetime.today() 

    # Just making sure next day is there before we click the show more dates button
    next_day = given_date + timedelta(days=1)
    # Extract next dayyear, month, and day
    nd_year, nd_month, nd_day = next_day.year, next_day.month, next_day.day
    nd_year = str(nd_year)
    nd_month = str(nd_month)
    nd_day = str(nd_day)
    bad_class="single-date-select-mobile"
    xpath = f'//button[@data-year={nd_year} and @data-month={nd_month} and @data-day={nd_day} and not(contains(@class,"{bad_class}"))]'
    next_day = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    if len(next_day) != 1:
        print("Next day not working")
    next_day[0].click()

    right_arrow_class = 'single-date-right-arrow'
    xpath = f'//button[contains(@class,"{right_arrow_class}")]'
    right_arrow = driver.find_elements(By.XPATH, xpath)
    if len(right_arrow) != 1:
        print("Right arrow not found, just skip for now")
    else:
        right_arrow[0].click()

    # next_week = driver.find_elements(By.XPATH,)
    # Add 7 days
    # next_week = given_date + timedelta(days=7)
    next_week = given_date + timedelta(days=2)

    
    # Extract year, month, and day
    year, month, day = next_week.year, next_week.month, next_week.day
    year = str(year)
    month = str(month)
    day = str(day)
    bad_class="single-date-select-mobile"
    xpath = f'//button[@data-year={year} and @data-month={month} and @data-day={day} and not(contains(@class,"{bad_class}"))]'
    next_week = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    # if len(next_day) != 1:
    #     print("Next week not working")
    next_week.click()

def wait_for_element(driver, locator, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda x: len(x.find_elements(*locator)) > 1
        )
        return True
    except:
        return False
    
def make_bookings(driver, court_link):
    bookings_made = []
    wait = WebDriverWait(driver, 10)
    driver.get(court_link)
    go_to_right_day(driver, wait)
    # Find all booking cards
    # time_slots = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "program-instance-card")))
    wait_for_element(driver, (By.CLASS_NAME, "program-instance-card"))
    time_slots = driver.find_elements(By.CLASS_NAME, "program-instance-card")
    
    for time_slot in time_slots:
        # Get the spot availability text
        spots_element = time_slot.find_element(By.CLASS_NAME, "spots-tag")
        spots_text = spots_element.text.strip()
        select_button = time_slot.find_element(By.CLASS_NAME, "program-select-btn")
        # Only proceed if there are spots left
        if "No spots left" not in spots_text and \
                "disabled" not in select_button.get_attribute("class") and \
                select_button.is_enabled():

            # Get the time
            time_element = time_slot.find_element(By.CLASS_NAME, "instance-time-header")
            time_text = time_element.text.strip()

            # Find the correct div with title="Location"
            location_div = time_slot.find_element(By.XPATH, './/div[@title="Location"]')
            # Extract court name from the <p> tag inside
            court_name = location_div.find_element(By.TAG_NAME, "p").text.replace("location_on", "").strip()

            select_button.click()
            # Wait for the "Register" button and click it
            register_button = wait.until(EC.element_to_be_clickable((By.ID, 'registerBtn')))
            register_button.click()
            # Proceed to Checkout
            to_checkout_class = "btn-NextRegistrationStep"
            xpath = f'//button[contains(@class,"{to_checkout_class}")]'
            wait_for_element(driver, (By.XPATH, xpath))
            # to_checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(element).click().perform()

            # Checkout
            checkout_button_id = "checkoutButton"
            checkout_button = wait.until(EC.element_to_be_clickable((By.ID, checkout_button_id)))
            checkout_button.click()

            # Final Proceed to Checkout - Checkout Button LOL
            btn_checkout_cart_id = "btnCheckoutCart"
            btn_checkout_cart = wait.until(EC.element_to_be_clickable((By.ID, btn_checkout_cart_id)))
            btn_checkout_cart.click()

            # Store booking details
            bookings_made.append({"time": time_text, "court_name": court_name})
            print(bookings_made)
            return bookings_made
    return bookings_made

def main():
    driver = webdriver.Chrome()

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

    # service = Service()  # You can specify the path to chromedriver here if needed
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    link = 'https://membership.gocrimson.com/program?classificationid=dc42ec33-82df-44ca-b06c-109c3685395d'
    driver.get(link)



    driver.maximize_window()
    cookie_button = driver.find_element(By.ID, 'gdpr-cookie-accept')
    cookie_button.click()

    elements = driver.find_elements(By.CLASS_NAME, "img-link")
    courts = {}
    for element in elements:
        court = element.text.split('\n')[0]
        court_link = element.get_attribute('href')
        courts[court] = court_link
        available_times_all = {}
    for court, court_link in courts.items():
        court_link = courts['Murr Tennis: Court 6 (1.5 Hours)']
        bookings_made = make_bookings(driver, court_link)
    
if __name__=="__main__":
    main()