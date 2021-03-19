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
    df2 = pd.DataFrame(columns=['time','Work/Life Balance', 'Culture & Values','Diversity & Inclusion','Career Opportunities','Compensation and Benefits','Senior Management','recommends','outlook','approvesOfCEO','mainText','pros','cons','rating','title','jobTitle'])
    for review in (soup.find_all("li", class_="empReview")):
        print("scraping review")
        reviewAttributes = {}
        timeObjects = review.find_all('time')
        if(len(timeObjects)>0):
            reviewAttributes['time'] = timeObjects[0]['datetime']

            #stars for each?
            subRatings = review.find_all('div', class_="subRatings")
            if(len(subRatings)>0): #it has to have subratings3
                liStars = subRatings[0].find_all('ul',class_='undecorated')[0].find_all('li')
                #above is expected to contain 5 dropdown subratings of each thing
                for liStar in liStars:
                    reviewAttributes[liStar.find_all('div', class_='minor')[0].text] = liStar.find_all('span',class_='subRatings__SubRatingsStyles__gdBars')[0]['title']
                


            #Do they recommend?
            
            recommendationObjects = review.find_all("div", class_='recommends')
            if(len(recommendationObjects) >0):
                reviewAttributes['recommends'] = None
                reviewAttributes['outlook'] = None
                reviewAttributes['approvesOfCEO'] = None
                for recommendation in recommendationObjects[0].find_all('div',class_="col-sm-4"):
                    if(recommendation.find('span').text == 'Recommends'):
                        reviewAttributes['recommends'] = True
                    elif(recommendation.find('span').text == "Doesn't Recommend"):
                        reviewAttributes['recommends'] = False
                    elif(recommendation.find('span').text == 'Positive Outlook'):
                        reviewAttributes['outlook'] = True
                    elif(recommendation.find('span').text == 'Negative Outlook'):
                        reviewAttributes['outlook'] = False
                    elif(recommendation.find('span').text == 'Neutral Outlook'):
                        reviewAttributes['outlook'] = "Neutral"
                    elif(recommendation.find('span').text == 'Approves of CEO'):
                        reviewAttributes['approvesOfCEO'] = True
                    elif(recommendation.find('span').text == 'Disapproves of CEO'):
                        reviewAttributes['approvesOfCEO'] = False
                    elif(recommendation.find('span').text == 'No Opinion of CEO'):
                        reviewAttributes['approvesOfCEO'] = "Neutral"
                    
            reviewAttributes['mainText'] = review.find_all("p", class_='mainText')[0].text
            reviewAttributes['pros'] = review.find_all("p", class_='v2__EIReviewDetailsV2__bodyColor')[0].find('span').text
            reviewAttributes['cons'] = review.find_all("p", class_='v2__EIReviewDetailsV2__bodyColor')[1].find('span').text
            reviewAttributes['rating'] = review.find('div', class_='v2__EIReviewsRatingsStylesV2__ratingNum').text
        
            reviewAttributes['title'] = review.find('a', class_='reviewLink').text
            reviewAttributes['jobTitle'] = review.find('span',class_='authorJobTitle').text
            df2 = df2.append(reviewAttributes, ignore_index=True)
            print(reviewAttributes)
        else:#It was a featured review, I think only happens first on the first page.
            print("passed, not a real review")

        
    return df2

pool = ThreadPool(5) 
results = pool.map(getReviewsFromPage, range(1,55))
pool.close()
pool.join()

newDataFrame = pd.concat(results, ignore_index=True, sort=False)

newDataFrame.to_csv('scrapedGlassdoorData.csv')
