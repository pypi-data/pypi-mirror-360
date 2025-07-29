from .make_request import *
from abstract_utilities import eatAll,eatInner
def get_urls():
    typicaly_url = "https://typicallyoutliers.com"
    dialectics_url = "https://thedailydialectics.com"
    clownworld_url = "https://clownworld.biz"
    urls = [typicaly_url,dialectics_url,clownworld_url]
    return urls
def get_url(domain):
    urls = get_urls()
    if domain not in urls:
        for url in urls:
            if domain in url:
                return url
    return urls[0]
def get_api_links():
    return {"typicallyoutliers":["api"],"thedailydialectics":["api"],"clownworld":["media"]}    
def get_api_link(url,endpoint=None):
    api_links = get_api_links()
    for domain, links in api_links.items():
        if domain in url:
            url = f"{url}/{links[0]}"
            if endpoint:
                endpoint = eatAll(eatInner(endpoint,links[0]),'/')
                url = f"{url}/{endpoint}"
                return url
    return domain
def make_request_link(url,endpoint=None,**kwargs):
    url = get_url(url)
    url = get_api_link(url,endpoint)
    return postRequest(url,**kwargs)
def abstract_api_call(url,endpoint=None,**kwargs):
    response= make_request_link(url,endpoint,**kwargs)
    return response
