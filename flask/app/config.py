import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///monitor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '<@tid!*m29!w,vw#hwa&{-!vp_~@$3*?`[u/i=e=c7?6x&vknz{~(`[5*1j_o+1'
