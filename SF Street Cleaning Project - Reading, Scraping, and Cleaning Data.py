
# coding: utf-8

# # Reading, Scraping, and Cleaning Our Data

# This notebook shows our process of data munging in more detail.

# ## Packages

# In[11]:

# Loading in data:
import numpy as np
import pandas as pd

# Parsing:
import requests
import requests_cache
import lxml
from bs4 import BeautifulSoup
import bs4
import re


# # I. Reading in the Data - Our Primary Data Source

# The following cell loads are data through read_csv and takes a long time to run, about 15 minutes on our devices. We use street.h5 to import the data faster after importing the csv once here.

# In[ ]:

# Should only run this cell the first time running this notebook:

# Convert these to datetimes
parseDates = ["Opened", "Closed", "Updated"] 
street_csv = pd.read_csv("Street_and_Sidewalk_Cleaning.csv", 
                         #nrows = 100000,
                         parse_dates=parseDates)

# Export h5 for faster reading in later
street.to_hdf('street.h5','table',append=False) 


# The next cell loads the h5 and displays the first few rows of our primary data source. All of the variables can be seen here.

# In[12]:

# Read h5: Run every second time and on of running this notebook
street_hdf = pd.HDFStore('street.h5')
street = street_hdf.select('/table')
street.head()


# ## Cleaning the data

# To keep counts of requests consistent over the months and days, we remove years with incomplete data since our original data set starts in November 2008 and ends in January 2017.  

# In[13]:

street = street.loc[street['Opened'].dt.year != 2008]
street = street.loc[street['Opened'].dt.year != 2017]
street = street.sort_values("Opened") # Re-sort data in date order
street = street.reset_index() # Re-set the indexing
street = street.drop('index', 1) # Get rid of old index column 


# Some neighborhood names need to be changed to allow merging with other data sources later and to match our shape files.   

# In[14]:

street.ix[street.Neighborhood == "None", "Neighborhood"] = np.nan
street.ix[street.Neighborhood == "Ocean View", "Neighborhood"] = "Oceanview"
street.ix[street.Neighborhood == "Downtown/Civic Center", "Neighborhood"] = "Civic Center"
street.ix[street.Neighborhood == "St. Mary's Park", "Neighborhood"] = "St. Marys Park"
street.ix[street.Neighborhood == "Presidio", "Neighborhood"] = "Presidio Heights"


# Next we create a month column for future plots and data merging. 

# In[15]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# A look of the first few rows of our cleaned data:

# In[16]:

street.head()


# We then exported the cleaned data set for use in the analysis notebook.

# In[17]:

# Export h5 for faster reading in later
# Warning: the resulting file is about 600 MB
street.to_hdf('street.h5','table',append=False)


# # II. Scraping - Demographic Data

# Here we scrape demographic data from the source talked about on our website.

# In[18]:

requests_cache.install_cache('sf_cache') # So we don't make too many requests to the website


# Grab the html from the website:

# In[19]:

url = "http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html"
response = requests.get(url)
response.raise_for_status


# We first parse using Beautiful Soup and lxml. Then we grab the section with  what information we want for each neighborhood and store it as a list in neighborhood_divs. 

# In[20]:

neighborhoods_bs = BeautifulSoup(response.text, 'lxml')
neighborhood_names = neighborhoods_bs.find_all(name = "span", attrs={'class':'street-name'})
neighborhood_names = [name.text.replace("-", " ") for name in neighborhood_names]
neighborhood_divs = neighborhoods_bs.body.find_all(name = "div", attrs={'class':'neighborhood'})


# Then, parsing the html for each neighborhood was not as simple as we thought. The format the website used involved a lot of navigable strings. The title of each section like "Area" and "Population" was not nested nicely. The value for the Area was stored as a navigable string as a sibling to Area instead of a child, so the parsing process got a bit more complicated. The function catch() was created to handle three different cases of how far the sibling of information was from the title. It is called catch because if the case fails, then the value should be NA, so the function makes use of try and except. The function also deals with converting the strings to numbers and removing any commas and dollar signs than get in the way.

# In[21]:

def catch(line, number, simple, c = "h", complicated = False):
    """
    This function was made to catch the cases when scraping where we want NAs. If grabbing what we want from line fails, 
    then NA is returned. If number is True, then the value we are grabbing needs to be converted from a string to a number. 
    If simple is True, then the value we are scraping is right there, otherwise we need to search for a particular class which
    is the c input variable. Complicated is for the last column we are scraping where finding that class is a bit more complicated.
    """
    try:
        # Value should be converted to a number 
        if number == True:
            # Case 1: value in the next sibling
            if simple == True:
                return float(line[0].next_sibling.replace(",", "").replace("$", "")) 
            
            else: 
                # Case 2: When the website had a horizontal bar plot with two bars. c = h is the first bar and c = a is the second. 
                if complicated == False:
                    return float(line[0].next_sibling.next_sibling.find_all(class_ = c)[0].next_sibling.replace(",", "").replace(" years", "").replace("$", ""))
                # Case 3: Bar plot but with an extra line before the plot
                else: 
                    return float(line[0].find_all_next(class_ = c)[0].next_sibling.replace(",", "").replace(" years", "").replace("$", ""))

        else:
            return line[0].next_sibling
    except:
        return np.nan # If the line failed, then no value and want NA


# We then created a demographic data frame with all the values we want to scrape stored as columns. For each one, one of the three cases is specified to the catch function and catch is also passed the find_all result of searching for the variable we want. Then the first few rows of the data frame are displayed. 

# In[22]:

demographic = pd.DataFrame({
        'Neighborhood': neighborhood_names, 
        'AreaSqMi': [catch(neigh.find_all(name = "b", string = "Area:"), True, True) for neigh in neighborhood_divs] ,
        'Population': [catch(neigh.find_all(name = "b", string = "Population:"), True, True) for neigh in neighborhood_divs], 
        'PeoplePerSqMi': [catch(neigh.find_all(name = "b", string = "Population density:"), True, False) for neigh in neighborhood_divs],
        'MedHouseholdIncome': [catch(neigh.find_all(name = "b", string = "Median household income in 2015: "), True, False) for neigh in neighborhood_divs],
        'MedRent': [catch(neigh.find_all(name = "b", string = "Median rent in in 2015: "), True, False) for neigh in neighborhood_divs],
        'Males': [catch(neigh.find_all(name = "b", string = "Male vs Females"), True, False) for neigh in neighborhood_divs],
        'Females': [catch(neigh.find_all(name = "b", string = "Male vs Females"), True, False, "a") for neigh in neighborhood_divs], 
        'MedAgeM': [catch(neigh.find_all(name = "b", string = "Median age"), True, False) for neigh in neighborhood_divs],
        'MedAgeF': [catch(neigh.find_all(name = "b", string = "Median age"), True, False, "a") for neigh in neighborhood_divs],
        'HousePrice': [catch(neigh.find_all(name = "b", string = "Average estimated value of detached houses in 2015 "), True, False, complicated = True) for neigh in neighborhood_divs],
})

demographic.head()


# So now we have lots of demographic data on gender, age, area, rent, income, population, and so on. All of this data is from 2015. Next, the neighborhood names from this data need to be cleaned to match up with our primary data set. The CombineNeighs() function was created to take two rows of the demographic data and combine them, either taking the average of the two columns (like median age for example) or sums the columns (like population for example). This is necessary in a few cases seen in the next cell. One example is where the demographic data had "Bayview District" and "Bayview Heights" while our primary street data only had "Bayview."

# In[23]:

def CombineNeighs(name1, name2, newName, df):
    """
    This function takes in two neighborhood names of the demographic dataframe, combines them, 
    and changes the name.
    """
    # Grab the two rows we want:
    one = df.ix[df.Neighborhood == name1]
    two = df.ix[df.Neighborhood == name2]
    # Sum or average all the columns:
    one.loc[one.index, "AreaSqMi"] = (one['AreaSqMi'].values[0] + two['AreaSqMi'].values[0]) / 2
    one.loc[one.index, 'Females'] = one['Females'].values[0] + two['Females'].values[0]
    one.loc[one.index, 'HousePrice'] = (one['HousePrice'].values[0] + two['HousePrice'].values[0]) / 2
    one.loc[one.index, 'Males'] = one['Males'].values[0] + two['Males'].values[0]
    one.loc[one.index, 'MedAgeF'] = (one['MedAgeF'].values[0] + two['MedAgeF'].values[0]) / 2
    one.loc[one.index, 'MedAgeM'] = (one['MedAgeM'].values[0] + two['MedAgeM'].values[0]) / 2
    one.loc[one.index, 'MedHouseholdIncome'] = (one['MedHouseholdIncome'].values[0] + two['MedHouseholdIncome'].values[0]) / 2
    one.loc[one.index, 'PeoplePerSqMi'] = (one['PeoplePerSqMi'].values[0] + two['PeoplePerSqMi'].values[0]) / 2
    one.loc[one.index, 'Population'] = one['Population'].values[0] + two['Population'].values[0]   
    one.loc[one.index, 'Neighborhood'] = newName
    # Drop the old rows:
    df = df.drop(one.index)
    df = df.drop(two.index)
    # Add the new row:
    df = df.append(one)
    return df


# In[24]:

# Clean up neighborhood names: make the demographic names match our data and shapefiles
demographic = CombineNeighs("Bayview District", "Bayview Heights", "Bayview", demographic)
demographic = CombineNeighs("Bernal Heights North", "Bernal Heights Park", "Bernal Heights1", demographic)
demographic = CombineNeighs("Bernal Heights South", "Bernal Heights", "Bernal Heights2", demographic)
demographic = CombineNeighs("Bernal Heights1", "Bernal Heights2", "Bernal Heights", demographic)
demographic = CombineNeighs("Balboa Park", "Balboa Terrace", "Balboa Terrace", demographic)
demographic = CombineNeighs("Aquatic Park", "Fort Mason", 'Aquatic Park / Ft. Mason', demographic)
demographic = CombineNeighs("Downtown", "Union Square", 'Downtown / Union Square', demographic)
demographic = CombineNeighs("Financial District", "Financial District South", "Financial District", demographic)


# The next cleaning section includes cases where the name just needs to be changed.

# In[25]:

demographic.loc[demographic.Neighborhood == "Buena Vista Park", "Neighborhood"] = "Buena Vista"
demographic.loc[demographic.Neighborhood == "Cayuga Terrace", "Neighborhood"] = "Cayuga"
demographic.loc[demographic.Neighborhood == "Ingleside Terrace", "Neighborhood"] = "Ingleside Terraces"
demographic.loc[demographic.Neighborhood == "Laurel Heights", "Neighborhood"] = 'Laurel Heights / Jordan Park'
demographic.loc[demographic.Neighborhood == "Lake Shore", "Neighborhood"] = 'Lakeshore'
demographic.loc[demographic.Neighborhood == "South Of Market", "Neighborhood"] = 'South of Market'
demographic.loc[demographic.Neighborhood == "North Waterfront", "Neighborhood"] = 'Northern Waterfront'
demographic.loc[demographic.Neighborhood == "St Marys Square", "Neighborhood"] = "St. Marys Park"
demographic.loc[demographic.Neighborhood == "Saint Francis Wood", "Neighborhood"] = "St. Francis Wood"
demographic.loc[demographic.Neighborhood == "Sea Cliff", "Neighborhood"] = "Seacliff"
demographic.loc[demographic.Neighborhood == "Parnassus", "Neighborhood"] = "Parnassus Heights"
demographic.loc[demographic.Neighborhood == "Park Merced", "Neighborhood"] = "Parkmerced"
demographic.loc[demographic.Neighborhood == "Mission District", "Neighborhood"] = "Mission"
demographic.loc[demographic.Neighborhood == "Marina District", "Neighborhood"] = "Marina"
demographic.loc[demographic.Neighborhood == "Mount Davidson Manor", "Neighborhood"] = "Mt. Davidson Manor"
demographic.loc[demographic.Neighborhood == "Lake", "Neighborhood"] = "Lake Street"


# Finally, the demographic information was exported for use in the analysis notebook.  

# In[26]:

# Export demographic here, then import in the other notebook and merge before plotting.  
demographic.to_csv("demographic.csv")


# --------

# # III. Scraping - Events and Festivals

# The dates and estimated attendance of the SF Pride parade were located in a table on the Wikipedia page.

# In[27]:

url_pride = "https://en.wikipedia.org/wiki/San_Francisco_Pride"
response = requests.get(url_pride)
response.raise_for_status

pride_bs = BeautifulSoup(response.text, 'lxml')

# Locate the right table
pride_table = pride_bs.find_all(name = "table", attrs={'class':'wikitable'})


# In[28]:

#type(pride_table[0])
# The table is the first element

rows = pride_table[0].find_all(name = "tr")

# The first row is the header
#print rows[0]
#for colname in rows[0].find_all(name = "th"):
#    print colname.text

# Determine the order of the columns
colnames = [colname.text for colname in rows[0].find_all(name = "th")]
print colnames


# In[29]:

# Extract the dates and attendance data from the appropriate columns
years = []
dates = []
attendance = []

for row in rows[1:]:
    cells = row.find_all(name = "td")
        
    years.append(cells[0].text)
    dates.append(cells[1].text)
    attendance.append(cells[4].text)
    
assert(len(years) == len(dates) == len(attendance))


# We could then create a data frame from the extracted data.  

# In[30]:

pride = pd.DataFrame.from_dict({"year": years,
                                "date": dates,
                                "attendance": attendance})

pride.year = pd.to_numeric(pride.year)

# Remove unused years
pride = pride[pride.year > 2007]

pride


# The dates and attendance estimates required parsing to get compatible types for later use.

# In[31]:

# Extract the start and end dates of the parade
startdates = [d[:-3] for d in pride.date]
enddates = [d[:4] + d[-2:] for d in pride.date]
startdatetimes = []
enddatetimes = []

for sdate, edate, year in zip(startdates, enddates, pride.year):
    startdatetimes.append(sdate + " " + str(year))
    enddatetimes.append(edate + " " + str(year))
    
pride["start_date"] = pd.to_datetime(startdatetimes)
pride["end_date"] = pd.to_datetime(enddatetimes)
#pride["datetimes"] = [pd.date_range(dt, periods=2) for dt in startdatetimes]
pride


# This function was used to parse the attendance strings and convert them to numeric data.

# In[32]:

def parse_attendance(attendance_str):
    """
    Parse the attendance strings in the table in the Wikipedia page for the Pride parade. 
    Returns a float or None if the string cannot be parsed.
    """
    
    if "million" in attendance_str.lower():
        # Multiply by 1000000 and remove the string "million"
        return float(attendance_str.split(" ")[0]) * 1000000
    
    else:
        return None

        
pride["attendance_num"] = [parse_attendance(x) for x in pride.attendance]
pride = pride.reset_index()
pride


# ### Outside Lands Music and Arts Festival

# The process of extracting the dates from the Wikipedia page for Outside Lands was more involved, because the data was less structured. Some of the dates were stored in heading tags, while others were in paragraphs.

# In[33]:

url_ol = "https://en.wikipedia.org/wiki/Outside_Lands_Music_and_Arts_Festival"
response = requests.get(url_ol)
response.raise_for_status

ol_bs = BeautifulSoup(response.text, 'lxml')


# Years are in h3
h3 = ol_bs.find_all(name = "h3")

ol = []

for h in h3:
    span = h.find_all(name = "span", attrs={"class":"mw-headline"})
    
    # If there is a span in the h3
    if span:
        year = span[0].text
        #print year 
        
        check_p = True
        
        #dates = []
        
        for sibling in h.find_next_siblings(limit=5):
            
            # Days are in h4 or p
            if sibling.name == "h4":
                #print "h4" + "\t" + sibling.text
                ol.append([year, sibling.text.replace(u"\u2013", "-").replace("[edit]","")])
                # If an h4 was found, stop looking for p
                check_p = False
                
            elif sibling.name == "p" and check_p:
                #print check_p
                #print "p" + "\t" + sibling.text
                ol.append([year, sibling.text.replace(u"\u2013", "-")])
                # Formatting for 2011+ uses the date in a p tag
                if "August" in sibling.text:
                    break
                
        #print "\n"
        #ol[str(year)] = dates

ol


# The extracted date ranges then had to be separated into individual dates.

# In[34]:

# Separate the date ranges and fix the formatting

ol2 = []
for year_and_date in ol:
    
    date_split = year_and_date[1].split()
    month = date_split[0]
    
    if len(date_split) > 2:
        # For format 'Friday August 22'
        # Keep the year
        year_and_date_new = [year_and_date[0]]
        # Discard the weekday
        year_and_date_new.extend(date_split[1:])
        ol2.append(year_and_date_new)
    else:
        # for format 'August 12-14'
        days = date_split[1].split("-")
        for day in days:
            # keep the year
            year_and_date_new = [year_and_date[0]]
            year_and_date_new.append(month)
            year_and_date_new.append(day)
            ol2.append(year_and_date_new)

ol2


# The dates could then be converted to a datetime for use with pandas.  

# In[35]:

ol_dates = pd.to_datetime([" ".join(date) for date in ol2])
ol_dates


# The dates were then exported for use in the analysis notebook. 

# In[36]:

ol_dates_df = pd.DataFrame({"Festival_Date": ol_dates})
ol_dates_df.to_csv("ol_dates.csv")


# ## Further Preparation for Pride Data

# For use in the analysis notebook, we calculated the number of requests in the surrounding neighborhoods on the days of the Pride parade.

# In[37]:


# Get all request from June
streetJune = street.loc[street["Opened"].dt.month == 6]
streetJune["DateOpened"] = streetJune["Opened"].dt.date # Yells at you

# Neighborhoods found on http://www.sfpride.org/parade/
prideNeighs = ["South of Market", "Tenderloin", "Financial District", "Downtown / Union Square", "Civic Center"]
# Get June requests in the right neighborhoods
streetJune = streetJune.loc[streetJune.Neighborhood.isin(prideNeighs)]

# Get the count of requests per day
JuneDayReqs = streetJune.groupby(by = "DateOpened").count().CaseID

# Get just the date 
pride["StartNoTime"] = pride["start_date"].dt.date 
pride["EndNoTime"] = pride["end_date"].dt.date 

# Get requests per day
JuneRequests = pd.DataFrame({"ReqCount": JuneDayReqs})
JuneRequests = JuneRequests.reset_index()

# If the parade took place on that day or not
JuneRequests["Pride"] = [row in pride.StartNoTime.values for row in JuneRequests.DateOpened]


# In[38]:

JuneRequests.head()


# We then determined the number of requests on the days of the parade for each year by combining the dates of the parade with the requests on each day in June from above.  

# In[39]:

# Merge with start and end dates
pride_merged_start = JuneRequests.merge(right = pride, right_on="StartNoTime", left_on="DateOpened")
pride_merged_end = JuneRequests.merge(right = pride, right_on="EndNoTime", left_on="DateOpened")

# Remove extraneous columns
cols = ["DateOpened", "ReqCount", "attendance_num", "StartNoTime", "EndNoTime"]
pride_merged_start = pride_merged_start[cols]
pride_merged_end = pride_merged_end[cols]

# Combine requests on both days into one df
pride_merged = pd.concat([pride_merged_start, pride_merged_end])
pride_merged["Year"] = [t.year for t in pride_merged.StartNoTime]

# Get sum of requests over the two days of the parade each year
req_year = pride_merged.groupby(by="Year").sum()
req_year.reset_index(inplace=True)


pride_merged_final = pride_merged_start

# Extract year
pride_merged_final["Year"] = [t.year for t in pride_merged_final.StartNoTime]

# Merge with requests per year 
pride_merged_final = pride_merged_final.merge(req_year, on = "Year")

# Remove extraneous columns
pride_merged_final = pride_merged_final[["DateOpened", 
                                         "ReqCount_y", 
                                         "attendance_num_x", 
                                         "Year",
                                         "StartNoTime", 
                                         "EndNoTime"]]
pride_merged_final


# In[40]:

pride_merged_final.to_csv("pride.csv")

