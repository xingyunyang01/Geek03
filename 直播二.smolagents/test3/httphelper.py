import requests

def get_html(url,encoding="utf-8"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    resp = requests.get(url, headers=headers)
    if resp.status_code==200:
        resp.encoding=encoding
        return resp.text
    print("获取html出错,code={}".format(resp.status_code))
    return ""