import pandas as pd
import numpy as np
import re

#INSTRUCTIONS
#1. Copy entire Code stress results grid, general stress results grid, and displacements results grid into separate .csv files.
#2. Create a .csv file for all bend node numbers / any nodes you need results at.
#3. Results will be saved in the same folder in a .xlsx format.

#NOTES
#Only make modifications to this first code block. 

#*INPUTS* 
#Legend of variables
#cs = code stress results grid, saved as a csv
#gs = general stress results grid, saved as a csv
#disp = displacements results grid, saved as a csv
#BendNodes = node numbers of bends. Input into the first column A. Start at Node A01. A00 should be "nodes"
cs = pd.read_csv('100cs.csv', usecols = ['Point', 'Category', 'Stress', 'Allowable'], low_memory=False).tail(-1)
gs = pd.read_csv('100G.csv',usecols = ['Point', 'Total Stress'], low_memory=False).tail(-1)
disp = pd.read_csv('100d.csv',usecols = ['Point', 'DX', 'DY','DZ'], low_memory=False).tail(-1)
BendNodes = pd.read_csv("nodes.csv")

#General stress, convert the total stress column to a float, to use in calculation
gs['Total Stress'] = gs['Total Stress'].astype(float)


#Data clean up
#Removes all duplicates based on soil points and bend midpoints
#replaces the points column in the original dataset to avoid any extra memory use
cs['Point'] = cs['Point'].str.split('[ NFM]').str[0]
gs['Point'] = gs['Point'].str.split('[ NMF]').str[0]
disp['Point'] = disp['Point'].str.split('[ NMF]').str[0]

#Manually calculate 'ratio' column to get more significant digits than the code stress tab gives
cs['Ratio'] = ((cs['Stress'].astype(float) / cs['Allowable'].astype(float))*100).round(2)
cs = cs.set_index(['Point', 'Category'])
cs = cs.groupby(level=['Point', 'Category']).max().sort_index()

#extract allowables only for use in general stress array
allowables = cs.reset_index()
allowables = allowables.set_index(['Point', 'Category', 'Allowable'])
allowables = allowables.groupby(level=['Point', 'Allowable']).max().reset_index().drop(['Stress', 'Ratio'], axis = 1).set_index(['Point']).groupby(level='Point').max().sort_index()

#General stress cleanu
gs = gs.set_index(['Point'])
gs = gs.groupby(level='Point').max().sort_index()
#Add the ratio column to general stress
gs['General Stress Ratio'] = ((gs['Total Stress'].astype(float) /allowables['Allowable'].astype(float))*100).round(1)

#print(cs['Category']['General Stress'] = gs['General Stress Ratio'])
cs = cs.reset_index()
gs = gs.reset_index()
print(cs)
print(gs)
overall = pd.merge(gs, cs, on=['Point'])
print(overall)

#overall_results = pd.merge(gs, cs, left_index=True, right_index=True)
#print(overall_results)

#Displacements: calculate horizontal displacements
#Creates a new column HD = horizontal displacement (sqrt(x^2 + z^2))
#Remove all duplicates of displacements, leave only max horizontal and max vertical displacements
disp['Horizontal Displacement'] = ((disp['DX'].astype(float)**2 + disp['DZ'].astype(float)**2)**0.5).round(2)
disp = disp.set_index(['Point'])
disp = disp.groupby(level='Point').max()
disp = disp.rename(columns={'DY': 'Vertical Displacement'}).drop(['DX','DZ'], axis=1) # leave only the maximum displacements




#Creates the code stress results table using a pivot table. 
table = pd.pivot_table(cs, values='Ratio',index=points, columns='Category', aggfunc=np.max)

#combine the general stresses and code stresses & cleanup the index column
#Change round(x) to x number of decimal points needed.
df_merged = table.merge(merged[['Point', 'General', 'Horizontal Displacement', 'Vertical Displacements']], on='Point').round(1)
df_merged = df_merged.set_index('Point').T

#RESULTS. This displays results localy for debugging purposes. 
BendResults = df_merged[BendNodes['Nodes']].T
BendResults

#OUTPUT RESULTS TO EXCEL
BendResults.to_excel("output.xlsx")  