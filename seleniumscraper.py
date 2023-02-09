from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd

"""
    Requirements:
        Selenium
        Pandas
        Chrome web driver and compatible version of chrome:
            https://chromedriver.chromium.org/

    Warning:
        Site appears to limit search results to roughly 500 results (20 per page with 25 page limit)
        recommend adjusting search parameters to ensure all records are retrieved by selecting a short
        time period to pull records IE jan to feb 2020 then second search for feb to apr etc...
        
        
        Functionality can be added if required for large time period requests.

        DEFAULT OUTPUT FILE

        file_output_name = 'sales_data.csv'

        If this file exists in the same directory it will be overwritten
"""



'''
    function to get the first page and enter search terms
    this can be expanded by adding different search terms in the
    form used here.
        <var> = driver.find_element(By.ID, <id from html>)
        <var>.send_keys;click etc

    params:
        driver - selenium driver object to browse pages
        uri - uri of base search page
        inputs - dict containing input information 
            default is search dates to and from
    returns:
        none
    
'''

def get_first_page(driver, uri, inputs):
    #use the driver to get the first page
    driver.get(uri)
    #enter date from in the field after clearing it
    datefrom = driver.find_element(By.ID, 'MainContent_txtSalesFrom')
    for x in range(0,30):
        datefrom.send_keys(Keys.BACK_SPACE)
    datefrom.send_keys(inputs.get('datefrom'))
    #enter date to in the field after clearing it
    dateto = driver.find_element(By.ID, 'MainContent_txtSalesTo')
    for x in range(0,30):
        dateto.send_keys(Keys.BACK_SPACE)
    dateto.send_keys(inputs.get('dateto'))
    #check the residential box
    housing_type = driver.find_element(By.ID, "MainContent_cblModels_1")
    housing_type.click()
    #check the vacant box
    housing_type = driver.find_element(By.ID, "MainContent_cblModels_0")
    housing_type.click()
    #check the multi-family box
    housing_type = driver.find_element(By.ID, "MainContent_cblModels_2")
    housing_type.click()
    #check the condo
    housing_type = driver.find_element(By.ID, "MainContent_cblModels_3")
    housing_type.click()
    #check the commercial
    housing_type = driver.find_element(By.ID, "MainContent_cblModels_4")
    housing_type.click()
    #press the search button
    searchbtn = driver.find_element(By.CLASS_NAME, "searchTrigger")
    searchbtn.click()
'''
    function to write dataframes to a csv file
    params:
        df - pandas dataframe to write to file
        first - bool true if first frame, false if subsequent
    returns:
        none
'''
def writeout(df, first):
    #output file name to be written to
    #if file exists it will be overwritten
    file_output_name = 'sales_data.csv'
    #remove dummy data imported from table
    df.drop(20, axis=0, inplace=True)
    df.drop(21, axis=0, inplace=True)
    df.drop("Unnamed: 6", axis=1, inplace=True)
    df.drop("Unnamed: 7", axis=1, inplace=True)
    df.drop("Unnamed: 8", axis=1, inplace=True)
    df.drop("Unnamed: 9", axis=1, inplace=True)
    df.drop("Unnamed: 10", axis=1, inplace=True)
    #if this is the first entry, use the headers
    if first:
        df.to_csv(file_output_name, index=False)
    #entries 2 thru end use no headers
    else:
        df.to_csv(file_output_name, mode='a', header=False, index=False)

'''
    function to get each paged result
    params:
        driver - selenium driver object to browse pages
    returns:
        none
'''
def paginated_results(driver):
    #set loop sentinel
    running = True
    #set counter for paginated sections
    tripledot = 0
    #set final set var to false
    final_set = False
    #set finished to false
    finished = False
    #set first sheet var for dataframe writer
    first = True
    while running:
            #loop through every sheet to 10000
            for i in range(2,10000):

                #take a pandas DF of the table and write to csv
                table = pd.read_html(driver.page_source)
                writeout(table[2], first)
                first = False
                #break out of for loop if finished
                if finished:
                    break
                #get count of elipses links on page
                #pages with a 'next page' link will have two
                next_page = driver.find_elements(By.LINK_TEXT, '...')
                #if past the first page with one elipses
                #and this page has only one elipse this is the final set
                if tripledot > 0 and len(next_page)<2:
                    final_set = True
                #try to find the link with the next page number
                try:
                    next_page = driver.find_element(By.LINK_TEXT, str(i))
                    next_page.click()
                #if the number does not exist
                #click the second elipses on the page
                except Exception as e:
                    #if we go past the highest number on the page
                    #and this is the final set
                    #trip the sentinel, set finished to break the for loop
                    #and break this loop
                    if final_set:
                        running = False
                        finished = True
                        break
                    #if not the final set, hit the second elipses and 
                    #increment tripledot
                    else:
                        next_page = driver.find_elements(By.LINK_TEXT, '...')
                        next_page[len(next_page)-1].click()
                        tripledot += 1

if __name__ == "__main__":
    #base uri to requested site
    uri = "https://gis.vgsi.com/bloomingtonmn/Sales.aspx"
    #path to your chrome driver
    PATH = "C:\Windows\chromedriver.exe"
    #driver object used to browse pages
    driver = webdriver.Chrome(PATH)

    #dictionary with input fields
    #used in the get_first_page function to fill search form
    inputs = {}
    inputs['datefrom'] = "01/01/2020"
    inputs['dateto'] = "01/01/2023"

    #run the initial search, and subsequent pages
    #write paged tables out to a csv file
    get_first_page(driver, uri, inputs)
    paginated_results(driver)