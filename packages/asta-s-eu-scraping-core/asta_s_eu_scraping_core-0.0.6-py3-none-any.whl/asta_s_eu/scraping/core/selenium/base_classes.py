from typing import Any, Iterable, Optional, Union, cast

import logging
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from ..config import CONFIG_DIR
from . import env

LOG = logging.getLogger(__name__)


class SeleniumBot(ABC):
    """
    A very general Selenium Bot
    """
    def __init__(self,
                 headless: Optional[bool] = True,
                 width: Optional[int] = 1024 + 200,
                 height: Optional[int] = 768 + 200,
                 driver: Optional[webdriver.Chrome] = None) -> None:

        LOG.info("Init selenium")

        del headless  # keep for compatibility

        if not driver:
            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                "debuggerAddress", f"localhost: {env.CHROME_DEBUGGER_ADDRESS_PORT}"
            )

            driver = webdriver.Chrome(
                service=Service(
                    # executable_path='/home/ada/Downloads/chromedriver-linux64/chromedriver'
                    executable_path=env.ADA_CHROME_DRIVER_EXECUTABLE_PATH or 'chromedriver'
                ),
                options=options
            )
            driver.set_window_position(0, 0)
            driver.set_window_size(width, height)

        self._driver = driver

        self._wait = WebDriverWait(driver, 20)

    # @staticmethod
    # def _extract_a_b_version(versions_a_b_c_d: str) -> str:
    #     return versions_a_b_c_d.rsplit(".", 2)[0]

    # def _check_chrome_compatibility(self) -> None:
    #     """
    #     Check browser chrome compatibility with selenium driver
    #     """
    #     # disable check because it should be handled by the deployments setup
    #     # example of api output '114.0.5735.198'
    #     # google_chrome_a_b = self._extract_a_b_version(
    #     #     self._driver.caps['browserVersion']
    #     # )
    #     #
    #     # # example of api output '114.0.5735.90 (38...9-refs/branch-heads/5735@{#1052})'
    #     # chrome_driver_a_b = self._extract_a_b_version(
    #     #     self._driver.caps['chrome']['chromedriverVersion'].split(' ', 1)[0]
    #     # )
    #     #
    #     # assert google_chrome_a_b == chrome_driver_a_b, \
    #     #     f"google chrome version {google_chrome_a_b} is
    #     #     different than {chrome_driver_a_b}, \n" \
    #     #     f"curl {DOWNLOAD_LINK} > " \
    #     #     f"  ~/bin/chromedriver_linux64.zip"

    def _mark_element(self, elem: WebElement) -> None:
        """
        Jump/Focus to element on page and highlight the text
        """
        # based on https://www.testim.io/blog/selenium-scroll-to-element/
        # https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView
        self._driver.execute_script( # type: ignore[no-untyped-call]
            """
            arguments[0].scrollIntoView({behavior: "auto", block: "center", inline: "center"});
            """, elem)

        self._driver.execute_script( # type: ignore[no-untyped-call]
            "arguments[0].style.fontWeight = 'bolder' ", elem
        )
        self._driver.execute_script( # type: ignore[no-untyped-call]
            "arguments[0].style.background = 'RED' ", elem
        )

    def _find_optional_element(self, value: str, by: str = By.XPATH) -> Optional[WebElement]:
        elem = self._driver.find_elements(by, value)
        if elem:
            assert len(elem) == 1, f"has to be just one element, but got {len(elem)}"
            return elem[0]

        return None

    def _find_only_one_element(self, value: str, by: str = By.XPATH) -> WebElement:
        elem = self._driver.find_elements(by, value)
        assert elem, 'has to be at lease one element'

        assert len(elem) == 1, f"has to be just one element, but got {len(elem)}"
        return elem[0]

    def _wait_until_page_fully_load(self,
                                    logo_xpath_selector: Optional[str] = None,
                                    sleep: Union[float, int] = 0.3) -> None:
        assert logo_xpath_selector, "keep the same signature in child method with a required field"
        time.sleep(sleep)
        self._wait.until(expected_conditions.element_to_be_clickable(
            (By.XPATH, logo_xpath_selector)
        ))

    @abstractmethod
    def open_home_page(self) -> None:
        """Open main page to find login page"""

    @abstractmethod
    def accept_cookie_if_needed(self) -> None:
        """To proceed to login page usr have to accept cookies"""

    @abstractmethod
    def login_if_needed(self, user: str, password: str) -> None:
        """To be able to fetch some personalised info we have to log in"""

    def __enter__(self) -> 'SeleniumBot':
        # self._check_chrome_compatibility()
        return self

    def __exit__(self, _: Any, value: Exception, traceback: Any) -> None:
        if isinstance(value, (selenium.common.exceptions.WebDriverException, AssertionError)):
            log_time = f"{datetime.utcnow():%Y-%m-%dT%H:%M:%S}"
            class_name = self.__class__.__qualname__
            screenshot_file = CONFIG_DIR / f"fail_on_screenshot.{class_name}-{log_time}.png"
            self._driver.save_screenshot(str(screenshot_file))
            LOG.error("Selenium failed, look into '%s'", screenshot_file)

    @staticmethod
    def random_human_sleep(start: int = 1) -> None:
        """
        Simulate human slow interaction
        """
        time.sleep(random.uniform(start, start+3))


class CouponsSeleniumBot(SeleniumBot, ABC):
    """
    Selenium Bot for Coupons services like Payback, deutschlandcard
    """
    @abstractmethod
    def open_e_coupons(self) -> None:
        """Open page with coupons to activate coupons"""

    @abstractmethod
    def activate_e_coupons(self, *partners: str) -> Iterable[str]:
        """Activate coupons once the coupon page is open"""

    def __enter__(self) -> 'CouponsSeleniumBot':
        """
        Explicitly return ``CouponsSeleniumBot`` object instead of ``SeleniumBot``
        """
        return cast('CouponsSeleniumBot', super().__enter__())
