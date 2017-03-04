
# coding: utf-8

# In[1]:

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import feather


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


# In[26]:

# Similar thing built in to pandas. Causes some error.
#street.to_hdf('street.h5','table',append=False)


# In[24]:

street = feather.read_dataframe('street.feather')


# In[27]:

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


# In[29]:

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


# In[34]:

# From: http://stackoverflow.com/questions/22391433/count-the-frequency-that-a-value-occurs-in-a-dataframe-column
counts = street.groupby('Neighborhood').count()
counts.head()


# We can get the total number of cases from CaseID
# unresolved cases by neighborhood

# In[52]:

counts.sort_values(by = "CaseID",
            ascending = False)

