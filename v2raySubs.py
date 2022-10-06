import base64
import requests
import json
import socket
import re

country = {'英国': 'UK', '摩尔多瓦': 'MDA'}
cn_province = {'香港特别行政区': 'HK', '台湾省': 'TW', '澳门特别行政区': 'MAC'}
nodes = {'country': 'index'}
node_count = 0


def get_ip_addr(ip_addr):
    try:
        ip_info_url = 'https://ip.useragentinfo.com/json?ip=' + ip_addr
        ip_info_json = json.loads(requests.get(ip_info_url).text)
        if ip_info_json['country'] == '泛播':
            country_str = ip_info_json['isp'] + ' CDN'
        else:
            if ip_info_json['short_name'] == '':
                country_str = country[ip_info_json['country']]
            else:
                if ip_info_json['short_name'] == 'CN':
                    try:
                        country_str = cn_province[ip_info_json['province']]
                    except KeyError:
                        country_str = ip_info_json['short_name']
                else:
                    country_str = ip_info_json['short_name']
        try:
            nodes[country_str] = nodes[country_str] + 1
        except KeyError:
            nodes[country_str] = 1
        try:
            return_str = country_str + ' ' + str(nodes[country_str])
        except KeyError:
            return_str = country_str + ' ' + country_str
        return return_str
    except socket.gaierror:
        return 0


def vmess_rewrite(share_link_vmess):
    link_json = json.loads(base64.b64decode(share_link_vmess.split('://')[1]).decode('utf-8'))
    try:
        ip = socket.getaddrinfo(link_json['add'], None)[0][4][0]
        link_json['ps'] = get_ip_addr(ip) + ' → MNT@CrystalTec'
    except socket.gaierror:
        link_json['ps'] = 'Unexpected IP → MNT@CrystalTec'
    return link_json


def trojan_ss_rewrite(share_link_trojan_ss):
    share_content = re.split('@|:|#', share_link_trojan_ss.split('://')[1])
    try:
        ip = socket.getaddrinfo(share_content[1], None)[0][4][0]
        share_content[3] = get_ip_addr(ip) + ' → MNT@CrystalTec'
    except socket.gaierror:
        share_content[3] = 'Unexpected IP → MNT@CrystalTec'
    return '{0[0]}@{0[1]}:{0[2]}#{0[3]}'.format(share_content)


SubscribeUrl = [
    'https://bulink.me/sub/pdftc/v2',
    'https://openit.daycat.space/long',
    'https://api.ndsxfkjfvhzdsfio.quest/link/sEDwSb6G45NV7yOG?sub=3&extend=1'
]
FullShareLinks = ''

for url in SubscribeUrl:
    response = requests.get(url)
    for link in base64.b64decode(response.content.decode('utf-8')).decode('utf-8').split():
        if link.split('://')[0] == 'vmess':
            share_link = 'vmess://' + base64.b64encode(str(vmess_rewrite(link)).encode('utf-8')).decode('utf-8')
            FullShareLinks = FullShareLinks + share_link + '\n'
        elif link.split('://')[0] == 'trojan' or link.split('://')[0] == 'ss':
            share_link = link.split('://')[0] + '://' + trojan_ss_rewrite(link).replace('\'', '\"')
            FullShareLinks = FullShareLinks + share_link + '\n'
        elif link.split('://')[0] == 'ss':
            FullShareLinks = FullShareLinks + link + '\n'
        node_count = node_count + 1

with open('long', mode='w', encoding='utf-8') as result_file:
    result_file.write(base64.b64encode(FullShareLinks.encode('utf-8')).decode('utf-8'))
