from pathlib import Path
from attrs import define, field
import cattrs
from typing import Optional
import toml

from ioproc.texts import (input_instruction, header_user_info, 
        quit_instruction, welcome_line_1, welcome_line_2, welcome_line_3, 
        welcome_line_4, welcome_line_5, check_info, discard_message, 
        goodbye_line_1, goodbye_line_2, goodbye_line_3, goodbye_line_4, 
        goodbye_line_5, header_meta_info, store_location, store_prompt)

__author__ = ["Benjamin Fuchs"]
__copyright__ = "Copyright 2022, German Aerospace Center (DLR)"
__credits__ = [
    "Felix Nitsch",
    "Jan Buschmann",
]

__license__ = "MIT"
__maintainer__ = "Benjamin Fuchs"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

@define
class AppConfigUserSection:
    firstname: Optional[str] = field(default=None)
    familyname: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)


@define
class AppConfigMetaDataDefaults:
    organisation: Optional[str] = field(default=None)
    keywords: list = field(factory=list)
    languages: list = field(factory=list)


@define
class AppConfig:
    user: AppConfigUserSection = field(factory=AppConfigUserSection)
    meta_data_defaults: AppConfigMetaDataDefaults = field(factory=AppConfigMetaDataDefaults)

    
    folder = Path.home()/'.ioproc'
    filepath = folder/'ioproc_config.toml'

    def write(self):
        data = cattrs.unstructure(self)
        self.folder.mkdir(parents=True, exist_ok=True)
        
        with self.filepath.open('w') as opf:
            toml.dump(data, opf)

    @classmethod
    def from_disk(cls):
        
        if not cls.filepath.exists():
            return cls()

        with cls.filepath.open('r') as ipf:
            data = toml.load(ipf)
        
        return cattrs.structure(data, cls)

    @classmethod
    def wizard(cls):
        what_to_do = 'update' if cls.filepath.exists() else 'generate'
        defaults = cls.from_disk()

        print(welcome_line_1)
        print(welcome_line_2)
        print(welcome_line_3)
        print(welcome_line_4)
        print(welcome_line_5)

        print()
        print(quit_instruction)
        print()
        print(input_instruction.format(what_to_do=what_to_do, filepath=cls.filepath))
        print(header_user_info)
        print()

        firstname = input(f'  Please state your first name [{defaults.user.firstname}]: ')

        if firstname.strip().lower() == 'q!':
            cls._goodby()
            return

        if firstname.strip() != "":
            defaults.user.firstname = firstname

        familyname = input(f'  Please state your family name [{defaults.user.familyname}]: ')

        if familyname.strip().lower() == 'q!':
            cls._goodby()
            return

        if familyname.strip() != "":
            defaults.user.familyname = familyname

        email = input(f'  Please state your email [{defaults.user.email}]: ')

        if email.strip().lower() == 'q!':
            cls._goodby()
            return


        if email.strip() != "":
            defaults.user.email = email

        print(header_meta_info)

        organisation = input(f'  Please state your organisation [{defaults.meta_data_defaults.organisation}]: ')

        if organisation.strip().lower() == 'q!':
            cls._goodby()
            return


        if organisation.strip() != "":
            defaults.meta_data_defaults.organisation = organisation

        d = ', '.join(defaults.meta_data_defaults.keywords)
        keywords = input(f'  Please state keywords as a comma separated list [{d}]: ')

        if keywords.strip().lower() == 'q!':
            cls._goodby()
            return


        if keywords.strip() != "":
            defaults.meta_data_defaults.keywords = list(keywords.split(','))

        d = ', '.join(defaults.meta_data_defaults.languages)
        languages = input(f'  Please state languages as a comma separated list [{d}]: ')

        if languages.strip().lower() == 'q!':
            cls._goodbye()
            return


        if languages.strip() != "":
            defaults.meta_data_defaults.languages = list(languages.split(','))

        print(check_info)
        print()
        print(defaults)
        print()
        resp = input(store_prompt)
        if resp.strip().lower() == 'y':
            print(store_location.format(filepath=cls.filepath))
            defaults.write()
        else:
            print(discard_message)

        cls._goodby()

    @classmethod
    def _goodbye(cls):
        print(goodbye_line_1)
        print(goodbye_line_2)
        print(goodbye_line_3)
        print(goodbye_line_4)
        print(goodbye_line_5)

    def __repr__(self):
        data = cattrs.unstructure(self)
        return toml.dumps(data)


if __name__ == "__main__":
    a = AppConfig.from_disk()
    a.wizard()
    print(a)

    