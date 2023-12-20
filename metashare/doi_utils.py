import json

import requests

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

from metashare import settings


def _get_credentials(test):
    if test:
        url = settings.DOI_URL_TEST
        username = settings.DOI_USER_TEST
        password = settings.DOI_PASSWORD_TEST
    else:
        url = settings.DOI_URL
        username = settings.DOI_USER
        password = settings.DOI_PASSWORD

    return url, username, password


# TODO: Finish
def _generate_doi(resource, test):
    payload = {'data': {'type': 'dois',
                        'attributes': {'prefix': '10.15155',
                                       'creators': [],
                                       'titles': [],
                                       'descriptions': [],
                                       'event': 'register'}}}
    headers = {"content-type": "application/json"}

    url, username, password = _get_credentials(test)

    soup = BeautifulSoup(resource.metadata, "xml")
    # Creators
    for hit in soup.find_all("contactPerson"):
        name = hit.find("givenName").get_text() + " " + hit.find("surname").get_text()
        payload["data"]["attributes"]["creators"].append({"name": name})
    # Titles
    for hit in soup.find("identificationInfo").find_all("resourceName"):
        payload["data"]["attributes"]["titles"].append({"lang": hit.attrs["lang"], "title": hit.get_text()})
    # Descriptions
    for hit in soup.find("identificationInfo").find_all("description"):
        payload["data"]["attributes"]["descriptions"].append({"lang": hit.attrs["lang"],
                                                              "description": hit.get_text(),
                                                              "descriptionType": "Abstract"})
    # Publication year
    payload["data"]["attributes"]["publicationYear"] = int(
        soup.find("metadataInfo").find("metadataCreationDate").text.split("-")[0])
    # URL
    payload["data"]["attributes"]["url"] = settings.DJANGO_URL + "/repository/browse/" + resource.identifier

    response = requests.post(url,
                             auth=HTTPBasicAuth(username, password),
                             json=payload,
                             headers=headers)

    doi = json.loads(response.text.replace("'", "\""))["data"]["id"]

    resource.doi_identifier = doi
    resource.save()

    assert resource.doi_identifier != ""


def _update_doi_state(resource, test, publish=False):
    url, username, password = _get_credentials(test)

    full_url = url + "dois" + "/" + resource.doi_identifier
    payload = {"data": {"type": "dois", "attributes": {}}}
    if publish:
        payload["data"]["attributes"]["event"] = "hide"
    else:
        payload["data"]["attributes"]["event"] = "publish"
    headers = {
        "content-type": "application/json",
    }

    response = requests.put(full_url,
                            auth=HTTPBasicAuth(username, password),
                            json=payload,
                            headers=headers)

    assert response.status_code == 200


def update_doi(resource, test=True):
    # If the resource is being ingested, generate a "draft" DOI using the metadata
    if resource.publication_status == 'i' and resource.doi_identifier == "":
        _generate_doi(resource, test)
    # If the resource is being published, update the DOI state to "findable"
    elif resource.publication_status == 'p':
        _update_doi_state(resource, test, publish=True)
    # If the resource is being unpublished or deleted, update the DOI state to "registered" (hidden)
    else:
        _update_doi_state(resource, test, publish=False)


def update_doi_url():
    # TODO: Write this!
    pass
