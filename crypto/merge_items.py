import json

import tablib

imported_organizations = tablib.Dataset().load(open('organizations.csv').read())
imported_members = tablib.Dataset().load(open('people.csv').read())

organizations_file_name = 'non_duplicate_organizations.json'
members_file_name = 'non_duplicate_members.json'

with open(organizations_file_name, 'w+') as f:
    f.write('')


with open(members_file_name, 'w+') as ndm_file:
    imported_members_json = json.loads(imported_members.export('json'))
    for index, organization in enumerate(json.loads(imported_organizations.export('json'))):
        with open(organizations_file_name, 'r+') as ndo_file:
            ndo_content = ndo_file.read()
            ndo_content = '[' + ndo_content[:len(ndo_content) - 1] + ']'
            ndo_content_json = json.loads(ndo_content)

            if index == 0:
                ndo_file.write(json.dumps(organization) + ',')
            else:
                print(ndo_content_json)
                to_write = True
                for ndo_organization in ndo_content_json:
                    for content_key, content_value in ndo_organization.items():
                        if 'link' in content_key.lower():
                            if organization[content_key] and \
                                    organization[content_key].lower() in content_value.lower():
                                organization[content_key] = organization[content_key] \
                                    if len(organization[content_key]) >= len(organization[content_key]) else content_value

                                for member in imported_members_json:
                                    if member['Organization'] in [organization['Name'], ndo_organization['Name']]:
                                        member['Organization'] = organization['Name']

                                ndo_file.write(json.dumps(organization) + ',')
                                to_write = False
                if to_write and index > 0:
                    ndo_file.write(json.dumps(organization) + ',')
    ndm_file.write(imported_members)