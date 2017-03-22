This is a final project for statistics 141B taken winter quarter 2017 done using Python. 

# Introduction

## Modivating Question 

The modivating question that got us interested in this topic is: How do big cities deal with cleaning problems, like when a mattress is left out on the street, human waste is all over the road, or a garbage can overflows? 

We found that the answer to this is through street cleaning requests. Street cleaning requests are made by people in the city through phone calls, mobile applications, tweets, and more. People can specify location, type, and so on. 

## Plan of Attack 

We are focusing on San Francisco for our main analysis. Some of our initial questions: 

* Does the frequency of requests change with time?
* How do cleaning requests vary in type and length to complete based on time of year or neighborhood? 
* Are these variations related to neighborhood demographics?

# Data

## Our Primary Data Source

Street and Sidewalk Cleaning from SF OpenData that we found [herej](https://data.sfgov.org/City-Management-and-Ethics/Street-and-Sidewalk-Cleaning/h3eg-w3pj). We were able to grab this data in a nice csv format that was simple to read into a DataFrame. This contains information on 693,612 cleaning requests in San Francisco. We subsetted the data to just examine requests from January 1st 2009 to December 31st 2016 to keep counts consistent for each month and day. Some key variables from this data set are 

* Opened and Closed: When the request was made and when it was cleaned up
* Request Type: Bulky items, Hazardous materials, ...
* Request Details: Mattress, Graffiti, Encampment Cleanup, ...
* Neighborhood: Downtown, Mission, Financial District, ...
* Point: The coordinates of the request
* Source: Voice in, Open311 App, Twitter, ...

## Adding Neighborhood Demographic Data

Adding demographic data to our primary data source, was not as simple as we thought. The avaliable census data is not by neighborhood and all websites we could find that used the kind of data we wanted did not list their source. So we ended up scraping [this website](http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html) which gives a statistics type of presentation on demographics for each neighborhood. This required a bit of cleaning due to differences between the neighborhood names between the scraped data and our primary data. 

## Getting Data for SF Pride and Outside Lands 

We are interested in if big yearly events cause more cleaning requests. In our analysis section, we learned that there are more requests in the summer, so we wanted to find two big summer events. San Francisco pride is a parade and festival held at the end of June each year to celebrate the lesbian, gay, bisexual, and transgender (LGBT) people and their allies. Outside lands is s a music festival held annually at Golden Gate Park. To get data on the dates these events were held each year of our primary data set and the attendance each year, we scraped wikipedia. [This page](https://en.wikipedia.org/wiki/San_Francisco_Pride) for Pride and [this page](https://en.wikipedia.org/wiki/Outside_Lands_Music_and_Arts_Festival) for Outside Lands. 

## More Detail on Our Data Munging Process

[Here]() is the jupyter notebook with all of our data munging exported to HTML.

# Analysis and Visualizations

