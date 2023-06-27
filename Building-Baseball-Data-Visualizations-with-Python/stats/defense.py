import pandas as pd
import matplotlib.pyplot as plt
from frames import games, info, events

#create new dataframe
plays = games.query("type == 'play' and event != 'NP'")
plays.columns = ['type', 'inning', 'team', 'player', 'count', 'pitches', 'event', 'game_id', 'year']

#remove the consecutive columns in the players using shift()
pa = plays.loc[plays['player'].shift() != plays['player'] , ['year','game_id','inning','team','player']]

#groupby function, size function, reset_index
pa = pa.groupby(['year','game_id','team']).size()
pa = pa.reset_index(name='PA')

#create events ưith index
events = events.set_index(['year','game_id','team','event_type'])
events = events.unstack().fillna(0)
events = events.reset_index()

#change the formating of the columns
events.columns = events.columns.droplevel()
events.columns = ['year', 'game_id', 'team', 'BB', 'E', 'H', 'HBP', 'HR', 'ROE', 'SO']
events = events.rename_axis(None)

#merge 2 DF: events and pa
events_plus_pa = pd.merge(events,pa,how='outer', left_on=['year','game_id','team'], right_on = ['year','game_id','team'])

#merge 2 DF: events_plus_pa and info
defense = pd.merge(events_plus_pa,info,how='outer',left_on=['year','game_id','team'], right_on = ['year','game_id','team'])

#calculate the DEC
defense.loc[:,'DER'] = 1-((defense['H'] + defense['ROE'])/(defense['PA']-defense['BB']-defense['SO']-defense['HBP']-defense['HR']))
defense.loc[:,'year'] = pd.to_numeric(defense.loc[:,'year'],errors='coerce')

#create the DF der
der = defense.loc[defense['year']>= 1978,['year','defense','DER']]

#set pivot on der
der = der.pivot(index='year',columns ='defense',values='DER')

#ve plot
der.plot(der['year'],der['DER'],x_compat=True,xticks=range(1978,2000,4),rot=45)
plt.show()



print('This is defense \n', defense.head(5))
print('this is der \n', der.head(5))

