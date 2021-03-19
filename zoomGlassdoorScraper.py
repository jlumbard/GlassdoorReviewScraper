import requests
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool

def getReviewsFromPage(pageNum):
    headers= {"user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    pagedURL = 'https://www.glassdoor.ca/Reviews/Zoom-Video-Communications-Reviews-E924644_P'+str(pageNum)+'.htm?filter.iso3Language=eng'
    print(pagedURL)
    r = requests.get(pagedURL, headers=headers)
    print("repsponse: " + str(r))
    soup = BeautifulSoup(r.text)
    df2 = pd.DataFrame(columns=['time','recommends','outlook','approvesOfCEO','mainText','pros','cons','rating','title','jobTitle'])
    for review in (soup.find_all("li", class_="empReview")):
        print("scraping review")
        reviewAttributes = {}
        timeObjects = review.find_all('time')
        if(len(timeObjects)>0):
            reviewAttributes['time'] = timeObjects[0]['datetime']


            recommendationObjects = review.find_all("div", class_='recommends')
            if(len(recommendationObjects) >0):
                reviewAttributes['recommends'] = False
                reviewAttributes['outlook'] = False
                reviewAttributes['approvesOfCEO'] = False
                for recommendation in recommendationObjects[0].find_all('div',class_="col-sm-4"):
                    if(recommendation.find('span').text == 'Recommends'):
                        reviewAttributes['recommends'] = True
                    elif(recommendation.find('span').text == 'Positive Outlook'):
                        reviewAttributes['outlook'] = True
                    elif(recommendation.find('span').text == 'Approves of CEO'):
                        reviewAttributes['approvesOfCEO'] = True
                    
            reviewAttributes['mainText'] = review.find_all("p", class_='mainText')[0].text
            reviewAttributes['pros'] = review.find_all("p", class_='v2__EIReviewDetailsV2__bodyColor')[0].find('span').text
            reviewAttributes['cons'] = review.find_all("p", class_='v2__EIReviewDetailsV2__bodyColor')[1].find('span').text
            reviewAttributes['rating'] = review.find('div', class_='v2__EIReviewsRatingsStylesV2__ratingNum').text
        
            reviewAttributes['title'] = review.find('a', class_='reviewLink').text
            reviewAttributes['jobTitle'] = review.find('span',class_='authorJobTitle').text
            df2 = df2.append(reviewAttributes, ignore_index=True)
        else:#It was a featured review, I think only happens first on the first page.
            print("passed, not a real review")

        
    return df2

pool = ThreadPool(5) 
results = pool.map(getReviewsFromPage, range(1,55))
pool.close()
pool.join()

newDataFrame = pd.concat(results, ignore_index=True, sort=False)

newDataFrame.to_csv('scrapedGlassdoorData.csv')
