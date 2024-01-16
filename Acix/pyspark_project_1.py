import time
import pyspark

from pyspark.sql import SparkSession
import requests
from pyspark.sql import Row
from pyspark.sql.functions import col, to_timestamp,unix_timestamp
from pyspark.sql.functions import expr
from pyspark.sql.functions import regexp_replace
from pyspark.sql.functions import concat, col
from pyspark.sql import functions as F
import datetime
from pyspark.sql.types import TimestampType



def spark_session():
    spark = SparkSession.builder \
        .appName("update to psql") \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config("spark.jars", "/home/user_989/postgresql-42.2.27.jre7.jar") \
        .config("spark.sql.shuffle.partitions", 4) \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .master("local[*]") \
        .getOrCreate()
    return spark
        
def fetch_data(url, username, password):
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def psql_properties():
    postgres_url = "jdbc:postgresql://199.34.21.14:5532/Acix_Attendance_Module"
    postgres_properties = {
        "driver": "org.postgresql.Driver",
        "user": "postgres",
        "password": "An$LytiCs_ults",
    }
    
    
    return postgres_url, postgres_properties



    
def attendance_api_url():
    sparksession = spark_session()
    postgres_url, postgres_properties = psql_properties()
    
    table_name = "acix_phase2_attendancetable_test2"

    
    while True:
        df = sparksession.read.jdbc(url=postgres_url, table=table_name, properties=postgres_properties)

        latest_row = df.orderBy(col("ProcessDate").desc()).first()
        
        df = df.withColumn("Punch1Timestamp", unix_timestamp(col("Punch1"), "dd/MM/yyyy HH:mm:ss").cast(TimestampType()))

        max_punch1_timestamp = df.agg({"Punch1Timestamp": "max"}).collect()[0][0]

        print(f"Latest Punch1 datetime: {max_punch1_timestamp}")        

        if max_punch1_timestamp is not None:
            

            processdate = latest_row["ProcessDate"]
            process_date_digits = processdate.split('/')
            from_date = f"{process_date_digits[0]}{process_date_digits[1]}{process_date_digits[2]}"

            today = datetime.datetime.today()
            today = str(today).split(' ')[0].split('-')
            today_date = f"{today[2]}{today[1]}{today[0]}"

            url = f'https://adaxbs.matrixvyom.com/api.svc/v2/attendance-daily?action=get;date-range={from_date}-{today_date};field-name=processdate,FirsthalfStatus,SecondhalfStatus,LateIN_HHMM,EarlyOut_HHMM,EarlyIn_HHMM,Overtime_HHMM,workingshift,worktime,username,joindt,outpunch,punch1'
            username = 'api'
            password = 'Adax@2023'
            attendance_data = fetch_data(url, username, password)

            if attendance_data is not None:
                attendance_data.pop(-1) 
                
                attendance_rdd = sparksession.sparkContext.parallelize(attendance_data)
                header_attendance = attendance_rdd.first()
                attendance_rdd = attendance_rdd.filter(lambda line: line != header_attendance)
                attendance_rdd = attendance_rdd.map(lambda line: line.split("|"))
                
                attendance_rdd = attendance_rdd.map(lambda line: Row(*line))
                schema_attendance = header_attendance.split("|")
                df_attendance = sparksession.createDataFrame(attendance_rdd, schema=schema_attendance)

                df_attendance = df_attendance.withColumn("Punch1Timestamp", unix_timestamp(col("Punch1"), "dd/MM/yyyy HH:mm:ss").cast(TimestampType()))

                df_filtered_attendance = df_attendance.filter((col("Punch1").isNotNull()) & (col("Punch1Timestamp") > max_punch1_timestamp))
                
                df_filtered_attendance.show()
                
                if df_filtered_attendance.count() > 0:
                    mode = "append"
                    df_filtered_attendance.write.jdbc(url=postgres_url, table=table_name, mode=mode, properties=postgres_properties)
                    print(f"Data successfully stored in {table_name}")
                else:
                    print("No data found!")
            time.sleep(5)
    
def visitor_event_api_url():
    sparksession = spark_session()
    postgres_url, postgres_properties = psql_properties()
    
    table_name = "visitor_events"

    
    while True:
        df = sparksession.read.jdbc(url=postgres_url, table=table_name, properties=postgres_properties)

        latest_row = df.orderBy(col("eventdatetime").desc()).first()
        
        df = df.withColumn("eventdatetimeTimestamp", unix_timestamp(col("eventdatetime"), "dd/MM/yyyy HH:mm:ss").cast(TimestampType()))

        max_eventdatetime_timestamp = df.agg({"eventdatetimeTimestamp": "max"}).collect()[0][0]

        print(f"Latest eventdatetime: {max_eventdatetime_timestamp}")        

        if max_eventdatetime_timestamp is not None:
            max_eventdatetime_datetime_updated = datetime.datetime.strptime(str(max_eventdatetime_timestamp), '%Y-%m-%d %H:%M:%S')

            max_eventdatetime_datetime_updated += datetime.timedelta(seconds=1)
            print(max_eventdatetime_datetime_updated)
    
            event_datetime_digit = str(max_eventdatetime_datetime_updated).split(' ')
            event_date = event_datetime_digit[0].split('-')
            event_time = event_datetime_digit[1].split(':')
            from_date = f"{event_date[2]}{event_date[1]}{event_date[0]}{event_time[0]}{event_time[1]}{event_time[2]}"

            today = datetime.datetime.today()
            today = str(today).split(' ')[0].split('-')
            today_date = f"{today[2]}{today[1]}{today[0]}000000"
            
            print(from_date, today_date)


            url = f'https://adaxbs.matrixvyom.com/api.svc/v2/visitor-event?action=get;date-range={from_date}-{today_date};field-name=appointment-no,eventdatetime,entryexittype,access_allowed,mobile-no,visitor-name'
            username = 'api'
            password = 'Adax@2023'
            visitor_event_data = fetch_data(url, username, password)
            if 'success' in visitor_event_data and visitor_event_data['success'] == ' 1220100000':
                print("No data found!")
            else:
                print(visitor_event_data)
                visitor_event_data.pop(-1)
                visitor_event_rdd = sparksession.sparkContext.parallelize(visitor_event_data)
                header_visitor_event = visitor_event_rdd.first()
                visitor_event_rdd = visitor_event_rdd.filter(lambda line: line != header_visitor_event)
                visitor_event_rdd = visitor_event_rdd.map(lambda line: line.split("|"))
                visitor_event_rdd = visitor_event_rdd.map(lambda line: Row(*line))
                schema_visitor_event = header_visitor_event.split("|")
                df_visior_event = sparksession.createDataFrame(visitor_event_rdd, schema=schema_visitor_event)
                df_visior_event.show()
        

        # table_name = "your_table_name"
        # mode = "append"  
        # df_attendance.write.jdbc(url=postgres_url, table=table_name, mode=mode, properties=postgres_properties)
        # print("Data successfully stored in PostgreSQL.")
        time.sleep(5)
        
def visitor_preregistration_api_url():
    sparksession = spark_session()
    postgres_url, postgres_properties = psql_properties()
    
    table_name = "visitor_preregistration"

    
    while True:
        df = sparksession.read.jdbc(url=postgres_url, table=table_name, properties=postgres_properties)

        latest_row = df.orderBy(col("final-ric-verdict-date").desc()).first()
        print((latest_row['final-ric-verdict-date']))
        
        df = df.withColumn("final-ric-verdict-date-timestamp", unix_timestamp(col("final-ric-verdict-date"), "MM/dd/yyyy HH:mm").cast(TimestampType()))
    
        max_eventdatetime_timestamp = df.agg({"final-ric-verdict-date-timestamp": "max"}).collect()[0][0]

        print(f"Latest eventdatetime: {max_eventdatetime_timestamp}")        

        if max_eventdatetime_timestamp is not None:
            
            event_datetime_digit = str(max_eventdatetime_timestamp).split(' ')
            event_date = event_datetime_digit[0].split('-')
            event_time = event_datetime_digit[1].split(':')
            from_date = f"{event_date[2]}{event_date[1]}{event_date[0]}"

            today = datetime.datetime.today()
            today = str(today).split(' ')[0].split('-')
            today_date = f"{today[2]}{today[1]}{today[0]}"
            
            print(from_date, today_date)


            url = f'https://adaxbs.matrixvyom.com/api.svc/v2/visitor-pre-registration?action=get;date-range={from_date}-{today_date};user-filter=2'
            username = 'api'
            password = 'Adax@2023'
            visitor_pre_reg_data = fetch_data(url, username, password)
            
            visitor_pre_reg_data.pop(-1)
            visitor_pre_reg_rdd = sparksession.sparkContext.parallelize(visitor_pre_reg_data)
            header_visitor_pre_reg = visitor_pre_reg_rdd.first()
            visitor_pre_reg_rdd = visitor_pre_reg_rdd.filter(lambda line: line != header_visitor_pre_reg)
            visitor_pre_reg_rdd = visitor_pre_reg_rdd.map(lambda line: line.split("|"))
            visitor_pre_reg_rdd = visitor_pre_reg_rdd.map(lambda line: Row(*line))
            schema_visitor_pre_reg = header_visitor_pre_reg.split("|")
            df_visitor_pre_reg = sparksession.createDataFrame(visitor_pre_reg_rdd, schema=schema_visitor_pre_reg)
            df_visitor_pre_reg = df_visitor_pre_reg.withColumn("final-ric-verdict-date_timestamp", unix_timestamp(col("final-ric-verdict-date"), "dd/MM/yyyy HH:mm:ss").cast(TimestampType()))
            df_filtered_visitor_pre_reg = df_visitor_pre_reg.filter((col("final-ric-verdict-date").isNotNull()) & (col("final-ric-verdict-date_timestamp") > max_eventdatetime_timestamp))
            df_filtered_visitor_pre_reg.show()

        # table_name = "your_table_name"
        # mode = "append"  
        # df_attendance.write.jdbc(url=postgres_url, table=table_name, mode=mode, properties=postgres_properties)
        # print("Data successfully stored in PostgreSQL.")
        time.sleep(5)
        
def timesheet_api_url():
    sparksession = spark_session()
    postgres_url, postgres_properties = psql_properties()
    
    table_name_user = "acix_phase2_usertable"
    
    table_name_timesheet = "timesheet_details"

    df_user = sparksession.read.jdbc(url=postgres_url, table=table_name_user, properties=postgres_properties)
    
    unique_userids = df_user.select("id").collect()
    userids_list = [row["id"] for row in unique_userids]

    print(userids_list)

    
    while True:
        for user_id in userids_list:
            df = sparksession.read.jdbc(url=postgres_url, table=table_name_timesheet, properties=postgres_properties)

            user_df = df.filter(col("userid") == user_id)

            user_df = user_df.withColumn("start-date-time-timestamp", unix_timestamp(col("start-date-time"), "MM/dd/yyyy HH:mm:ss").cast(TimestampType()))

            max_eventdatetime_timestamp = user_df.agg({"start-date-time-timestamp": "max"}).collect()[0][0]

            print(f"Latest eventdatetime for User ID {user_id}: {max_eventdatetime_timestamp}")
            if max_eventdatetime_timestamp is not None:
            
                event_datetime_digit = str(max_eventdatetime_timestamp).split(' ')
                event_date = event_datetime_digit[0].split('-')
                event_time = event_datetime_digit[1].split(':')
                from_date = f"{event_date[2]}{event_date[1]}{event_date[0]}"

                today = datetime.datetime.today()
                today = str(today).split(' ')[0].split('-')
                today_date = f"{today[2]}{today[1]}{today[0]}"
                
                print(from_date, today_date)


                url = f'https://adaxbs.matrixvyom.com/api.svc/v2/timesheet?action=get;%20;userid={user_id};date-range={from_date}-{today_date}'
                username = 'api'
                password = 'Adax@2023'
                timesheet_data = fetch_data(url, username, password)
                timesheet_data.pop(-1)
                timesheet_rdd = sparksession.sparkContext.parallelize(timesheet_data)
                header_timesheet = timesheet_rdd.first()
                timesheet_rdd = timesheet_rdd.filter(lambda line: line != header_timesheet)
                timesheet_rdd = timesheet_rdd.map(lambda line: line.split("|"))
                timesheet_rdd = timesheet_rdd.map(lambda line: Row(*line))
                schema_timesheet = header_timesheet.split("|")
                df_timesheet = sparksession.createDataFrame(timesheet_rdd, schema=schema_timesheet)
                df_visitor_pre_reg = df_visitor_pre_reg.withColumn("final-ric-verdict-date_timestamp", unix_timestamp(col("final-ric-verdict-date"), "dd/MM/yyyy HH:mm:ss").cast(TimestampType()))
                df_filtered_visitor_pre_reg = df_visitor_pre_reg.filter((col("final-ric-verdict-date").isNotNull()) & (col("final-ric-verdict-date_timestamp") > max_eventdatetime_timestamp))
                df_filtered_visitor_pre_reg.show()

            # table_name = "your_table_name"
            # mode = "append"  
            # df_attendance.write.jdbc(url=postgres_url, table=table_name, mode=mode, properties=postgres_properties)
            # print("Data successfully stored in PostgreSQL.")
        time.sleep(5)


if __name__ == "__main__":


    timesheet_api_url()

