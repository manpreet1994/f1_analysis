# -*- coding: utf-8 -*-
"""
Created on Sat May  6 22:54:29 2023

@author: manpreet
"""
import json
import pandas as pd
import os
from tqdm import tqdm
from itertools import combinations
from os.path import exists
import altair as alt

#%%
def read_json(json_name):
	with open('{}.json'.format(json_name)) as user_file:
		file_contents = json.load(user_file)
	return file_contents

def save_json(json_name, data):
    with open(json_name+'.json', 'w') as f:
        json.dump(data, f)
    print("saved ", json_name)

def generate_top_teams_and_write(total_cost = 100, top_k = 3):

	if not exists("data/fantasy_teams/entry.json"):
		save_json("data/fantasy_teams/entry.json", {})

	entries_json = read_json("data/fantasy_teams/entry")
	entry_exists = True if str(round(float(total_cost), 2)) in entries_json.keys() else False

	if not entry_exists:

		driver_names = pd.read_csv('data/driver.csv') 
		team_names = pd.read_csv('data/team.csv')

		race_driver_data = pd.read_csv('data/race_driver_metadata.csv')
		race_team_data = pd.read_csv('data/race_team_metadata.csv')

		race_driver_data = race_driver_data[~pd.isna(race_driver_data.score)]
		race_team_data = race_team_data[~pd.isna(race_team_data.score)]

		latest_driver_data = race_driver_data[race_driver_data.race_no == max(race_driver_data.race_no)]
		latest_team_data = race_team_data[race_team_data.race_no == max(race_team_data.race_no)]

		# aggregated_matrix 
		aggregated_driver_matrix = latest_driver_data[['driver_id', 'score', 'cost']]
		aggregated_driver_matrix['mean_score'] = list(race_driver_data.groupby('driver_id', as_index=False).mean()['score'])
		aggregated_driver_matrix['score_variance'] = list(race_driver_data.groupby('driver_id', as_index=False).var()['score'])
		aggregated_driver_matrix['score_variance'] = round(aggregated_driver_matrix['score_variance']/max(aggregated_driver_matrix['score_variance']),3)


		aggregated_team_matrix = latest_team_data[['team_id', 'score', 'cost']]
		aggregated_team_matrix['mean_score'] = list(race_team_data.groupby('team_id', as_index=False).mean()['score'])
		aggregated_team_matrix['score_variance'] = list(race_team_data.groupby('team_id', as_index=False).var()['score'])
		aggregated_team_matrix['score_variance'] = round(aggregated_team_matrix['score_variance']/max(aggregated_team_matrix['score_variance']),3)

		combo_list = []
		avg_score = []

		for d_combo in tqdm(combinations(range(1,21), 5)):
		    for t_combo in combinations(range(21,25), 2):
		        driver_sum = sum(latest_driver_data[latest_driver_data.driver_id.isin(d_combo)]['cost'])
		        team_sum = sum(latest_team_data[latest_team_data.team_id.isin(t_combo)]['cost'])
		        if driver_sum + team_sum <= total_cost:
		            a = driver_names[driver_names.driver_id.isin(d_combo)]['driver_name'].tolist()
		            b = team_names[team_names.team_id.isin(t_combo)]['team_name'].tolist()
		            avg_driver_score = sum(aggregated_driver_matrix[aggregated_driver_matrix.driver_id.isin(d_combo)]['mean_score'])
		            avg_driver_var = sum(aggregated_driver_matrix[aggregated_driver_matrix.driver_id.isin(d_combo)]['score_variance'])
		            avg_team_score = sum(aggregated_team_matrix[aggregated_team_matrix.team_id.isin(t_combo)]['mean_score'])
		            avg_team_var = sum(aggregated_team_matrix[aggregated_team_matrix.team_id.isin(t_combo)]['score_variance'])
		            combo_list.append(((a+b), avg_driver_score+avg_team_score, avg_driver_var+avg_team_var))

		sorted_combo = sorted(combo_list, key = lambda x: (x[1], x[2]), reverse=True)[:top_k]
		save_json("data/fantasy_teams/fantasy_teams_{}".format(total_cost), {"top_fantasy_teams": sorted_combo} )
		entries_json[round(float(total_cost), 2)] = True
		save_json("data/fantasy_teams/entry", entries_json)
	else:
		print("already processed in past")


def get_fantasy_team_scores(fantasy_team_1, id_no):

	driver_names = pd.read_csv('data/driver.csv') 
	team_names = pd.read_csv('data/team.csv')

	race_driver_data = pd.read_csv('data/race_driver_metadata.csv')
	race_team_data = pd.read_csv('data/race_team_metadata.csv')

    #drivers
	abc = race_driver_data.merge(driver_names)
	a = abc[abc['driver_name'].isin(fantasy_team_1[0:5])].groupby('race_no').sum()
    #teams
	constructor = race_team_data.merge(team_names)
	b = constructor[constructor['team_name'].isin(fantasy_team_1[-2:])].groupby('race_no').sum()
    
	return (a+b).fillna(id_no)

def plot_fantasy_team_comparisons(sorted_combo, cost):
	fantasy = pd.DataFrame()
	fantasy_team_1 = sorted_combo[0][0]
	fantasy_team_2 = sorted_combo[1][0]
	fantasy_team_3 = sorted_combo[2][0]
	fantasy_team_4 = ['max', 'alo', 'per', 'zhou', 'str', 'redbull', 'aston']

	fantasy = get_fantasy_team_scores(fantasy_team_1, "fantasy_team_1")
	fantasy = pd.concat([fantasy, get_fantasy_team_scores(fantasy_team_2, "fantasy_team_2")], axis =0)
	fantasy = pd.concat([fantasy, get_fantasy_team_scores(fantasy_team_3, "fantasy_team_3")], axis =0)
	fantasy = pd.concat([fantasy, get_fantasy_team_scores(fantasy_team_4, "your_team")], axis =0)
	fantasy['race_no'] = fantasy.index
	fantasy

	plot = alt.Chart(fantasy, width = 600, title="Fantasy teams over the course of races").mark_line(point=True).encode(
	x = "race_no:N",
	y = "score",
	color = "team_id:N",
	tooltip = ['cost', 'score'])
	plot.save('templates/fantasy_comparison_{}.html'.format(cost))