from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

database_uri = "sqlite:///database.db"
engine = create_engine(database_uri, echo=True)


class Base(DeclarativeBase):
    pass


class VkontakteProfile(Base):
    __tablename__ = "vk_user"
    user_id = Column(Integer, primary_key=True)
    Pairs = relationship("Pair", back_populates="vk_user")


class Pair(Base):
    __tablename__ = "pair"
    id = Column(Integer, primary_key=True)
    pair = Column(Integer)
    vk_user_id = Column(Integer, ForeignKey("vk_user.user_id"))
    vk_user = relationship("VkUser", back_populates="pairs")


Base.metadata.create_all(bind=engine)
engine = create_engine(database_uri, echo=False)
Session = sessionmaker(autoflush=False, bind=engine)


def save_vk_user(user_id):
    if find_vk_user_by_id(user_id) is None:
        with Session(autoflush=False, bind=engine) as db:
            vk_user = VkUser(user_id=user_id)
            db.add(vk_user)
            db.commit()


def get_users():
    with Session(autoflush=False, bind=engine) as db:
        return db.query(VkUser).all()


def find_vk_user_by_id(user_id):
    with Session(autoflush=False, bind=engine) as db:
        return db.query(VkUser).filter(VkUser.user_id == user_id).first()


def look_for_pairs_in_database(user_id):
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(VkUser).filter(VkUser.user_id == user_id).first()
        return [i.pair_user_id for i in user.pairs]


def add_to_database(user_id, pair_user_id):
    with Session(autoflush=False, bind=engine) as db:
        pair = pair(pair_user_id=pair_user_id, vk_user_id=user_id)
        db.add(pair)
        db.commit()
