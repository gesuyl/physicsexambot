from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



Base = declarative_base()


class ImageData(Base):
    __tablename__ = "image_data"
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    recog_text = Column(Text)


    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "recog_text": self.recog_text
            }


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    role = Column(String)


    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
            }


class MainConf(Base):
    __tablename__ = "main_conf"
    id = Column(Integer, primary_key=True)
    img_proc_count = Column(Integer)
    precision = Column(Float)


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)        
        self.Sessionmaker = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        with self.Sessionmaker() as session:
                    if session.query(MainConf).count() == 0:
                        default_main_conf = MainConf(img_proc_count=0, precision=0.0)
                        session.add(default_main_conf)
                        session.commit()

        print("[#] Database connected")


    def add_user(self, id, username, role):
        with self.Sessionmaker() as session:
            user = Users(
                id=id,
                username=username,
                role=role
            )
            session.add(user)
            session.commit()


    def delete_user(self, username):
        with self.Sessionmaker() as session:
            user = session.query(Users).filter_by(username=username).first()
            if not user:
                return
            session.delete(user)
            session.commit()


    def save_image_data(self, file_name, recog_text):
        with self.Sessionmaker() as session:
            image_data = ImageData(
                file_name=file_name,
                recog_text=recog_text
            )
            session.add(image_data)
            session.commit()


    def save_image_data_batch(self, image_data_list):
        with self.Sessionmaker() as session:
            session.bulk_save_objects(image_data_list)
            session.commit()


    def get_images(self, image_id=None):
        with self.Sessionmaker() as session:
            if image_id:
                return session.query(ImageData).filter_by(id=image_id).first()
            else:
                return session.query(ImageData).all()


    def get_users(self, username=None):
        with self.Sessionmaker() as session:
            if username:
                return session.query(Users).filter_by(username=username).first()
            else:
                return session.query(Users).all()


    def update_attr(self, count=None, precision=None):
        with self.Sessionmaker() as session:
            conf = session.query(MainConf).first()
            if count:
                conf.img_proc_count = count
            if precision:
                conf.precision = precision
            session.commit()


    def get_image_processing_count(self):
        with self.Sessionmaker() as session:
            main_conf = session.query(MainConf).first()
            if main_conf:
                return main_conf.img_proc_count
            return 0


    def get_precision(self):
        with self.Sessionmaker() as session:
            main_conf = session.query(MainConf).first()
            if main_conf:
                return main_conf.precision
            return 0


    def empty_table(self, table_name):
        table_to_empty = Base.metadata.tables.get(table_name)

        with self.Sessionmaker() as session:
            session.execute(table_to_empty.delete())
            session.commit()
