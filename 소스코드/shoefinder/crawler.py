import re
import requests
import urllib.request
import asyncio
import pprint

SITE_ROOT_URL = 'https://store.musinsa.com'
HTTPS_STRING = "https:"

url = "https://store.musinsa.com/app/items/lists/005/?category=&d_cat_cd=005&u_cat_cd=&brand=timberland&sort=pop&display_cnt=120&page=1&page_kind=category&list_kind=small&free_dlv=&ex_soldout=&sale_goods=&exclusive_yn=&price=&color=&a_cat_cd=&sex=&size=&tag=&popup=&brand_favorite_yn=&goods_favorite_yn=&price1=&price2="
received = requests.get(url)

text = received.content
text = text.decode('utf-8')

item_json_list = []


searchList_html = re.findall(r'id="searchList">(.+?)<div class="pagingNumber-box box">', text, re.DOTALL)
searchList_html_stripped = searchList_html[0].strip()

img_html = re.findall(r'<div class="list_img">(.+?)</div>', searchList_html_stripped, re.DOTALL)


### first page parsing (item name, detail page url, represent img url) ###
for idx, img_tags in enumerate(img_html):
    img_a_html = re.findall(r'<a (.+?)</a>', img_tags.strip(), re.DOTALL)
    last_img_a_html = img_a_html[-1]

    ### item detail url parsing  ###
    item_detail_url = re.findall(r'href="(.+?)"', last_img_a_html)[0]
    item_detail_url = SITE_ROOT_URL + item_detail_url

    ### item 대표 img url parsing ###
    item_img_src = re.findall(r'src="(.+?)"', last_img_a_html, re.DOTALL)
    if len(item_img_src) == 0: # img src property가 없고, data-original property에 url이 있는 경우.
        item_img_src = re.findall(r'data-original="(.+?)"', last_img_a_html, re.DOTALL)[0]
    else:
        item_img_src = item_img_src[0]
    if HTTPS_STRING not in item_img_src: # //image.musinsa 이런식으로 되어있으면 앞에 https:를 붙여주자.
        item_img_src = HTTPS_STRING + item_img_src
    ###########################

    ### item name parsing        ###
    item_name = re.findall(r'alt="(.+?)"', last_img_a_html, re.DOTALL)[0]
    ###########################

    item_json = {
        'item_name': item_name,
        'item_img_src': [item_img_src],
        'item_idx': idx+1,
        'item_detail_url': item_detail_url
    }
    item_json_list.append(item_json)


# async def item_detail_page_parsing(item_json_list):
#     [asyncio.ensure_future(page_parse(item_json['item_detail_url'])) for item_json in item_json_list]
#
# async def page_parse(detail_page_url):
#     detail_page_received = await loop.run_in_executor(None, requests.get, url)
#     detail_page_text = detail_page_received.content
#     detail_page_text = detail_page_text.decode('utf-8')
#
#     ### ul tag parsing ###
#     ul_tag_html = re.findall(r'<ul class="product_thumb">(.+?)</ul>', detail_page_text,re.DOTALL)[0]
#     ######################
#
#     ### img tag parsing ###
#     img_tag_html = re.findall(r'<img(.+?)<span class="vertical_standard">', ul_tag_html, re.DOTALL)
#
#     ### img_src url parsing ###
#     for img_tag in img_tag_html:
#         img_src_list = re.findall(r'src="(.+?)"', img_tag, re.DOTALL)
#         if len(img_src_list) == 0: ### src 가 아니라 data-original property에 url이 존재할 때
#             img_src_list = re.findall(r'data-original="(.+?)"', img_tag, re.DOTALL)
#
#         for img_src in img_src_list:
#             if HTTPS_STRING not in img_src:
#                 img_src = HTTPS_STRING + img_src
#                 item_json['item_img_src'].append(img_src)
#
#
# async def all_items_imgs_download(item_json_list):
#     [asyncio.ensure_future(download_img()) for item_json in item_json_list]
#
# async def download_img(url):
#
#
# loop = asyncio.new_event_loop()  # 이벤트 루프를 얻음
# loop.run_until_complete(item_detail_page_parsing(item_json_list))  # item_detail_page_parsing이 끝날 때까지 기다림
# print(item_json_list)
# loop.close()


### item detail page parsing ###
for item_json in item_json_list:
    detail_page_url = item_json['item_detail_url']
    detail_page_received = requests.get(detail_page_url)
    detail_page_text = detail_page_received.content
    detail_page_text = detail_page_text.decode('utf-8')

    ### ul tag parsing ###
    ul_tag_html = re.findall(r'<ul class="product_thumb">(.+?)</ul>', detail_page_text,re.DOTALL)[0]
    ######################

    ### img tag parsing ###
    img_tag_html = re.findall(r'<img(.+?)<span class="vertical_standard">', ul_tag_html, re.DOTALL)

    ### img_src url parsing ###
    for img_tag in img_tag_html:
        img_src_list = re.findall(r'src="(.+?)"', img_tag, re.DOTALL)
        if len(img_src_list) == 0: ### src 가 아니라 data-original property에 url이 존재할 때
            img_src_list = re.findall(r'data-original="(.+?)"', img_tag, re.DOTALL)

        for img_src in img_src_list:
            if HTTPS_STRING not in img_src:
                img_src = HTTPS_STRING + img_src
                item_json['item_img_src'].append(img_src)


print("log: item json parse completed.")

print(item_json_list)
for item_json in item_json_list:
    print(len(item_json['item_img_src']))
    for img_url in item_json['item_img_src']:
        ### 같은 상품의 여러 가지 각도에서의 이미지를 따로 구분하여 local에 저장하기 위해서  img_number 필드를 도입
        img_number_start_index = img_url[:img_url.rfind("_")].rfind("_") + 1
        img_number_end_index = img_url.rfind("_")
        img_number = img_url[img_number_start_index:img_number_end_index]

        ### url을 조정하여 500 * 600 pixel의 사진을 get. ###
        start_index = img_url.rfind('_') + 1
        end_index = img_url.rfind('.')
        img_url = img_url[:start_index] + '500' + img_url[end_index:] # 500 pixel 이미지 url.

        ### local에 저장할 file name 전처리.
        item_name = item_json['item_name'].replace('/', '') # '/'이 들어있으면 FileNotFound Error발생.

        ### local에 저장.
        urllib.request.urlretrieve(img_url, "data/TIMBERLAND/" + item_name + '_' + img_number + '_' + str(item_json['item_idx']) + '.' + img_url.split('.')[-1])