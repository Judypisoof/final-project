# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 19:55:49 2023

@author: 83531
"""
import json
import pandas as pd
import plotly.express as px
from plotly.offline import plot
cache_file = open("top_100_beaches.json","r", encoding='utf-8')
top_100_beaches = json.loads(cache_file.read())
cache_file.close()

cache_file = open("country_info.json","r", encoding='utf-8')
country_beaches = json.loads(cache_file.read())
cache_file.close()

all_beaches = top_100_beaches.copy()
            
option = '0'
while option != '5':
    option = input("1. Give information on a specific beach\n"
                   "2. Give the recommendation beach list for a specific country\n"
                   "3. Give the world top 100 beach list\n"
                   "4. Give the statistical data of different countires beached.\n"
                   "5. Exit program.\n"
                   "Please input number 1 to 5:")
    if option == "1":
        second_option = input("Give the name of this beach: ")
        if second_option in all_beaches.keys():
            print(all_beaches[second_option])
        else:
            print("this beach is not in our system, please find another one.")
    elif option == "3":
        print(list(top_100_beaches.keys()))
    elif option == "2":     
        second_option = input("Give the name of the country: ")
        if second_option in country_beaches.keys():
            print(country_beaches[second_option]["beaches"].keys())
        else:
            print("this country is not in our system, please find another one.")            
    elif option == "4":
        df = {}
        for key in country_beaches.keys():
            num_beaches = len(country_beaches[key]["beaches"])
            df[key] = num_beaches
        data = pd.DataFrame(list(df.items()), columns=['Country', 'Num_Beaches'])
        fig = px.bar(data, x='Country', y='Num_Beaches', title='Number of Beaches in Each Country')
        plot(fig, filename='pl.html')
    elif option == "5":
        break
    else:
        print("warning: invalid input, please input number between 1 and 5:")