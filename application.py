from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo 


application = Flask(__name__)
app=application

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search = request.form['content'].replace(" ","")
            url = "https://www.flipkart.com/search?q=" + search

            webpage = requests.get(url)
            html_webpage = bs (webpage.text , "html.parser")
            
            bigbox= html_webpage.find_all('a' , {"class" : ["IRpwTa","_1fQZEK"]})

            link_list = []
            for i in bigbox:
                lnk = "https://www.flipkart.com" + i["href"]
                link_list.append(lnk)
            
            filename = search + ".csv"
            fp = open(filename , "w")
            headers = "Title, Price, Rating, Total Rating\n"
            fp.write(headers)
            reviews = []
            for details in link_list:
                try:
                    web_pg = requests.get(details)    
                    web_pg.encoding='utf-8'
                    html_pg = bs ( web_pg.text , "html.parser")
                except Exception as e:
                    print("Exception While Fetching Page: ",e)

                try:
                    title = html_pg.find("span" , {"class": "B_NuCI"}).text
                except:
                    title = "No Title"
                    
                try:
                    price = html_pg.find("div" , {"class": "_30jeq3 _16Jk6d"}).text
                except:
                    price = "Not Mention"
                    
                try:
                    rating = html_pg.find("div" , {"class": "_3LWZlK"}).text 
                except:
                    rating = "No Rating"
                    

                try:
                    total_rating = html_pg.find("span" , {"class": "_2_R_DZ"}).text
                except:
                    total_rating = "No Ratings"
                    

                mydict = {"Title": title, "Price":price , "Rating": rating , "Total Rating": total_rating }
                
                reviews.append(mydict)
            

            
            client = pymongo.MongoClient("mongodb+srv://arjunvermam:2758@cluster0.uqflnth.mongodb.net/?retryWrites=true&w=majority")
            db = client["flipkart_scrap"]
            flip_scrap_coll = db["flipkart_scrap_data"]
            flip_scrap_coll.insert_many(reviews)                
            return render_template("results.html", reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print("Exception is ",e)
            
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")