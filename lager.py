#!/usr/bin/python3
import cgi
import sqlite3
import time
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
CONTENT_PATH = "/usr/share/nginx/www/dashboard/"

def drawplot(time, metric_name, x,y):
    # draw a graph for this item
    fig, ax = plt.subplots()
    ax.plot(x,y)
    ax.set(xlabel='time (s)', ylabel=metric_name, title=metric_name + ' over time')
    ax.grid()
    imgname = str(time) + '_' + metric_name + '.png'
    fig.savefig(CONTENT_PATH + imgname)
    return str(imgname)

def drawtodash( metric_name, x,y):
    filebody = "<table><tr><th>Time</th><th>" + metric_name + "</th></tr>"
    for i in range(len(x)):
        filebody += "<tr><td>" + str(x[i]) + "</td><td>" + str(y[i]) + "</td></tr>\n"
    filebody += "</table>"
    return filebody

def main():
  form = cgi.FieldStorage()
  now = int(time.time())
  print("Content-type: text/html\n\n")

  # creates the file if it doesn't exist 
  conn = sqlite3.connect('analytics.db')

  # create the big table if it does not exist
  conn.execute("create table if not exists AnalyticResults (time INTEGER, key TEXT, value REAL)")
  metrics = []
  for i in form.keys():
    metrics.append((now,cgi.escape(form[i].name, True), cgi.escape(form[i].value, True)))
    #debugging... print(" | " + form[i].name + " = " + form[i].value)
  conn.executemany('INSERT INTO AnalyticResults VALUES (?, ?, ?)', metrics)
  conn.commit()

  # pull the data and sort respective to the variables.
  # then for each section, print by time.
  cur = conn.cursor()
  cur.execute('SELECT time, key, value FROM AnalyticResults ORDER BY key, time')
  rows = cur.fetchall()
  lastkey = ""
  filebody = "<html><body>"
  x = []
  y = []
  for row in rows:
    if lastkey != row[1]:
        if lastkey != "":
            imgname = drawplot(now, lastkey, x, y)
            filebody += "<img src='" + imgname + "'></img>"
            filebody += drawtodash(lastkey, x, y)
            x.clear()
            y.clear()
    x.append(row[0])
    y.append(row[2])
    lastkey = row[1]
  if lastkey != "":
    imgname = drawplot(now, lastkey, x, y)
    filebody += "<img src='" + imgname + "'></img>"
    filebody += drawtodash(lastkey, x, y)
  conn.close()
  filebody += "</body></html>"

  # now write the dashboard itself
  dashboard_file = open(CONTENT_PATH + 'index.html', 'w')
  dashboard_file.write(filebody)
  dashboard_file.close()
  
  # write the result html file.
if __name__ == "__main__":
  main()
