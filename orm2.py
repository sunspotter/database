import datetime

from sqlalchemy import create_engine, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean,\
    ForeignKey
from sqlalchemy.orm import relationship

def _convert_bool(s): 
    '''
    Function to be just used here!!
    '''
    if s == "true": 
        return True; 
    return False

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String)

    def __repr__(self):
        return "<User {0}>".format(self.username)

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    zoo_id = Column(String)
    filename = Column(String)   # previously it was unique, now it's the fd image!
    sszn = Column(Integer)
    sszstatus = Column(Integer) # I don't know what's this 1,..,7
    ar_id = Column(Integer)  # SMART id? ARs identified?  1,...,<20
    # awk -F'","' '{print $1 "," $10}' 2014-06-15_sunspot_rankings.csv | grep -e ",2." | wc -l
    obs_date = Column(DateTime)
    url = Column(String)  # Now it's unique! and reference for classifications.
    bipolesep = Column(Float)
    bmax = Column(Float)
    deg2dc = Column(Float)      # I don't know what's this
    detstatus = Column(Integer) # I don't know what's this - All 7
    # awk -F'","' '{print $1 "," $19}' 2014-06-15_sunspot_rankings.csv | grep -v ",7"
    flux = Column(Float)
    flux_frac = Column(Float)
    magstatus = Column(Integer)  # I don't know what's this - All 0
    # awk -F'","' '{print $1 "," $28}' 2014-06-15_sunspot_rankings.csv | grep -v ",0" | wc -l
    npsl = Column(Integer)       # I don't know what's this - 0,..,32
    # awk -F'","' '{print $1 "," $29}' 2014-06-15_sunspot_rankings.csv | grep -e ",3." | wc -l
    # 4 >= 30
    posstatus = Column(Integer)  # I don't know what's this - all 7 except 4
    # awk -F'","' '{print $1 "," $30}' 2014-06-15_sunspot_rankings.csv | grep -v ',7' | wc -l
    pslcurvature = Column(Float) # I don't know what's this - all 0.0
    # awk -F'","' '{print $1 "," $31}' 2014-06-15_sunspot_rankings.csv | grep -v ',0.0' | wc -l
    psllength = Column(Float)
    wlsg = Column(Float)
    hcpos_x = Column(Float)
    hcpos_y = Column(Float)
    pxpos_x = Column(Float)
    pxpos_y = Column(Float)
    c1flr12h = Column(Boolean)
    c1flr24h = Column(Boolean)
    c5flr12h = Column(Boolean)
    c5flr24h = Column(Boolean)
    m1flr12h = Column(Boolean)
    m1flr24h = Column(Boolean)
    m5flr12h = Column(Boolean)
    m5flr24h = Column(Boolean)
    pxscl_hpc2stg = Column(Float) # I don't know what's this - all 0.0
    # awk -F'","' '{print $1 "," $34}' 2014-06-15_sunspot_rankings.csv | grep -e ",0.0" | wc -l
    rvalue = Column(Float)
    

    def __repr__(self):
        return "<Image {zoo}[{hcx:.2f}{hcy:.2f}]@{date}:{url}>".format(
            zoo=self.zoo_id, 
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

    user = relationship('User', backref = 'users')

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
    area = Column(Float)  # is this AR or rank?
    areafrac = Column(Float)
    areathesh = Column(String)
    
    image = relationship('Images', backref = 'images')

    def __repr__(self):
        return "<ZooRank {image}:{score:.2f}>".format(image=self.image_id,
                                                      score=self.score)


engine = create_engine('sqlite:///sunspotter.db')
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session = Session(bind=engine)

# INGESTING DATA
file_ranking = '2014-06-15_sunspot_rankings.csv'
file_classification = '2014-06-15_sunspot_classifications_awk.csv'

print("Starting with the images")
# 1st ingesting ranking file (it contains images info and ranking)
with open(file_ranking, 'r') as rank_file:
    for line in rank_file:
        if line[0] == '"' and line[1] != 'i':
            line_list = line.replace('"','').\
                replace('[','').replace(']','').split(',')

            # list positions obtained from:
            # a = '"image","zooniverse_id","count","k","score","std_dev","area","areafrac","areathesh","arid","bipolesep","bmax","c1flr12hr","c1flr24hr","c5flr12hr","c5flr24hr","date","deg2dc","detstatus","filename","flux","fluxfrac","hcpos","m1flr12hr","m1flr24hr","m5flr12hr","m5flr24hr","magstatus","npsl","posstatus","pslcurvature","psllength","pxpos","pxscl_hpc2stg","rvalue","sszn","sszstatus","wlsg"'
            # alist = a.replace('hcpos','hcposx,hcposy').replace('pxpos','pxposx,pxposy').replace('"','').replace('[','').replace(']','').split(',')
            # for i,elem in enumerate(alist):
            #    print "{0:2d}: {1}".format(i, elem)

            #Convert date_obs to datetime
            date_obs = datetime.datetime.strptime(line_list[16], 
                                                  '%Y-%m-%dT%H:%M:%SZ')

            image = Images(url=line_list[0],
                           zoo_id=line_list[1],
                           ar_id=line_list[9],
                           bipolesep=line_list[10],
                           bmax=line_list[11],
                           c1flr12h=_convert_bool(line_list[12]),
                           c1flr24h=_convert_bool(line_list[13]),
                           c5flr12h=_convert_bool(line_list[14]),
                           c5flr24h=_convert_bool(line_list[15]),
                           obs_date=date_obs,
                           deg2dc=line_list[17],
                           detstatus=line_list[18],
                           filename=line_list[19],
                           flux=line_list[20],
                           flux_frac=line_list[21],
                           hcpos_x=line_list[22],
                           hcpos_y=line_list[23],
                           m1flr12h=_convert_bool(line_list[24]),
                           m1flr24h=_convert_bool(line_list[25]),
                           m5flr12h=_convert_bool(line_list[26]),
                           m5flr24h=_convert_bool(line_list[27]),
                           magstatus=line_list[28],
                           npsl=line_list[29],
                           posstatus=line_list[30],
                           pslcurvature=line_list[31],
                           psllength=line_list[32],
                           pxpos_x=line_list[33],
                           pxpos_y=line_list[34],
                           pxscl_hpc2stg=line_list[35],
                           rvalue=line_list[36],
                           sszn=line_list[37],
                           sszstatus=line_list[38],
                           wlsg=line_list[39]
                           )
            session.add(image)

            rank = ZooRank(count=line_list[2],
                           k_value=line_list[3],
                           score=line_list[4],
                           std_dev=line_list[5],
                           area=line_list[6],
                           areafrac=line_list[7],
                           areathesh=line_list[8],
                           image=image
                           )
            session.add(rank)
            session.commit()

            
def create_or_get_user(user_name):
    (ret,), = session.query(exists().where(User.username == user_name))
    if not ret:
        obj = User(username = user_name)
        session.add(obj)
    else:
        obj = session.query(User).filter(User.username == user_name).first()
    return obj

def create_or_get_image(url):
    (ret,), = session.query(exists().where(Images.url == url))
    if not ret:
        obj = Images(url=url)
        session.add(obj)
    else:
        obj = session.query(Images).filter(Images.url == url).first()
    return obj



print("Images and it's ranking added to the database.")
# Add the users and the classifications from the second file
with open(file_classification, 'r') as classif_file:
    for line in classif_file:
        if line[0] == '"' and line[1:4] != 'cla':
            line_list = line.replace('"','').replace('GMT',',').replace('UTC',',').split(',')
            
            #user = User(username=line_list[3])

            # Check whether this user is already in the db (Thanks Derdon!)
            #(ret,), = session.query(exists().where(
            #        User.username == user.username))

            #if not ret:
            #    session.add(user)
                #session.commit()
            #else:
            #    user.id = query[0].id

            # Query for the images
            image0 = create_or_get_image(line_list[4])
            image1 = create_or_get_image(line_list[8])
            try: # Some are not selected
                complexity = int(line_list[12]) == 0
            except ValueError:
                complexity = None
            inverted = line_list[13] == 'true'

            # "Wed, 26 Feb 2014 20:13:59 GMT" - carefull, day of the week
            # becomes as part of the column before. Also, replaced the GMT or UTC out of it
            date_started =  datetime.datetime.strptime(line_list[16],
                                                       ' %d %b %Y %H:%M:%S ')
            date_finished = datetime.datetime.strptime(line_list[19],
                                                       ' %d %b %Y %H:%M:%S ')
            # "2014-02-26 20:14:19 "
            date_created =  datetime.datetime.strptime(line_list[1],
                                                       '%Y-%m-%d %H:%M:%S ')

            classification = Classification(image_id_0=image0.id,
                                            image_id_1=image1.id,
                                            image0_more_complex_image1=complexity,
                                            used_inverted=inverted,
                                            language=line_list[14],
                                            date_started=date_started,
                                            date_finished=date_finished,
                                            date_created=date_created, 
                                            user=create_or_get_user(line_list[3])
                                            )
            session.add(classification)
            session.commit()


