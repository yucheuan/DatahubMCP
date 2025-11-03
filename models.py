from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, Float
from database import Base

class ChildAttendance(Base):
    __tablename__ = "child_attendance_test"

    id = Column(Integer, primary_key=True, index=True)
    childname = Column(String(45))
    child_attendance_testcol = Column(Integer)

class DailyAttendanceLog(Base):
    __tablename__ = "dailyattendancelog_new"

    Form_ID = Column(String(100), primary_key=True)
    DOR = Column(DateTime)
    Site_ID = Column(String(100))
    Room_ID = Column(String(100))
    Form_Date = Column(DateTime)
    Log_Type1 = Column(Integer)
    Log_Type2 = Column(Integer)
    Log_Description = Column(Text)
    Timein = Column(String(100))
    Timeout = Column(String(100))
    Breakfast = Column(Integer)
    Lunch = Column(Integer)
    PM_Snack = Column(Integer)
    Meal_Confirm_Datetime = Column(DateTime)

class AgencySites(Base):
    __tablename__ = "agencysites"

    Site_ID = Column(String(50), primary_key=True)
    Site_Name = Column(String(200))
    Site_Zip = Column(String(50))
    Site_Address = Column(String(500))

class AgencySiteRooms(Base):
    __tablename__ = "agencysiterooms"

    Room_ID = Column(String(100), primary_key=True)
    Site_ID = Column(String(100))
    Room_Name = Column(String(100))
    Room_AgeGroup = Column(String(50))

class CenterSupportReport(Base):
    __tablename__ = "centersupportreport"

    Form_ID = Column(String(100), primary_key=True)
    User_ID = Column(String(100))
    Site_ID = Column(String(500))
    Form_Date = Column(DateTime)
    Start_Time = Column(String(100))
    End_Time = Column(String(100))
    Support_Log = Column(Text)
    Category = Column(String(100))
    OnsiteRemote = Column(Integer)
    Strategies = Column(String(500))
    Strategies_Other = Column(Text)
    Debrief = Column(String(500))

class LessonPlansPreschool(Base):
    __tablename__ = "lessonplans_2324_preschool"

    Form_ID = Column(String(100), primary_key=True)
    DOR = Column(DateTime)
    Site_ID = Column(String(100))
    Room_ID = Column(String(100))
    WeekCount = Column(Integer)
    Teacher_Name = Column(String(100))
    Study_Topic = Column(String(1000))
    Focus_Week = Column(Text)
    IntentionalTeachingCards = Column(Text)
    MightyMinutes = Column(Text)
    Vocabulary = Column(Text)
    Books = Column(Text)
    FamilyEngagement = Column(Text)
    Individualizations = Column(Text)
    Blocks = Column(Text)
    Science = Column(Text)
    L_Math = Column(Text)
    WaterSensory = Column(Text)
    Writing = Column(Text)
    DramaticPlay = Column(Text)
    Manipulatives = Column(Text)
    Art = Column(Text)
    MusicMovement = Column(Text)
    Library = Column(Text)
    OutdoorClassroom = Column(Text)
    Other = Column(Text)
    Teachers = Column(String(500))
    Enroll_Year = Column(String(100))

class LessonPlansIT(Base):
    __tablename__ = "lessonplans_2324_it"

    Form_ID = Column(String(100), primary_key=True)
    DOR = Column(DateTime)
    Site_ID = Column(String(100))
    Room_ID = Column(String(100))
    WeekCount = Column(Integer)
    Teacher_Name = Column(String(100))
    Study_Topic = Column(String(1000))
    Focus_Week = Column(Text)
    IntentionalTeachingCards = Column(Text)
    MightyMinutes = Column(Text)
    Vocabulary = Column(Text)
    Books = Column(Text)
    FamilyEngagement = Column(Text)
    Individualizations = Column(Text)
    Infant_Modification = Column(Text)
    Blocks = Column(Text)
    ScienceMath = Column(Text)
    MusicMovement = Column(Text)
    WaterSensory = Column(Text)
    Art = Column(Text)
    DramaticPlay = Column(Text)
    Manipulatives = Column(Text)
    OutdoorClassroom = Column(Text)
    Teachers = Column(String(500))
    Enroll_Year = Column(String(100))

class LessonPlansDetail(Base):
    __tablename__ = "lessonplans_detail"

    Log_ID = Column(String(100), primary_key=True)
    Form_ID = Column(String(100))
    P_No = Column(String(100))
    P_Content = Column(Text)

class DRDPItems(Base):
    __tablename__ = "drdp_items"

    UUID_Item = Column(String(200), primary_key=True)
    Item_Name = Column(Text)
    Item_Catagory = Column(Text)

class DRDPRecord(Base):
    __tablename__ = "drdp_record"

    Form_ID = Column(String(100), primary_key=True)
    Enroll_Year = Column(String(100))
    Child_ID = Column(String(100))
    DOR = Column(DateTime)
    Site_ID = Column(String(100))
    Room_ID = Column(String(100))
    Submit_Datetime = Column(DateTime)
    ATL_REG_1 = Column(Float)
    ATL_REG_2 = Column(Float)
    ATL_REG_3 = Column(Float)
    ATL_REG_4 = Column(Float)
    ATL_REG_5 = Column(Float)
    ATL_REG_6 = Column(Float)
    ATL_REG_7 = Column(Float)
    SED_1 = Column(Float)
    SED_2 = Column(Float)
    SED_3 = Column(Float)
    SED_4 = Column(Float)
    SED_5 = Column(Float)
    LLD_1 = Column(Float)
    LLD_2 = Column(Float)
    LLD_3 = Column(Float)
    LLD_4 = Column(Float)
    LLD_5 = Column(Float)
    LLD_6 = Column(Float)
    LLD_7 = Column(Float)
    LLD_8 = Column(Float)
    LLD_9 = Column(Float)
    LLD_10 = Column(Float)
    ELD_1 = Column(Float)
    ELD_2 = Column(Float)
    ELD_3 = Column(Float)
    ELD_4 = Column(Float)
    COG_1 = Column(Float)
    COG_2 = Column(Float)
    COG_3 = Column(Float)
    COG_4 = Column(Float)
    COG_5 = Column(Float)
    COG_6 = Column(Float)
    COG_7 = Column(Float)
    COG_8 = Column(Float)
    COG_9 = Column(Float)
    COG_10 = Column(Float)
    COG_11 = Column(Float)
    PD_HLTH_1 = Column(Float)
    PD_HLTH_2 = Column(Float)
    PD_HLTH_3 = Column(Float)
    PD_HLTH_4 = Column(Float)
    PD_HLTH_5 = Column(Float)
    PD_HLTH_6 = Column(Float)
    PD_HLTH_7 = Column(Float)
    PD_HLTH_8 = Column(Float)
    PD_HLTH_9 = Column(Float)
    PD_HLTH_10 = Column(Float)

__all__ = ['ChildAttendance', 'DailyAttendanceLog', 'AgencySites', 'AgencySiteRooms', 'CenterSupportReport', 'LessonPlansPreschool', 'LessonPlansIT', 'LessonPlansDetail', 'DRDPItems', 'DRDPRecord']
