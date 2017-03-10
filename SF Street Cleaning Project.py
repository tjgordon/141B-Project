
# coding: utf-8

# In[5]:

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import feather
import requests
import requests_cache
import lxml
from bs4 import BeautifulSoup
import bs4
import re
get_ipython().magic('matplotlib inline')
#plt.rcParams['figure.figsize'] = (12,12)


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

feather.write_dataframe(street_csv, 'street.feather')


# In[ ]:

# Similar thing built in to pandas. Causes some error.
street.to_hdf('street.h5','table',append=False)


# In[2]:

#street2 = pd.read_hdf('street.h5')


# In[3]:

street = feather.read_dataframe('street.feather')


# In[4]:

# To use the csv version
# street = street_csv


# In[6]:

#all(street == street_csv)


# In[3]:

street.head()


# In[37]:

street = street.loc[street['Opened'].dt.year != 2008]
street = street.loc[street['Opened'].dt.year != 2017]
street = street.sort_values("Opened")
street = street.reset_index()
street = street.drop('index', 1)
street.head()


# Some basic statistics on the dataset we are starting with:

# In[50]:

numRows = street.shape[0]
print "We are working with", numRows, "rows."
print "Our dates range from", street.loc[numRows - 1, "Opened"],"to", street.loc[0, "Opened"], "."


# In[91]:

#plt.figure(figsize=(2,100)) # Doesn't do much
theOrder = ["Voice In", "Open311", "Web Self Service", "Integrated Agency", "Twitter", "e-mail In", "Other Department"]
#sns.set(font_scale = 1.5)
sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Source", data = street, kind = "count", orient = "h", order = theOrder, aspect = 2)#, size = 10)
plt.title("How the Cleaning Request Was Made") 
plt.show()


# According to [the project's website](http://www.open311.org/learn/), Open311 allows people to report issues in public spaces to city officials through a [website](https://sf311.org/index.aspx?page=797) or [mobile app](https://www.sf311.org/mobile).  

# In[52]:

street.Neighborhood.unique()


# In[53]:

street.Neighborhood.value_counts


# In[54]:

# From: http://stackoverflow.com/questions/22391433/count-the-frequency-that-a-value-occurs-in-a-dataframe-column
counts = street.groupby('Neighborhood').count()


# We can get the total number of cases from CaseID
# unresolved cases by neighborhood

# In[55]:

counts = counts.sort_values(by = "CaseID",
                            ascending = False)
counts = counts.reset_index()


# In[56]:

counts.head()


# In[57]:

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


# In[58]:

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


# In[59]:

counts['UnclosedProp'] = (counts.Opened - counts.Closed) / counts.Opened


# In[60]:

counts.head()


# In[88]:

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


# Use supervisor district where there are too many neighborhoods. 

# In[62]:

request_counts = street.groupby(by = "Request Type").count().reset_index().ix[:,["Request Type","CaseID"]].sort_values(by = "CaseID", ascending = False)
request_counts.head()


# In[90]:

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

# In[64]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# In[65]:

street.head()


# In[66]:

count_by_month = street.groupby(by='month').count().CaseID.reset_index()
count_by_month


# In[67]:

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


# In[68]:

count_by_month.plot(y = "CaseID", 
                    x = "month")


# Faster at closing requests by time?
# Time to close requests by neighborhood?

# In[92]:

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


# In[69]:

[(colname, len(street[colname].unique())) for colname in list(street)]


# In[70]:

by_month_req_type = street.groupby(by=['month','Request Type']).count().CaseID.reset_index()
by_month_req_type = by_month_req_type.sort_values(by = ['month', "CaseID"], ascending=[True,False])
by_month_req_type.head()


# In[71]:

#by_month_req_type = street.groupby(by=['month','Request Type']).plot()


# In[72]:

#street.groupby(by=['month','Request Type']).plot(y = 'CaseID', x = 'month')


# In[73]:

by_month_req_type.plot(y = 'CaseID', x = 'month')


# # Scraping

# In[74]:

requests_cache.install_cache('sf_cache')


# In[75]:

url = "http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html"
response = requests.get(url)
response.raise_for_status

neighborhoods_bs = BeautifulSoup(response.text, 'lxml')

neighborhood_names = neighborhoods_bs.find_all(name = "span", attrs={'class':'street-name'})


# In[76]:

neighborhood_names = [name.text for name in neighborhood_names]


# In[77]:

neighborhood_names


# In[78]:

neighborhood_divs = neighborhoods_bs.body.find_all(name = "div", attrs={'class':'neighborhood'})


# In[79]:

neighborhood_divs[0].text


# regular expressions
# [capital letter][lowercase][:][ ][numbers or , or $]

# In[80]:

neighborhood_divs[0].find_all(name = "b")


# In[81]:

neighborhood_divs[0].contents


# In[82]:

type(neighborhood_divs[0].contents[1])


# Loop through contents  
# if a navigable string can be converted to int,  
# then grab it and the first <b> that precedes it  

# In[83]:

neighborhood_divs[0].strings


# In[84]:

# Add to a list of strings
strings = []

for descendant in neighborhood_divs[0].strings:
    strings.append(descendant)
    
strings


# In[85]:

#contents = neighborhood_divs[0].contents

value_dict_list = []

# Replace $
for i in range(1, len(strings)):
    if len(strings[i]) > 0:
        if strings[i][0] == '$':
            strings[i] = strings[i][1:]
        # remove commas and whitespace
        strings[i] = strings[i].replace(',', '').strip()

        try:
            value = float(strings[i])
            try:
                # what the value refers to
                what_value_is = strings[i - 1]
                
                # units
                if strings[i + 1][-1] != ":":
                    units = strings[i + 1]
                else:
                    units = ""
                
                value_dict = {"value": value,
                              "what_value_is": what_value_is,
                              "units": units}
                
                value_dict_list.append(value_dict)
                
            except:
                print "bad idea"

        except ValueError:
            continue
            
value_dict_list


# In[86]:

strings


# In[87]:

int("9,999")

