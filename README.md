This is a final project for Statistics 141B in winter quarter 2017 done using Python. 

Notebooks:  
- [Data Acquisition and Munging](https://tjgordon.github.io/141B-Project/SF Street Cleaning Project - Reading, Scraping, and Cleaning Data.html)  
- [Analysis and Results](https://tjgordon.github.io/141B-Project/SF%20Street%20Cleaning%20Project%20-%20Analysis.html)  


# Introduction

## Motivating Question 

The question that led us to this topic is: How do big cities deal with cleaning problems, like when a mattress is left out on the street, human waste is all over the road, or a garbage can overflows? 

We found that the answer to this is through street cleaning requests. Street cleaning requests are made by people in the city through phone calls, mobile applications, tweets, and more. People can specify location, type of request, and so on. 

## Plan of Attack 

We are focusing on San Francisco for our main analysis. Some of our initial questions are: 

* Does the frequency of requests change with time?
* How do cleaning requests vary in type and length to complete based on time of year or neighborhood? 
* Are these variations related to neighborhood demographics?

# Data

## Our Primary Data Source

Street and Sidewalk Cleaning from SF OpenData that we found [here](https://data.sfgov.org/City-Management-and-Ethics/Street-and-Sidewalk-Cleaning/h3eg-w3pj). The data set contains information on 693,612 cleaning requests in San Francisco. We subsetted the data to just examine requests from January 1st 2009 to December 31st 2016 to keep counts consistent for each month. Some key variables from this data set are: 

* Opened and Closed: When the request was made and when it was cleaned up
* Request Type: Bulky items, Hazardous materials, ...
* Request Details: Mattress, Graffiti, Encampment Cleanup, ...
* Neighborhood: Downtown, Mission, Financial District, ...
* Point: The coordinates of the request
* Source: Voice in, Open311 App, Twitter, ...

## Adding Neighborhood Demographic Data

Adding demographic data to our primary data source was not as straightforward. The avaliable census data is not by neighborhood and all websites we could find that used the kind of data we want did not list their source. So we ended up scraping [this website](http://www.city-data.com/nbmaps/neigh-San-Francisco-California.html) which lists demographic statistics for each neighborhood. This required a bit of cleaning due to differences between the neighborhood names in the scraped data and the cleaning requests data set. 

## Getting Data for SF Pride and Outside Lands 

We are interested whether or not big yearly events in San Francisco are associated with more cleaning requests. In our analysis section, we learned that there are more requests in the summer, so we wanted to find two big summer events to look into. San Francisco Pride is a parade and festival held at the end of June each year to celebrate the lesbian, gay, bisexual, and transgender (LGBT) people and their allies. Outside lands is a music festival held annually at Golden Gate Park. To get data on the dates these events were held each year and the yearly attendance, we scraped Wikipedia: [this page](https://en.wikipedia.org/wiki/San_Francisco_Pride) for Pride and [this page](https://en.wikipedia.org/wiki/Outside_Lands_Music_and_Arts_Festival) for Outside Lands. 

# More Detail on Our Data Munging Process

[Here](https://tjgordon.github.io/141B-Project/SF Street Cleaning Project - Reading, Scraping, and Cleaning Data.html) is the notebook with the data munging exported to HTML.

# Analysis and Visualizations

The HTML exported notebook containing our analysis, visualizations, and conclusions is [here](https://tjgordon.github.io/141B-Project/SF%20Street%20Cleaning%20Project%20-%20Analysis.html).   


-----

The notebook source files are available in [the repository here](https://github.com/tjgordon/141B-Project).
