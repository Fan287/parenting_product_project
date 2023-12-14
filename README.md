# Parenting Product Insight Study
This project aims to gain insights into parenting products by web scraping data from the online shopping platforms, HKTVmall and Petit Tippi.
The project collects basic information (product name, price, origin, etc.) of at least 100 products in each category (e.g., powder) from these platforms daily and analyzes customer comments to understand customer preferences. Please note that the demo for Petit Tippi's website is not uploaded due to recent changes on their website.

## Project's structure
1. Use VS Code to perform web scraping and save the data as CSV files.
2. Combine all the CSV files into one.
3. Import the merged CSV file into an SQL database.
4. Perform analysis in SQL.

## Explain code in hktv_demo.py
Here will explain the structure of code and some reasons of the design. The code is divided into 7 parts.
### Part 1: Import and install the required libraries
The script requires several libraries, which are specified in the "requirements.txt" file. The libraries are used for the following reasons:
1. time and datetime: used to work with dates and times. They are utilized to indicate the date of data scraping.
2. selenium: used for web scraping. It allows the script to interact with web browsers and retrieve data from web pages.
3. re: support for regular expressions. It is used for data cleansing, specifically for extracting and manipulating text patterns.
4. pandas: used to save the scraped data into a data frame format. 
### Part 2: Land to the target page and category (setting needed)
1.  It starts by setting the starting URL to the parenting products category on HKTVmall.
2.  It then attempts to close any ads that may appear on the page. If an ad is found, it locates the close button and clicks on it to close the ad.
   ```python
   try:
    close_ad_button = driver.find_element(By.XPATH, '//i[@class="btnCloseLarge"]')
    time.sleep(2)
    close_ad_button.click()
    print('ad closed')
   except:
    print('no ad')
  ```
3. HKTVmall's parenting products category has 16 subcategories, and the code allows the user to choose which category to scrape. ***The user needs to specify the category number (0-15) in the code to indicate the desired category.*** The code then retrieves the URL for the selected category and navigates to that page. 
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
### Part 3: Sort the top sales' product
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
3. Function for scraping the data from individual product pages: This function is responsible for scraping the origin and comments of each product. In order to understand why some customers  like or dislike the product, we specifically choose the 5-star (the best) and 1-star (the worst) comments.
  scrap the 5 star comments:
     ```python
     try:            
        driver.find_element(By.XPATH, "//div[@data-tabname='star5']").click()
        time.sleep(1)

        tem_star5_comment = [] # for combining all 5 star comments
        five_star_comments = driver.find_elements(By.XPATH, '//div[@class="review-title"]')
        for five_star_comment in five_star_comments:
            tem_star5_comment.append(five_star_comment.text)
        star5_comment.append(tem_star5_comment)

    except:
        star5_comment.append('')
        print('fail to click 5 star tap')
     ```
      scrap the 1 star comments:
     ```python
     try:
        driver.find_element(By.XPATH, "//div[@data-tabname='star1']").click()
        time.sleep(1)

        tem_star1_comment = [] # for combining all 1 star comments
        one_star_comments = driver.find_elements(By.XPATH, '//div[@class="review-title"]')
        for one_star_comment in one_star_comments:
            tem_star1_comment.append(one_star_comment.text)
        star1_comment.append(tem_star1_comment)
    except:
        star1_comment.append('')
        print('fail to click 1 star tap')
     ```
### Part 6: Execution steps
1. This section documents the process of execution and applies the defined functions mentioned earlier.
2. It is also responsible for scraping approximately 60 product links on a result page.
```python
# scrap individual product's page
 upper_lvs = driver.find_elements(By.XPATH, '//span[@class="product-brief-wrapper"]')
 product_links = [] # save about 60 links
 for upper_lv in upper_lvs:
     target_link = upper_lv.find_elements(By.TAG_NAME, "a")[-1].get_attribute('href') # [-1] = the link stored in the last bag
     product_links.append(target_link)
```
3. It requires running the loop twice to obtain more than 100 top-selling products instead of all of them. However, users can input higher numbers to scrape more products.
4. To indicate when each data was scraped, a timestamp will be generated for each data entry.

### Part 7: Store data into DataFrame and CSV file
1. The data will be stored in a DataFrame, and the CSV file will be named based on the date and time of its generation. This ensures that the file generated on the same day will not be replaced and allows for easy identification of different data files.
```python
file_name = f'hktvmall_powder_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
```
2. The uploaded CSV file 'hktvmall_powder_2023-12-14_18-22-17' is provided as an example to demonstrate the result after scraping. The file contains the scraped data from the HKTVmall website, specifically related to powder products.
## Usage
To use this project, follow these steps:
1. Install the required dependencies by running pip install -r requirements.txt.
2. Run the web scraping script to collect data from HKTVmall.
3. Analyze the collected data to gain insights into parenting products and customer preferences.

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




