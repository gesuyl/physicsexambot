from sqlalchemy import create_engine, inspect, func
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



Base = declarative_base()


class Images(Base):
    """
    Class for Images table

    id: int
    file_name: str
    recog_text: str
    """
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    recog_text = Column(Text)


    def to_dict(self) -> dict:
        """
        Convert object to dict

        :return: dict
        """
        return {
            "id": self.id,
            "file_name": self.file_name,
            "recog_text": self.recog_text
            }


class Users(Base):
    """
    Class for Users table
    
    id: int
    username: str
    role: str
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    role = Column(String)


    def to_dict(self) -> dict:
        """
        Convert object to dict

        :return: dict
        """
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
            }


class MainConf(Base):
    """
    Class for MainConf table

    img_proc_count: int
    precision: float
    """
    __tablename__ = "main_conf"
    id = Column(Integer, primary_key=True)
    img_proc_count = Column(Integer)
    precision = Column(Float)


    def to_dict(self) -> dict:
        """
        Convert object to dict

        :return: dict
        """
        return {
            "img_proc_count": self.img_proc_count,
            "precision": self.precision,
            }


class Database:
    """
    Class for database

    engine: object
    sessionmaker: object
    """
    def __init__(self, db_url: str) -> None:
        """
        Initialize database
        
        :param db_url: str
        """
        self.engine = create_engine(db_url)      
        self.sessionmaker = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        with self.sessionmaker() as session:
                    if session.query(MainConf).count() == 0:
                        default_main_conf = MainConf(img_proc_count=0, precision=0.0)
                        session.add(default_main_conf)
                        session.commit()

        print("[#] Database connected")


    def add_user(self, id: int, username: str, role: str) -> None:
        """
        Add user to database
        
        :param id: int
        :param username: str
        :param role: str
        """
        with self.sessionmaker() as session:
            user = Users(
                id=id,
                username=username,
                role=role
            )
            session.add(user)
            session.commit()


    def delete_user(self, username: str) -> None:
        """
        Delete user from database

        :param username: str
        """
        with self.sessionmaker() as session:
            user = session.query(Users).filter_by(username=username).first()
            if not user:
                return
            session.delete(user)
            session.commit()


    def save_image_data(self, file_name: str, recog_text: str) -> None:
        """
        Save image data to database

        :param file_name: str
        :param recog_text: str
        """
        with self.sessionmaker() as session:
            images = Images(
                file_name=file_name,
                recog_text=recog_text
            )
            session.add(images)
            session.commit()


    def save_image_data_batch(self, image_data_list: list) -> None:
        """
        Save batch image data to database

        :param image_data_list: list
        """
        with self.sessionmaker() as session:
            session.bulk_save_objects(image_data_list)
            session.commit()


    def get_images(self, image_id: int = None) -> list:
        """
        Get image data from database
        
        :param image_id: int
        """
        with self.sessionmaker() as session:
            if image_id:
                return session.query(Images).filter_by(id=image_id).first()
            else:
                return session.query(Images).all()


    def get_users(self, username: str = None) -> list:
        """
        Get user data from database

        :param username: str
        """
        with self.sessionmaker() as session:
            if username:
                return session.query(Users).filter_by(username=username).first()
            else:
                return session.query(Users).all()


    def update_attr(self, count: int = None, precision: float = None) -> None:
        """
        Update image count or precision in MainConf table

        :param count: int
        :param precision: float
        """
        with self.sessionmaker() as session:
            conf = session.query(MainConf).first()
            if count:
                conf.img_proc_count = count
            if precision:
                conf.precision = precision
            session.commit()


    def get_main_conf(self) -> list:
        """
        Get main configuration from database

        :return: list
        """
        with self.sessionmaker() as session:
            return session.query(MainConf).all()



    def empty_table(self, table_name: str) -> None:
        """
        Empty table by table name

        :param table_name: str
        """
        table_to_empty = Base.metadata.tables.get(table_name)

        with self.sessionmaker() as session:
            session.execute(table_to_empty.delete())
            session.commit()


    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists

        :param table_name: str

        :return: bool
        """
        insp = inspect(self.engine)

        return insp.has_table(table_name)


    def get_row_count(self, table_name: str) -> int:
        """
        Get row count from table

        :param table_name: str

        :return: int
        """
        with self.sessionmaker() as session:            
            return session.query(func.count(f"{table_name}.id")).scalar()
