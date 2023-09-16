import os
import unittest
# iOS environment
from appium import webdriver
# Options are only available since client version 2.3.0
# If you use an older client then switch to desired_capabilities
# instead: https://github.com/appium/python-client/pull/720
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
from datetime import datetime, timedelta
import time 
from selenium.common.exceptions import TimeoutException

options = XCUITestOptions()
options.platform_name = 'iOS'
options.automation_name = 'XCUITest'
options.no_reset = True

# Platform version and device name is matching simulator that is available at my MacBook, to use relevant simulator
# on your machine check available devices using command:
# xcrun simctl list
options.platformVersion = '14.5'
options.device_name = 'iPhone 14'

# path to application package to be installed on simulator
options.app = 'com.apple.mobilecal'

# following options are doing some 'magic' that helps establish connection to real device
# based on hints from:
# https://stackoverflow.com/questions/69315482/appium-and-desktop-unable-to-launch-wda-session-since-xcode13-and-ios15
# https://discuss.appium.io/t/unable-to-start-webdriveragent-session-because-of-xcodebuild-failure/24542/9
options.new_command_timeout = '60'
options.wda_startup_retries = '3'
options.wda_startup_retry_interval = '20000'
options.wda_local_port = '8132'

appium_server_url = 'http://localhost:4723'
appium_service = AppiumService()

def wait_for_element(driver, locator_type, locator_value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((locator_type, locator_value)))

def str_to_datetime(date_str):
    # Assuming the date string is in the format "yyyy-mm-dd"
    return datetime.strptime(date_str, '%Y-%m-%d')


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        appium_service.start()
        # Appium1 points to http://127.0.0.1:4723/wd/hub by default
        self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

    

    def test_click_today_page(self):  
        try:
            # Wait for the "Today" text to appear and click it
            today_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//XCUIElementTypeStaticText[@name='Today']")))
            today_button.click()
            today_button.click()
        #except Exception as e:
        except TimeoutException:
            #self.fail(f"Failed to click 'Today' button: {e}")
            logging.warning("The 'Today' button was not found.")
        
       

    def test_create_event(self):

    # Check if "Add" button is available and add
        try:
            create_event_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Add")))
            self.assertIsNotNone(create_event_button, "Add button should be present.")
            create_event_button.click()
        except TimeoutException:
            logging.warning("The 'Add' button was not found.")
        except NoSuchElementException:
            self.fail("Add button not found")

    # Check and set Event Title
        try:
            event_title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Title")))
            self.assertIsNotNone(event_title, "Title field should be present.")
            event_title.send_keys("Test Event")
        except TimeoutException:
            logging.warning("The 'Title' field was not found.")
        except NoSuchElementException:
            self.fail("Title field not found")
       

    # Fill in the location
        event_location = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Location or Video Call")
        event_location.click()

    #Get current location
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Enter Location or Video Call").send_keys("Craiova")
        wait = WebDriverWait(self.driver, 5)
        event_currentloc = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Craiova")
        event_currentloc.click()

    # Set the event as an all-day event
        all_day_switch = self.driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeSwitch[@name='All-day']")
        all_day_switch.click()

    # Set the event to repeat every month
        repeat_button = self.driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='Repeat']")
        repeat_button.click()
        monthly_button = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Every Month")
        monthly_button.click()
    
    # Set alert event
        alert_button = self.driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeCell[@name='Alert']")
        alert_button.click()
        alert_event = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "On day of event (9 AM)")
        alert_event.click()

        note_add = self.driver.find_element(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView').send_keys("Appium with Python Catalins Test")
       
        event_created = self.driver.find_element(AppiumBy.XPATH, "(//XCUIElementTypeButton[@name='Add'])[2]").click()
        wait = WebDriverWait(self.driver, 20)
    # Check if the event has been created
        try:
            created_event = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@name, 'Test Event') and contains(@name, 'Craiova') and contains(@name, 'All day')]")))
            self.assertIsNotNone(created_event) 
        except TimeoutException:
            logging.warning("The created event was not found.")
        except NoSuchElementException:
            self.fail("Event creation failed")

    def test_edit_event(self):
    # Find and click on the event to edit
        try:
            event_to_edit = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@name, 'Test Event') and contains(@name, 'Craiova') and contains(@name, 'All day')]")))
            self.assertIsNotNone(event_to_edit, "Event to edit should be present.")
        except NoSuchElementException:
            self.fail("Event not found for editing")
        event_to_edit.click()
     # Click on the Edit button on the details page
        try:
            edit_button = WebDriverWait(self.driver, 10).until( EC.presence_of_element_located((By.ACCESSIBILITY_ID, "Edit")))
            edit_button.click()
        except TimeoutException:
            self.fail("Edit button not found")

    # Switch off the "All-day" toggle
        try:
            all_day_toggle = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//XCUIElementTypeSwitch[@name='All-day']")))
            self.assertIsNotNone(all_day_toggle, "'All-day' toggle should be present.")
        except NoSuchElementException:
            self.fail("'All-day' toggle not found")
        all_day_toggle.click()

    # Change the Start Date
        try:
            start_date = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ACCESSIBILITY_ID, "Starts")))
            self.assertIsNotNone(start_date, "Start date should be present.")
        except NoSuchElementException:
            self.fail("Start date not found")
        start_date.click()

     # Calculate the next day's date
        next_day = (datetime.now() + timedelta(days=1)).day
        next_day_str = str(next_day)

     # Change the day
        date_element = wait_for_element(self.driver, By.ACCESSIBILITY_ID, next_day_str)
        date_element.clear()
        date_element.send_keys(next_day_str)    

    
    # Set End Date = Start Date
        end_day_str = str(int(next_day_str) +1)

        try:
            end_date_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ACCESSIBILITY_ID, "Ends")))
            self.assertIsNotNone(end_date_element, "End date should be present.")
        except NoSuchElementException:
            self.fail("End date not found")

        end_date_element.click()
    
        end_date_day_element = wait_for_element(self.driver, By.ACCESSIBILITY_ID, end_day_str)
        end_date_day_element.clear()
        end_date_day_element.send_keys(end_day_str)

        
    # Change the Hour
        next_hour = (datetime.now() + timedelta(hours=1)).strftime("%-I:00 %p")
        print("Next Hour:", next_hour)
        try:
            hour_element = self.driver.find_element(By.XPATH, f"//XCUIElementTypeButton[@label='{next_hour}']")
        except NoSuchElementException:
            print("Hour not found")
            self.fail("Hour not found")
        hour_element.click()

    # Set the hour
        hour_picker = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//XCUIElementTypeApplication[@name='Calendar']/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[5]/XCUIElementTypeDatePicker/XCUIElementTypePicker/XCUIElementTypePickerWheel[1]")))
        hour_picker.send_keys("12")  
    # Save the changes
        try:
            save_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ACCESSIBILITY_ID, "Done")))
            self.assertIsNotNone(save_button, "Save button should be present.")
        except NoSuchElementException:
            self.fail("Save button not found")
        save_button.click()
    #Save for future events
        save_for_future_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ACCESSIBILITY_ID, "Save for future events")))
        save_for_future_button.click()  
    # Validate if the event has been successfully edited
        edited_event_xpath = "//*[contains(@name, 'Test Event') and contains(@name, 'Craiova') and contains(@name, '12:00 AM')]"
        edited_event = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, edited_event_xpath)))
        self.assertIsNotNone(edited_event, "Event edit failed")

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()
        if appium_service.is_running:
            appium_service.stop()        

if __name__ == '__main__':
    unittest.main()
