import base64
import requests
import json
import socket
import re

# Unrecorded country short names
country = {'英国': 'UK', '摩尔多瓦': 'MDA'}
# Special Internet places in cn
cn_province = {'香港特别行政区': 'HK', '台湾省': 'TW', '澳门特别行政区': 'MAC'}
nodes = {'country': 'index'}
node_count = 0


def get_ip_addr(ip_addr):
    try:
        # Get IP info from ip.useragentinfo.com
        ip_info_url = 'https://ip.useragentinfo.com/json?ip=' + ip_addr
        ip_info_json = json.loads(requests.get(ip_info_url).text)
        # Check if CDN
        if ip_info_json['country'] == '泛播':
            country_str = ip_info_json['isp'] + ' CDN'
        else:
            # Check if short name exists
            if ip_info_json['short_name'] == '':
                # If not, get short name from dictionary
                country_str = country[ip_info_json['country']]
            else:
                # Check If 'CN'
                if ip_info_json['short_name'] == 'CN':
                    try:
                        # Check If 'TW', 'HK', 'MAC'
                        country_str = cn_province[ip_info_json['province']]
                    except KeyError:
                        # If not, then use 'CN'
                        country_str = ip_info_json['short_name']
                else:
                    country_str = ip_info_json['short_name']
        try:
            # Try to add count of node in place
            nodes[country_str] = nodes[country_str] + 1
        except KeyError:
            # If this node does not exists, then create one
            nodes[country_str] = 1
        try:
            # Build place and count
            return_str = country_str + ' ' + str(nodes[country_str])
        except KeyError:
            return_str = country_str + ' ' + country_str
        return return_str
    except socket.gaierror:
        return 0


def vmess_rewrite(share_link_vmess):
    link_json = json.loads(base64.b64decode(share_link_vmess.split('://')[1]).decode('utf-8'))
    try:
        # Get IP address by host
        ip = socket.getaddrinfo(link_json['add'], None)[0][4][0]
        # Replace value of 'ps'
        link_json['ps'] = get_ip_addr(ip) + ' → MNT@CrystalTec'
    except socket.gaierror:
        # If can't get, use 'Unexpected IP' instead
        link_json['ps'] = 'Unexpected IP → MNT@CrystalTec'
    return link_json


def trojan_ss_rewrite(share_link_trojan_ss):
    share_content = re.split('@|:|#', share_link_trojan_ss.split('://')[1])
    try:
        # Get IP address by host
        ip = socket.getaddrinfo(share_content[1], None)[0][4][0]
        # Replace value of description
        share_content[3] = get_ip_addr(ip) + ' → MNT@CrystalTec'
    except socket.gaierror:
        # If can't get, use 'Unexpected IP' instead
        share_content[3] = 'Unexpected IP → MNT@CrystalTec'
    return '{0[0]}@{0[1]}:{0[2]}#{0[3]}'.format(share_content)


# Encoded source subscribe links
SubscribeUrl = [
    'aHR0cHM6Ly9idWxpbmsubWUvc3ViL3BkZnRjL3Yy',
    'aHR0cHM6Ly9vcGVuaXQuZGF5Y2F0LnNwYWNlL2xvbmc=',
    'aHR0cHM6Ly9hcGkubmRzeGZramZ2aHpkc2Zpby5xdWVzdC9saW5rL3NFRHdTYjZHNDVOVjd5T0c/c3ViPTMmZXh0ZW5kPTE='
]
FullShareLinks = ''

for url in SubscribeUrl:
    response = requests.get(base64.b64decode(url).decode('utf-8')) # Decode url and get content
    for link in base64.b64decode(response.content.decode('utf-8')).decode('utf-8').split(): # Split share links line by line
        if link.split('://')[0] == 'vmess': # Vmess use Json as its link format
            share_link = 'vmess://' + base64.b64encode(str(vmess_rewrite(link)).encode('utf-8')).decode('utf-8')
            FullShareLinks = FullShareLinks + share_link + '\n'
        elif link.split('://')[0] == 'trojan' or link.split('://')[0] == 'ss': # Trojan and Shadowsocks has similar link format
            share_link = link.split('://')[0] + '://' + trojan_ss_rewrite(link).replace('\'', '\"')
            FullShareLinks = FullShareLinks + share_link + '\n'

# Encode and write whole link to file
with open('long', mode='w', encoding='utf-8') as result_file:
    result_file.write(base64.b64encode(FullShareLinks.encode('utf-8')).decode('utf-8'))
