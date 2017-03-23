
# coding: utf-8

# # Analysis and Visualization

# This notebook includes the analysis and visualizations of the data obtained in the previous notebook. 

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


# Most requests seem to be made by phone call.  
# According to [the project's website](http://www.open311.org/learn/), Open311 allows people to report issues in public spaces to city officials through a [website](https://sf311.org/index.aspx?page=797) or [mobile app](https://www.sf311.org/mobile).  

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


# We also examined the proportion of unclosed requests at the time we downloaded the data set. 

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


# As also seen on the following map, Lincoln Park / Ft. Miley has the highest proportion of unclosed requests. 

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


# We then calculated the number of requests by type.  

# In[107]:

request_counts = street.groupby(by = "Request Type").count().reset_index().ix[:,["Request Type","CaseID"]].sort_values(by = "CaseID", ascending = False)


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


# We added the month of each request to compare the counts of requests by month.  

# In[17]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# In[108]:

count_by_month = street.groupby(by='month').count().CaseID.reset_index()
#count_by_month


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


# The number of requests seems to be highest in the summer, and lowest in late winter and spring.  

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


# ### Demographic Plots

# We calculated the number of hours required to close each request.

# In[72]:

def get_Timedelta_hours(endtime, starttime):
    # import pandas as pd
    #assert(isinstance(endtime, pd.tslib.Timestamp) and isinstance(starttime, pd.tslib.Timestamp))
    
    try:
        td = endtime - starttime

        # Return hours
        return td.seconds / 3600.0
    except:
        return None

get_Timedelta_hours(street.ix[0,"Closed"], street.ix[0,"Opened"])


# In[73]:

street["HoursToClose"] = [get_Timedelta_hours(closed, opened) for closed, opened in zip(street.Closed, street.Opened)]


# In[84]:

street.hist("HoursToClose")


# From the histogram, it seems that requests take at most about a day to close. 

# To check for potential associations between the time to close a request and the other numeric variables, we used a correlation matrix.  

# In[82]:

# Source: https://stackoverflow.com/questions/29432629/correlation-matrix-using-pandas
corr = street[["month", 
               "AreaSqMi", 
               "Females", 
               "Males", 
               "HousePrice",
               "MedAgeF",
               "MedAgeM",
               "MedHouseholdIncome",
               "MedRent",
               "PeoplePerSqMi",
               "Population",
               "year",
               "HoursToClose"]].corr()
sns.heatmap(corr, 
            xticklabels=corr.columns.values,
            yticklabels=corr.columns.values)


# There seems to be a small negative correlation between the hours required to close a request and the year, which indicates that requests are being closed faster now than they were initially. The correlations between the hours required to close a request and the other variables seem to be very weak.

# We calculated the mean hours to close requests for each neighborhood.

# In[92]:

hrs_by_neigh = street.groupby("Neighborhood").mean()[["HoursToClose"]].reset_index()


# In[97]:

hrs_by_neigh.hist("HoursToClose")


# In[106]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "HoursToClose", 
                    y = "Neighborhood",
                    data = hrs_by_neigh.sort_values(by = "HoursToClose",
                                                    ascending = False).head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )
plt.title("Mean Time to Close Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# This plot indicates that Yerba Buena Island, West of Twin Peaks, Twin Peaks, and Castro/Upper Market have cleaning requests that take longer to fill than any other neighborhoods. 
# 
# Yerba Buena Island is an island, which might make it more difficult to get cleaning staff and equipment to. The Twin Peaks neighborhood contains the titular hills, which might cause some requests to be more remote and difficult to access. It isn't immediately apparent why cleaning requests in Castro/Upper Market might take longer than in most neighborhoods. According to the [Wikipedia page](https://en.wikipedia.org/wiki/Castro_District,_San_Francisco) for Castro, the neighborhood has historically included a large Scandinavian and LGBT population.   

# In[104]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "HoursToClose", 
                    y = "Neighborhood",
                    data = hrs_by_neigh.sort_values(by = "HoursToClose",
                                                    ascending = False).tail(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 2
                   )
plt.title("Mean Time to Close Requests by Neighborhood (Bottom 15 Neighborhoods)") 
plt.show()


# In comparison, there don't seem to be any neighborhoods that have substantially lower mean time to close requests than almost all other neighborhoods.  

# In[95]:

fig, ax = plt.subplots(figsize=(10,20))

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

neighs = neighs.merge(hrs_by_neigh, on = "Neighborhood", how = "left")

cmap = plt.get_cmap('Oranges')   
pc = PatchCollection(neighs.shapes, zorder = 2)
norm = Normalize()
pc.set_facecolor(cmap(norm(neighs['HoursToClose'].fillna(0).values)))
ax.add_collection(pc) # was ax.

mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
mapper.set_array(neighs['HoursToClose'])
plt.colorbar(mapper, shrink=0.4)

plt.title("Mean Time to Close Requests (Hours) by Neighborhood")


# This map also shows the time to close requests by neighborhood; Yerba Buena island, which has the longest time, is visible in the upper right.  

# --------

# # Events and Festivals Plots

# ## Pride

# We merged data about attendance scraped from the [San Francisco Pride Wikipedia Page](https://en.wikipedia.org/wiki/San_Francisco_Pride) with the requests data to find the number of requests that were submitted on the days of the parade and in the neighborhoods surrounding the parade, shown in the following table.    

# In[25]:

# Read the data scraped in the other notebook
pride = pd.DataFrame.from_csv("pride.csv")
pride


# We used a scatterplot to see if there might be an association between the event attendance and the number of requests.

# In[26]:

pride.plot(x="ReqCount_y", y="attendance_num_x", kind="scatter")
plt.title("Request in Neighborhoods Surrounding the SF Pride Parade and Parade Attendance")
plt.ylabel("Attendance")
plt.xlabel("Requests in Surrounding Neighborhoods")


# There does not seem to be an association between the pride parade and requests in the surrounding neighborhoods.  
# We used the correlation between these variables, shown below, for confirmation:  

# In[27]:

pride[["ReqCount_y", "attendance_num_x"]].corr()


# ## Outside Lands

# We used the dates of the Outside Lands Festival obtained by scraping the Wikipedia page to assess any association between cleaning requests and the festival.

# In[28]:

# Read the dates of the festival obtained from scraping
ol_dates_df = pd.DataFrame.from_csv("ol_dates.csv", parse_dates=["Festival_Date"])
#ol_dates_df

ol_dates = pd.DatetimeIndex(ol_dates_df.Festival_Date)
ol_dates


# In[29]:

# Find all requests in August in Golden Gate Park
AugustRequests = street.loc[street["Opened"].dt.month == 8]
AugustRequests["DateOpened"] = AugustRequests["Opened"].dt.date 
OLNeighs = ["Golden Gate Park"]
AugustRequests = AugustRequests.loc[AugustRequests.Neighborhood.isin(OLNeighs)]


# In[30]:

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

# In[31]:

# Add a new day column to allow groupby
AugustRequests["Day"] = AugustRequests["Opened"].dt.day

# Count the number of requests per day across all years
Aug_req_by_day = AugustRequests[["CaseID", "Day"]].groupby('Day').count()

# There are 8 years in the data set, so divide the counts by 8 to get the average for each day
Aug_req_by_day.CaseID = Aug_req_by_day.CaseID / 8

Aug_req_by_day.head()


# In[32]:

Aug_req_by_day.hist()
plt.title("Average Requests in Golden Gate Park on Days of August")
plt.xlabel("Average Requests")
plt.ylabel("Frequency")


# In[33]:

np.mean(Aug_req_by_day.CaseID)


# In[34]:

np.median(Aug_req_by_day.CaseID)


# From the mean and median, a "normal" number of requests in Golden Gate Park on a day in August is about 1.3. All but one of the number of requests on the days of the festival is 1 or 2, so it seems fairly clear that there is no consistent association between the festival and cleaning request in the park. 

# Neither event we examined seems to be associated with increased cleaning requests. This may be because the city allocates additional cleaning resources in anticipation of large events, or the events may hire their own staff for cleaning.  

# --------
