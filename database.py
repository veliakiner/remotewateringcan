from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session

Base = declarative_base()


class MoistureReading(Base):
    __tablename__ = "reading"

    id = Column(Integer, primary_key=True)
    reading = Column(Float)
    date = Column(Date)

    def __repr__(self):
        return "<User(reading='%s', date='%s')>" % (
            self.reading, self.date)


class WateringEvent(Base):
    __tablename__ = "watering"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    duration = Column(Integer)

    def __repr__(self):
        return "<User(date='%s', duration='%s')>" % (
            self.date, self.duration)


def init_db():
    engine = create_engine('sqlite:///waterer.db', echo=False)
    Base.metadata.create_all(engine)
    return Session()



if __name__ == "__main__":
    engine = create_engine('sqlite:///waterer.db', echo=False)
    db = Base.metadata.create_all(engine)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    # import pdb;pdb.set_trace()
    session = Session()
    from datetime import datetime
    event = MoistureReading(reading=100, date=datetime.now())
    session.add(event)
    session.flush()
    session.commit()
    session.flush()
    print(session.query(MoistureReading.date).all())
