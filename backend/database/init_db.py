from database.connection import engine
from database.base import Base

# Import all models here
import models.user
import models.portfolio
import models.watchlist
import models.prediction
import models.news


def init_database():
    Base.metadata.create_all(bind=engine)