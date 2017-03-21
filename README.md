# San Francisco Street Cleaning Analysis  

[https://data.sfgov.org/City-Management-and-Ethics/Street-and-Sidewalk-Cleaning/h3eg-w3pj](https://data.sfgov.org/City-Management-and-Ethics/Street-and-Sidewalk-Cleaning/h3eg-w3pj)  

## Plan of attack  
We are taking a bit of an exploratory data analysis approach by seeing what questions we have as we go along and what data we want to try and find to add in. We plan on using visualizations as much as possible and we definitely want to make use of plotting over a map of SF.  

## New Phrasing of Question
How does it work in a big city when a mattress is left out on the street, human waste is all over the street, or when a garbage can overflows? How do these cleaning requests vary in type and length to fulfill based on type or neighborhood demographics. 

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
