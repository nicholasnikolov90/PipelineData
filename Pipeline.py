import pandas as pd
import numpy as np
import re

#Author: Nick Nikolov

#INSTRUCTIONS
#1. Copy entire Code stress results grid, general stress results grid, and displacements results grid into separate .csv files.
#2. Create a .csv file for all bend node numbers / any nodes you need results at.
#3. Results will be saved in the same folder in a .xlsx format.

#NOTES
#Only make modifications to this first code block. 

#*INPUTS* 
#Legend of variables
#code_stresses = code stress results grid, saved as a csv
#general_stresses = general stress results grid, saved as a csv
#displacements = displacements results grid, saved as a csv
#bend_nodes = node numbers of bends. Input into the first column A. Start at Node A01. A00 should be "nodes"

#reads all the data from csv files
code_stresses = pd.read_csv('100cs.csv', usecols = ['Point', 'Category', 'Stress', 'Allowable'], low_memory=False).tail(-1)
general_stresses = pd.read_csv('100G.csv',usecols = ['Point', 'Total Stress'], low_memory=False).tail(-1)
displacements = pd.read_csv('100d.csv',usecols = ['Point', 'DX', 'DY','DZ'], low_memory=False).tail(-1)
bend_nodes = pd.read_csv("nodes.csv")

#convert the total stress column to a float, to use in calculations
general_stresses['Total Stress'] = general_stresses['Total Stress'].astype(float)

#Data clean up
#Removes all duplicates based on soil points and bend midpoints
code_stresses['Point'] = code_stresses['Point'].str.split('[ NFM]').str[0]
general_stresses['Point'] = general_stresses['Point'].str.split('[ NMF]').str[0]
displacements['Point'] = displacements['Point'].str.split('[ NMF]').str[0]

#Manually calculate 'ratio' column of the code stresses to get more significant digits than the code stress tab gives
code_stresses['Ratio'] = ((code_stresses['Stress'].astype(float) / code_stresses['Allowable'].astype(float))*100).round(2)
code_stresses = code_stresses.set_index(['Point', 'Category'])
code_stresses = code_stresses.groupby(level=['Point', 'Category']).max().sort_index()

#extract material allowables at each node (only for use in general stress array)
allowables = code_stresses.reset_index()
allowables = allowables.set_index(['Point', 'Category', 'Allowable'])
allowables = allowables.groupby(level=['Point', 'Allowable']).max().reset_index().drop(['Stress', 'Ratio'], axis = 1).set_index(['Point']).groupby(level='Point').max().sort_index()

#General stress cleanup
general_stresses = general_stresses.set_index(['Point'])
general_stresses = general_stresses.groupby(level='Point').max().sort_index()
#Add the ratio column to general stress
general_stresses['General Stress Ratio'] = ((general_stresses['Total Stress'].astype(float) /allowables['Allowable'].astype(float))*100).round(1)

#turn general stress and code stresses into pivot tables
code_stresses = pd.pivot_table(code_stresses, values = 'Ratio', index = ['Point'], columns = 'Category')
general_stresses = pd.pivot_table(general_stresses, values='General Stress Ratio', index = ['Point'])

#Displacements: calculate horizontal displacements
#Creates a new column for horizontal displacement (sqrt(x^2 + z^2))
#Remove all duplicates of displacements, leave only max horizontal and max vertical displacements
displacements['Horizontal Displacement'] = ((displacements['DX'].astype(float)**2 + displacements['DZ'].astype(float)**2)**0.5).round(2)
displacements = displacements.set_index(['Point'])
displacements = displacements.groupby(level='Point').max()
displacements = displacements.rename(columns={'DY': 'Vertical Displacement'}).drop(['DX','DZ'], axis=1) # leave only the maximum displacements

#Merge all results into one sheet
overall_results = pd.merge(displacements, code_stresses, left_on=['Point'], right_index=True)
overall_results = pd.merge(overall_results, general_stresses, left_on=['Point'], right_index=True)

#RESULTS. 
#Prints only the results for the nodes needed
BendResults = overall_results.loc[bend_nodes['Nodes']]
print(BendResults)

#OUTPUT RESULTS TO EXCEL
BendResults.to_excel("output.xlsx")  