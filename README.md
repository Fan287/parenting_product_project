# Parenting Product Insight Study
This project aims to gain insights into parenting products by web scraping data from the online shopping platform, HKTVmall, and Petit Tippi.
The goal is to collect basic product information(product name,price,origin etc.) from these platforms and analyze customer comments to understand customer preferences. 
However, please note that the demo for Petit Tippi's website is not uploaded due to recent changes on their website.

## Project's structure
1. Use VS Code to perform web scraping and save the data as CSV files.
2. Combine all the CSV files into one.
3. Import the merged CSV file into an SQL database.
4. Perform analysis in SQL.

## Explain code in hktv_demo.py
Here will explain the structure of code and some reasons of the design. The code is divided into 7 parts.
### Part 1: import and install the required libraries
The libraries needed for the script are specified in the "requirements.txt" file.
### Part 2: land to the target page and category (setting needed)
1.  It starts by setting the starting URL to the parenting products category on HKTVmall.
2.  It then attempts to close any ads that may appear on the page. If an ad is found, it locates the close button and clicks on it to close the ad. If no ad is found, it prints a message indicating that there is no ad.
   ```python
   try:
    close_ad_button = driver.find_element(By.XPATH, '//i[@class="btnCloseLarge"]')
    time.sleep(2)
    close_ad_button.click()
    print('ad closed')
   except:
    print('no ad')
  ```
3. HKTVmall's parenting products category has 17 subcategories, and the code allows the user to choose which category to scrape. The user needs to specify the category number (0-16) in the code to indicate the desired category. The code then retrieves the URL for the selected category and navigates to that page. 
   ```python
   # decide which category to scrap
    # 0=嬰兒奶粉 1=尿片/學習褲 2=身體清潔/淋浴/護理 3=衣物/奶樽/清潔用品 4=奶樽/餐具/哺育用品
    # 5=母乳餵補用品 6=嬰兒醫藥/護膚 7=嬰兒食物/飲品/保健品 8=嬰兒玩具教育
    # 9=嬰兒外出用品 10=嬰兒床上用品 11=嬰兒傢俱/安全用品 12=嬰兒服飾/髮飾/帽
    # 13=成長紀錄/禮短套裝 14=孕婦清潔護理 15=產前/產後/專區
    target_cate_link = cate_links[0] # put the number into the slice to decide the scrapped category
    driver.get(target_cate_link)
    time.sleep(5)
    ```
### Part 3: sort the top sales' product
This project selects only the top-selling product from each category, so it requires sorting the products based on their sales.
```python
sales_volume = driver.find_element(By.XPATH, '//option[@value="sales-volume-desc"]')
time.sleep(2)
sales_volume.click()
time.sleep(5)
```
### Part 4: Set up empty sets for data storage in scrap_result_page
Empty sets are created to store the scraped data and generate a dataframe.

### Part 5: Set up three def functions for execution part
1. Function for price cleansing: The price format in HKTVmall can be complicated, as some vendors may not fill in the price field with numbers or may include multiple prices.
```python
def price_cleasing(a_string):
    last_split_string = a_string.split('$')[-1]
    numbers = re.findall(r'\d+', last_split_string)
    if len(numbers)==1:
        if int(numbers) < 10: # some label is about 'No.1 sale', which is not a price
            pass
        else:
            return numbers[0]
    elif len(numbers)==2: # some price are seperated with , or .
        return '.'.join(numbers)
    else:
        return ''.join(numbers[-3:-1]) + '.' + numbers[-1] # some price are seperated with , and . 
```
2. Function for scraping the data from result pages: This function utilizes a for loop to scrape the data of each product. The price_cleansing function will also be used in this part to clean the price before appending it to the empty sets.
   for example:
   ```python
   try: # find original price
        ori_price_sign = product_info.find_element(By.CLASS_NAME, 'promotional').text
        original_price.append(price_cleasing(ori_price_sign))
    except: 
        original_price.append('')
   ```
3. Function for scraping the data from individual product pages: This function is responsible for scraping the origin and comments of each product. In order to understand why some customers like or dislike the product, we specifically choose the 5-star (the best) and 1-star (the worst) comments.
  scrap the 5 star comments:
  ```python
  try:
      star_5_tap = driver.find_element(By.XPATH, "//div[@data-tabname='star5']")
      star_5_tap.click()
  except:
      print('fail to click 5 star tap')
  ```
   scrap the 1 star comments:
  ```python
  try:
      driver.find_element(By.XPATH, "//div[@data-tabname='star1']").click()
      time.sleep(1)
  except:
      print('fail to click 1 star tap')
  ```
## Usage
To use this project, follow these steps:
Install the required dependencies by running pip install -r requirements.txt.
Run the web scraping script to collect data from HKTVmall.
Analyze the collected data to gain insights into parenting products and customer preferences.

## Analysis the data between 9-15, Aug, 2023
### origins
Top 6 Origin:
![top origin](https://github.com/Fan287/parenting_product_project/assets/148685693/77bd8744-4263-4b0f-acb6-71efb09a4972)
Best sales of top 6 origin:
![top 3 origin   product](https://github.com/Fan287/parenting_product_project/assets/148685693/d2234c47-38d6-4f35-ae3b-e4385c7c7d23)
![top 4-6 origin   product](https://github.com/Fan287/parenting_product_project/assets/148685693/7ba88c31-e9b4-4623-b656-0f7621c100f6)

### Vendor
top 10 vendeors:
![top_vendor](https://github.com/Fan287/parenting_product_project/assets/148685693/9c80f1f4-0fe8-457a-b309-bb0143e61895)




