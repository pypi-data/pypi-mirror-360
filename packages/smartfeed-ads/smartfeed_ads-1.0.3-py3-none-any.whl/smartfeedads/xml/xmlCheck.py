import xml.etree.ElementTree as ET
import requests

def check_xml_all(xmlUrl, expertCouont=None, expert_attr_dicts=None):
    """
    校验xml内容的正确性
    expertCouont : 预期xml中商品总数，传None则不校验商品数量
    expert_attr_dicts : 预期要校验的xml字段值，key为字段名称，value为字段值
    """
    flag = True
    result = {}
    # 第一步：校验xml格式的正确性
    flag, msg = checkXMLformat(xmlUrl)
    if not flag:
        return False, "xml格式错误，请检查是否存在特殊字符"

    # 第二步：校验xml商品总数(如果expertCouont不传值，则不校验商品总数）
    if expertCouont is not None:
        countlag, msg = checkProductCount(xmlUrl, expertCouont)
        if not countlag:
            flag = False
            result = {**result, "商品总数预期值：" + str(expertCouont) : msg}
            return flag,result

    # 第三步：判断待上传和已上传的商品在XML中存在 并且 字段值正确
    responseBody = requests.get(xmlUrl).text
    root = ET.fromstring(responseBody)
    namespace = {'g': 'http://base.google.com/ns/1.0'}

    # 遍历所有<item>节点
    item_matched = True  # 假设当前item匹配所有字段
    for item_idx, item in enumerate(root.findall('.//channel/item', namespaces=namespace)):
        xml_element = item.find("{http://base.google.com/ns/1.0}id", namespaces=namespace)
        try:
            # 如果被校验的字典中不存在商品id，则提示缺少id参数
            expert_attr_dicts["id"]
        except BaseException as msg:
            return False, "预期字典中必须指定【商品id字段】"
        if (xml_element.tag == '{http://base.google.com/ns/1.0}id' and xml_element.text == expert_attr_dicts["id"]):
            # 检查字典中的每个字段
            for field, expected_value in expert_attr_dicts.items():
                expert_tag = "{http://base.google.com/ns/1.0}"+field
                # 在xml中查找该节点
                tag_element = item.find(expert_tag, namespaces=namespace)
                # 检查节点是否存在且值匹配
                if tag_element is None:
                    item_matched = False
                    result = {**result, "xml中缺失字段：": field}
                elif str(tag_element.text) == "None":
                    if expected_value!="":
                        result = {**result, "xml字段不匹配，预期：" + field + "=" + str(expected_value): " 实际值：" + str(tag_element.text)}
                elif str(tag_element.text) != expected_value:
                    print(str(expected_value))
                    print(str(tag_element.text))
                    item_matched = False
                    result = {**result, "xml字段不匹配，预期："+field+ "="+str(expected_value):" 实际值："+ str(tag_element.text)}
            return item_matched,result

    return False, {**result, "xml中没找到预期商品id：" : expert_attr_dicts["id"]}


def checkXMLformat(xmlUrl):
    """
    校验xml格式的是否正确
    """
    response = requests.get(xmlUrl)
    xmlTree = ET.ElementTree(ET.fromstring(response.text))
    if xmlTree:
        return True, "xml格式正确"
    else:
        return False, "xml格式错误，请检查是否存在特殊字符"

def checkProductCount(xmlUrl,expertCouont):
    """
    校验xml的商品总数与预期是否一致
    """
    response = requests.get(xmlUrl)
    # 检查请求是否成功
    if response.status_code == 200:
        responseBody = response.text
        root = ET.fromstring(responseBody)
        # 解析XML总商品总数
        item_count = len(root.findall(".//item"))
        return (False, {"实际值：": item_count}) if item_count != expertCouont else (True, "校验期望结果校验通过")
    else:
        return (False, "解析xml失败，请检查xml地址是否正确")

def main():
    attr_dicts = {"id": "18061095383903649198151625",
                  "title": "勿动-促销价专用商品",
                  "link":"https://panxiaojiepre-feed1.myshopline.com/products/勿动-促销价专用商品?sku=18061095383903649198151625",
                  "price":"888.00USD"}
    redditXML = 'http://public.myshopline.com/prod/file/reddit/feed/panxiaojiepre-feed1_27746.xml'
    # xml商品数量不正确
    flag, result = check_xml_all(xmlUrl=redditXML, expertCouont=5, expert_attr_dicts=attr_dicts)
    print(flag, result)
    # 不校验商品数量
    attr_dicts = {"id": "18061095383903649198151625",
                  "title": "勿动-促销价专用商品",
                  "link": "https://panxiaojiepre-feed1.myshopline.com/products/勿动-促销价专用商品?sku=18061095383903649198151625",
                  "price": "888.00 USD",
                  "description":"Heel Type:Thin Heel Origin:CN(Origin)  Upper Material:PU  Toe Shape:Pointed Toe  With Platforms:No  Heel Height:High (5cm-8cm)  Pump Type:Basic  Fit:Fits true to size, take your normal size  Style:Fashion  Fashion Element:Shallow  Lining Material:PU  Season:Spring/Autumn  Outsole Material:Rubber  Closure Type:Slip-On  is_handmade:Yes  Pattern Type:Solid  Insole Material:PU  Occasion:Office &amp; Career  Item Type:Pumps  Model Number:zg7a37  Gender:WOMEN  High Heels:8cm high heels pumps shoes  Color:nude black pink red white  Season:spring autumn summer shoes 2022",
                  "image_link":"https://img-preview-va.myshopline.com/image/store/2002755686/1668841606971/1.png?w=1042&h=1288",
                  "availability":"in stock",
                  "mpn":"sku-字段规则专用"
                  }
    flag, result = check_xml_all(xmlUrl=redditXML, expert_attr_dicts=attr_dicts)
    print(flag, result)

    # 校验商品在xml中不存在
    attr_dicts = {"id": "1806109538390364919815162588",
                  "title": "勿动-促销价专用商品"
                  }
    flag, result = check_xml_all(xmlUrl=redditXML, expert_attr_dicts=attr_dicts)
    print(flag, result)
    # 校验商品在xml中不存在
    attr_dicts = {"iddd": "1806109538390364919815162588",
                  "title": "勿动-促销价专用商品"
                  }
    flag, result = check_xml_all(xmlUrl=redditXML, expert_attr_dicts=attr_dicts)
    print(flag, result)
    # 校验商品字段为空的情况
    attr_dicts = {"id": "18069227238384227212541625",
                  "title": "😊beautiful Rings OK , Good-u",
                  "gtin":""
                  }
    flag, result = check_xml_all(xmlUrl=redditXML, expert_attr_dicts=attr_dicts)
    print(flag, result)

if __name__ == '__main__':
    main()


