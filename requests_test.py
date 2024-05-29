import requests

res = requests.get(
    url="https://image.anosu.top/pixiv/direct?r18=1&keyword=azurlane", allow_redirects=False
)
content = res.content
url = res.headers.get('Location')
print(type(url))
# with open(u"1.png", "wb") as f:
#     f.write(content)
