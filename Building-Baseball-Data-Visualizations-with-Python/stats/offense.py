from data import games 
import pandas as pd
import matplotlib.pyplot as plt

#select all rows that have a type of play
plays = games[games['type'] == 'play']
#plays = games.loc[games['type'] == 'play', :]
plays.columns = ['type','inning','team','player','count','pitches','event','game_id','year']

#create hits DF from plays DF 
hits = plays.loc[plays['event'].str.contains('^(?:S(?!B)|D|T|HR)'),['inning','event']]

#change the type of inning columns to numeric
hits.loc[:,'inning'] = pd.to_numeric(hits.loc[:,'inning'])

#create a dictionary 
replacements = {
  r'^S(.*)' : 'single',
  r'^D(.*)' : 'double',
  r'^T(.*)' : 'triple',
  r'^HR(.*)' :'hr'
}

#change the column event and assign result to new dataframe
hit_type = hits['event'].replace(replacements,regex=True)

#add the new column as hit_type to the hits DF
hits = hits.assign(hit_type=hit_type)

#group by inning and hit_type , count number of hits per inning
hits = hits.groupby(by=['inning','hit_type']).size()
hits = hits.reset_index(name='count')

#categorical hit type to 4 groups
hits['hit_type'] = pd.Categorical(hits['hit_type'],['single','double','triple','hr'],ordered=True)

#sort the value of hits DF by inning and hit_type
hits = hits.sort_values(by=['inning','hit_type'])

#pivot on hits DF
hits = hits.pivot(index='inning',columns='hit_type',values='count')

#create a barchar, each bar represent the value as count of hits
hits.plot.bar(stacked=True)

plt.xlabel('Inning')
plt.ylabel('Count')
plt.show()



print(hits.head())

