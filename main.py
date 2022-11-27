import os
import json
import time
import urllib

# chromedriver: https://chromedriver.storage.googleapis.com/107.0.5304.62/chromedriver_linux64.zip
# install chrome: wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome-stable_current_amd64.deb
from selenium import webdriver
from selenium.webdriver.common.by import By

# Constants
ArchiveURL = os.getenv("ARCHIVE_URL")
ArchiveLocalURL = os.getenv("ARCHIVE_LOCAL_URL")
LoginURL = ArchiveLocalURL+"/admin/login/"  # ?next=/add/
AddURL = ArchiveLocalURL+"/add/"
PublicURL = ArchiveLocalURL+"/public/"
mode = os.getenv("ARCHIVE_DISPLAY_MODE")
username = os.getenv("ARCHIVE_USERNAME")
password = os.getenv("ARCHIVE_PASSWORD")
# 要存档的网址
URL = os.getenv("URL")

Mode = {
    "Index": "index.html",
    "SingleFile": "singlefile.html",
    "Screenshot": "screenshot.png",
    "PDF": "output.pdf",
}


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)


def getArchivePage():
    # 获取归档后的页面链接
    driver.get(LoginURL)
    loginForm = driver.find_element(By.ID, "login-form")
    loginForm.find_element(By.ID, "id_username").send_keys(username)
    loginForm.find_element(By.ID, "id_password").send_keys(password)
    loginForm.submit()

    driver.get(AddURL)
    addForm = driver.find_element(By.ID, "add-form")
    URLwithTime = "{URL}#{UTC}".format(
        URL=URL, UTC=time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()))
    addForm.find_element(By.ID, "id_url").send_keys(URLwithTime)
    # 一秒后停止加载, 这样返回比较快
    StopLoadingJS = """
    setTimeout(function () {
    window.stop();
    }, 1000);
    """
    driver.execute_script(StopLoadingJS)
    addForm.submit()
    searchURL = "{PublicURL}?q={URLComponent}".format(PublicURL=PublicURL,
                                                      URLComponent=urllib.parse.quote_plus(URLwithTime))
    driver.get(searchURL)
    href = driver.find_element(By.ID, "table-bookmarks").find_element(
        By.CLASS_NAME, "title-col").find_elements(By.TAG_NAME, "a")[0].get_attribute("href")
    href = urllib.parse.urlparse(href).path[:-11]  # 去掉最后的/index.html
    return "{ArchiveURL}{path}/{filemode}".format(ArchiveURL=ArchiveURL, path=href, filemode=Mode[mode])


Result = {"status": "unknown"}

try:
    Result["url"] = getArchivePage()
    Result["status"] = "success"
except Exception as e:
    Result["status"] = "failed"
    Result["error"] = str(e)

print(json.dumps(Result))
