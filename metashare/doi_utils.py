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


def _get_resource_type(resource):
    soup = BeautifulSoup(resource.metadata, "xml")
    # Corpus | Tool/Service
    if soup.find("resourceType").get_text() in ["corpus", "tool"]:
        visual = False
        audio = False

        for media_type in soup.find_all("mediaType"):
            if media_type.get_text() == "video":
                audio = True
                visual = True
            elif media_type.get_text() == "audio":
                audio = True
            elif media_type.get_text() == "image":
                visual = True

        if visual and audio:
            return "Audiovisual"
        elif visual:
            return "Image"
        elif audio:
            return "Audio"
        else:
            return "Text"

    # Language Description
    elif soup.find("resourceType").get_text() == "languageDescription":
        return "Text"
    # Lexical Conceptual Resource
    elif soup.find("resourceType").get_text() == "lexicalConceptualResource":
        return "Text"


def _generate_doi(resource, test):
    payload = {'data': {'type': 'dois',
                        'attributes': {'prefix': '10.15155',
                                       'creators': [],
                                       'titles': [],
                                       'descriptions': [],
                                       'types': {}}}}
    headers = {"content-type": "application/json"}

    url, username, password = _get_credentials(test)

    soup = BeautifulSoup(resource.metadata, "xml")
    # Creators
    for hit in soup.find_all("contactPerson"):
        name = hit.find("givenName").get_text().encode('utf-8') + " " + hit.find("surname").get_text().encode('utf-8')
        payload["data"]["attributes"]["creators"].append({"name": name})
    # Titles
    for hit in soup.find("identificationInfo").find_all("resourceName"):
        payload["data"]["attributes"]["titles"].append({"lang": hit.attrs["lang"].encode('utf-8'), "title": hit.get_text().encode('utf-8')})
    # Descriptions
    for hit in soup.find("identificationInfo").find_all("description"):
        payload["data"]["attributes"]["descriptions"].append({"lang": hit.attrs["lang"].encode('utf-8'),
                                                              "description": hit.get_text().encode('utf-8'),
                                                              "descriptionType": "Abstract"})
    # Publication year
    payload["data"]["attributes"]["publicationYear"] = int(
        soup.find("metadataInfo").find("metadataCreationDate").text.split("-")[0])
    # URL
    payload["data"]["attributes"]["url"] = settings.DJANGO_URL + "/repository/browse/" + resource.identifier.encode('utf-8')
    # Publisher
    payload["data"]["attributes"]["publisher"] = "Center of Estonian Language Resources"
    # ResourceTypeGeneral
    payload["data"]["attributes"]["types"]["resourceTypeGeneral"] = _get_resource_type(resource)

    response = requests.post(url,
                             auth=HTTPBasicAuth(username, password),
                             json=payload,
                             headers=headers)

    resource.doi_identifier = json.loads(response.text.replace("'", "\""))["data"]["id"]
    resource.save()


def _update_doi_state(resource, test, publish=False):
    url, username, password = _get_credentials(test)

    full_url = url + "/" + resource.doi_identifier
    payload = {"data": {"type": "dois", "attributes": {}}}
    if publish:
        payload["data"]["attributes"]["event"] = "publish"
    else:
        payload["data"]["attributes"]["event"] = "hide"
    headers = {"content-type": "application/json"}

    requests.put(full_url,
                 auth=HTTPBasicAuth(username, password),
                 json=payload,
                 headers=headers)


def update_doi(resource, test=True):
    # with open("/opt/base-meta/metashare/doi_update.txt", "w") as f:
    #     f.write(resource.publication_status + " | " + resource.doi_identifier)
    # # If the resource has a DOI and is being deleted or unpublished, update the DOI state to "registered" (hidden).
    # # Only "draft" DOIs can be deleted, hiding is all we can do.
    # if resource.deleted or (resource.publication_status == "g" and resource.doi_identifier != ""):
    #     # This second check is not redundant - it avoids update calls where the deleted resource has no DOI.
    #     # The first one isn't redundant either - without it, the update calls meant for the next elif go here instead.
    #     if resource.doi_identifier != "":
    #         _update_doi_state(resource, test, publish=False)
    # # If the resource is being ingested, generate a "draft" DOI using the metadata
    # elif resource.publication_status == 'g' and resource.doi_identifier == "":
    #     _generate_doi(resource, test)
    # # If the resource is being published, update the DOI state to "findable"
    # elif resource.publication_status == 'p':
    #     _update_doi_state(resource, test, publish=True)

    # with open("/opt/base-meta/metashare/doi_update.txt", "w") as f:
    #     f.write(resource.publication_status + " | " + resource.doi_identifier)
    
    # If the resource has a DOI and is being deleted or unpublished, update the DOI state to "registered" (hidden).
    # Since only "draft" DOIs can be deleted and the other states cannot be changed to "draft", hiding is all we can do.
    if ((resource.deleted or resource.publication_status == "g")
            and resource.doi_identifier != "" and resource.doi_identifier is not None):
        _update_doi_state(resource, test, publish=False)
    # If the resource is being published for the first time, generate a "draft" DOI using the metadata and publish it
    elif resource.publication_status == 'p' and (resource.doi_identifier == "" or resource.doi_identifier is None):
        _generate_doi(resource, test)
        _update_doi_state(resource, test, publish=True)
    # If the resource is being published, update the DOI state to "findable"
    elif resource.publication_status == 'p':
        _update_doi_state(resource, test, publish=True)


def update_doi_url():
    # TODO
    pass
