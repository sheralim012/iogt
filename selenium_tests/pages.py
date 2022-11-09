from typing import List
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

class BasePage(object):

    body_text_locator = (By.TAG_NAME, 'body')
    content_text_locator = (By.CLASS_NAME, 'content')
    message_text_locator = (By.CLASS_NAME, 'messages')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver        

    def url_matches(self, path: str) -> bool:
        return urlparse(self.driver.current_url).path == path

    def get_body_text(self):
        return self.driver.find_element(*self.body_text_locator).text

    def get_content_text(self):
        return self.driver.find_element(*self.content_text_locator).text

    def get_messages_text(self):
        return self.driver.find_element(*self.message_text_locator).text

    @property
    def footer(self) -> 'FooterElement':
        return FooterElement(self.driver)

    @property
    def navbar(self) -> 'NavbarElement':
        return NavbarElement(self.driver)


class LoginPage(BasePage):    

    user_name_locator = (By.NAME, 'login')
    password_locator = (By.NAME, 'password')
    submit_locator = (By.CSS_SELECTOR, "button[type='Submit']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
        self.login_user_name = driver.find_element(*self.user_name_locator)
        self.login_password = driver.find_element(*self.password_locator)
        self.login_submit = driver.find_element(*self.submit_locator)

    def get_username(self):
        return self.login_user_name
 
    def get_password(self):
        return self.login_password
 
    def get_login_submit(self):
        return self.login_submit

    def login_user(self, user):
        self.login_user_name.send_keys(user.username)
        self.login_password.send_keys('test@123')
        self.login_submit.click()

class LogoutPage(BasePage):    

    logout_button_locator = (By.CSS_SELECTOR, "button[type='Submit']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
        self.logout_submit = driver.find_element(*self.logout_button_locator)

    def logout_user(self):
        self.logout_submit.click()


class ArticlePage(BasePage):

    heading_locator = (By.TAG_NAME, 'h1')
    lead_image_locator = (By.CLASS_NAME, 'article__lead-img-featured')
    navigate_next_locator = (By.CLASS_NAME, 'article__navigation--next')
    navigate_previous_locator = (By.CLASS_NAME, 'article__navigation--previous')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    @property
    def comments_section(self) -> 'CommentsSectionElement':
        return CommentsSectionElement(self.driver)
        
    @property
    def title(self) -> str:
        return self.driver.find_element(*self.heading_locator).text

    def has_lead_image(self):
        lead_image = self.driver.find_element(*self.lead_image_locator)
        return (
            lead_image.size['width'] > 0
            and lead_image.size['height'] > 0
            and lead_image.is_displayed()
        )
         
    def navigate_next(self):
        self.driver.find_element(*self.navigate_next_locator).click() 
        return BasePage(self.driver)  

    def navigate_previous(self):
        self.driver.find_element(*self.navigate_previous_locator).click()
        return BasePage(self.driver)        


class BaseElement():
    locator = (By.TAG_NAME, 'html')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.html = self.driver.find_element(*self.locator)

    def safe_click(self, button):
        self.driver.execute_script("arguments[0].click();", button)

    @property
    def is_displayed(self) -> bool:
        return self.html.is_displayed()

class CommentsSectionElement(BaseElement):
    locator =  (By.CLASS_NAME, 'comments')

    comment_area_locator = (By.NAME, "comment")
    reply_comment_area_locator = (By.NAME, "comment")
    comment_holder_locator = (By.CLASS_NAME, 'comments-holder')
    leave_comment_locator = (By.CSS_SELECTOR, "input[value='Leave comment']")
    delete_comment_locator = (By.LINK_TEXT, 'Remove')
    reply_comment_locator = (By.LINK_TEXT,'Reply')
    report_comment_locator = (By.LINK_TEXT,'Report') 
    report_button_locator = (By.CSS_SELECTOR, "input[value='Report']")

    def submit_comment(self, text):
        self.comment_area = self.driver.find_element(*self.comment_area_locator)
        self.comment_area.send_keys(text)
        self.safe_click(self.driver.find_element(*self.leave_comment_locator))

    def retrieve_comments(self):
        self.comment_holder = self.driver.find_element(*self.comment_holder_locator)
        return self.comment_holder.text

    def delete_last_comment(self):
        self.safe_click(self.driver.find_element(*self.delete_comment_locator))

    def reply_last_comment(self, reply):
        self.safe_click(self.driver.find_element(*self.reply_comment_locator))
        self.submit_comment(reply)

    def report_last_comment(self):
        self.safe_click(self.driver.find_element(*self.report_comment_locator))
        self.driver.find_element(*self.report_button_locator).click() 

class FooterElement(BaseElement):
    locator = (By.CSS_SELECTOR, '.footer-main .bottom-level')

    @property
    def items(self) -> List['FooterItemElement']:
        return [
            FooterItemElement(self.driver, el)
            for el in self.html.find_elements(By.CSS_SELECTOR, 'nav a')
        ]

class FooterItemElement():
    def __init__(self, driver, el) -> None:
        self.driver = driver
        self.html = el

    @property
    def title(self) -> str:
        return self.html.text

    @property
    def has_icon(self) -> bool:
        icon = self.html.find_element(By.TAG_NAME, 'img')
        return (
            icon.size['width'] > 0
            and icon.size['height'] > 0
            and icon.is_displayed()
        )

    @property
    def background_color(self):
        return self.html.value_of_css_property('background-color')

    @property
    def font_color(self):
        return self.html.value_of_css_property('color')

    def click(self) -> 'BasePage':
        self.html.click()
        return BasePage(self.driver)


class NavbarElement(FooterElement):
    locator = (By.CSS_SELECTOR, '.footer-main .top-level')
