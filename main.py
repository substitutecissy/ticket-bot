import sys
import pytz
from typing import Tuple
from time import sleep
from datetime import time, datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from joblib import Parallel, delayed


# params

# ticketing site parameters 
event_url = 'https://boxoffice-music.sydney.edu.au/WEBPAGES/EntaWebShow/ShowPerformance.aspx'
email = 'cissy.yu.808@gmail.com'
password = 'Tov2ovTov3!'

# program running parameters
max_try = 500
city = 'Sydney'
desired_timezone = pytz.timezone('Australia/Sydney')
time_zone = timezone(timedelta(hours=+11), 'AEDT')
begin_time = desired_timezone.localize(datetime(2023, 10, 29, 11, 00, 0))
end_time = desired_timezone.localize(datetime(2023, 10, 29, 11, 15, 0))

# form info
card_number = '0000000000000000'
expiry_month = '12'
expiry_year = '2027'
cvv = '111'


options = Options()
options.add_argument('--headless')
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


def check_current_time(begin_time:datetime, end_time:datetime) -> Tuple[time, bool]:
    '''
    Check current time is between 00:00 and 00:15. 
    Returns current time and if it is between begin and end time.
    '''
    dt_now = datetime.now(time_zone)
    return dt_now, (begin_time <= dt_now) and (dt_now < end_time)

def open_chrome_and_login():
    '''
    Open a Chrome window.
    Navigate to the website url and log in.
    Navigate to the event page.
    '''
    print('Trying to navigate to event page and log in...')
    driver.get(event_url)
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00$ucSessionDetails$cmdLogin')))
    login_btn.click()

    email_input = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContentPlaceHolder_txtEmail')))
    email_input.send_keys(email)
    password_input = find_element_with_retry(By.ID, 'ctl00_MainContentPlaceHolder_txtPassword')
    password_input.send_keys(password) 

    submit_btn = find_element_with_retry(By.ID, 'ctl00$MainContentPlaceHolder$CmdLogon')
    submit_btn.click()
    
    sleep(5)

    driver.get(event_url)
    print("Logged in and ready to book!")


def make_a_reservation() -> bool:
    '''
    Attempt to buy 2 tickets.
    Return the status if the tickets are bought successfully or not.
    '''
    try:
        print('Trying to buy ticket...')
        driver.refresh()
        max_attempts = 200 
        attempts = 1

        while attempts <= max_attempts:
            try:
                print(f'trying to click buy, attempt #{attempts}')
                buy_btn = driver.find_element(By.ID, 'ctl00$NavigationContentPlaceHolder$CmdNext')
                buy_btn.click()
                print('Clicked buy button.')
                # If the element is found, break out of the loop
                break
            except (NoSuchElementException, ElementNotInteractableException) as e:
                print("Element not found. Refreshing the page...")
                driver.refresh()
                attempts += 1

        wait.until(EC.element_to_be_clickable((By.ID, 'ddlSeatPlanMap')))
        sleep(1)
        dropdown_btn = find_element_with_retry(By.ID, 'ddlSeatPlanMap')
        dropdown_btn.click()
        print('Clicked seats dropdown.')
        select = Select(dropdown_btn)
        select.select_by_visible_text('STALLS')
        print('Select seats and click NEXT in the browser.')

        wait.until(EC.element_to_be_clickable((By.ID, 'DiscountDialog')))
        next_btn = find_element_with_retry(By.ID, 'ctl00$NavigationContentPlaceHolder$CmdNext')
        next_btn.click()
        print('Clicked NEXT button.')

        find_out = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContentPlaceHolder_Q2A8')))
        find_out.click()
        print('Filled out how did you find out about us.')
        alum = find_element_with_retry(By.ID, 'ctl00_MainContentPlaceHolder_Q3A11')
        alum.click()
        print('Filled out alum checkbox.')
        next_btn = find_element_with_retry(By.ID, 'ctl00$NavigationContentPlaceHolder$CmdNext')
        next_btn.click()
        print('Clicked NEXT.')

        agree = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContentPlaceHolder_chkAgree')))
        agree.click()
        print('Agree with terms and conditions.')
        book_btn = find_element_with_retry(By.ID, 'ctl00$NavigationContentPlaceHolder$cmdBook')
        book_btn.click()
        print('Clicked NEXT.')

        next_btn = find_element_with_retry(By.ID, 'ctl00$NavigationContentPlaceHolder$CmdNext')
        next_btn.click()
        print('Clicked NEXT.')

        card_input = find_element_with_retry(By.ID, 'pan')
        card_input.send_keys(card_number)
        expiry_month = find_element_with_retry(By.ID, 'expiry_month')
        expiry_month.click()
        select = Select(expiry_month)
        select.select_by_visible_text(expiry_month)
        
        expiry_year = find_element_with_retry(By.ID, 'expiry_year')
        expiry_year.click()
        select = Select(expiry_year)
        select.select_by_visible_text(expiry_year)
        cvv_input = find_element_with_retry(By.ID, 'cvv')
        cvv_input.send_keys(cvv)
        print('Filled out credit card info.')

        return True
    except Exception as e:
        print(e)
        return False
    finally:
        return False
	    # close the drivers
        # driver.quit()


def try_booking(max_try:int=1000) -> None:
    '''
    Try booking a reservation until either one reservation is made successfully or the attempt time reaches the max_try
    '''
    # initialize the params
    current_time, is_during_running_time = check_current_time(begin_time, end_time)
    reservation_completed = False
    try_num = 1

    # open_chrome_and_login()

    # repeat booking a reservation every second
    while True:
      if not is_during_running_time:
          print(f'Not Running the program. In {city}, it is {current_time.strftime('%H:%M:%S')} and not between {begin_time.strftime('%H:%M:%S')} and {end_time.strftime('%H:%M:%S')}.')

          # sleep less as the time gets close to the begin_time
          one_second_left = begin_time - timedelta(seconds=1)
          two_seconds_left = begin_time - timedelta(seconds=2)
          if current_time >= one_second_left:
            sleep(0.001)
          elif two_seconds_left <= current_time < one_second_left:
            sleep(0.5)
          else:
            sleep(1)

          try_num += 1
          current_time, is_during_running_time = check_current_time(begin_time, end_time)
          continue

      print(f'----- try : {try_num} -----')
      # try to get tickets
      reservation_completed = make_a_reservation()

      if reservation_completed:
          print('Reached payment page!!')
          break
      else:
          print(f'Tried {try_num} times, but couldn\'t get tickets..')
          break
    #   else:
    #       sleep(1)
    #       try_num += 1
    #       current_time, is_during_running_time = check_current_time(begin_time, end_time)


# Function to find element with retries
def find_element_with_retry(by, value, max_retries=5, retry_interval=1):
    retries = 0
    while retries < max_retries:
        try:
            element = driver.find_element(by, value)
            print(f"Found element {value}")
            return element
        except NoSuchElementException:
            print(f"Element not found. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
            retries += 1
    print("Element not found after {max_retries} retries")
    raise NoSuchElementException(f"Element not found after {max_retries} retries")

if __name__ == '__main__':    
    try_booking(max_try)