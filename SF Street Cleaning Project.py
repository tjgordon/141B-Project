
# coding: utf-8

# # Libraries

# In[1]:

# Loading in data:
import pandas as pd
#import feather

# Plotting:
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
get_ipython().magic('matplotlib inline')

# Maps:
import matplotlib.cm
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
import geopandas as gpd
import shapely.geometry as geom
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
import folium

# Parsing:
import requests
import requests_cache
import lxml
from bs4 import BeautifulSoup
import bs4
import re

# Other
import statsmodels
import numpy as np

#plt.rcParams['figure.figsize'] = (12,12)


# # Reading in the Data

# In[ ]:

#%%timeit -r1 -n1 
# timeit args from: http://stackoverflow.com/questions/32565829/simple-way-to-measure-cell-execution-time-in-ipython-notebook 
# For some reason the varible isn't saved when using timeit

# Note: To just read in part add nrows =
parseDates = ["Opened", "Closed", "Updated"] # Convert these to datetimes
street_csv = pd.read_csv("Street_and_Sidewalk_Cleaning.csv", 
                         #nrows = 100000,
                         parse_dates=parseDates)


# In[ ]:

# Write feather
feather.write_dataframe(street_csv, 'street.feather')


# In[ ]:

# Write h5
street.to_hdf('street.h5','table',append=False)


# In[2]:

# Katherine run only this
#street2 = pd.read_hdf('street.h5')
street2 = pd.HDFStore('street.h5')
street = street2.select('/table')
street.head()


# In[3]:

# Read feather
#street = feather.read_dataframe('street.feather')


# In[4]:

# To use the csv version
# street = street_csv


# In[5]:

# Check if the binary version is equivalent
#all(street == street_csv)


# In[6]:

# TODO: Only use this subset for some analysis, since some major events are outside this range. 
street = street.loc[street['Opened'].dt.year != 2008]
street = street.loc[street['Opened'].dt.year != 2017]
street = street.sort_values("Opened")
street = street.reset_index()
street = street.drop('index', 1)

# Some cleaning:
street.ix[street.Neighborhood == "Ocean View", "Neighborhood"] = "Oceanview"
street.ix[street.Neighborhood == "None", "Neighborhood"] = np.nan
street.ix[street.Neighborhood == "Downtown/Civic Center", "Neighborhood"] = "Civic Center"
street.ix[street.Neighborhood == "St. Mary's Park", "Neighborhood"] = "St. Marys Park"
street.ix[street.Neighborhood == "Presidio", "Neighborhood"] = "Presidio Heights"

street.head()


# Some basic statistics on the dataset we are starting with:

# In[7]:

numRows = street.shape[0]
print "We are working with", numRows, "rows."
print "Our dates range from", street.loc[numRows - 1, "Opened"],"to", street.loc[0, "Opened"], "."


# # Plots

# In[8]:

#plt.figure(figsize=(2,100)) # Doesn't do much
theOrder = ["Voice In", "Open311", "Web Self Service", "Integrated Agency", "Twitter", "e-mail In", "Other Department"]
#sns.set(font_scale = 1.5)
sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Source", data = street, kind = "count", orient = "h", order = theOrder, aspect = 2)#, size = 10)
plt.title("How the Cleaning Request Was Made") 
plt.show()


# According to [the project's website](http://www.open311.org/learn/), Open311 allows people to report issues in public spaces to city officials through a [website](https://sf311.org/index.aspx?page=797) or [mobile app](https://www.sf311.org/mobile).  

# In[9]:

street.Neighborhood.value_counts


# In[10]:

# From: http://stackoverflow.com/questions/22391433/count-the-frequency-that-a-value-occurs-in-a-dataframe-column
counts = street.groupby('Neighborhood').count()


# We can get the total number of cases from CaseID
# unresolved cases by neighborhood

# In[11]:

counts = counts.sort_values(by = "CaseID",
                            ascending = False)
counts = counts.reset_index()
counts['UnclosedProp'] = (counts.Opened - counts.Closed) / counts.Opened
counts.head()


# In[12]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "CaseID", 
                    y = "Neighborhood",
                    data = counts.head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )#, size = 10)
ax.set_xlabels("Requests")
plt.title("Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# In[13]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "CaseID", 
                    y = "Neighborhood",
                    data = counts.tail(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )#, size = 10)
ax.set_xlabels("Requests")
plt.title("Requests by Neighborhood (Bottom 15 Neighborhoods)") 
plt.show()


# To get a sense of where these neighborhood fall on a map, we created this plot:

# In[14]:

fig, ax = plt.subplots(figsize=(10,20))

# Using counts: "Neighborhood" and "Opened"

myMap = Basemap(llcrnrlon=-122.523, llcrnrlat=37.7, urcrnrlon=-122.36, urcrnrlat=37.83, resolution="f",
    projection="merc") 
myMap.drawcoastlines()
myMap.drawcounties()
myMap.readshapefile("ShapeFiles/geo_export_c540f0fb-6194-47ad-9fa9-12150ac3dd4c", "noises")

neighs  = gpd.read_file("ShapeFiles/geo_export_c540f0fb-6194-47ad-9fa9-12150ac3dd4c.shp")

neighs = pd.DataFrame({
        'shapes': [Polygon(np.array(shape), True) for shape in myMap.noises], 
        'Neighborhood': [n['name'] for n in myMap.noises_info] })

neighs = neighs.merge(counts, on = "Neighborhood", how = "left")

cmap = plt.get_cmap('Oranges')   
pc = PatchCollection(neighs.shapes, zorder = 2)
norm = Normalize()
pc.set_facecolor(cmap(norm(neighs['Opened'].fillna(0).values)))
ax.add_collection(pc) # was ax.

mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
mapper.set_array(neighs['Opened'])
plt.colorbar(mapper, shrink=0.4)

plt.title("The Amount of Cleaning Requests For Each Neighborhood")


# In[15]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "UnclosedProp", 
                    y = "Neighborhood",
                    data = counts.sort_values(by = "UnclosedProp",
                                              ascending = False).head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )#, size = 10)
plt.title("Proportion of Unclosed Cleaning Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# In[16]:

fig, ax = plt.subplots(figsize=(10,20))

# Using counts: "Neighborhood" and "Opened"

myMap = Basemap(llcrnrlon=-122.523, llcrnrlat=37.7, urcrnrlon=-122.36, urcrnrlat=37.83, resolution="f",
    projection="merc") 
myMap.drawcoastlines()
myMap.drawcounties()
myMap.readshapefile("ShapeFiles/geo_export_c540f0fb-6194-47ad-9fa9-12150ac3dd4c", "noises")

neighs  = gpd.read_file("ShapeFiles/geo_export_c540f0fb-6194-47ad-9fa9-12150ac3dd4c.shp")

neighs = pd.DataFrame({
        'shapes': [Polygon(np.array(shape), True) for shape in myMap.noises], 
        'Neighborhood': [n['name'] for n in myMap.noises_info] })

neighs = neighs.merge(counts, on = "Neighborhood", how = "left")

cmap = plt.get_cmap('Oranges')   
pc = PatchCollection(neighs.shapes, zorder = 2)
norm = Normalize()
pc.set_facecolor(cmap(norm(neighs['UnclosedProp'].fillna(0).values)))
ax.add_collection(pc) # was ax.

mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
mapper.set_array(neighs['UnclosedProp'])
plt.colorbar(mapper, shrink=0.4)

plt.title("The Proportion of Unclosed Requests For Each Neighborhood")


# Use supervisor district where there are too many neighborhoods. 

# In[17]:

request_counts = street.groupby(by = "Request Type").count().reset_index().ix[:,["Request Type","CaseID"]].sort_values(by = "CaseID", ascending = False)
request_counts.head()


# In[18]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Request Type", 
                    x = "CaseID",
                    data = request_counts, 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )#, size = 10)
plt.title("Requests Type") 
plt.show()


# Differences by time of year:
# - Mattresses in summer  
# - Holiday shopping  
# 

# Note: only use 2009 through 2016 to only count full years.  
# Ask TA if we should do this for all analysis or just this part.

# In[19]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# In[20]:

street.head()


# In[21]:

count_by_month = street.groupby(by='month').count().CaseID.reset_index()
count_by_month


# In[22]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.pointplot(y = "CaseID", 
                    x = "month",
                    data = count_by_month, 
                    kind = "bar", 
                    aspect = 3,
                   )#, size = 10)
ax.set_ylabel("Cleaning Requests")
ax.set_xlabel("Month")
plt.title("Requests by Month") 
plt.show()


# In[23]:

count_by_month.plot(y = "CaseID", 
                    x = "month")


# Faster at closing requests by time?
# Time to close requests by neighborhood?

# In[24]:

street['year'] = [timestamp.year for timestamp in street.Opened]
count_by_year = street.groupby(by='year').count().CaseID.reset_index()
sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.pointplot(y = "CaseID", 
                    x = "year",
                    data = count_by_year, 
                    kind = "bar", 
                    aspect = 3,
                   )#, size = 10)
ax.set_ylabel("Cleaning Requests")
ax.set_xlabel("Year")
plt.title("Requests by Year") 
plt.show()


# In[25]:

[(colname, len(street[colname].unique())) for colname in list(street)]


# In[26]:

by_month_req_type = street.groupby(by=['month','Request Type']).count().CaseID.reset_index()
by_month_req_type = by_month_req_type.sort_values(by = ['month', "CaseID"], ascending=[True,False])
by_month_req_type.head()


# In[27]:

#by_month_req_type = street.groupby(by=['month','Request Type']).plot()


# In[28]:

#street.groupby(by=['month','Request Type']).plot(y = 'CaseID', x = 'month')


# In[29]:

by_month_req_type.plot(y = 'CaseID', x = 'month')


# # Scraping

# In[30]:

requests_cache.install_cache('sf_cache')


# In[31]:

url = "http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html"
response = requests.get(url)
response.raise_for_status

neighborhoods_bs = BeautifulSoup(response.text, 'lxml')
neighborhood_names = neighborhoods_bs.find_all(name = "span", attrs={'class':'street-name'})
neighborhood_names = [name.text.replace("-", " ") for name in neighborhood_names]
neighborhood_divs = neighborhoods_bs.body.find_all(name = "div", attrs={'class':'neighborhood'})


# In[32]:

def catch(line, number, simple, c = "h", complicated = False):
    """
    This function was made to catch the cases when scraping where we want NAs. If grabbing what we want from line fails, 
    then NA is returned. If number is True, then the value we are grabbing needs to be converted from a string to a number. 
    If simple is True, then the value we are scraping is right there, otherwise we need to search for a particular class which
    is the c input variable. Complicated is for the last column we are scraping where finding that class is a bit more complicated.
    """
    try:
        if number == True:
            if simple == True:
                return float(line[0].next_sibling.replace(",", "").replace("$", ""))
            
            else: 
                if complicated == False:
                    return float(line[0].next_sibling.next_sibling.find_all(class_ = c)[0].next_sibling.replace(",", "").replace(" years", "").replace("$", ""))
                else: 
                    return float(line[0].find_all_next(class_ = c)[0].next_sibling.replace(",", "").replace(" years", "").replace("$", ""))

        else:
            return line[0].next_sibling
    except:
        return np.nan


# In[33]:

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


# In[34]:

def CombineNeighs(name1, name2, newName, df):
    """
    This function takes in two neighborhood names of the demographic dataframe, combines them, and changes the name.
    """
    one = df.ix[df.Neighborhood == name1]
    two = df.ix[df.Neighborhood == name2]
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
    df = df.drop(one.index)
    df = df.drop(two.index)
    df = df.append(one)
    return df


# In[35]:

# Clean up neighborhood names: make the demographic names match our data and shapefiles
demographic = CombineNeighs("Bayview District", "Bayview Heights", "Bayview", demographic)
demographic = CombineNeighs("Bernal Heights North", "Bernal Heights Park", "Bernal Heights1", demographic)
demographic = CombineNeighs("Bernal Heights South", "Bernal Heights", "Bernal Heights2", demographic)
demographic = CombineNeighs("Bernal Heights1", "Bernal Heights2", "Bernal Heights", demographic)
demographic = CombineNeighs("Balboa Park", "Balboa Terrace", "Balboa Terrace", demographic)
demographic = CombineNeighs("Aquatic Park", "Fort Mason", 'Aquatic Park / Ft. Mason', demographic)
demographic = CombineNeighs("Downtown", "Union Square", 'Downtown / Union Square', demographic)
demographic = CombineNeighs("Financial District", "Financial District South", "Financial District", demographic)


# In[36]:


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


# In[37]:

# set(street.Neighborhood.unique()) - set(demographic.Neighborhood.unique())


# In[38]:

street = street.merge(demographic, on = "Neighborhood", how = "left") 
street.head()


# --------

# ## Events and Festivals

# In[39]:

url_pride = "https://en.wikipedia.org/wiki/San_Francisco_Pride"
response = requests.get(url_pride)
response.raise_for_status

pride_bs = BeautifulSoup(response.text, 'lxml')

pride_table = pride_bs.find_all(name = "table", attrs={'class':'wikitable'})


# In[40]:

#type(pride_table[0])
# The table is the first element

rows = pride_table[0].find_all(name = "tr")

# The first row is the header
#print rows[0]
#for colname in rows[0].find_all(name = "th"):
#    print colname.text

colnames = [colname.text for colname in rows[0].find_all(name = "th")]
print colnames

#pride = [{colname, []} for colname in colnames]
#print pride


# In[41]:

years = []
dates = []
attendance = []

for row in rows[1:]:
    cells = row.find_all(name = "td")
        
    years.append(cells[0].text)
    dates.append(cells[1].text)
    attendance.append(cells[4].text)
    
assert(len(years) == len(dates) == len(attendance))


# In[42]:

pride = pd.DataFrame.from_dict({"year": years,
                                "date": dates,
                                "attendance": attendance})

pride.year = pd.to_numeric(pride.year)

# Remove unused years
pride = pride[pride.year > 2007]

pride


# In[45]:

#pride.date[0][-2:]


# In[46]:

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


# In[47]:

def parse_attendance(attendance_str):
    """
    
    """
    
    if "million" in attendance_str.lower():
        # Multiply by 1000000 and remove the string "million"
        return float(attendance_str.split(" ")[0]) * 1000000
    
    else:
        return None

        
pride["attendance_num"] = [parse_attendance(x) for x in pride.attendance]
pride


# In[48]:

pride = pride.reset_index()


# ### Outside Lands Music and Arts Festival

# In[49]:

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


# In[50]:

# Separate the date ranges and fix the formatting

ol2 = []
for year_and_date in ol:
    
    date_split = year_and_date[1].split()
    month = date_split[0]
    if len(date_split) > 2:
        # keep the year
        year_and_date_new = [year_and_date[0]]
        year_and_date_new.extend(date_split[1:])
        ol2.append(year_and_date_new)
    else:
        days = date_split[1].split("-")
        for day in days:
            # keep the year
            year_and_date_new = [year_and_date[0]]
            year_and_date_new.append(month)
            year_and_date_new.append(day)
            ol2.append(year_and_date_new)

ol2


# In[51]:

ol_dates = pd.to_datetime([" ".join(date) for date in ol2])
ol_dates


# # Events Plots

# Grab all of June and group by day to get count of requests, then add boolean pride or not

# In[52]:

streetJune = street.loc[street["Opened"].dt.month == 6]
streetJune["DateOpened"] = streetJune["Opened"].dt.date # Yells at you

# http://www.sfpride.org/parade/
prideNeighs = ["South of Market", "Tenderloin", "Financial District", "Downtown / Union Square", "Civic Center"]
streetJune = streetJune.loc[streetJune.Neighborhood.isin(prideNeighs)]

JuneDayReqs = streetJune.groupby(by = "DateOpened").count().CaseID
pride["StartNoTime"] = pride["start_date"].dt.date 
pride["EndNoTime"] = pride["end_date"].dt.date 
JuneRequests = pd.DataFrame({"ReqCount": JuneDayReqs})
JuneRequests = JuneRequests.reset_index()
JuneRequests["Pride"] = [row in pride.StartNoTime.values for row in JuneRequests.DateOpened]


# In[53]:

streetJune.head()


# In[54]:

pride_merged_start = JuneRequests.merge(right = pride, right_on="StartNoTime", left_on="DateOpened")
pride_merged_end = JuneRequests.merge(right = pride, right_on="EndNoTime", left_on="DateOpened")
cols = ["DateOpened", "ReqCount", "attendance_num", "StartNoTime", "EndNoTime"]
pride_merged_start = pride_merged_start[cols]
pride_merged_end = pride_merged_end[cols]
pride_merged = pd.concat([pride_merged_start, pride_merged_end])
pride_merged["Year"] = [t.year for t in pride_merged.StartNoTime]
req_year = pride_merged.groupby(by="Year").sum()
req_year.reset_index(inplace=True)
pride_merged_final = pride_merged_start
pride_merged_final["Year"] = [t.year for t in pride_merged_final.StartNoTime]
pride_merged_final = pride_merged_final.merge(req_year, on = "Year")
pride_merged_final = pride_merged_final[["DateOpened", "ReqCount_y", "attendance_num_x", "Year","StartNoTime", "EndNoTime"]]
pride_merged_final


# In[55]:

pride_merged_final.plot(x="ReqCount_y", y="attendance_num_x", kind="scatter")


# There does not seem to be an association between the pride parade and requests in the surrounding neighborhoods.  

# In[56]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.pointplot(y = "CaseID", 
                    x = "month",
                    data = count_by_month, 
                    kind = "bar", 
                    aspect = 3,
                   )#, size = 10)
ax.set_ylabel("Cleaning Requests")
ax.set_xlabel("Month")
plt.title("Requests by Month") 
plt.show()


# # Outside Lands Plot

# In[57]:

ol_dates


# In[58]:

AugustRequests = street.loc[street["Opened"].dt.month == 8]
AugustRequests["DateOpened"] = AugustRequests["Opened"].dt.date # Yells at you
OLNeighs = ["Golden Gate Park"]
AugustRequests = AugustRequests.loc[AugustRequests.Neighborhood.isin(OLNeighs)]


# In[59]:

type(AugustRequests["DateOpened"][29006])


# In[60]:

type(ol_dates[0])


# In[61]:

ol_dt = [d.date() for d in ol_dates]


# In[62]:

AugustRequests[AugustRequests.DateOpened.isin(ol_dt)]


# todo: compare to normal # of requests

# In[ ]:




# --------

# ## Maps

# In[63]:

# Coordinates from https://en.wikipedia.org/wiki/San_Francisco and 
# http://andrew.hedges.name/experiments/convert_lat_long/
m = folium.Map(location=[37.783, -122.416], zoom_start=12)
m


# In[64]:

# Points
street.ix[1,'Point']


# In[65]:

def to_coordinates(point):
    """
    Converts a string in the format '(37.7695911772607, -122.415577110949)' to coordinates.
    """
    
    # Tests
    assert(isinstance(point, str) and point.startswith('(') and point.endswith(')'))
    
    (lat, lon) = point.split(',')
    
    # Remove '('
    lat = lat[1:]
    
    # Remove ')' and space
    lon = lon[:-1].strip()
    
    
    
    return (float(lat), float(lon))
    
to_coordinates(street.ix[1,'Point'])


# In[66]:

# TODO: Make this a function
folium.Marker(to_coordinates(street.ix[1,'Point']), popup = street.ix[1,'Request Type']).add_to(m)
m


# In[67]:

street_mattress = street[street["Request Details"] == "Mattress"]
street_mattress.head(2)


# In[68]:

len(street_mattress)


# In[69]:

#from IPython.display import display
for index, row in street_mattress.iterrows():
    #print type(row["Status"])
    pass
    # Add to the map with marker cluster?
    # http://nbviewer.jupyter.org/github/ocefpaf/folium_notebooks/blob/master/test_clustered_markes.ipynb
    


# In[70]:

mattress_map = folium.Map(location=[37.783, -122.416], zoom_start=12)
folium.GeoJson(open('Analysis Neighborhoods.geojson'), name='geojson').add_to(mattress_map)
mattress_map


# In[71]:

# Neighborhood geojson from 
# https://data.sfgov.org/Geographic-Locations-and-Boundaries/Analysis-Neighborhoods/p5b7-5n3h

folium.GeoJson(open('Analysis Neighborhoods.geojson'), name='geojson').add_to(m)
m


# Map of neighborhoods shaded by count of requests:

# In[ ]:




# In[ ]:



