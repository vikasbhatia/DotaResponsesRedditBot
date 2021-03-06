import datetime
import random
import urllib.parse as up

from pony.orm import db_session, commit

from config import CACHE_TTL, DB_URL, DB_PROVIDER
from util.database.models import Responses, Heroes, RedditCache, db
from util.logger import logger

__author__ = 'MePsyDuck'


class DatabaseAPI:
    def __init__(self):
        """Method to initialize db connection. Binds PonyORM Database object `db` to configured database.
        Creates the mapping between db tables and models.
        """
        self.db = db
        if DB_PROVIDER == 'sqlite':
            self.db.bind(provider='sqlite', filename=DB_URL, create_db=True)
        elif DB_PROVIDER == 'mysql':
            up.uses_netloc.append("mysql")
            url = up.urlparse(DB_URL)
            self.db.bind(provider='mysql', host=url.hostname, user=url.username, passwd=url.password, db=url.path[1:])
        elif DB_PROVIDER == 'postgres':
            up.uses_netloc.append("postgres")
            url = up.urlparse(DB_URL)
            self.db.bind(provider='postgres', user=url.username, password=url.password, host=url.hostname,
                         database=url.path[1:])
        else:
            self.db.bind(provider='sqlite', filename='bot.db', create_db=True)

        self.db.generate_mapping(create_tables=True)

    # Responses table queries
    @db_session
    def get_link_for_response(self, processed_text, hero_id=None):
        """Method that returns the link for the processed response text. First tries to match with the given hero_id,
        otherwise returns random result.

        :param processed_text: The plain processed response text.
        :param hero_id: The hero's id.
        :return The link to the response
        """
        # TODO review
        responses = Responses.select(lambda r: r.processed_text == processed_text)

        if len(responses):
            if hero_id is not None:
                for response in responses:
                    if response.hero_id == hero_id:
                        return response.response_link, response.hero_id.id
            else:
                response = random.choice(list(responses))
                return response.response_link, response.hero_id.id
        else:
            return None, None

    # RedditCache table queries
    @db_session
    def add_thing_to_cache(self, thing_id):
        """Method that adds current time and Reddit replyable or submission to RedditCache table by their id(fullname).

        :param thing_id: The fullname of replyable/submission on Reddit
        """
        RedditCache(thing_id=thing_id)

    @db_session
    def delete_old_thing_ids(self):
        """Method used to remove things in cache older than a period of time `CACHE_TTL` defined in the config file.
        """
        furthest_date = datetime.datetime.utcnow() - datetime.timedelta(days=CACHE_TTL)

        RedditCache.select(lambda t: t.added_datetime < furthest_date).delete(bulk=True)

    @db_session
    def check_if_thing_exists(self, thing_id):
        """Method that checks if the replyable id given is already present in the RedditCache table

        :param thing_id: The id of the replyable/submission on Reddit
        :return: True if the `thing_id` is already present in table, else False
        """
        thing = RedditCache.select(lambda t: t.thing_id == thing_id)
        return thing is not None

    # Heroes table queries
    @db_session
    def add_hero_to_table(self, hero_name, img_path=None, flair_css=None):
        """Method to add hero to the table. All parameters are strings.

        :param hero_name: Hero's name
        :param img_path: path to hero's image
        :param flair_css: CSS for the flair
        """
        Heroes(hero_name=hero_name, img_path=img_path, flair_css=flair_css)

    @db_session
    def get_hero_id_from_table(self, hero_name):
        """Method to get hero's id from table.

        :param hero_name: Hero's name
        :return: Hero's id
        """
        h = Heroes.get(hero_name=hero_name)
        return h.id if h is not None else None

    @db_session
    def get_hero_name(self, hero_id):
        """Method to get hero's name from table.

        :param hero_id: Hero's id
        :return: Hero's name
        """
        h = Heroes[hero_id]
        return h.hero_name if h is not None else None

    @db_session
    def get_hero_id_by_flair_css(self, flair_css):
        """Method to get hero_id from the table based on the flair css.

        :param flair_css: Hero's css class as in r/DotA2 subreddit
        :return: Hero's id
        """
        if flair_css:
            h = Heroes.get(flair_css=flair_css)
            return h.id if h is not None else None

    @db_session
    def get_img_dir_by_id(self, hero_id):
        """Method to get image directory for hero's flair.

         :param hero_id: Hero's id.
         :return: The directory path to the image.
         """
        h = Heroes[hero_id]
        return h.img_path if h is not None else None

    @db_session
    def get_all_hero_names(self):
        """Method to get all heroes' names.

        :return: All heroes' names as a list.
        """
        heroes = Heroes.select()[:]
        return [hero.hero_name for hero in heroes]

    @db_session
    def update_hero(self, hero_name, img_path, flair_css):
        """Method to update hero's attributes in the Heroes table.

        :param hero_name: Hero's name
        :param img_path: Hero's img dir/path
        :param flair_css: Hero's css class
        """
        hero = Heroes.get(hero_name=hero_name)
        hero.img_path = img_path
        hero.flair_css = flair_css

    def create_all_tables(self):
        """Method to create all tables defined in the models
        """
        self.db.create_tables()

    def drop_all_tables(self):
        """Method to drop all tables defined in the models
        """
        self.db.drop_all_tables(with_all_data=True)

    @db_session
    def add_hero_and_responses(self, hero_name, response_link_list):
        """Method to add hero and it's responses to the db.

        :param hero_name: Hero name who's responses will be inserted
        :param response_link_list: List with tuples in the form of (original_text, processed_text, link)
        """
        h = Heroes(hero_name=hero_name, img_path=None, flair_css=None)
        commit()

        for original_text, processed_text, link in response_link_list:
            existing_response = Responses.get(response_link=link)
            if not existing_response:
                Responses(processed_text=processed_text, original_text=original_text, response_link=link, hero_id=h.id)
            else:
                logger.debug('Link already exists : ' + link + ' for response ' + existing_response.original_text)


db_api = DatabaseAPI()
