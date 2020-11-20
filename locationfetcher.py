# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 19:43:46 2020

@author: CCCam
"""

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd

#initialize geolocator object
geolocator = Nominatim(user_agent='CCCammilleri@gmail.com')
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


#load in dataset
df = pd.read_csv(r'C:\Users\CCCam\OneDrive\DataScience\IBM\US_Accidents_June20.csv', index_col=0)

knowns = dict()
def getLocations(df):
    print('starting...')
    i=0
    
    #get list of unique city, state, and county combinations
    copy = df.copy()
    combos = copy[['City','State','County']].apply(tuple, axis=1)
    uniques = combos.unique()
    
    #for each combination, fetch its location
    for unique in uniques:
        #if city is null, skip over it 
        if isinstance(unique[0],float):
            continue
        
        location = geocode(unique[0]+', '+unique[1]+', United States')
        key = unique[0]+unique[1]+unique[2]
        
        #if city not found, try removing spaces from name
        if location is None:
            location = geocode(unique[0].replace(' ','')+', '+unique[1]+', United States')
            
        #if still not found, take location of most common city in county
        try:
            if location is None:
                location =  geocode(df[(df['State']==unique[1])& (df['County']==unique[2])]['City'].mode().item()+ ', '+unique[1]+', United States')
        except:
            print('error caught')
        #if still not found, take location of most common city in state
        if location is None:
            location =  geocode(df[(df['State']==unique[1])]['City'].mode().item() + ', ' + unique[1]+', United States')
        
        #if all else fails, do nothing
        if location is None:
            print()
        
        #add location to dictionary
        city_lat = location[-1][0]
        city_lng= location[-1][1]
        knowns[key] = (city_lat,city_lng)
        
        #report progress every 1000 entries
        i+=1
        if i%1000 ==0:
            print(i, ' rows complete')
        
getLocations(df)

#create dataframe from dictionary
city_locations = pd.DataFrame(knowns).transpose()

#save as csv file
city_locations.to_csv('citylocs.csv')

city_locations.head()