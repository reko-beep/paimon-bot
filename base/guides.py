from nextcord import Embed, File
from nextcord.ext import commands,tasks

from os import getcwd, listdir,remove
from os.path import isfile, join,exists
from json import load,dump

from nextcord.ext.commands.cooldowns import C

from core.paimon import Paimon
from util.logging import logc

'''

 |- Guides
    |
    |
    --- Character Name
        |
        |
        ----- builds
        |           sub_dps.jpg
        |           main_dps.jpg
        |
        |
        ------ ascension_talents

'''

class GenshinGuides:
    def __init__(self, pmon: Paimon):
        '''
        initializes genshin guide module
        '''

        self.path = f'{getcwd()}/guides/'
        self.assets = f'{getcwd()}/assets/'
        self.characters = []
        self.pmon = pmon

        self.images_path = '{base_path}/{character_name}/{type}/'
        self.options = {'as':
                            {
                                'folder': 'ascension_talents',
                                'title': 'Ascension and Talent Mats'
                            },
                        'b':
                            {
                            'folder': 'builds',
                            'title': 'Builds'
                            }
                        }

        self.thumbnails = {}

        self.load_info()
        self.load_characters()
    
    def load_characters(self):
        '''
        ---
        returns
        ---
        loads character from bot config file
        '''
        
        if 'characters' in self.pmon.p_bot_config:
            self.characters = self.pmon.p_bot_config['characters']
            logc('loaded characters from bot config file!')

    def load_info(self):
        with open(f'{self.assets}/characters.json','r') as f:
            self.info = load(f)['data']
            logc('loaded character information.')

    def get_info(self, character_name: str):

        search = character_name.lower()
        for character_data in self.info:

            if search in character_data['name'].lower():
                return {                    
                    'element' : character_data['element']['name'],
                    'weapon' : character_data['weapon']['name'],
                    'nation' : character_data['nation'],
                    'stars': '⭐' * int(character_data['stars'])
                },character_data['img']


    def search_character(self, character_name: str):
        '''
        searches provided character in allowed list of characters
        ---
        args
        ---
        character_name

        ---
        returns
        ---
            character name 
            
        '''
        if character_name != '':
            for character in self.characters:
                if character_name.lower() in character.lower():
                    return character
        return None
    
    def get_option(self, option_name: str):
        '''
        directory name for option_name provided

        ---
        args
        ---
        option_name : as for ascension, b for builds

        ---
        returns:
        ---
            directory name
            
        '''
        if option_name.lower() in self.options:
            return self.options[option_name.lower()]['folder']
        return None
    
    def get_files(self, character_name: str, option_name: str):
        '''
        returns all files in a directory

        ---
        args
        ---
            character_name 
            option_name: as for ascension, b for builds

        ---
        returns
        ---
            list: [files path]
        '''
        
        character = self.search_character(character_name)        
        option = self.get_option(option_name)
        
        if character and option:

            images_path = self.images_path.format(base_path=self.path,character_name=character,type=option)
            if exists(images_path):
                logc(f'found files for {character} | Path {images_path}')
                files = [join(images_path,f) for f in listdir(images_path) if isfile(join(images_path,f))]
                return files

        return None
    
    def prettify_file_name(self,option_name: str, file_path :str):
        '''
        prettifies the file name for displaying

        ---
        args
        ---
            option_name: as for ascension | b for builds
            file_path

        ---
        returns
        ---
            main_heading_text -> generated from option
            title_text -> generated from filename
        '''

        file_path_list = file_path.split('/')
        file_name = file_path_list[-1][:file_path_list[-1].find('.')]

        character_name = file_path.split('/')[-3]

        if option_name in self.options:
            if option_name == 'b':
                main_heading_text = f"{self.options[option_name]['title']}"
                title_text = ' '.join([name.title() for name in file_name[:file_name.find('dps')].split('_')])
                if file_name.find('dps'):
                    title_text += ' DPS'
            if option_name == 'as':
                main_heading_text = f"{self.options[option_name]['title']}"
                title_text = ''

        return main_heading_text,title_text

                
    def create_embeds(self,option_name: str, character_name:str):
        '''
        creates embeds and files to send for discord bot

        ---
        args
        ---

            option_name: as for ascension | b for builds
            character_name

        ---
        returns
        ---

            tuple: (embeds_list,files_list) or (None,None)
        '''

        files = self.get_files(character_name,option_name)
        character = self.search_character(character_name)
        if files:
            embeds = []
            embed_files = []
            for file in files:

                main_title,sub_title = self.prettify_file_name(option_name,file)
                file_name = file.split('/')[-1]
                information,thumbnail = self.get_info(character)

                embed = Embed(title=main_title,description=sub_title,color=0xf5e0d0)
                embed_files.append(File(file,filename=file_name))                
                if (information and thumbnail) and character:
                    for inf in information:
                        embed.add_field(name=inf.title(),value=information[inf])
                    logc(f'Information fetched for {character_name} ')
                    embed.set_author(name=character,icon_url=thumbnail)
                embed.set_image(url=f'attachment://{file_name}')
                embeds.append(embed)

            return embeds,embed_files
        
        return None,None

        
