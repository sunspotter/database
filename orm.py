import datetime

def _convert_bool(s): 
    '''
    Function to be just used here!!
    '''
    if s == "true": 
        return True; 
    return False

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean,\
    ForeignKey

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String)

    def __repr__(self):
        return "<User {0}>".format(self.username)

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    sszn = Column(Integer)
    hale = Column(String)
    zurich = Column(String(3))
    ars_n = Column(Integer)
    obs_date = Column(DateTime)
    url = Column(String)
    noaa_n = Column(Integer)
    bipolesep = Column(Float)
    flux = Column(Float)
    flux_frac = Column(Float)
    hcpos_x = Column(Float)
    hcpos_y = Column(Float)
    pxpos_x = Column(Float)
    pxpos_y = Column(Float)
    c1flr24h = Column(Boolean)
    m1flr24h = Column(Boolean)
    m5flr12h = Column(Boolean)

    def __repr__(self):
        return "<Image {noaa}[{hcx:.2f}{hcy:.2f}]@{date}:{url}>".format(
            noaa=self.noaa_n, 
            hcx=self.hcpos_x,
            hcy=self.hcpos_y,
            date=self.obs_date,
            url=self.url)

class Classification(Base):
    __tablename__ = 'classification'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    image_id_0 = Column(Integer, ForeignKey('images.id'))
    image_id_1 = Column(Integer, ForeignKey('images.id'))
    image0_more_complex_image1 = Column(Boolean)
    used_inverted = Column(Boolean)
    language = Column(String(2))
    date_started = Column(DateTime)
    date_finished = Column(DateTime)
    date_created = Column(DateTime)
    
    def __repr__(self):
        return "<Classification {image0} {direction} {image1} by {user}>".format(
            image0=self.image_id_0,
            direction='>' if self.image0_more_complex_image1 else '<',
            image1=self.image_id_1,
            user=self.user_id)

class ZooRank(Base):
    __tablename__ = 'zoorank'
    
    id = Column(Integer, primary_key = True)
    image_id = Column(Integer, ForeignKey('images.id'))
    count = Column(Integer)
    k_value = Column(Integer)
    score = Column(Float)
    std_dev = Column(Float)
    angle = Column(Float)
    area = Column(Float)  # is this AR or rank?
    areafrac = Column(Float)
    areathesh = Column(Float)

    def __repr__(self):
        return "<ZooRank {image}:{score:.2f}>".format(image=self.image_id,
                                                      score=self.score)


from sqlalchemy import create_engine
engine = create_engine('sqlite:///sunspotter.db')
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session = Session(bind=engine)

# INGESTING DATA
file_ranking = '2014-03-29_sunspot_rankings.csv'
file_classification = '2014-03-29_sunspot_classifications.csv'

# # 1st ingesting ranking file (it contains images info and ranking)
# with open(file_ranking, 'r') as rank_file:
#     for line in rank_file:
#         if line[0] == '"':
#             line_list = line.replace('"','').\
#                 replace('[','').replace(']','').split(',')

#             # list positions obtained from:
#             # a = '"image","zooniverse_id","count","k","score","std_dev","angle","area","areafrac","areathesh","bipolesep","c1flr24hr","date","filename","flux","fluxfrac","hale","hcpos","m1flr12hr","m5flr12hr","n_nar","noaa","pxpos","sszn","zurich"'
#             # alist = a.replace('hcpos','hcposx,hcposy').replace('pxpos','pxposx,pxposy').replace('"','').replace('[','').replace(']','').split(',')
#             # for i,elem in enumerate(alist):
#             #    print "{0:2d}: {1}".format(i, elem)

#             #Convert date_obs to datetime
#             date_obs = datetime.datetime.strptime(line_list[12], 
#                                                   '%Y-%m-%dT%H:%M:%SZ')

#             image = Images(filename=line_list[13],
#                           sszn=line_list[25],
#                           hale=line_list[16],
#                           zurich=line_list[26],
#                           ars_n=line_list[21],
#                           obs_date=date_obs,
#                           url=line_list[0],
#                           noaa_n=line_list[22],
#                           bipolesep=line_list[10],
#                           flux=line_list[14],
#                           flux_frac=line_list[15],
#                           hcpos_x=line_list[17],
#                           hcpos_y=line_list[18],
#                           pxpos_x=line_list[23],
#                           pxpos_y=line_list[24],
#                           c1flr24h=_convert_bool(line_list[11]),
#                           m1flr24h=_convert_bool(line_list[19]),
#                           m5flr12h=_convert_bool(line_list[20]),
#                           )
#             session.add(image)
#             session.commit()

#             rank = ZooRank(image_id=image.id,
#                            count=line_list[2],
#                            k_value=line_list[3],
#                            score=line_list[4],
#                            std_dev=line_list[5],
#                            angle=line_list[6],
#                            area=line_list[7],
#                            areafrac=line_list[8],
#                            areathesh=line_list[9],
#                            )
#             session.add(rank)
#             session.commit()
            

# Add the users and the classifications from the second file
with open(file_classification, 'r') as classif_file:
    for line in classif_file:
        if line[0] == '"':
            line_list = line.replace('"','').replace('GMT',',').replace('UTC',',').split(',')
            
            user = User(username=line_list[3])

            # Check whether this user is already in the db
            query = session.query(User).filter(User.username == user.username).all()
            if not query:
                session.add(user)
                session.commit()
            else:
                user.id = query[0].id

            # Query for the images
            image0 = session.query(Images).filter(Images.filename == line_list[6]).all()[0]
            image1 = session.query(Images).filter(Images.filename == line_list[12]).all()[0]
            try: # Some are not selected
                complexity = True if int(line_list[17]) == 0 else False
            except:
                complexity = None
            inverted = True if line_list[18] == 'true' else False

            # "Wed, 26 Feb 2014 20:13:59 GMT" - carefull, day of the week
            # becomes as part of the column before. Also, replaced the GMT or UTC out of it
            date_started =  datetime.datetime.strptime(line_list[21],
                                                       ' %d %b %Y %H:%M:%S ')
            date_finished = datetime.datetime.strptime(line_list[24],
                                                       ' %d %b %Y %H:%M:%S ')
            # "2014-02-26 20:14:19 "
            date_created =  datetime.datetime.strptime(line_list[1],
                                                       '%Y-%m-%d %H:%M:%S ')

            classification = Classification(user_id = user.id,
                                            image_id_0=image0.id,
                                            image_id_1=image1.id,
                                            image0_more_complex_image1=complexity,
                                            used_inverted=inverted,
                                            language=line_list[18],
                                            date_started=date_started,
                                            date_finished=date_finished,
                                            date_created=date_created, 
                                            )
            session.add(classification)
            session.commit()


