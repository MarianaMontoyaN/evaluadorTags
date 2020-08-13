
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime

class InstagramBot:

    def __init__(self, username, password):

        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()

    def closeBrowser(self):
        self.driver.close()

    def login(self):

        driver = self.driver
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        user_name_elem = driver.find_element_by_xpath("//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        passworword_elem = driver.find_element_by_xpath("//input[@name='password']")
        passworword_elem.clear()
        passworword_elem.send_keys(self.password)
        passworword_elem.send_keys(Keys.RETURN)
        time.sleep(3)


    def recent_post_links(self, tag, number_posts):

    	driver = self.driver
    	url = "https://www.instagram.com/explore/tags/" + tag + "/"
    	driver.get(url)
    	post = 'https://www.instagram.com/p/'

    	post_links = []
    	while len(post_links) < number_posts:
    		links = [a.get_attribute('href') 
    				for a in driver.find_elements_by_tag_name('a')]

    		for link in links:

    			if post in link and link not in post_links:
    				post_links.append(link)

    		scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
    		driver.execute_script(scroll_down)
    		time.sleep(2)

    	driver.quit()

    	return post_links[:number_posts]

    def insta_details_json(self, url, min_followers):

        
        url_final = url + "?__a=1" 
        res = requests.get(url_final)
        
        #logger.info(type(res))

        try: 
            name_count = res.json()["graphql"]["shortcode_media"]["owner"]["username"]
            is_private = res.json()["graphql"]["shortcode_media"]["owner"]["is_private"]
            followers = res.json()["graphql"]["shortcode_media"]["owner"]["edge_followed_by"]["count"]
            #post_type='photo'
            if followers >= min_followers and is_private == False:
                count_details = {'name':'https://www.instagram.com/'+name_count, 'is_private':is_private, 'followers':followers}
                return count_details

            else: 
                return None

        except Exception as e:
            print(e)
            

    def export_info(self, username_posts, tag):

        date = datetime.now()
        name_archive = tag + '(' + str(date.day) + '-' + str(date.month) + '-' + str(date.year) + ')'

        dataFrame_tag = pd.DataFrame(username_posts) 
        dataFrame_tag.drop(['is_private'], axis='columns', inplace=True)
        dataFrame_tag.to_csv('tags/' + name_archive + '.csv') 


if __name__ == "__main__":

	#------------------------------------------
	#------------------------------------------
	#------------------------------------------

    print(".................................................")
    print(".................................................")
    print("..................BIENVENIDO.....................")
    print('\n')

    username = input("Usuario Instagram: ")
    password = input("Contraseña Instagram: ")
    tag = input("¿Qué etiqueta quieres buscar? ")
    posts_counts = int(input("¿Cuántos posts quieres evaluar? "))
    min_followers = int(input("Cantidad mínima de seguidores en las cuentas: "))
    print('\n')
    final_details = []

    #------------------------------------------
    #------------------------------------------
    #------------------------------------------

    t0 = time.time()
    print ("Tiempo 0: {} segundos".format(t0))

    ig = InstagramBot(username, password)
    ig.login()

    t1 = time.time()-t0
    print ("Ya ingrese a Instagram, llevo: {} segundos".format(t1))

    list_urls = ig.recent_post_links(tag, posts_counts)

    t2 = time.time()-t0
    print ("Ya tome los links, llevo: {} segundos".format(t2))

    for url in list_urls:
        details = ig.insta_details_json(url, min_followers)

        if details != None:
            final_details.append(details)

    t3 = time.time()-t0
    print ("Ya tome las cuentas con mas de {} seguidores, llevo: {} segundos".format(min_followers, t3))

    if final_details:
        ig.export_info(final_details, tag)
    else: 
        print('\n')
        print('****************************************************************************')
        print('WARNING: NO SE ENCONTRARON CUENTAS CON SEGUIDORES POR ENCIMA DE {}'.format(min_followers))
        print('****************************************************************************')
        print('\n')
    t4 = time.time() - t0
    print ("Tiempo final: {} segundos".format(t4))
