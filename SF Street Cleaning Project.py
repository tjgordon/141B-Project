
# coding: utf-8

# In[131]:

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import feather
get_ipython().magic('matplotlib inline')


# In[20]:

#%%timeit -r1 -n1 
# timeit args from: http://stackoverflow.com/questions/32565829/simple-way-to-measure-cell-execution-time-in-ipython-notebook 
# For some reason the varible isn't saved when using timeit

# Note: To just read in part add nrows =
parseDates = ["Opened", "Closed", "Updated"] # Convert these to datetimes
street_csv = pd.read_csv("Street_and_Sidewalk_Cleaning.csv", 
                         #nrows = 100000,
                         parse_dates=parseDates)


# In[22]:

feather.write_dataframe(street_csv, 'street.feather')


# In[53]:

# Similar thing built in to pandas. Causes some error.
street.to_hdf('street.h5','table',append=False)


# In[56]:

#street2 = pd.read_hdf('street.h5')


# In[24]:

street = feather.read_dataframe('street.feather')


# In[57]:

# To use the csv version
# street = street_csv


# In[19]:

all(street == street_csv)


# In[5]:

street.head()


# Some basic statistics on the dataset we are starting with:

# In[28]:

numRows = street.shape[0]
print "We are working with", numRows, "rows."
print "Our dates range from", street.loc[numRows - 1, "Opened"],"to", street.loc[0, "Opened"], "."


# In[63]:

#plt.figure(figsize=(2,100)) # Doesn't do much
theOrder = ["Voice In", "Open311", "Web Self Service", "Integrated Agency", "Twitter", "e-mail In", "Other Department"]
#sns.set(font_scale = 1.5)
sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Source", data = street, kind = "count", orient = "h", order = theOrder, aspect = 2)#, size = 10)
plt.title("How the Cleaning Request Was Made") 
plt.show()


# According to [the project's website](http://www.open311.org/learn/), Open311 allows people to report issues in public spaces to city officials through a [website](https://sf311.org/index.aspx?page=797) or [mobile app](https://www.sf311.org/mobile).  

# In[100]:

#plt.figure(figsize=(2,100)) # Doesn't do much
#theOrder = ["Voice In", "Open311", "Web Self Service", "Integrated Agency", "Twitter", "e-mail In", "Other Department"]
#sns.set(font_scale = 1.5)
#sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Neighborhood", data = street, kind = "count", orient = "h")# order = theOrder, aspect = 2)#, size = 10)
#plt.title("How the Cleaning Request Was Made") 
plt.show()


# In[7]:

street.Neighborhood.unique()


# In[8]:

street.Neighborhood.value_counts


# In[59]:

# From: http://stackoverflow.com/questions/22391433/count-the-frequency-that-a-value-occurs-in-a-dataframe-column
counts = street.groupby('Neighborhood').count()


# We can get the total number of cases from CaseID
# unresolved cases by neighborhood

# In[90]:

counts = counts.sort_values(by = "CaseID",
                            ascending = False)
counts = counts.reset_index()


# In[91]:

counts.head()


# In[101]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "CaseID", 
                    y = "Neighborhood",
                    data = counts.head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 3
                   )#, size = 10)
plt.title("Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# In[109]:

counts['UnclosedProp'] = (counts.Opened - counts.Closed) / counts.Opened


# In[110]:

counts.head()


# In[112]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "UnclosedProp", 
                    y = "Neighborhood",
                    data = counts.sort_values(by = "UnclosedProp",
                                              ascending = False).head(15), 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 3
                   )#, size = 10)
plt.title("Proportion of Unclosed Requests by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# Use supervisor district where there are too many neighborhoods. 

# In[125]:

request_counts = street.groupby(by = "Request Type").count().reset_index().ix[:,["Request Type","CaseID"]].sort_values(by = "CaseID", ascending = False)
request_counts.head()


# In[132]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(y = "Request Type", 
                    x = "CaseID",
                    data = request_counts, 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 3
                   )#, size = 10)
plt.title("Requests Type by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# Differences by time of year:
# - Mattresses in summer  
# - Holiday shopping  
# 

# Note: only use 2009 through 2016 to only count full years.  
# Ask TA if we should do this for all analysis or just this part.

# In[139]:

street['month'] = [timestamp.month for timestamp in street.Opened]


# In[140]:

street.head()


# In[148]:

count_by_month = street.groupby(by='month').count().CaseID.reset_index()
count_by_month


# In[150]:

sns.set_context("notebook", rc={"font.size" : 40}) # font_scale=1.5
ax = sns.factorplot(x = "CaseID", 
                    y = "month",
                    data = count_by_month, 
                    kind = "bar", 
                    orient = "h", 
                    aspect = 3
                   )#, size = 10)
plt.title("Requests Type by Neighborhood (Top 15 Neighborhoods)") 
plt.show()


# Faster at closing requests by time?
# Time to close requests by neighborhood?
