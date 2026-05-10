from sqlmodel import Session, SQLModel, create_engine, select, delete
from system.globals import APPS_FOLDER, WORKSPACE


#sqlite:///:memory: (or, sqlite://)
#sqlite:///relative/path/to/file.db
#sqlite:////absolute/path/to/file.db
#json_deserializer: Callable[..., Any] = ...,
#json_serializer: Callable[..., Any] = ...,     

#db = SQLAlchemy(session_options={"autoflush": False})


class engine_db:
    def __init__(self, db_addr, model, name="database"): 
        self.db_addr   = db_addr
        self.engine    = None
        self.name      = name
        self.model     = model


    def initialize(self):
        self.engine = create_engine   (self.db_addr)#,echo=True)
        self.model.metadata.create_all(self.engine)

        if __debug__:
            print(f"{self.db_addr} Data Base Initilized")  


    async def add_record(self, record):
        with Session(self.engine) as session:
            session.add(record)
            session.commit()


    async def add_records(self, records):
        if len(records) == 0: return 

        with Session(self.engine) as session:
            [session.add(rec) for rec in records]                
            session.commit()


    async def get_record(self, model, key, value, to_json = False):
        with Session(self.engine) as session:
            record = session.exec(
                select(model).where(key == value)
            ).first() 
        
            if (to_json): return record.to_json() 
            return record
    

    async def get_records(self, model, key, value, to_json = False, order_by=None):
        with Session(self.engine) as session:
            if order_by:
                records = session.exec(
                    select(model).where(key == value).order_by(order_by)
                ).all()
            else:
                records = session.exec(
                    select(model).where(key == value)
                ).all()
        
            if (to_json): return [rec.to_json() for rec in records]
            return records
           

    async def get_all_records(self, model, to_json = False, order_by=None):
        with Session(self.engine) as session:
            if order_by:
                records  = session.exec( select(model) ).all().order_by(order_by)
            else:
                records  = session.exec( select(model) ).all() 

        if (to_json): return [rec.to_json() for rec in records]        
        return records
    

    async def update_record(self, updated_record, key, value, to_json = False):
        with Session(self.engine) as session:           
            record = session.exec(
                select(type(updated_record)).where(key == value)
            ).first()

            for dict in record.__dict__:
                if dict == "_sa_instance_state": continue
                record.__setattr__(dict, updated_record.__getattribute__(dict))

            session.commit()
            session.refresh(record)

            if to_json == True: return record.to_json()            
            return record
        

    async def update_records(self, updated_records, key):
        with Session(self.engine) as session:
            for updated_record in updated_records:                
                record = session.exec(
                    select(type(updated_record)).where(key == updated_record.id)
                ).first()

                for dict in record.__dict__:
                    if dict == "_sa_instance_state": continue
                    record.__setattr__(dict, updated_record.__getattribute__(dict)) 

            session.commit()     


    async def update_fields(self, model, key, value, fields, to_json = False): #files = {"fieldname": "123"}, etc
        with Session(self.engine) as session:           
            record = session.exec(
                select(model).where(key == value)
            ).first()

            for fld in fields.keys():
                record.__setattr__(fld, fields[fld])

            session.commit()
            session.refresh(record)

            if to_json == True: return record.to_json()            
            return record
        

    async def update_multi_fields(self, model, key, field_key, fields): #files = [{key: val, "fieldname": "123"},] etc
        with Session(self.engine) as session:
            for item in fields:
                record = session.exec(
                    select(model).where(key == item[field_key])
                ).first()

                for fld in item.keys():
                    if dict == key: continue
                    record.__setattr__(fld, item[fld])

            session.commit()


    async def delete_record(self, model, key, value):
        with Session(self.engine) as session:           
            record = session.exec(
                select(model).where(key == value)
            ).first()

            session.delete(record)
            session.commit()


    async def delete_records(self, model, key, values):
        with Session(self.engine) as session:
            for value in values:          
                record = session.exec(
                    select(model).where(key == value)
                ).first()
                session.delete(record)
                
            session.commit()            


    async def delete_all_records(self, model):
        with Session(self.engine) as session:
            session.exec(delete(model))
            session.commit() 


    async def delete_records_recursively(self, model, key, value):
        with Session(self.engine) as session:        
            records = session.exec(
                select(model).where(key == value)
            ).all()
            
            for record in records:
                session.delete(record)
                
            session.commit()             


    def terminate(self):
        self.engine.dispose()
