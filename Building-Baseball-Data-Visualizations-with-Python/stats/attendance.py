import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
import data

#select data.games DataFrame with the conditions and assign it to attendance DataFrame
games = data.games
attendance = games.loc[(games['type'] == 'info') & (games['multi2'] == 'attendance'), ['year' , 'multi3']]

#change the column name of the attendance DataFrame
attendance.columns = ['year','attendance']

#select only attendance and change to numeric, change at the original place
attendance['attendance'] = pd.to_numeric(attendance.loc[:,'attendance'],errors='coerce')

#plot for attendance DataFrame with keyword
attendance.plot(x='year',y='attendance',figsize=(15,7),kind='bar')

plt.xlabel('year')
plt.ylabel('attendance')

plt.axhline(x=attendance['attendance'].mean(),label='mean', linestyle='--',color='green')
plt.show()

