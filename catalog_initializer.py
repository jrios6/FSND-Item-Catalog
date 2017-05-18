from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, CatalogItem, Category, User

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Soccer Category
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

item1 = CatalogItem(user=User1, name = "Ball", description="Good Ball", category=category1)
session.add(item1)
session.commit()

# Items for Basketball Category
category2 = Category(name="Basketball")
session.add(category2)
session.commit()

item2 = CatalogItem(user=User1, name = "BBall", description="Good BBall", category=category2)
session.add(item2)
session.commit()

# Items for Baseball category
category3 = Category(name="Baseball")
session.add(category3)
session.commit()

item3 = CatalogItem(user=User1, name = "baseBall", description="Good baseBall", category=category3)
session.add(item3)
session.commit()


# category4 = Category(name="Frisbee")
# session.add(category4)
# session.commit()
#
# category5 = Category(name="Snowboarding")
# session.add(category5)
# session.commit()
#
# category6 = Category(name="Rock Climbing")
# session.add(category6)
# session.commit()
#
# category7 = Category(name="Foosball")
# session.add(category7)
# session.commit()
#
# category8 = Category(name="Skating")
# session.add(category8)
# session.commit()
#
# category9 = Category(name="Hockey")
# session.add(category9)
# session.commit()


print "added catalog items!"
