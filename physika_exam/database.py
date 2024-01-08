from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)


    def add_user(self, username, role):
        with self.Session() as session:
            user = Users(username=username, role=role)
            session.add(user)
            session.commit()


    def save_image_data(self, file_name, recog_text):
        with self.Session() as session:
            image_data = ImageData(file_name=file_name, recog_text=recog_text)
            session.add(image_data)
            session.commit()

    
    def get_image_data(self, image_id=None):
        with self.Session() as session:
            if image_id:
                return session.query(ImageData).filter_by(id=image_id).first()
            else:
                return session.query(ImageData).all() 


    def get_users(self, username=None):
        with self.Session() as session:
            if username:
                return session.query(Users).filter_by(username=username).first()
            else:
                return session.query(Users).all()

    def update_image_processing_count(self, count, precision):
        with self.Session() as session:
            conf = session.query(MainConf).first()
            conf.img_proc_count = count
            conf.precision = precision
            session.commit()


    def get_image_processing_count(self):
        with self.Session() as session:
            return session.query(MainConf).first().img_proc_count


    def get_precision(self):
        with self.Session() as session:
            return session.query(MainConf).first().precision
        

class ImageData(Base):
    __tablename__ = 'image_data'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    recog_text = Column(Text)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    role = Column(String)


class MainConf(Base):
    __tablename__ = 'main_conf'
    id = Column(Integer, primary_key=True)
    img_proc_count = Column(Integer)
    precision = Column(Float)
