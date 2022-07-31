'''
Created on 02 27, 2022

@author: Nguyen Duc Tien
'''

from math import nan
import numbers
import string
from time import sleep
from matplotlib import backend_bases
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import selenium.common.exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import validators
from datetime import datetime
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# create a url variable that is the website link that needs to crawl
#BASE_USL = 'https://exam.hust.edu.vn/group/members.php?group=6810'
#BASE_URL = 'https://exam.hust.edu.vn/user/index.php?id=135'

# Select Webbrowser
WebBrowserSelector=3

CONFIG_URLINLINE="_inline_"  
"""URL được nhúng ở dòng đầu tiên trong file dữ liệu, thay vì trong file cấu hình ./config.json"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def AddUserToGroup(baseURL, input_list):
    """
    This function takes as an input parameter the name of the stock item, and crawls the data of stock codes and prices. 
    Then put the data into the stock_list array

    Parameters:
    section (String): A input string describes the name of the stock section like ABC, DEF, GHI, ...

    Returns:
    this function doesn't return anything
    
    """
    global driver
    global backup_cookies
    global errorhandler
      
    # Yêu cầu User phải đăng nhập qua AD từ trước rồi. Như vậy crawler này sẽ pass qua luôn
    # mà không cần username/password nữa. 
    # Login done.
    
    # Vòng lặp nhảy qua tất cả các trang chứa thông tin user
    line = 0
    TotalCount = len(input_list)
    for student in input_list:
        line = line + 1
        
        #Hiển thị thông tin ra màn hình
        print(f'{line}/{TotalCount}', end='')    
        print(student.toString())           

        
        # Tìm tới bảng chứa các PTID, vào trong tbody
        while (True):
            try:
                # Mở nội dung của group cần bổ sung sinh viên
                # Ví dụ 'https://exam.hust.edu.vn/group/members.php?group=6810' 
                if (config['reloadURL']):   
                    driver.get(baseURL)
                    #if (backup_cookies != ""):
                    #    driver.add_cookie(backup_cookies[0])
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
                    elif type.find("validator")>=0: # nội dung phải chứa giá trị phù hợp   
                        victim_content=handler.get_attribute('innerHTML')
                        found = (victim_content.find(content) >= 0)
                        if (type == "validator_not" and found)   \
                                or (type == "validator_contain" and not found) :
                            print(f"Validate: fail {content}")
                            errorhandler.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} Validate fail : line {line} | data {student.toString()}\n")
                            errorhandler.flush()
                            continue                        
                        
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
    #backup_cookies = driver.get_cookies()
    errorhandler.close()
    pass
    #Kêt thúc vòng lặp đọc tất cả các sinh viên

class Student:
    mssv : string
    name : string
    email: string
    grade: string
    stt:string
    birthday: string

    def toString(this): 
        res = "";       
        if hasattr(this ,"mssv"):
           res = res + ' ' + this.mssv
        if hasattr(this,"stt"):
           res = res + ' ' + this.stt
        if hasattr(this,"name"):
           res = res + ' ' + this.name
        if hasattr(this ,"email"):
           res = res + ' ' + this.email
        return res
    
    

config = dict()
    
def ReadConfig():
    global config
    config = json.load(open('config.json', encoding="utf-8"))
    print(config)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def ReadImportData(startfromline: numbers = 1): 
    """Đọc thông tin cấu hình từ ./config.json
    
    Keyword arguments:
        startfromline: đọc file dữ liệu từ dòng nào? Mặc định =1, đọc từ dòng đầu tiên.
    Returns: [,]
        baseURL: đường link để nhập liệu
        array[]: danh sách dữ liệu cần nhập
        lastline: chỉ số dòng cuối cùng đọc dữ liệu. -1 nếu đã đọc hết
    """
    import csv
    myURL = ""
    
    # Create stock-list to contain the stock-object
    # Each item contains infomation of 1 stock like code, prices
    stock_list = []

    lineOfData = 0
    with open(config['inputfile'],  encoding="utf-8") as csvfile:
        data = csv.reader(csvfile, delimiter = '\t')
        for row in data:
            lineOfData = lineOfData + 1
            #Bỏ dòng trống
            if (len(row) == 0):
                continue
            #Bỏ qua một lượng dòng đầu tiên
            if (lineOfData < startfromline):
                continue            
            #Xử lý dòng tiêu đề trong trường hợp CONFIG_URLINLINE
            if config["baseURL"] == CONFIG_URLINLINE and validators.url(row[0]):
                # nếu là lần đầu thi thực hiện, nếu là lần 2 thì kết thúc để quá trình nhập liệu sau bắt đầu
                if myURL == "":
                    myURL = row[0]
                    continue
                else:
                    # cần giảm đi 1 dòng để lượt sau đọc lại URL
                    lineOfData = lineOfData -1 
                    break;
            #Phân tích dữ liệu
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
        if data.line_num == lineOfData:
            lineOfData = -1
    return [myURL,stock_list,lineOfData]

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
#Đọc thông số cấu hình
ReadConfig()

errorhandler = open(config["errorfile"], encoding="utf-8", mode="a")

if WebBrowserSelector == 1:
    driver = webdriver.Firefox()   # import browser firefox}    
elif WebBrowserSelector == 2:   
    driver = webdriver.Chrome(executable_path=r'./BrowserDrivers/chromedriver.exe')  # import browser firefox}    
elif WebBrowserSelector == 3:   
    driver = webdriver.Edge(executable_path=r'./BrowserDrivers/msedgedriver.exe')   # import browser firefox}    

#Đọc nội dung đầu vào
lastline = 0
while lastline >=0:
    [myBaseURL, input_list, lastline] = ReadImportData(lastline+1)
    # call crawl_stock_data function to start crawling data from stock sections
    AddUserToGroup(myBaseURL, input_list)

print ("Done. ")
if config['keepaliveaftercompleted']:
    text=''
    while (text != "exit"):
        text = input("Gõ từ 'exit' để kết thúc chương trình ...")  # Python 3
# close web browser
driver.close()
