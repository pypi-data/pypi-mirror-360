from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable,
)
from selenium.webdriver.support.expected_conditions import (
    invisibility_of_element,
)
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
)
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from movsviewer.constants import GECKODRIVER_PATH

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator

    from selenium.webdriver.remote.webdriver import WebDriver

logger = getLogger(__name__)


def get_options(dtemp: str) -> Options:
    profile = FirefoxProfile()
    # set download folder
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir', dtemp)

    options = Options()
    options.profile = profile
    return options


def _w(
    wait: 'WebDriverWait[WebDriver]',
    condition: """Callable[[tuple[str, str]],
                           Callable[[WebDriver], bool | WebElement]]""",
    css_selector: str,
) -> WebElement:
    ret = wait.until(condition((By.CSS_SELECTOR, css_selector)))
    if not isinstance(ret, WebElement):
        raise TypeError
    return ret


def _c(wait: 'WebDriverWait[WebDriver]', css_selector: str) -> WebElement:
    return _w(wait, element_to_be_clickable, css_selector)


def _p(wait: 'WebDriverWait[WebDriver]', css_selector: str) -> WebElement:
    return _w(wait, presence_of_element_located, css_selector)


def _i(wait: 'WebDriverWait[WebDriver]', css_selector: str) -> WebElement:
    return _w(wait, invisibility_of_element, css_selector)


def pl(wait: 'WebDriverWait[WebDriver]', wd: 'WebDriver') -> None:
    _p(wait, '.pageLoader')
    founds = wd.find_elements(By.CSS_SELECTOR, '.pageLoader')
    wait.until(all_of(*(invisibility_of_element(found) for found in founds)))


HP = 'https://bancoposta.poste.it/bpol/public/BPOL_ListaMovimentiAPP/index.html'


@contextmanager
def get_movimenti(
    username: str, password: str, num_conto: str, get_otp: 'Callable[[], str]'
) -> 'Iterator[Path]':
    with (
        TemporaryDirectory() as dtemp,
        Firefox(
            service=Service(executable_path=str(GECKODRIVER_PATH)),
            options=get_options(dtemp),
        ) as wd
    ):  # fmt: skip
        wait = WebDriverWait(wd, 1000)
        # login
        wd.get(HP)
        pl(wait, wd)
        wd.find_element(By.CSS_SELECTOR, '#username').send_keys(username)
        wd.find_element(By.CSS_SELECTOR, '#password').send_keys(
            password + Keys.RETURN
        )
        wait.until(
            url_contains(
                'https://idp-poste.poste.it/jod-idp-retail/cas/app.html'
            )
        )
        pl(wait, wd)
        _c(wait, '#_prosegui').click()
        otp = get_otp()
        wd.find_element(By.CSS_SELECTOR, '#otp').send_keys(otp + Keys.RETURN)

        # choose conto and download text
        _p(wait, f'select.numconto>option[value="string:{num_conto}"]')
        pl(wait, wd)
        Select(_p(wait, 'select.numconto')).select_by_value(
            f'string:{num_conto}'
        )

        # hide cookie banner
        wd.execute_script(
            'document.querySelector("#content-alert-cookie")'
            '.style.display="none"'
        )
        _c(wait, '#select>option[value=TESTO]')
        Select(_p(wait, '#select')).select_by_value('TESTO')

        pdtemp = Path(dtemp)

        logger.info('prima: %s', list(pdtemp.iterdir()))
        _c(wait, '#downloadApi').click()
        _i(wait, '.waiting')
        logger.info('dopo:  %s', list(pdtemp.iterdir()))

        yield pdtemp / 'ListaMovimenti.txt'
