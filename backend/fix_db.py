from database import engine
from sqlmodel import SQLModel
from models import User, Task
print('Dropping old tables in Neon...')
SQLModel.metadata.drop_all(engine)
print('Creating fresh tables with new columns...')
SQLModel.metadata.create_all(engine)
print('Database Synced Successfully!')