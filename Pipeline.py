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

#General stress cleanup
gs = gs.set_index(['Point'])
gs = gs.groupby(level='Point').max().sort_index()
#Add the ratio column to general stress
gs['General Stress Ratio'] = ((gs['Total Stress'].astype(float) /allowables['Allowable'].astype(float))*100).round(1)

cs = pd.pivot_table(cs, values = 'Ratio', index = ['Point'], columns = 'Category')
gs = pd.pivot_table(gs, values='General Stress Ratio', index = ['Point'])

#Displacements: calculate horizontal displacements
#Creates a new column HD = horizontal displacement (sqrt(x^2 + z^2))
#Remove all duplicates of displacements, leave only max horizontal and max vertical displacements
disp['Horizontal Displacement'] = ((disp['DX'].astype(float)**2 + disp['DZ'].astype(float)**2)**0.5).round(2)
disp = disp.set_index(['Point'])
disp = disp.groupby(level='Point').max()
disp = disp.rename(columns={'DY': 'Vertical Displacement'}).drop(['DX','DZ'], axis=1) # leave only the maximum displacements

overall_results = pd.merge(disp, cs, left_on=['Point'], right_index=True)
overall_results = pd.merge(overall_results, gs, left_on=['Point'], right_index=True)

#RESULTS. 
#Prints only the results for the nodes needed
BendResults = overall_results.loc[BendNodes['Nodes']]

#OUTPUT RESULTS TO EXCEL
BendResults.to_excel("output.xlsx")  