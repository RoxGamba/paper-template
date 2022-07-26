"""
Submit a paper to the arxiv. Requires:
- selenium library (pip install selenium)
- chromium-chromedriver (apt install chromium-chromedriver)
- schedule library

See also:
https://stackoverflow.com/questions/33155454/how-to-find-an-element-by-href-value-using-selenium-python/33155512
https://towardsdatascience.com/controlling-the-web-with-python-6fceb22c5f08
"""

from selenium import webdriver

def create_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Using Chrome to access web
    return webdriver.Chrome('chromedriver',options=options) 

def arxiv_login(wd, usr, pwd, hrf):
    from selenium.webdriver.common.by import By
    # Open the website
    wd.get('https://arxiv.org/login')

    # Send id information
    usrname = wd.find_element(By.NAME, "username")
    usrname.send_keys(usr)

    # Send pwd information
    pwd     = wd.find_element(By.NAME, "password")
    pwd.send_keys(pwd)

    # login
    submit_button = wd.find_element(By.XPATH,'//input[@value="Submit"]')
    submit_button.click()

    # find the correct paper to update/submit via href
    # eg: https://arxiv.org/submit/4013143/resume --> hrf = '4013143'
    update_button = wd.find_element(By.XPATH,('//a[@href="https://arxiv.org/submit/' + hrf + '/resume"]'))
    update_button.click()

    return 0

def arxiv_submit(usr, pwd, hrf, time="18:00:00"):
    from   selenium.webdriver.common.by import By
    import schedule; import time
    
    # create a chrome session
    wd = create_webdriver()

    # open and login to the arxiv, go to the paper update page
    arxiv_login(wd, usr, pwd, hrf)

    # find the submit button
    submit_button = wd.find_element(By.XPATH,'//input[@value="Submit"]')

    # local function to click submit
    def click_submit():
        submit_button.click()
        return schedule.CancelJob

    # scheduler: run it at specified UTC time
    schedule.every().day.at(time).do(click_submit)

    while True:
      schedule.run_pending()
      time.sleep(0.0001)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', action='store', required=True, type=str, help='your arxiv password')
    parser.add_argument('-u', action='store', required=True, type=str, help='your arxiv username')
    parser.add_argument('-href', action='store', required=True, type=str, help='your arxiv href.\n E.g: https://arxiv.org/submit/4013143/resume --> href = 4013143')


    args = parser.parse_args()

    arxiv_submit(args.u, args.p, args.href)


