import cx_Oracle

# Set the connection details
#username = 'your_username'
#password = 'your_password'
#dsn = 'your_dsn'  # e.g., host:port/service_name
class Labelinfo:
    def __init__(self):
        self.dsn_tns = cx_Oracle.makedsn('192.168.1.99', '1521', service_name='tpx')
        self.connection = cx_Oracle.connect(user=r'BI', password='Prd5632Bi2018B', dsn=self.dsn_tns)
        
        # Establish a connection
        #connection = cx_Oracle.connect(username, password, dsn)
        
        # Create a cursor
        self.cursor = self.connection.cursor()
        
        # Execute the query

    def get_info(self, article):
        self.query = f"""
        select aconlign,
               acocomm
        from GCPRODOWN.ARTCOMM,
             GCPRODOWN.ARTRAC
        where artcinr = acocinr
          and langue = 'RU'
          and artcexr = '{article}'
          union all 
        select 99,
               arccode
        from GCPRODOWN.ARTCOCA,
             GCPRODOWN.ARTRAC
        where arccinr = artcinr
          and arcddeb <= trunc(sysdate)
          and arcdfin >= trunc(sysdate)
          and artcexr = '{article}'
        """
        self.cursor.execute(self.query)
        
        # Fetch all rows
        rows = self.cursor.fetchall()
        d = {"name": rows[0][1],
             "weight": rows[1][1],
             "delta": rows[2][1],
             "ttu": rows[3][1],
             "ingredients": rows[4][1],
             "manufacturer": rows[5][1],
             "nutrition": rows[6][1],
             "storage": rows[7][1],
             "barcode": rows[8][1]
            }
        
        # Close the cursor and connection
        self.cursor.close()
        self.connection.close()
        return d
