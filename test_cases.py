import os
import time
import unittest
import HtmlTestRunner
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from dotenv import load_dotenv
import tracemalloc

tracemalloc.start()

load_dotenv()


class TestSalixnigra(unittest.TestCase):
    chrome_options = None

    @classmethod
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def locate_element(self, tag: str, name: str, delay: int = 15):
        return WebDriverWait(self.driver, delay, ignored_exceptions=self.ignored_exceptions).until(
            ec.presence_of_element_located((tag, name)))

    def login(self, _email, _password):
        # Give browser time to load
        self.driver.get(os.getenv("web_app"))
        self.locate_element(By.ID, "email")
        email = self.driver.find_element(By.ID, 'email')
        password = self.driver.find_element(By.ID, 'password')
        submit = self.driver.find_element(By.TAG_NAME, 'button')
        email.send_keys(_email)
        password.send_keys(_password)
        time.sleep(3)
        submit.click()
        time.sleep(3)

    def can_deposit(self):
        global can_pay
        try:
            self.driver.find_element(By.CLASS_NAME, "alert-success")
            can_pay = True
        except NoSuchElementException:
            can_pay = False
        finally:
            return can_pay

    def test_login(self):
        self.login(os.getenv("iemail"), os.getenv("ipassword"))
        print(os.getenv("web_app"))
        title = self.driver.title

        expected_title = "Dashboard - Salix Nigra"
        self.assertEqual(expected_title, title)
        self.driver.quit()

    def test_dashboard_home(self):
        self.login(os.getenv("iemail"), os.getenv("ipassword"))
        investment_value = self.locate_element(By.XPATH,
                            "/html/body/div[2]/div[2]/main/div/div/div[2]/div/div[1]/div/div[1]/h6")
        investment_indice = self.locate_element(By.XPATH,
                                                     "/html/body/div[2]/div[2]/main/div/div/div[2]/div/div[2]/div/div[1]/h6")
        self.assertIn("Valeur de rachat des Feuilles", investment_value.get_attribute("innerText"))
        self.assertIn("Indice Salix", investment_indice.get_attribute("innerText"))
        self.driver.quit()

    def test_investor_access_investors_list(self):
        self.login(os.getenv("iemail"), os.getenv("ipassword"))
        self.driver.get(os.getenv("investors_list_url"))
        title = self.driver.title
        expected_title = "Dashboard - Salix Nigra"
        self.assertEqual(expected_title, title)
        self.driver.quit()

    def test_founder_access_investors_list(self):
        self.login(os.getenv("femail"), os.getenv("fpassword"))
        self.driver.get(os.getenv("investors_list_url"))
        title = self.driver.title
        expected_title = "Dashboard - Salix Nigra"
        self.assertNotEqual(expected_title, title)
        self.driver.quit()

    def test_deposit(self):
        self.login(os.getenv("iemail"), os.getenv("ipassword"))
        self.driver.get(os.getenv("deposit_url"))
        investment_amount = 1000000
        amount = self.driver.find_element(By.ID, 'amount')
        amount.send_keys(investment_amount)
        product_price = self.driver.find_element(By.ID, 'product_price')
        firstName = self.driver.find_element(By.ID, 'firstName')
        lastName = self.driver.find_element(By.ID, 'lastName')
        email = self.driver.find_element(By.ID, 'email')
        phone = self.driver.find_element(By.ID, 'phone')
        address = self.driver.find_element(By.ID, 'address')
        state = self.driver.find_element(By.ID, 'state')

        # Test default values presence
        self.assertEqual(int(product_price.get_attribute("innerText").replace(" ", "")), investment_amount)
        self.assertNotEqual(firstName.get_attribute("value"), "")
        self.assertNotEqual(lastName.get_attribute("value"), "")
        self.assertNotEqual(email.get_attribute("value"), "")

        # Try a submit. This should fail
        submit_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/form/button")
        submit_button.click()
        self.driver.switch_to.alert.dismiss()
        self.assertFalse(self.can_deposit())

        # Set compulsory value if absent. This should also failed because a payment method must be selected
        address.send_keys(os.getenv("address"))
        phone.send_keys(os.getenv("phone"))
        state.send_keys(os.getenv("state"))
        submit_button.click()
        self.driver.switch_to.alert.dismiss()
        self.assertFalse(self.can_deposit())

        # Select a payment method. This should pass
        mtn_mobilemoney_cm = self.driver.find_element(By.ID, 'mtn_mobilemoney_cm')
        mtn_mobilemoney_cm.click()
        submit_button.click()
        self.assertTrue(self.can_deposit())
        self.driver.quit()

    def test_withdraw(self):
        self.login(os.getenv("iemail"), os.getenv("ipassword"))
        self.driver.get(os.getenv("withdraw_url"))
        # Confirm we are on withdraw page
        withdraw_amount = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/main/div/div/div[2]/div/div["
                                                             "2]/div/div[1]/h6")
        self.assertIn("retrait", withdraw_amount.get_attribute("innerText"))
        self.driver.quit()

    def test_logout(self):
        self.driver.get(os.getenv("logout_url"))

        # Successful login title should contain "Services d'investissement"
        in_title = "Services d'investissement"
        self.assertIn(in_title, self.driver.title)
        self.driver.quit()

    def test_wrong_user_login(self):
        self.login(os.getenv("remail"), os.getenv("rpassword"))

        # Wrong credentials should display a warning
        warning = self.driver.find_element(By.CLASS_NAME, "alert-warning")
        message = "Oups"
        self.assertIn(message, warning.get_attribute("innerText"))
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='reports'))
