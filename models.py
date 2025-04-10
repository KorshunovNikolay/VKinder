from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column


Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[str] = mapped_column(String(length=20), unique=True)

    def __repr__(self):
        return f'User {self.id}: {self.vk_id}'


class Candidate(Base):
    __tablename__ = 'Candidates'

    id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[str] = mapped_column(String(length=20), unique=True)
    first_name: Mapped[str] = mapped_column(String(length=50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=50), nullable=True)
    link: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f'Candidate {self.id}: {self.vk_id}'


class Photo(Base):
    __tablename__ = 'Photos'

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String(length=20), ForeignKey('Candidates.vk_id'), nullable=False)
    link: Mapped[str] = mapped_column(String)

    candidate: Mapped['Candidate'] = relationship(backref='photo')

    def __repr__(self):
        return f'Photo {self.id}: {self.candidate_id}, {self.link}'


class Reaction(Base):
    __tablename__ = 'Reactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(length=20), ForeignKey('Users.vk_id'), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(length=20), ForeignKey('Candidates.vk_id'), nullable=False)
    mark: Mapped[bool] = mapped_column(nullable=True)

    user: Mapped['User'] = relationship(backref='reaction')
    candidate: Mapped['Candidate'] = relationship(backref='reaction')

    def __repr__(self):
        return f"Reaction {self.id}: {self.user_id}, {self.candidate_id}, {self.mark}"


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def create_tables(engine):
    Base.metadata.create_all(engine)
