# -*- coding: utf-8 -*-
import requests
import heimdall
from heimdall.decorators import get_database, create_database
from urllib.parse import urlparse

"""
Provides connector to Opentheso.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501

EID = 'concept'  # Entity ID of all imported items
AID = 'uri'  # EID.attribute ID of each item URL
DEPTH = {
    'http://www.w3.org/2004/02/skos/core#broader': 0,
    'http://www.w3.org/2004/02/skos/core#narrower': None,
    'http://www.w3.org/2004/02/skos/core#related': 1,
    }

ARK2API = {
    'ark.frantiq.fr': 'https://pactols.frantiq.fr/api/',
    }

@get_database('api:opentheso')
def getDatabase(**options):
    r"""Imports a database from Opentheso

    :param \**options: Keyword arguments, see below.
    :return: HERA element tree
    :rtype: :py:class:`heimdall.elements.Root`

    :Keyword arguments:
        * **url** (:py:class:`str`, optional, default: ``https://opentheso.huma-num.fr/api/``) -- Opentheso API URL ; must ends with a ``/``.
        * **thesaurus** (:py:class:`str`, optional) -- Thesaurus identifier
        * **concept** (:py:class:`str`, optional) -- Concept identifier
        * **naan** (:py:class:`str`, optional) -- Name Assigning Authority Number (NAAN)
        * **ark** (:py:class:`str`, optional) -- ARK identifier
        * **eid** (:py:class:`str`, optional, default: ``concept``) -- Entity identifier of imported concepts ; if set to ``None``, no entity will be generated.

    Keywords arguments must comply to the following rules:
        * you have to provide either ``naan`` and ``ark``, or ``thesaurus`` and ``concept`` arguments ;
        * if ``naan`` and ``ark`` are provided, ``thesaurus`` and ``concept`` are ignored.

    If ``url`` is not provided, URL ``https://opentheso.huma-num.fr/api/`` will be used.
    You can use any other Opentheso instance, however.
    For example, ``https://pactols.frantiq.fr/api/``.

    See https://opentheso.huma-num.fr/swagger-ui/index.html for details about Opentheso API.
    See https://arks.org/about/ark-naans-and-systems/ for details about NAANs and ARKs identifiers.
    """
    baseurl = options.get('url', 'https://opentheso.huma-num.fr/api/')
    eid = options.get('eid', EID)
    depths = options.get('depth', DEPTH)
    depth = 0
    url2api = options.get('url2api', _url2api)

    naan = options.get('naan', None)
    ark = options.get('ark', None)
    if ((naan is not None and ark is None)
        or (ark is not None and naan is None)):
        raise ValueError("Expected both 'naan' AND 'ark'")

    if (naan is None and ark is None):
        thesaurus = options.get('thesaurus', None)
        concept = options.get('concept', None)
        if ((thesaurus is not None and concept is None)
            or (concept is not None and thesaurus is None)):
            raise ValueError("Expected both 'thesaurus' AND 'concept'")
        main = thesaurus
        sub = concept
        separator = '.'
    else:
        main = naan
        sub = ark
        separator = '/'

    url = f'{baseurl}/{main}{separator}{sub}.json'
    visited = set()
    properties = dict()
    tree = heimdall.util.tree.create_empty_tree()

    _create_items(tree, url, visited, eid, properties, depth, depths)

    if eid is not None:
        heimdall.util.update_entities(tree)
        entity = heimdall.getEntity(tree, lambda e: e.get('id') == eid)
        for uri in depths.keys():
            pid = _get_property_uid(uri)
            a = heimdall.getAttribute(entity, lambda a: a.get('id') == pid)
            a.type = f'@{eid}.{AID}'

    return tree


def _request(url, headers, payload):
    response = requests.get(url, headers=headers, params=payload)
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    # NOTE: maybe check for response.headers, too?
    return response.json()

def _create_items(tree, url, visited, eid, properties, depth, depths):
    headers = {'accept': 'application/json', }
    payload = {}
    response = _request(url, headers, payload)
    #import json
    #print(json.dumps(response, sort_keys=True, indent=2))

    for ark, data in response.items():
        visited.add(ark)
        item = heimdall.createItem(tree, eid=eid)
        aid = AID if eid is not None else None
        _create_metadata(item, 'identifier', aid, {'value': ark})
        for puri, values in data.items():
            follow = _must_follow_relation(puri, depths, depth)
            p = properties.get(puri, None)
            if p is None:
                p = _create_property(tree, puri)
                properties[puri] = p
            pid = p.get('id')
            aid = pid if eid is not None else None
            for value in values:
                _update_property_type(p, value)
                value = _create_metadata(item, pid, aid, value)
                if follow and value not in visited:
                    if '/ark:/' in value:
                        neighbor = _ark2api(value)
                    else:
                        neighbor = url2api(value)
                    visited = _create_items(tree, neighbor, visited, eid, properties, depth+1, depths)
    return visited



def _must_follow_relation(puri, depths, depth):
    # - puri must be an URI to another concept we want to follow
    # - we must be below max depth OR there is no max depth
    return (puri in depths) and (depths[puri] is None or depth < depths[puri])


def _create_property(tree, puri):
    pid = _get_property_uid(puri)
    return heimdall.createProperty(tree, id=pid, uri=[puri])

def _ark2api(url):
    x = urlparse(url)
    #print(url, type(x))
    #print(f"fragment: {x.fragment} ({x.fragment is None},{len(x.fragment)}), hostname: {x.hostname}, netloc: {x.netloc}, params: {x.params}, password: {x.password}, path: {x.path}, port: {x.port}, query: {x.query}, scheme: {x.scheme}, username: {x.username}")
    baseurl = ARK2API[x.hostname]
    parts = x.path.split('/')
    naan = parts[-2]
    ark = parts[-1]
    url = f'{baseurl}/{naan}/{ark}.json'
    return url

def _url2api(url):
    raise ValueError(f"Deducing API URL from URL '{url}': Not Implemented")


def _get_property_uid(uri):
    parts = uri.split('#')
    if len(parts) > 1:
        return parts[-1]
    parts = uri.split('/')
    return parts[-1]

def _update_property_type(p, data):
    type_uri = data.get('datatype', None)
    heratype = _opentheso2hera_type(data.get('type', None), type_uri)
    p.type = heratype

def _opentheso2hera_type(value, type_uri):
    if value == 'uri':
        return 'uri'
    if value == 'literal':
        if type_uri is not None and type_uri.endswith('#date'):
            return 'date'
    return 'text'

def _create_metadata(item, pid, aid, data):
    value = data.get('value', None)  # should be present
    language = data.get('lang', None)  # present for definition and prefLabel
    data = {language: value} if language is not None else value
    heimdall.createMetadata(item, data, pid=pid, aid=aid)
    return value


__version__ = '0.2.0'
__all__ = ['getDatabase', '__version__']
__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
