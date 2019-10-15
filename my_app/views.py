from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from requests.compat import quote_plus
from . import models

BASE_CRAIGSLIST_URL = "https://chattanooga.craigslist.org/search/?query={}"
BASE_IMAGE_URL = "https://images.craigslist.org/{}_300x300.jpg"

# Create your views here.
def home(request):
    return render(request, 'base.html')

def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    # Extracting the source code of the page
    data = response.text
    # Passing the source code to to Beautiful Soup to create a BeautifulSoup object for it
    soup = BeautifulSoup(data, features='html.parser')
    # Extracting all the <a> tags whose class name is 'result-title'
    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')
        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0][2:]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https:///craigslist.org/images/peace.jpg'


        post_price = post.find(class_='result-price').text if post.find(class_='result-price') else "N/A"
        final_postings.append((post_title, post_url, post_price, post_image_url))

    stuff_for_frontend = {'search':search, 'final_postings': final_postings}
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
