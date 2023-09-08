#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 17:34:57 2021

@author: manpreet
"""

from flask import Flask, render_template, request, Response, redirect
import time
import json
import requests
import os
import pandas as pd
from datetime import datetime
from fantasy_combinator import (generate_top_teams_and_write, 
    read_json, plot_fantasy_team_comparisons,
    refresh_graphs
    )
from model_training import train, predict
PASS = "8960"

#%%
app = Flask(__name__)

@app.route('/generate_top_fantasy_teams')
def generate_top_fantasy_teams():
    print(request.args["cost"])
    generate_top_teams_and_write(float(request.args["cost"]), 3)
    return redirect("/", code=200) 

@app.route('/update_metadata', methods = ['POST'])
def update_metadata():
    if request.method == 'POST':
        if request.form.get("psw") == PASS:
            f = request.files['race_driver_metadata']
            f.save(os.path.join("../data",f.filename))
            # return 'file uploaded successfully'
            f = request.files['race_team_metadata']
            f.save(os.path.join("../data",f.filename))
            refresh_graphs()
            return redirect("/home", code=200) 
        else:
            return redirect("/home", code=400) 

@app.route('/update_free_practice', methods = ['POST'])
def update_free_practice():
    passwd = request.form.get('psw')
    if passwd == PASS:
        f = request.files['free_practice_metadata']
        f.save(os.path.join("../data",f.filename))
        train()
        return redirect("/home", code=200)
    else:
        return redirect("/home", code=400)

@app.route('/')
@app.route('/home')
def index(text=None):
    return render_template('index.html')

@app.route('/driver_per_race')
def driver_per_race():
    return render_template('driver_teams/driver_per_race.html')

@app.route('/driver_per_race_per_cost')
def driver_per_race_per_cost():
    return render_template('driver_teams/driver_per_race_per_cost.html')

@app.route('/team_per_race')
def team_per_race():
    return render_template('driver_teams/team_per_race.html')

@app.route('/team_per_race_per_cost')
def team_per_race_per_cost():
    return render_template('driver_teams/team_per_race_per_cost.html')

@app.route('/fantasy_entries')
def fantasy_entries():
    return read_json('../data/fantasy_teams/entry') 

@app.route('/driver_latest_cost')
def driver_latest_cost():
    driver_names = pd.read_csv('../data/driver.csv') 
    race_driver_data = pd.read_csv('../data/race_driver_metadata.csv')
    latest_cost_df = race_driver_data[race_driver_data.race_no == max(race_driver_data.race_no)]
    latest_cost_df = latest_cost_df.merge(driver_names)
    final_json = [{"id":k+"_cost", "cost": v} for k,v in zip(latest_cost_df['driver_name'], latest_cost_df['cost'])]
    return {"response" : final_json}

@app.route('/get_free_practice')
def get_free_practice():
    free_practice_data = pd.read_csv('../data/free_practice_metadata.csv')
    free_practice_data = free_practice_data[free_practice_data.race_no == max(free_practice_data.race_no)]
    final_json = [{"fp1_id":d+"_fp1", "fp1_score": fp1, "fp2_id":d+"_fp2", "fp2_score": fp2 ,"fp3_id":d+"_fp3", "fp3_score": fp3} for d,fp1,fp2,fp3 in zip(free_practice_data['driver_name'], free_practice_data['fp1'], free_practice_data['fp2'], free_practice_data['fp3'])]
    return {"response" : final_json}


@app.route('/predict', methods = ['POST'])
def make_prediction():
    driver_names = pd.read_csv('../data/driver.csv') 
    fp1_list = []
    fp2_list = []
    fp3_list = []
    cost_list = []

    input_data = [(k,v) for k,v  in request.form.items()]

    for i in range(len(input_data)):
        if input_data[i][0].split("_")[-1] != "pred":
            if i%4 ==0:
                fp1_list.append(float(input_data[i][1].strip()))
            elif i%4 ==1:
                fp2_list.append(float(input_data[i][1].strip()))
            elif i%4 ==2 :
                fp3_list.append(float(input_data[i][1].strip()))
            else:
                cost_list.append(float(input_data[i][1].strip()))

    prediction_df = pd.DataFrame({
        "fp1": fp1_list,
        "fp2": fp2_list,
        "fp3": fp3_list,
        "cost": cost_list
    })
    y_pred = predict(prediction_df)
    return {"prediction" : [{"id":k+"_pred", "pred":v } for k,v in zip(driver_names.driver_name, y_pred)]}

@app.route('/fantasy_teams_comparison')
def fantasy_team_comparisons():
    print(request.args.get('cost_options', 100.0))
    cost_for_fantasy = float(request.args.get('cost_options', 100.0))
    print(cost_for_fantasy)
    combos = read_json('../data/fantasy_teams/fantasy_teams_{}'.format(cost_for_fantasy))
    print(combos)
    plot_fantasy_team_comparisons(combos['top_fantasy_teams'], cost_for_fantasy)
    return render_template('fantasy_comparisons/fantasy_comparison_{}.html'.format(cost_for_fantasy))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)