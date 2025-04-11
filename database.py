import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import User, Candidate, Photo, Reaction, create_tables, drop_tables
import logging

logging_level = logging.DEBUG
logging.basicConfig(level=logging_level,
                    filename="db_log.log", filemode="w",
                    format='%(asctime)s - %(levelname)s – %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf-8')


class VkBotDatabase:
    def __init__(self):
        self.engine = create_engine(self.create_dsn())
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
        logging.info(f"tables for {self.db_name} recreated")

    def user_exists(self, vk_id):
        with self.Session() as session:
            with session.begin():
                user = session.query(User).where(User.vk_id == vk_id).first()
                if user:
                    logging.debug(f"checked: user {vk_id=} exists")
                    return True
                else:
                    logging.debug(f"checked: user {vk_id=} doesn't exist")
                    return False

    def add_user(self, vk_id):
        if self.user_exists(vk_id):
            logging.warning(f"user {vk_id=} already exists")
        else:
            user = User(vk_id=vk_id)
            with self.Session() as session:
                try:
                    with session.begin():
                        session.add(user)
                    session.refresh(user)
                    logging.info(f"added: user {vk_id=}")
                except Exception as e:
                    logging.error(f"couldn't add: user {vk_id=} ({e.__class__.__name__})")

    def candidate_exists(self, vk_id):
        with self.Session() as session:
            with session.begin():
                candidate = session.query(Candidate).where(Candidate.vk_id == vk_id).first()
                if candidate:
                    logging.debug(f"checked: candidate {vk_id=} exists")
                    return True
                else:
                    logging.debug(f"checked: candidate {vk_id=} doesn't exist")
                    return False

    def add_candidate(self, vk_id, first_name=None, last_name=None, link=None):
        if self.candidate_exists(vk_id):
            logging.warning(f"candidate {vk_id=} already exists")
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
                    logging.info(f"added: candidate {vk_id=}")
                except Exception as e:
                    logging.error(f"couldn't add: candidate {vk_id=} ({e.__class__.__name__}) \n"
                                  f"{first_name=}, {last_name=}, {link=}")

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
                logging.info(f"added: photo for {vk_id=}")
            except Exception as e:
                logging.error(f"couldn't add: photo for {vk_id=} ({e.__class__.__name__})")

    def add_reaction(self, user_id, candidate_id, mark=None):
        if self.reaction_exists(user_id, candidate_id):
            with self.Session() as session:
                with session.begin():
                    reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                             Reaction.candidate_id == candidate_id).first()
                    reaction.mark = mark
                    logging.info(f"updated: reaction with {mark=} for {user_id=}, {candidate_id=}")
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
                    logging.info(f"added: reaction '{bool(mark)}' for {user_id=}, {candidate_id=}")
                except Exception as e:
                    logging.error(f"couldn't add: reaction {mark=} for "
                                  f"{user_id=}, {candidate_id=} ({e.__class__.__name__})")

    def reaction_exists(self, user_id, candidate_id):
        with self.Session() as session:
            with session.begin():
                reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                         Reaction.candidate_id == candidate_id).one_or_none()
                if reaction:
                    logging.debug(f"checked: reaction for {user_id=}, {candidate_id=} exists")
                    return True
                else:
                    logging.debug(f"checked: reaction for {user_id=}, {candidate_id=} doesn't exist")
                    return False

    def get_reaction(self, user_id, candidate_id):
        with self.Session() as session:
            with session.begin():
                reaction = session.query(Reaction).where(Reaction.user_id == user_id,
                                                         Reaction.candidate_id == candidate_id).one_or_none()
                if reaction:
                    logging.debug(f"got: {reaction}")
                    session.expunge(reaction)
                    return reaction
                else:
                    logging.warning(f"not found: reaction for {user_id=}, {candidate_id=}")
                    return None

    def get_photos(self, candidate_id):
        with self.Session() as session:
            with session.begin():
                photos = session.query(Photo).where(Photo.candidate_id == candidate_id).all()
                session.expunge_all()
                if len(photos) != 0:
                    logging.debug(f"got: {len(photos)} photos for {candidate_id=}")
                else:
                    logging.warning(f"not found: any photo for {candidate_id=}")
                return photos

    def get_all_candidates(self, user_id):
        with (self.Session() as session):
            with session.begin():
                candidates = session.query(Candidate).select_from(Candidate).join(Reaction) \
                    .where(Reaction.user_id == user_id).all()
                session.expunge_all()
                logging.info(f"getting all {len(candidates)} candidates for {user_id=}")
                return candidates

    def count_candidates_with_mark(self, user_id, mark=None):
        with (self.Session() as session):
            with session.begin():
                amount = session.query(Candidate).select_from(Candidate).join(Reaction) \
                    .where(Reaction.user_id == user_id, Reaction.mark == mark).count()
                logging.debug(f"checked: there are {amount} candidates with {mark=} for {user_id=}")
                return amount

    def get_candidates_with_mark(self, user_id, mark=None):
        if self.count_candidates_with_mark(user_id, mark):
            with (self.Session() as session):
                with session.begin():
                    candidates = session.query(Candidate).select_from(Candidate).join(Reaction) \
                        .where(Reaction.user_id == user_id, Reaction.mark == mark).all()
                    session.expunge_all()
                    logging.info(f"getting {len(candidates)} candidates with {mark=} for {user_id=}")
                    return candidates
        else:
            logging.warning(f"not found: any candidate with {mark=} for {user_id=}")

    def get_random_none_candidate(self, user_id):
        if self.count_candidates_with_mark(user_id):
            with self.Session() as session:
                with session.begin():
                    try:
                        logging.info(f"getting random candidate for {user_id=}")
                        got_candidate = 0
                        while not got_candidate:
                            count = session.query(func.count(Candidate.id)).scalar_subquery()
                            offset_param = func.floor(func.random() * count)

                            all_candidates = session. \
                                query(Candidate) \
                                .select_from(Candidate).join(Reaction) \
                                .where(Reaction.user_id == user_id, Reaction.mark == None)
                            rand_candidates = all_candidates.offset(offset_param)
                            candidate = rand_candidates.limit(1).all()
                            got_candidate = len(candidate)
                        session.expunge_all()
                        logging.info(f"got: {candidate} (random) with mark=None for {user_id=}")
                        return candidate[0]
                    except Exception as e:
                        logging.error(f"couldn't get: random candidate for {user_id=} ({e.__class__.__name__})")
        else:
            logging.warning(f"not found: any candidate with mark=None for {user_id=}")


if __name__ == '__main__':
    vk_db = VkBotDatabase()

    # vk_db.recreate_tables()
