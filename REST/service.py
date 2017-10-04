from __future__ import print_function
import json
import os
import urllib

#import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/")
def hello():
    return rest(request.args.get('food'))

@app.route("/test")
def tst():
    return "Yo"

def rest(food):
    food = food.replace(" ", "%20")
    #print(food)

    url = 'https://cse.google.com/cse?cx=partner-pub-7534866755529881%3Af9204j3v19y&ie=ISO-8859-1&q=' + food + '&sa=Search#gsc.tab=0&gsc.q=' + food + '&gsc.page=1'
    #print(url)
    #page = urllib.urlopen(url)
    browser = webdriver.PhantomJS()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup)
    urlTAG = soup.find('div', attrs = {'class': 'gs-per-result-labels'})
    urlOfRecipe = urlTAG['url']
    #print(urlOfRecipe)


    #page = urllib.urlopen(urlOfRecipe)
    page = urllib.request.urlopen(urlOfRecipe)


    #browser.get(urlOfRecipe)
    #html = browser.page_source
    #recipeSoup = BeautifulSoup(html, 'html.parser')
    recipeSoup = BeautifulSoup(page, 'html.parser')
    #print(recipeSoup)
    instructionTAG = recipeSoup.find('ol', attrs = {'class': 'instructions'})
    #print(str(recipeSoup).find('<ol class="instructions">'))
    #print(instructionTAG)
    inst = str(instructionTAG)
    curbeginOpen = 0
    curBeginEnd = 0;
    openVar = '<li itemprop="recipeInstructions">'
    endVar = '</li>'
    recipeSteps = []
    for i in range(0, len(instructionTAG)):
        locOpen = inst.find(openVar, curbeginOpen)
        locEnd = inst.find(endVar, curBeginEnd)
        if(locOpen == -1 or locEnd == -1):
            break
        curbeginOpen = locOpen + 1
        curBeginEnd = locEnd + 1
        instruc = inst[locOpen + len(openVar):locEnd]
        recipeSteps.append(instruc)
        #print(instruc)

    recipeSteps.reverse()
    resp = {"request": url, "steps": recipeSteps}
    return json.dumps(resp)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


