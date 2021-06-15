from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys


if __name__ == "__main__":
    url = "https://habr.com/ru/"
    # ff_bin = FirefoxBinary()
    browser = webdriver.Firefox()
    browser.get(url)
    print(1)
