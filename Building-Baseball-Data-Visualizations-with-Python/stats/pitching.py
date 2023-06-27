import pandas as  pd 
import matplotlib
import matplotlib.pyplot as plt
from data import games 

#new DataFrame , with condition type column equal to play
plays = games.loc[games['type']=='play', :]

#create a newdataframe by filtering directly from the original dataframe
strike_outs = plays[plays['event'].str.contains('K')]
strike_outs = strike_outs.groupby(['year','game_id']).size()

#convert strikeout from groupby object to Dataframe and name 
#create the new index column, and set the name as strike_outs for the previous index column
strike_outs = strike_outs.reset_index(name='strike_outs')

#apply the to_numeric function to multiple columns in Dataframe
strike_outs = strike_outs.loc[:,['year','strike_outs']].apply(pd.to_numeric)

#plot
strike_outs.plot(x='year',y='strike_outs',kind='scatter')
plt.legend(['Strike Outs'])
plt.show()
