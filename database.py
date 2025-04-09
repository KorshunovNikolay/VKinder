import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from models import User, Candidate, Photo, Reaction, create_tables, drop_tables
import logging

time_format = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO,
                    filename="db_log.log", filemode="w",
                    format='%(asctime)s – %(message)s', datefmt=time_format,
                    encoding='utf-8')


class VkBotDatabase:
    def __init__(self):
        self.engine = sq.create_engine(self.create_dsn())
        self.Session = sessionmaker(bind=self.engine)
        self.db_name = os.getenv('DATABASE')

    @staticmethod
    def create_dsn():
        load_dotenv()
        login = os.getenv('LOGIN')
        password = os.getenv('PASSWORD')
        db_name = os.getenv('DATABASE')
        server_name = os.getenv('SERVER_NAME')
        server_host = os.getenv('SERVER_HOST')
        dsn = f'postgresql://{login}:{password}@{server_name}:{server_host}/{db_name}'
        return dsn

    def drop_tables(self):
        drop_tables(self.engine)
        logging.info(f"tables for {self.db_name} dropped")

    def create_tables(self):
        create_tables(self.engine)
        logging.info(f"tables for {self.db_name} created")

    def recreate_tables(self):
        self.drop_tables()
        self.create_tables()

    def user_exists(self, vk_id):
        with self.Session() as session:
            with session.begin():
                user = session.query(User).where(User.vk_id == vk_id).first()
                if user:
                    return True
                else:
                    return False

    def add_user(self, vk_id):
        if self.user_exists(vk_id):
            logging.debug(f"user {vk_id=} already exists")
        else:
            user = User(vk_id=vk_id)
            with self.Session() as session:
                try:
                    with session.begin():
                        session.add(user)
                    session.refresh(user)
                    logging.info(f"user {vk_id=} added")
                except Exception as e:
                    logging.error(f"couldn't add user {vk_id=} ({e.__class__.__name__})")

    def candidate_exists(self, vk_id):
        with self.Session() as session:
            with session.begin():
                candidate = session.query(Candidate).where(Candidate.vk_id == vk_id).first()
                if candidate:
                    return True
                else:
                    return False

    def add_candidate(self, vk_id, first_name=None, last_name=None, link=None):
        if self.candidate_exists(vk_id):
            logging.debug(f"candidate {vk_id=} already exists")
        else:
            candidate = Candidate(
                vk_id=vk_id,
                first_name=first_name,
                last_name=last_name,
                link=link
            )
            with self.Session() as session:
                try:
                    with session.begin():
                        session.add(candidate)
                    session.refresh(candidate)
                    logging.info(f"candidate {vk_id=} added")
                except Exception as e:
                    logging.error(f"couldn't add candidate {vk_id=} ({e.__class__.__name__})")

    def add_photo(self, vk_id, link):
        photo = Photo(
            candidate_id=vk_id,
            link=link
        )
        with self.Session() as session:
            try:
                with session.begin():
                    session.add(photo)
                session.refresh(photo)
                logging.info(f"photo for {vk_id=} added")
            except Exception as e:
                logging.error(f"couldn't add photo for {vk_id=} ({e.__class__.__name__})")

    def add_reaction(self, user_id, candidate_id, mark=None):
        if self.reaction_exists(user_id, candidate_id):
            with self.Session() as session:
                with session.begin():
                    reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                             Reaction.candidate_id == candidate_id).first()
                    reaction.mark = mark
                    logging.info(f"reaction updated with {mark=} for {user_id=}, {candidate_id=}")
        else:
            new_reaction = Reaction(
                    user_id=user_id,
                    candidate_id=candidate_id,
                    mark=mark
                )
            with self.Session() as session:
                try:
                    with session.begin():
                        session.add(new_reaction)
                    session.refresh(new_reaction)
                    logging.info(f"reaction '{bool(mark)}' added for {user_id=}, {candidate_id=}")
                except Exception as e:
                    logging.error(f"couldn't add reaction {mark=} for user "
                          f"{user_id=}, {candidate_id=} ({e.__class__.__name__})")

    def reaction_exists(self, user_id, candidate_id):
        with self.Session() as session:
            with session.begin():
                reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                         Reaction.candidate_id == candidate_id).one_or_none()
                if reaction:
                    return True
                else:
                    return False

    def find_reaction(self, user_id, candidate_id):
        with self.Session() as session:
            with session.begin():
                reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                         Reaction.candidate_id == candidate_id).one_or_none()
                if reaction:
                    logging.debug(f"found {reaction}")
                    session.expunge(reaction)
                    return reaction
                else:
                    logging.debug(f"reaction not found")
                    return None


if __name__ == '__main__':
    vk_db = VkBotDatabase()

    vk_db.recreate_tables()

    vk_db.add_user(vk_id="u1")
    vk_db.add_user(vk_id="u2")
    vk_db.add_user(vk_id="u2")
    vk_db.add_candidate(vk_id="c1")
    vk_db.add_candidate(vk_id="c2")
    vk_db.add_candidate(vk_id="c2")
    vk_db.add_candidate(vk_id="c3", first_name="xs", link="c3_link")

    vk_db.add_photo(vk_id="c1", link="link_photo1")
    vk_db.add_photo(vk_id="c1", link="link_photo2")
    vk_db.add_photo(vk_id="c2", link="link_photo3")
    vk_db.add_photo(vk_id="c2", link="link_photo3")

    vk_db.add_reaction("u1", "c1", 1)
    vk_db.add_reaction("u1", "c2", 1)
    vk_db.add_reaction("u1", "c2", 0)

    vk_db.find_reaction("u1", "c1")
    vk_db.find_reaction("u1", "c2")
    vk_db.find_reaction("u1", "c3")
