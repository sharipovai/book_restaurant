import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS requests (user_id int primary_key,  user_name varchar(50), book_hall varchar(50),"
            "book_date varchar(50), book_time varchar(50), book_table varchar(50), book_people_cnt varchar(50), "
            "chat_id int, first_name varchar(50), registration_date varchar(50), phone_number varchar(50))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS statistics (number int primary_key, date varchar(20), user_id varchar(5000), "
            "new_user int, unique_users int)")
        conn.commit()
        cur.close()
        conn.close()

    def write_statistics(self, parameter_name, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        today_date = (datetime.now()).strftime("%d.%m.%y")
        count = cur.execute(f"SELECT {parameter_name} FROM statistics WHERE date = '%s'"
                                         % today_date).fetchall()[0][0]
        count += 1
        cur.execute(f"UPDATE statistics SET {parameter_name}  = %d WHERE date = '%s'" % (count, today_date))
        conn.commit()
        user_id_str = str(cur.execute("SELECT user_id FROM statistics WHERE date = '%s'"
                                         % today_date).fetchall()[0][0])
        if str(user_id) not in user_id_str:
            user_id_str = str(user_id_str + "n" + str(user_id))
            cur.execute("UPDATE statistics SET user_id = ? WHERE date = ?", (user_id_str, today_date))
            conn.commit()
            unique_users = int(cur.execute("SELECT unique_users FROM statistics WHERE date = '%s'"
                                    % today_date).fetchall()[0][0])
            unique_users += 1
            cur.execute("UPDATE statistics SET unique_users = '%d' WHERE date = '%s'" % (unique_users, today_date))
            conn.commit()
        cur.close()
        conn.close()

    def get_date_str_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        result = cur.execute("SELECT date FROM statistics").fetchall()
        if len(result) > 0:
            result_list = [i[0] for i in result]
        else:
            result_list = []
        cur.close()
        conn.close()
        return result_list

    def write_new_date_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        today_date = (datetime.now()).strftime("%d.%m.%y")
        cur.execute("INSERT INTO statistics (date, user_id, new_user, unique_users) VALUES "
                    "('%s', '%s', '%d', '%d')" % (today_date, "", 0, 0))
        conn.commit()
        cur.close()
        conn.close()

    def check_new_user(self, user_id):
        # for new user return 1
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        result = cur.execute("SELECT * FROM requests WHERE user_id = '%d'" % user_id).fetchall()
        cur.close()
        conn.close()
        return not bool(len(result))

    def write_new_user(self, message, phone_number):
        if not self.check_new_user(message.from_user.id):
            return
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        reg_date = (datetime.now()).strftime("%d.%m.%y")
        cur.execute("INSERT INTO requests (user_id, user_name, book_hall, book_date, book_time, book_table, book_people_cnt, chat_id, first_name, "
                    "registration_date, phone_number) VALUES ('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s')" %
                    (message.from_user.id, message.from_user.username, "", "", "", "", "", message.chat.id,
                     message.from_user.first_name, reg_date, phone_number))
        conn.commit()
        cur.close()
        conn.close()

    def get_user_parameter(self, user_id, parameter_name):
        # return parameter value
        parameters = ["user_name", "chat_id", "first_name", "registration_date", "book_hall", "book_date", "book_time",
                      "book_table", "book_people_cnt", "phone_number"]
        parameter_value = 0
        if parameter_name in parameters:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            parameter_value = cur.execute(f"SELECT {parameter_name} FROM requests WHERE user_id = '%d'"
                                          % user_id).fetchall()[0][0]
            cur.close()
            conn.close()
        return parameter_value

    def write_user_parameter(self, user_id, parameter_name, new_value):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(f"UPDATE requests SET {parameter_name}  = '%s' WHERE user_id = '%d'" % (new_value, user_id))
        conn.commit()
        cur.close()
        conn.close()

    def get_chat_id_list(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        chat_id_tuple = cur.execute(f"SELECT chat_id FROM requests").fetchall()
        chat_id_list = [i1[0] for i1 in chat_id_tuple if i1[0] != 0]
        cur.close()
        conn.close()
        return chat_id_list

