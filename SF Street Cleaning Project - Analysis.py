
# coding: utf-8

# # Introduction

# 

# # Libraries

# In[1]:

# Loading in data:
import numpy as np
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


# # Reading in the Data

# See the other notebook for the process of reading, scraping, and cleaning the data.  

# In[2]:

# Read the data from the h5 file exported in the other notebook
street2 = pd.HDFStore('street.h5')
street = street2.select('/table')
street.head()


# Some basic statistics on the dataset we are starting with:

# In[3]:

numRows = street.shape[0]
print "We are working with", numRows, "rows."
print "Our dates range from", street.loc[numRows - 1, "Opened"],"to", street.loc[0, "Opened"], "."


# We supplemented this data with demographic statistics from [city-data.com](http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html).  

# In[4]:

demographic = pd.DataFrame.from_csv("demographic.csv")
demographic.head()


# In[5]:

street = street.merge(demographic, on = "Neighborhood", how = "left") 
street.head()


# # Plots

# In[6]:

#plt.figure(figsize=(2,100)) # Doesn't do much
theOrder = ["Voice In", "Open311", "Web Self Service", "Integrated Agency", "Twitter", "e-mail In", "Other Department"]
#sns.set(font_scale = 1.5)
sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Source", data = street, kind = "count", orient = "h", order = theOrder, aspect = 2)#, size = 10)
plt.title("How the Cleaning Request Was Made") 
plt.show()


# According to [the project's website](http://www.open311.org/learn/), Open311 allows people to report issues in public spaces to city officials through a [website](https://sf311.org/index.aspx?page=797) or [mobile app](https://www.sf311.org/mobile).  

# In[7]:

street.Neighborhood.value_counts


# In[8]:

# From: http://stackoverflow.com/questions/22391433/count-the-frequency-that-a-value-occurs-in-a-dataframe-column
counts = street.groupby('Neighborhood').count()


# We can get the total number of cases from CaseID
# unresolved cases by neighborhood

# In[9]:

counts = counts.sort_values(by = "CaseID",
                            ascending = False)
counts = counts.reset_index()
counts['UnclosedProp'] = (counts.Opened - counts.Closed) / counts.Opened
counts.head()


# In[10]:

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


# In[11]:

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

# In[12]:

fig, ax = plt.subplots(figsize=(10,20))

# Using counts: "Neighborhood" and "Opened"

myMap = Basemap(llcrnrlon=-122.523, llcrnrlat=37.7, urcrnrlon=-122.36, urcrnrlat=37.83, resolution="f",
    projection="merc") 
myMap.drawcoastlines()
myMap.drawcounties()
myMap.readshapefile("ShapeFiles/geo_export_c540f0fb-6194-47ad-9fa9-12150ac3dd4c", 
                    "noises")

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


# In[13]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "UnclosedProp", 
                    y = "Neighborhood",
                    data = counts.sort_values(by = "UnclosedProp",
                                              ascending = False).head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )
plt.title("Proportion of Unclosed Cleaning Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# In[14]:

fig, ax = plt.subplots(figsize=(10,20))

# Using counts: "Neighborhood" and "Opened"

myMap = Basemap(llcrnrlon=-122.523, 
                llcrnrlat=37.7, 
                urcrnrlon=-122.36, 
                urcrnrlat=37.83, 
                resolution="f",
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

# In[15]:

request_counts = street.groupby(by = "Request Type").count().reset_index().ix[:,["Request Type","CaseID"]].sort_values(by = "CaseID", ascending = False)
request_counts.head()


# In[16]:

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

# We added the month of each request to compare the counts of requests by month.  

# In[17]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# In[18]:

count_by_month = street.groupby(by='month').count().CaseID.reset_index()
count_by_month


# In[19]:

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


# In[20]:

count_by_month.plot(y = "CaseID", 
                    x = "month")


# Faster at closing requests by time?
# Time to close requests by neighborhood?

# In[21]:

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


# In[22]:

[(colname, len(street[colname].unique())) for colname in list(street)]


# In[23]:

by_month_req_type = street.groupby(by=['month','Request Type']).count().CaseID.reset_index()
by_month_req_type = by_month_req_type.sort_values(by = ['month', "CaseID"], ascending=[True,False])
by_month_req_type.head()


# --------

# ## Events and Festivals

# ### Pride

# In[24]:

# Read the data scraped in the other notebook
pride = pd.DataFrame.from_csv("pride.csv")
pride


# ### Outside Lands Music and Arts Festival

# In[25]:

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


# In[26]:

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


# In[27]:

ol_dates = pd.to_datetime([" ".join(date) for date in ol2])
ol_dates


# # Events

# We merged data about attendance scraped from the [San Francisco Pride Wikipedia Page](https://en.wikipedia.org/wiki/San_Francisco_Pride) with the requests data to find the number of requests that were submitted on the days of the parade and in the neighborhoods surrounding the parade, shown in the following table.    

# In[28]:

pride


# We used a scatterplot to see if there might be an association between the event attendance and the number of requests.

# In[87]:

pride.plot(x="ReqCount_y", y="attendance_num_x", kind="scatter")
plt.title("Request in Neighborhoods Surrounding the SF Pride Parade and Parade Attendance")
plt.ylabel("Attendance")
plt.xlabel("Requests in Surrounding Neighborhoods")


# There does not seem to be an association between the pride parade and requests in the surrounding neighborhoods.  
# We used the correlation between these variables, shown below, for confirmation:  

# In[30]:

pride[["ReqCount_y", "attendance_num_x"]].corr()


# # Outside Lands

# We used the dates of the Outside Lands Festival obtained by scraping the Wikipedia page to assess any association between cleaning requests and the festival.

# In[83]:

# Read the dates of the festival obtained from scraping
ol_dates_df = pd.DataFrame.from_csv("ol_dates.csv", parse_dates=["Festival_Date"])
#ol_dates_df

ol_dates = pd.DatetimeIndex(ol_dates_df.Festival_Date)
ol_dates


# In[33]:

# Find all requests in August in Golden Gate Park
AugustRequests = street.loc[street["Opened"].dt.month == 8]
AugustRequests["DateOpened"] = AugustRequests["Opened"].dt.date 
OLNeighs = ["Golden Gate Park"]
AugustRequests = AugustRequests.loc[AugustRequests.Neighborhood.isin(OLNeighs)]


# In[88]:

type(AugustRequests["DateOpened"].values[0])
type(ol_dates[0])

# Convert the dates
ol_dt = [d.date() for d in ol_dates]

# Select all cleaning requests on the days of the festival
ol_req = AugustRequests[AugustRequests.DateOpened.isin(ol_dt)]

# Count the cleaning requests on each day of the festival
ol_req_counts = ol_req[["CaseID", "DateOpened"]].groupby("DateOpened").count()
ol_req_counts


# To determine if the number of cleaning requests on the days that Outside Lands took place was unusual, we compared it with the usual number of requests on days in August.  

# In[76]:

# Add a new day column to allow groupby
AugustRequests["Day"] = AugustRequests["Opened"].dt.day

# Count the number of requests per day across all years
Aug_req_by_day = AugustRequests[["CaseID", "Day"]].groupby('Day').count()

# There are 8 years in the data set, so divide the counts by 8 to get the average for each day
Aug_req_by_day.CaseID = Aug_req_by_day.CaseID / 8

Aug_req_by_day.head()


# In[81]:

Aug_req_by_day.hist()
plt.title("Average Requests in Golden Gate Park on Days of August")
plt.xlabel("Average Requests")
plt.ylabel("Frequency")


# In[69]:

np.mean(Aug_req_by_day.CaseID)


# In[70]:

np.median(Aug_req_by_day.CaseID)


# From the mean and median, a "normal" number of requests in Golden Gate Park on a day in August is about 1.3. All but one of the number of requests on the days of the festival is 1 or 2, so it seems fairly clear that there is no consistent association between the festival and cleaning request in the park. 

# Neither event we examined seems to be associated with increased cleaning requests. This may be because the city allocates additional cleaning resources in anticipation of large events, or the events may hire their own staff for cleaning.  

# --------

# ## Maps

# In[39]:

# Coordinates from https://en.wikipedia.org/wiki/San_Francisco and 
# http://andrew.hedges.name/experiments/convert_lat_long/
m = folium.Map(location=[37.783, -122.416], zoom_start=12)
m


# In[40]:

# Points
street.ix[1,'Point']


# In[41]:

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


# In[42]:

# TODO: Make this a function
folium.Marker(to_coordinates(street.ix[1,'Point']), popup = street.ix[1,'Request Type']).add_to(m)
m


# In[43]:

street_mattress = street[street["Request Details"] == "Mattress"]
street_mattress.head(2)


# In[44]:

len(street_mattress)


# In[45]:

mattress_count_by_month = street_mattress.groupby(by='month').count().CaseID.reset_index()


# In[46]:

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


# In[47]:

#from IPython.display import display
for index, row in street_mattress.iterrows():
    #print type(row["Status"])
    pass
    # Add to the map with marker cluster?
    # http://nbviewer.jupyter.org/github/ocefpaf/folium_notebooks/blob/master/test_clustered_markes.ipynb
    


# In[48]:

mattress_map = folium.Map(location=[37.783, -122.416], zoom_start=12)
folium.GeoJson(open('Analysis Neighborhoods.geojson'), name='geojson').add_to(mattress_map)
mattress_map


# In[49]:

# Neighborhood geojson from 
# https://data.sfgov.org/Geographic-Locations-and-Boundaries/Analysis-Neighborhoods/p5b7-5n3h

folium.GeoJson(open('Analysis Neighborhoods.geojson'), name='geojson').add_to(m)
m


# In[ ]:



