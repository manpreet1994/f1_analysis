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
from model_training import train

#%%
app = Flask(__name__)

@app.route('/generate_top_fantasy_teams')
def generate_top_fantasy_teams():
    print(request.args["cost"])
    generate_top_teams_and_write(float(request.args["cost"]), 3)
    return redirect("/", code=200) 

# @app.route('/refresh_graphs', methods = ['GET','POST'])
# def refresh_graphs():
#     refresh_graphs()

@app.route('/update_metadata', methods = ['POST'])
def update_metadata():
   if request.method == 'POST':

      f = request.files['race_driver_metadata']
      f.save(os.path.join("../data",f.filename))
      # return 'file uploaded successfully'
      f = request.files['race_team_metadata']
      f.save(os.path.join("../data",f.filename))
      refresh_graphs()
      return redirect("/home", code=200) 

@app.route('/update_free_practice', methods = ['POST'])
def update_free_practice():
    f = request.files['free_practice_metadata']
    f.save(os.path.join("../data",f.filename))
    train()
    return redirect("/home")

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