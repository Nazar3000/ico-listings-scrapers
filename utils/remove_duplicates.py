import json
import sys
from copy import deepcopy

import tablib

from constants import OrgFields
from crypto.utils import unify_title, unify_website


class RemoveDuplicateItems:
    """
    Remove matchings with old orgs list from newly arrived orgs.

    old orgs file is the file of orgs imported from pipedrive
    new orgs file should previously be generated by merge_items.py script

    """
    def __init__(self, old_orgs_file_name=None, new_orgs_file_name=None,
                 *args, **kwargs):
        self.old_orgs_file_name = old_orgs_file_name
        self.new_orgs_file_name = new_orgs_file_name

        old_orgs = tablib.Dataset().load(open(self.old_orgs_file_name).read())
        new_orgs = tablib.Dataset().load(open(self.new_orgs_file_name).read())

        self.old_orgs_json = json.loads(old_orgs.export('json'))
        self.new_orgs_json = json.loads(new_orgs.export('json'))

        self.ndo_clean_file_name = '{}_clean.json'.format(self.new_orgs_file_name.split('.')[0])

        self.main()

    def main(self):
        new_orgs_json_clean = deepcopy(self.new_orgs_json)
        for new_index, new_org in enumerate(self.new_orgs_json):
            for old_index, old_org in enumerate(self.old_orgs_json):
                if unify_title(old_org[getattr(OrgFields, 'name')]).lower() == new_org['name'].lower() \
                        or unify_website(old_org[getattr(OrgFields, 'site')]) == new_org['site']:

                    if new_org in new_orgs_json_clean:
                        new_orgs_json_clean.remove(new_org)
                        print(len(new_orgs_json_clean))

        new_orgs_json_clean_prepared = []
        for org in new_orgs_json_clean:
            prepared_org = {}
            for key, value in org.items():
                prepared_org[getattr(OrgFields, key)] = value
            new_orgs_json_clean_prepared.append(prepared_org)

        with open(self.ndo_clean_file_name, 'w+') as f:
            f.write(json.dumps(new_orgs_json_clean))

    def get_output_file_name(self):
        return self.ndo_clean_file_name


if __name__ == '__main__':
    print(sys.argv[1:3])
    RemoveDuplicateItems(*sys.argv[1:3])
