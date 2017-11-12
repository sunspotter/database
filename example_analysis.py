import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('sunspotter.sqlite3')

cur = conn.cursor()

# From the same table
df = pd.read_sql_query("select i.area, i.flux from images as i;", conn)
df.plot(x='area', y='flux', kind='scatter')
plt.savefig('area_flux.png')

# Joining images with rank
df = pd.read_sql_query("select r.score, i.area from zoorank as r inner join images as i on i.id = r.image_id;", conn)
df.plot(x='score', y='area', kind='scatter')
plt.savefig('score_area.png')

df = pd.read_sql_query("select r.score, i.flux from zoorank as r inner join images as i on i.id = r.image_id;", conn)
df.plot(x='score', y='flux', kind='scatter')
plt.savefig('score_flux.png')

# Joining images, rank and fitsfiles (dates)
df = pd.read_sql_query("""
select r.score, f.obs_date as date from zoorank as r inner join images as i on i.id = r.image_id inner join fitsfiles as f on f.id = i.id_filename;
""", conn)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df['score'].plot()
plt.savefig('date_score.png')
