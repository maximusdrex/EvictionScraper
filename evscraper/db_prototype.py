import psycopg

class EvictDBManager:
    def __init__(self):
        try:
            connection = psycopg.connect("dbname=EvictionDB user=postgres password=test123")
            self.conn = connection
        except:
            print("error, connection could not be established")

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()


    def create_tables(self):
        if self.conn==None:
            return None
        conn = self.conn
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS searches (
                        case_id int PRIMARY KEY,
                        case_num CHAR(15),
                        file_date date,
                        status CHAR(5)
                        );
                    """)
            except psycopg.errors.DuplicateTable as E:
                print("Table 'search' already exists")
                conn.rollback()

            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS cases (
                        case_id int REFERENCES searches (case_id) PRIMARY KEY,
                        case_num CHAR(15),
                        case_name VARCHAR(80),
                        file_date date,
                        case_status VARCHAR(80),
                        status_date date,
                        type VARCHAR(80),
                        disp VARCHAR(120),
                        disp_date date
                        );
                    """)
            except psycopg.errors.DuplicateTable as E:
                print("Table already exists")
                conn.rollback()
            
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        case_id int REFERENCES searches (case_id),
                        description VARCHAR(128),
                        time timestamp,
                        UNIQUE (case_id, time, description)
                        );
                    """)
            except psycopg.errors.DuplicateTable as E:
                print("Table already exists")
                conn.rollback()

            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hearings (
                        id SERIAL PRIMARY KEY,
                        case_id int REFERENCES searches (case_id),
                        description VARCHAR(80),
                        jud_mag VARCHAR(80),
                        result VARCHAR(80),
                        time timestamp,
                        UNIQUE (case_id, time)
                        );
                    """)
            except psycopg.errors.DuplicateTable as E:
                print("Table already exists")
                conn.rollback()

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS parties (
                        party_id SERIAL PRIMARY KEY,
                        case_id int REFERENCES searches (case_id),
                        Name VARCHAR(80),
                        party VARCHAR(80),
                        is_attorney boolean,
                        UNIQUE (case_id, Name)
                        );
                    """)

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS addresses (
                        id SERIAL PRIMARY KEY,
                        party_id int REFERENCES parties (party_id),
                        case_id int REFERENCES searches (case_id),
                        address VARCHAR(80),
                        city VARCHAR(80),
                        state VARCHAR(80),
                        zip CHAR(5),
                        type VARCHAR(80),
                        UNIQUE (case_id, party_id)
                        );
                    """)

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS finance (
                        id SERIAL PRIMARY KEY,
                        party_id int REFERENCES parties (party_id),
                        case_id int REFERENCES searches (case_id),
                        connection VARCHAR(80),
                        balance DEC (10,2),
                        last_viewed timestamp,
                        assesed DEC (10,2),
                        payments DEC (10,2),
                        description  VARCHAR(80),
                        UNIQUE (case_id, party_id, description)
                        );
                    """)

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id int PRIMARY KEY,
                        section_id int REFERENCES finance (id),
                        tdate date,
                        chg DEC (10,2),
                        receipt int,
                        type VARCHAR(80)
                        );
                    """)
            self.create_views()
            conn.commit()

    def create_views(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE VIEW properties AS SELECT DISTINCT addresses.case_id,
                    addresses.address,
                    addresses.city,
                    addresses.zip
                FROM addresses
                WHERE addresses.type::text = 'Property Address'::text;

                CREATE OR REPLACE VIEW case_properties AS SELECT cases.case_id,
                    cases.case_num,
                    cases.file_date,
                    cases.case_status,
                    cases.type,
                    cases.status_date,
                    properties.address,
                    properties.city,
                    properties.zip,
                    cases.case_name
                FROM cases
                    LEFT JOIN properties ON cases.case_id = properties.case_id;

                CREATE OR REPLACE VIEW move_outs AS  SELECT DISTINCT events.case_id,
                    events.description
                FROM events
                WHERE events.description::text ~~ '%Move Out Scheduled%'::text;

                CREATE OR REPLACE VIEW output_data AS SELECT 
                    case_properties.case_id,
                    case_properties.case_num,
                    case_properties.file_date,
                    case_properties.case_status,
                    case_properties.type,
                    case_properties.status_date,
                    case_properties.address,
                    case_properties.city,
                    case_properties.zip,
                    move_outs.description,
                    case_properties.case_name
                FROM case_properties
                    LEFT JOIN move_outs ON case_properties.case_id = move_outs.case_id;""")
                    

    def add_search(self, case):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO searches (case_id, case_num, file_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
            """, (case["ID"], case["Name"], case["Date"]))
            return True


    def add_party(self, party, case_id, attorney):
        if(self.conn == None):
            try:
                connection = psycopg.connect("dbname=EvictionDB user=postgres password=test123")
                self.conn = connection
            except:
                print("error, connection could not be re-established")
                return None
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO parties (case_id, name, party, is_attorney) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING returning party_id;
            """, (case_id, party["Name"], party["P/D"], attorney))
            return cur.fetchone()

    def add_address(self, case_id, party_id, party):
        if(self.conn == None):
            try:
                connection = psycopg.connect("dbname=EvictionDB user=postgres password=test123")
                self.conn = connection
            except:
                print("error, connection could not be re-established")
                return None
        with self.conn.cursor() as cur:
            if(len(party["Address"])>80):
                party["Address"] = party["Address"][0:79]
            cur.execute("""
                INSERT INTO addresses (case_id, party_id, address, city, state, zip, type) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
            """, (case_id, party_id, party["Address"], party["City"], party["State"], party["Zip"], party["P/D"]))
            return True
    
    def add_case(self, case_id, case_obj):
        with self.conn.cursor() as cur:
            if(len(case_obj["Name"]) > 79):
                case_obj["Name"] = case_obj["Name"][0:79]
            cur.execute("""
                INSERT INTO cases (case_id, case_num, case_name, file_date, case_status, status_date, type, disp, disp_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (case_id) DO UPDATE SET (type, status_date, case_status) = (excluded.type, excluded.status_date, excluded.status_date);
            """, (case_id, case_obj["Number"], case_obj["Name"], case_obj["FileDate"], case_obj["Status"], case_obj["StatusDate"], case_obj["Type"], case_obj["Disposition"], case_obj["DispositionDate"]))
            return True
    
    def add_event(self, case_id, event):
        with self.conn.cursor() as cur:
            #print(event["EventType"])
            cur.execute("""
                INSERT INTO events (case_id, description, time) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
            """, (case_id, event["EventType"], event["Datetime"]))
            return True

    def add_hearing(self, case_id, hearing):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO hearings (case_id, description, time, jud_mag, result) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
            """, (case_id, hearing["EventType"], hearing["Datetime"], hearing["JudgeOrMagistrateDesc"], hearing["Result"]))
            return True

    def add_fin(self, case_id, fin):
        with self.conn.cursor() as cur:
            cur.execute(""" SELECT party_id FROM parties WHERE case_id=%s AND Name=%s""", (case_id, fin["Party_Name"]))
            pid = cur.fetchone()
            if(pid):
                pid = int(pid[0])
            cur.execute("""
                INSERT INTO finance (party_id, case_id, connection, balance, last_viewed, assesed, payments, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING returning id;
                """, (pid, case_id, fin["Connection"], fin["Balance"], fin["Last_Viewed"], fin["Assesed"], fin["Payments"], fin["Description"]))
            id = cur.fetchone()
            if id:
                return id
            else:
                #TODO: finish the case where the finance was already added
                #cur.execute(""" SELECT id FROM finance WHERE 
                return None

    def add_transaction(self, fin_id, transaction):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transactions (section_id, id, tdate, chg, type)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
            """, (fin_id, transaction["ID"], transaction["Date"], transaction["Chg"], transaction["Type"]))
            return True

    def get_searches(self):
        with self.conn.cursor() as cur:
            cur.execute(""" SELECT case_id FROM searches """)
            return [x[0] for x in cur.fetchall()]
    
    def get_new_cases(self):
        with self.conn.cursor() as cur:
            cur.execute(""" SELECT searches.case_id FROM searches LEFT JOIN cases ON cases.case_id=searches.case_id WHERE cases.case_id IS NULL """)
            return [x[0] for x in cur.fetchall()]

    def get_cases(self):
        with self.conn.cursor() as cur:
            cur.execute(""" SELECT searches.case_id FROM searches""")
            return [x[0] for x in cur.fetchall()]


    def drop_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                DROP Table transactions CASCADE;
                drop table hearings CASCADE;
                drop table finance CASCADE;
                drop table events CASCADE;
                drop table addresses CASCADE;
                drop table parties CASCADE;
                drop table cases CASCADE;
                DROP TABLE searches CASCADE;
            """)
        self.conn.commit()

    def get_output(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM output_data;
            """)
            self.conn.commit()
            return cur.fetchall()

    def get_table_cols(self, table):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns WHERE table_name=%s;
            """, (table,))
            self.conn.commit()
            return cur.fetchall()
    
    def get_table(self, table):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM {};".format(table))
            self.conn.commit()
            return cur.fetchall()

db = EvictDBManager()
db.create_tables()
db.close()