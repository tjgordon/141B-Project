This is a final project for statistics 141B taken winter quarter 2017. 

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

## Datasets  
Our primary dataset is the Street and Sidewalk Cleaning dataset from SF OpenData:  
https://data.sfgov.org/City-Management-and-Ethics/Street-and-Sidewalk-Cleaning/h3eg-w3pj   
We plan to use this dataset for geographic boundaries of the neighborhoods:  
https://data.sfgov.org/Geographic-Locations-and-Boundaries/Analysis-Neighborhoods/p5b7-5n3h/data   
We also hope to use information about the demographics of the different neighborhoods. One possible source, which will probably require scraping, is:  
http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html  


## Questions  
Do the type and frequency of requests differ by neighborhood? How does this relate to neighborhood demographics?  
Does the time taken to fulfill requests differ by type and neighborhood?  

What are the more common sources of how the cleaning request was sent in? How common is it to submit a request through twitter? Does that affect the amount of time it took the request to be fulfilled?  





**Other Question ideas**  
- Important events? (Ex: OWS?)
- Find proportion of a type of requests (ex: mattress)  
- Are the neighborhood names with slashes on the borders of two neighborhoods?  
- Determine day of week using doomsday algorithm and do analysis by weekday.  
- histograms of columns
- interactive maps with https://github.com/python-visualization/folium
- Requests by income in neighborhood
- other demographics
    - housing prices
- more specific neighborhoods
- maps
    - by request type (mattresses)
    - refrigerator
    - mattresses
- time to fill requests
    - by neighborhood
- parse address
- sources
    - twitter
    - open311?
    
**Parades and Festivals**
(Make list of events manually and scrape wiki for past dates of these events)
- San Francisco Pride
- Outside Lands Music and Arts Festival
- San Francisco Chinese New Year Festival and Parade

street = street.merge(demographic,  on = "Neighborhood", how = "left")
street.head()
