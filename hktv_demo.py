# Part 1: required libraries
import time
from datetime import date
from datetime import datetime
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import re
from hktv_database_git import connect, insertDF, create_table

driver = webdriver.Chrome()

# -------------------------------------------------------------------------------------------
# Part 2: set up empty set for data storage in scrap_result_page
    # must put before def scrap_result_page
product_name = []
package = []
sales = []
rating = []
review_number = []
original_price = []
selling_price = []
vendor_name = []
origin = []
star5_comment = []
star1_comment = []

# -------------------------------------------------------------------------------------------
# Part 3: set up three def function for execution part
    # def for price_cleasing, used in def 'scrap_result_page' below
def price_cleasing(a_string):
    last_split_string = a_string.split('$')[-1]
    numbers = re.findall(r'\d+', last_split_string)
    if len(numbers)==1:
        if int(numbers) < 10: # some label are about 'No.1 sale'
            pass
        else:
            return numbers[0]
    elif len(numbers)==2: # some label are 100.90, then re will seperate them into '100', '00'
        return '.'.join(numbers)
    else:
        return ''.join(numbers[-3:-1]) + '.' + numbers[-1] # some label are 1,000.90, then re will seperate them into '1', '100', '00'

    # def for scrap data in result page
def scrap_result_page(product_list):
    for product_info in product_list:
        try: # find the product name
            product_name.append(product_info.find_element(By.CLASS_NAME, 'brand-product-name').text)
        except: 
            product_name.append(None)

        try: # find the package
            package.append(product_info.find_element(By.CLASS_NAME, 'packing-spec').text)
        except: 
            package.append(None)

        try: # find the sales
            sales_with_word = product_info.find_element(By.CLASS_NAME, 'salesNumber-container').text
            sales.append(int(sales_with_word.split(' ')[-1].replace('+','').replace(',',''))) # sales numbers' format '已售出 1,000+'
        except: 
            sales.append(None)

        try: # find the rating
            rating.append(float(product_info.find_element(By.CLASS_NAME, 'star_container').get_attribute('data-rating')))
        except: 
            rating.append(None)

        try: # find the review number
            review_number.append(float(product_info.find_element(By.CLASS_NAME, 'review-number').text.replace("(", "").replace(")", "")))
        except: 
            review_number.append(None)

        try: # find original price
            ori_price_sign = product_info.find_element(By.CLASS_NAME, 'promotional').text
            original_price.append(float(price_cleasing(ori_price_sign))) # apply the defined def
        except: 
            original_price.append(None)

        try: # find price
            selling_price_sign = product_info.find_element(By.CLASS_NAME, 'price').text
            selling_price.append(float(price_cleasing(selling_price_sign))) # apply the defined def
        except: 
            selling_price.append(None)

        try: # find the vendor name
            vendor_name.append(product_info.find_element(By.CLASS_NAME, 'store-name-label').text)
        except: 
            vendor_name.append(None)

    # def for scrap data in individual product page
def single_product_page(product_links):
    # open a tap to run 60 individual product page
    driver.execute_script("window.open('about:blank', 'new_window')")
        # switch the control to the newly opened tap
    driver.switch_to.window("new_window")
    for individual_link in product_links:
        driver.get(individual_link)
        time.sleep(1)

        # close the ad before scrapping
        try:
            close_ad_button = driver.find_element(By.XPATH, '//i[@class="btnCloseLarge"]')
            time.sleep(0.5)
            close_ad_button.click()
            print('ad closed')
        except:
            pass

        # find the origin
        try: 
            # first [1] = second bag, second [1] = 荷蘭 (產地 荷蘭)
            origin_location = driver.find_elements(By.XPATH, '//tr[@class="productPackingSpec"]')[-1]
            origin.append(origin_location.text.split(' ')[1])
        except:
            origin.append(None)
        time.sleep(1)

        # find the comment
            # 5 star comment
        try:            
            driver.find_element(By.XPATH, "//div[@data-tabname='star5']").click()
            time.sleep(1)

            tem_star5_comment = [] # for combining all 5 star comments
            five_star_comments = driver.find_elements(By.XPATH, '//div[@class="review-title"]')
            for five_star_comment in five_star_comments:
                tem_star5_comment.append(five_star_comment.text)
            star5_comment.append(tem_star5_comment)

        except:
            star5_comment.append(None)
            # print('fail to click 5 star tap')

            # 1 star comment
        try:
            driver.find_element(By.XPATH, "//div[@data-tabname='star1']").click()
            time.sleep(1)

            tem_star1_comment = [] # for combining all 1 star comments
            one_star_comments = driver.find_elements(By.XPATH, '//div[@class="review-title"]')
            for one_star_comment in one_star_comments:
                tem_star1_comment.append(one_star_comment.text)
            star1_comment.append(tem_star1_comment)
        except:
            star1_comment.append(None)
            # print('fail to click 1 star tap')

        
    # close the tap after runing 60 individual product pages
    driver.close()

    # detect the category for each products and files' name
def category_name():
    if cate_num+start_cate_num == 0:
        return 'powder'
    elif cate_num+start_cate_num == 1:
        return 'diaper'
    elif cate_num+start_cate_num == 2:
        return 'clean'
    elif cate_num+start_cate_num in [3,4]:
        return 'utensil'
    elif cate_num+start_cate_num in [5,14,15]:
        return 'mama'
    elif cate_num+start_cate_num in [6,12]:
        return 'other'
    elif cate_num+start_cate_num == 7:
        return 'food'
    elif cate_num+start_cate_num == 8:
        return 'toy'
    elif cate_num+start_cate_num == 9:
        return 'outdoor'
    elif cate_num+start_cate_num in [10,11]:
        return 'sleep'
    elif cate_num+start_cate_num == 13:
        return 'gift'

# -------------------------------------------------------------------------------------------
# Part 4: land to the target page and category (setting needed)
# starting page, parenting products
url = 'https://www.hktvmall.com/hktv/zh/mothernbaby'

# connect to the website
try:
    driver.get(url)
except:
    print('URL not found')
    exit()
time.sleep(2)

# close the ad, if any
try:
    close_ad_button = driver.find_element(By.XPATH, '//i[@class="btnCloseLarge"]')
    time.sleep(2)
    close_ad_button.click()
    print('ad closed')
except:
    print('no ad')

# find out categories' links
upper_lvs = driver.find_elements(By.XPATH, '//div[@class="subnav"]/ul/li')[1:17] # 17 categories but eliminate the first ad and final category 'insurance'
cate_links = []
for link_location in upper_lvs:
    cate_links.append(link_location.find_element(By.XPATH, './a[@class="link"]').get_attribute('href'))
    #  test cate_links
    # print(cate_links[5])

# Part 5: execution steps: scrap all selected categories' data
    # decide which category to scrap (setting needed, important!!!)
        # 0=嬰兒奶粉 1=尿片/學習褲 2=身體清潔/淋浴/護理 3=衣物/奶樽/清潔用品 4=奶樽/餐具/哺育用品
        # 5=母乳餵補用品 6=嬰兒醫藥/護膚 7=嬰兒食物/飲品/保健品 8=嬰兒玩具教育
        # 9=嬰兒外出用品 10=嬰兒床上用品 11=嬰兒傢俱/安全用品 12=嬰兒服飾/髮飾/帽
        # 13=成長紀錄/禮短套裝 14=孕婦清潔護理 15=產前/產後/專區
    # selected_cate = 15 # put the desired category's number into the slicing
start_cate_num = 0
end_cate_num = None
for cate_num, cate in enumerate(cate_links[start_cate_num:end_cate_num]):
    driver.get(cate)
    # for checking
    print(f'The target category link:{cate}')
    time.sleep(5)

# -------------------------------------------------------------------------------------------
# Part 5.1: sort the top sales' product

    # target at the top sales
    sales_volume = driver.find_element(By.XPATH, '//option[@value="sales-volume-desc"]')
    time.sleep(2)
    sales_volume.click()
    time.sleep(5)
# -------------------------------------------------------------------------------------------
# Part 5.2: scrap result and individual product page
    for times in range(1): # need 2 result pages' data, should put 2
        # scrap result pages' data
        product_infos = driver.find_elements(By.XPATH, '//div[@class="info-wrapper"]')
        # apply def
        scrap_result_page(product_infos)

        # scrap individual product's page
        upper_lvs = driver.find_elements(By.XPATH, '//span[@class="product-brief-wrapper"]')
                    # driver.find_elements(By.XPATH, '//div[@class="product-brief"]')
        print(f'The upper level has {len(upper_lvs)} bags.')
        product_links = [] # save 60 links
        for upper_lv in upper_lvs:
            target_link = upper_lv.find_elements(By.TAG_NAME, "a")[-1].get_attribute('href') # [-1] = the link stored in the last bag
            product_links.append(target_link)
                #print(f'it has {len(product_links)} links.') # for checking
    
            # apply def, running on the newly open page
        single_product_page(product_links) # the def will close the page after completion

            # switch the control to the old page
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)

        # go to the next result page
        try:
            next_button = driver.find_element(By.XPATH, '//a[@class="next-btn"]')
            try:  # close the small ad on the right hand side
                driver.find_element(By.XPATH, '//i[@class="closeBtn"]').click()
            except:
                pass
            time.sleep(5)
            next_button.click()
            time.sleep(5)  # Add a delay to allow the next page to load
        except:
            # break  # Exit the loop if there is no "Next" button
            print('fail next page')
            break
        time.sleep(2)


# -------------------------------------------------------------------------------------------
    # Part 5.3: store data into data frame and csv file
        # add some labels to the data
    website = []
    product_cate = []
    today = []
    category = category_name() # don't want to loop the def too many times so let it do once only
    for i in range(len(product_name)):
        website.append('hktvmall')
        product_cate.append(category)
        today.append(date.today())


        # simplify the category and generate the cate name for file name 
            # 0=嬰兒奶粉 1=尿片/學習褲 2=身體清潔/淋浴/護理 3=衣物/奶樽/清潔用品 4=奶樽/餐具/哺育用品
            # 5=母乳餵補用品 6=嬰兒醫藥/護膚 7=嬰兒食物/飲品/保健品 8=嬰兒玩具教育
            # 9=嬰兒外出用品 10=嬰兒床上用品 11=嬰兒傢俱/安全用品 12=嬰兒服飾/髮飾/帽
            # 13=成長紀錄/禮短套裝 14=孕婦清潔護理 15=產前/產後/專區      

        # checking the length of each column (not necessary)
    '''
    print(len(website))
    print(len(product_cate))
    print(len(product_name))
    print(len(vendor_name))
    print(len(sales))
    print(len(package))
    print(len(selling_price))
    print(len(original_price))
    print(len(rating))
    print(len(review_number))
    print(len(origin))
    print(len(star5_comment))
    print(len(star1_comment))
    print(len(today))
    '''

        # Create DataFrame
    df = pd.DataFrame({
        'website': website,
        'product_cate': product_cate,
        'product_name': product_name,
        'vendor_name': vendor_name,
        'sales': sales,
        'package': package,
        'selling_price': selling_price,
        'original_price': original_price,
        'rating': rating,
        'review_number': review_number,  
        'origin':origin,
        'star5_comment':star5_comment,
        'star1_comment':star1_comment,       
        'date': today
    })
        # print(df) # for checking


        # store dataframe to csv file connect and write to postgresql(option 1/2)       
    time.sleep(3)
    connection = connect()
    resp = insertDF(connection, df, 'parenting_product')

        # store dataframe to csv file (option 2/2)
    '''
    folder_path =  r'.\hktvmall_csv\\'
    file_name = f'hktvmall_{category}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv' #current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path_name = folder_path + file_name
    df.to_csv(path_name, index=False, encoding='utf-8_sig')
    '''

    # reset the column for next loop
    website = []
    product_cate = []
    product_name = []
    package = []
    sales = []
    rating = []
    review_number = []
    original_price = []
    selling_price = []
    vendor_name = []
    origin = []
    star5_comment = []
    star1_comment = []
    today = []
    
    print(f'The {cate_num+start_cate_num} - {category} category is ended.')
    time.sleep(5)
