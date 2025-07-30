import xml.etree.ElementTree as ET
import requests

def checkTotal(xmlUrl,expertCouont):
    # 解析XML获取某个元素的内容
    response = requests.get(xmlUrl)
    # 检查请求是否成功
    if response.status_code == 200:
        responseBody = response.text
        root = ET.fromstring(responseBody)
        # 解析XML总商品总数
        item_count = len(root.findall(".//item"))
        return (False, {"商品总数与期望结果存在差异，实际值：": item_count}) if item_count != expertCouont else (True, "校验期望结果校验通过")
    else:
        return (False,"解析xml失败，请检查xml地址是否正确")

def checkXMLformat(xmlUrl):
    response = requests.get(xmlUrl)
    xmlTree = ET.ElementTree(ET.fromstring(response.text))
    if xmlTree:
        return True,"xml格式正确"
    else:
        return False,"xml格式错误，请检查是否存在特殊字符"

def getTotal(xmlUrl):
    # 解析XML获取某个元素的内容
    response = requests.get(xmlUrl)
    # 检查请求是否成功
    if response.status_code == 200:
        responseBody = response.text
        root = ET.fromstring(responseBody)
        return len(root.findall(".//item"))
    else:
        return ("解析xml失败，请检查xml地址是否正确")

def main():
    code,message = checkTotal("http://public.myshopline.com/prod/file/google/feed/panxiaojiepre-feed1_38331.xml",14)
    print(code,message)

    print(getTotal("http://public.myshopline.com/prod/file/google/feed/panxiaojiepre-feed1_38331.xml"))

    print(checkXMLformat("http://public.myshopline.com/prod/file/google/feed/panxiaojiepre-feed1_38331.xml"))

if __name__ == '__main__':
    main()
