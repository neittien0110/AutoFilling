'''
Created on 02 27, 2022

@author: Nguyen Duc Tien
'''

from math import nan
import numbers
import string
from time import sleep
from unittest import case
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import json
import selenium.common.exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# create a url variable that is the website link that needs to crawl
#BASE_USL = 'https://exam.hust.edu.vn/group/members.php?group=6810'
#BASE_URL = 'https://exam.hust.edu.vn/user/index.php?id=135'

# Select Webbrowser
WebBrowserSelector=3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def AddUserToGroup():
    """
    This function takes as an input parameter the name of the stock item, and crawls the data of stock codes and prices. 
    Then put the data into the stock_list array

    Parameters:
    section (String): A input string describes the name of the stock section like ABC, DEF, GHI, ...

    Returns:
    this function doesn't return anything
    
    """
    global input_list
    global driver
    
    
    if WebBrowserSelector == 1:
        driver = webdriver.Firefox()   # import browser firefox}    
    elif WebBrowserSelector == 2:   
        driver = webdriver.Chrome(executable_path=r'./BrowserDrivers/chromedriver.exe')  # import browser firefox}    
    elif WebBrowserSelector == 3:   
        driver = webdriver.Edge(executable_path=r'./BrowserDrivers/msedgedriver.exe')   # import browser firefox}    

    driver.get(config["baseURL"])   # access the url
    # Yêu cầu User phải đăng nhập qua AD từ trước rồi. Như vậy crawler này sẽ pass qua luôn
    # mà không cần username/password nữa. 
    # Login done.

    # Mở link Homepage của couse 
    # Ví dụ https://exam.hust.edu.vn/course/view.php?id=885
    #driver.get(BASE_URL + '/course/view.php?id={courseid}'.format(courseid=CourseID))
    
    # Vòng lặp nhảy qua tất cả các trang chứa thông tin user
    line = 0
    for student in input_list:
        line = line + 1
        print(f'{line}/{len(input_list)}', end='')
        if hasattr(student,"stt"):
           print(student.stt, end='')
        if hasattr(student,"name"):
           print(student.name, end='')           
        if hasattr(student,"email"):
           print(student.email, end='')           
        print('')           

        
        # Tìm tới bảng chứa các PTID, vào trong tbody
        while (True):
            try:
                # Mở nội dung của group cần bổ sung sinh viên
                # Ví dụ 'https://exam.hust.edu.vn/group/members.php?group=6810' 
                if (config['reloadURL']):
                    driver.get(config["baseURL"])
                #search_box = driver.find_elements(By.XPATH, '//*[@id="addselect_clearbutton"]')
                # Lần lượt điền thông tin vào từng hạng mục
                for victim in config["outputformat"]:
                    xpath_id = victim["id"]
                    content = victim["fillin"]
                    type = victim["type"]
                    
                    
                    
                    if (xpath_id == ""):  # 1 phần tử output là giá trị cần điền vào web
                        handler = ActionChains(driver) 
                    else:
                        xpath=f"//*[@id='{xpath_id}']"
                        xpath=f"//*[contains(@id, '{xpath_id}')]"
                        handler = driver.find_element(By.XPATH, xpath)                        
                                            
                    if type == "field":
                        content = getattr(student, content)
                        print(f" - send key {content} ", end='')
                        handler.send_keys(content)
                    elif type == "control": # 1 phần tử output chỉ 1 kí tự điều khiển
                        print(f" - send key {content} ", end='')
                        ControlKey=0
                        if content[0]=='+':
                            ControlKey=Keys.SHIFT
                        if content[0]=='^':
                            ControlKey=Keys.CONTROL
                        if content[0]=='!':  
                            ControlKey=Keys.ALT
                        if ControlKey != 0:
                            handler.key_down(ControlKey);
                            content=content[1::]    
                        
                        if (content == u'{ENTER}'):
                            handler.send_keys(Keys.ENTER)
                        elif (content == u'{TAB}'):
                            handler.send_keys(Keys.TAB)
                        elif (content == u'{LEFT}'):
                            handler.send_keys(Keys.LEFT)
                        elif (content == u'{RIGHT}'):
                            handler.send_keys(Keys.RIGHT)
                        else:
                            handler.send_keys(content)
                            
                        try:
                            handler.perform()
                        except:
                            print(f"Không được dùng phím điều khiển với control {xpath_id}. Gợi ý để id=""")
                        if ControlKey != 0:    
                            handler.key_up(ControlKey);
                            handler.perform() 
                    print(f"...sleeping in {victim['sleep']}")
                    sleep(victim["sleep"])
                break;                                    
            except selenium.common.exceptions.NoSuchElementException as ex:
                print ("Không tim thấy đối tượng. Thêm 3 giây để thử.")
                sleep(3)
                pass
            except Exception as ex:
                print(ex)                
                break
                    
    #Kêt thúc vòng lặp đọc tất cả các sinh viên

class Student:
    mssv : string
    name : string
    email: string
    grade: string
    stt:string
    birthday: string

config = dict()
    
def ReadConfig():
    global config
    config = json.load(open('config.json', encoding="utf-8"))
    print(config)
        
def ReadImportData(): 
    import csv
    
    # Create stock-list to contain the stock-object
    # Each item contains infomation of 1 stock like code, prices
    stock_list = []

    with open('./diem.txt',  encoding="utf-8") as csvfile:
        data = csv.reader(csvfile, delimiter = '\t')
        for row in data:
            record = Student()
            col_index = 0
            column_num = len(row)
            for col_index in range(column_num):
                if config['inputformat'][col_index] == "mssv":
                    record.mssv = row[col_index]
                if config['inputformat'][col_index]  == "name":
                    record.name = row[col_index]
                if config['inputformat'][col_index]  == "email":
                    record.email = row[col_index]
                if config['inputformat'][col_index]  == "grade":
                    record.grade = row[col_index]      
                if config['inputformat'][col_index]  == "stt":
                    record.stt = row[col_index]      
                if config['inputformat'][col_index]  == "birthday":
                    record.birthday = row[col_index]                          
            stock_list.append(record)        
    return stock_list

# main

#Đọc thông số cấu hình
ReadConfig()

#Đọc nội dung đầu vào
input_list = ReadImportData()


# call crawl_stock_data function to start crawling data from stock sections
AddUserToGroup()

print ("Done. ")
if config['keepaliveaftercompleted']:
    text=''
    while (text != "exit"):
        text = input("Gõ từ 'exit' để kết thúc chương trình ...")  # Python 3
# close web browser
driver.close()
