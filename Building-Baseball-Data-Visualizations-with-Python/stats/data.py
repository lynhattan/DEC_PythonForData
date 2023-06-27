import os
import glob 
import pandas as pd 

#set path to files in the games folder
#FIND all files end with .eve in game folder 
path = os.path.join(os.getcwd(), "games" , "*.EVE")
game_files = glob.glob(path)

#create empty game_frames list
game_frames = []

#loop through each file and game_files and read 
for file in game_files:
  #read csv file and set the column name
  game_frame = pd.read_csv(file, names = ['type','multi2','multi3','multi4','multi5','multi6','event'])
  game_frames.append(game_frame)

#concat all the elements in the list of game frames to a new DATAFRAME
games = pd.concat(game_frames)

#clean up - multi5 column, choose the cell that has value of ??
games.loc[games['multi5'] == '??','multi5'] = ""

#set game identifiers
#note this identifiers have 2 col , using print(identifiers.shape[1]) to know
identifiers = games['multi2'].str.extract(r'(.LS(\d{4})\d{5})')
#fill na by method forward fillings
identifiers = identifiers.fillna(method='ffill')
#change column name of dataframe
name_list = ['game_id','year']
identifiers.columns = name_list

#concat vertically (stacking rows) 
games = pd.concat([games,identifiers],axis=1,sort=False)

#cleanup, fill NaN  with ' '
games = games.fillna('')

#categorize data
games['type'] = pd.Categorical(games.loc[:,'type'])



  

