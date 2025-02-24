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
    # bad_class="single-date-select-mobile"
    # xpath = f'//button[@data-year={nd_year} and @data-month={nd_month} and @data-day={nd_day} and not(contains(@class,"{bad_class}"))]'
    xpath = f'//button[@data-year={nd_year} and @data-month={nd_month} and @data-day={nd_day}]'
    print(xpath)
    wait = WebDriverWait(driver, 10)
    next_day = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # if len(next_day) != 1:
    #     print("Next day not working")
    # next_day[0].click()
    actions = ActionChains(driver)
    # actions.move_to_element(next_day).click().perform()
    driver.execute_script("arguments[0].click();", next_day)



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
    # bad_class="single-date-select-mobile"
    # xpath = f'//button[@data-year={year} and @data-month={month} and @data-day={day} and not(contains(@class,"{bad_class}"))]'
    xpath = f'//button[@data-year={year} and @data-month={month} and @data-day={day}]'
    next_week = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # if len(next_day) != 1:
    #     print("Next week not working")
    # next_week.click()
    driver.execute_script("arguments[0].click();", next_week)

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
    
    for index in range(len(time_slots)):
        # Dynamically find the time_slot again to avoid stale references
        time_slots = driver.find_elements(By.CLASS_NAME, "program-instance-card")
        time_slot = time_slots[index]
        # Get the spot availability text
        spots_element = time_slot.find_element(By.CLASS_NAME, "spots-tag")
        spots_text = spots_element.text.strip()
        select_button = 'program-select-btn'
        xpath = f'//button[contains(@class,"{select_button}")]'
        select_buttons = driver.find_elements(By.XPATH, xpath)
        # Assume number of slots equals number of buttons
        select_button = select_buttons[index]
        is_disabled = select_button.get_attribute("disabled") is not None
        # Only proceed if there are spots left
        if "No Spots Left" not in spots_text and not is_disabled:
            time_slot = driver.find_elements(By.CLASS_NAME, "program-instance-card")[index]
            # Get the time
            time_text = time_slot.find_element(By.CLASS_NAME, "instance-time-header").text.strip()

            # Find the correct div with title="Location"
            # Extract court name from the <p> tag inside
            time_slot = driver.find_elements(By.CLASS_NAME, "program-instance-card")[index]
            court_name = time_slot.find_element(By.XPATH, './/div[@title="Location"]').find_element(By.TAG_NAME, "p").text.replace("location_on", "").strip()
            # Assume number of slots equals number of buttons
            select_button = driver.find_elements(By.XPATH, xpath)[index]
            driver.execute_script("arguments[0].click();", select_button)


            # Wait for the "Register" button and click it
            register_button = wait.until(EC.presence_of_element_located((By.ID, 'registerBtn')))
            driver.execute_script("arguments[0].click();", register_button)

            # Proceed to Checkout
            to_checkout_class = "btn-NextRegistrationStep"
            xpath = f'//button[contains(@class,"{to_checkout_class}")]'
            wait_for_element(driver, (By.XPATH, xpath))
            # to_checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            proceed_to_checkout_button = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", proceed_to_checkout_button)

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
        bookings_made = make_bookings(court_link)
        if bookings_made:
            print("Booking was made")
            break
    
if __name__=="__main__":
    main()