# -*- coding: utf-8 -*-
"""
Created on Wed May 18 19:10:12 2022

@author: Swapnil Khante
"""

import kopf
import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
import requests


try:
    k8s_config.load_kube_config()
except k8s_config.ConfigException:
    k8s_config.load_incluster_config()

def get_short_url(url):
    url_shortener_api = 'https://api.shrtco.de/v2/shorten?url='
    return requests.get(f"{url_shortener_api}{url}").json()['result']['short_link']


def __to_config_map_data(url, short_url):
    return {
        'data': {
             str(url) :str(short_url)
        }
    }

def create_exchange_rate_config_map(namespace, data):
    api_instance = k8s_client.CoreV1Api()
    return api_instance.create_namespaced_config_map(namespace, data)


@kopf.on.create('operators.sk.com', 'v1', 'urlshorteners')
def on_create(namespace, spec, body, **kwargs):
    url = spec['url']
    short_url = get_short_url(url)
    data = __to_config_map_data(url, short_url)
    kopf.adopt(data)
    configmap = create_exchange_rate_config_map(namespace, data)
    return {'configmap-name': configmap.metadata.name}



