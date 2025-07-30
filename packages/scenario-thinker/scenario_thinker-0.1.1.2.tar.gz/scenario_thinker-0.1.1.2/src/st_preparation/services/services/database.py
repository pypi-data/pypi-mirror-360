import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cur = self.conn.cursor()
        
        # self.cur.execute("CREATE TABLE IF NOT EXISTS bdd_moves(command, action, bdd_script)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS bdd_moves(command, action)")


    def insert_into_table(self, command, action):
        res = self.cur.execute("SELECT 1 FROM bdd_moves WHERE command = ?", (command,))
        if res.fetchone() is None:
            self.cur.execute("INSERT INTO bdd_moves VALUES (?, ?)", (command, action))
            self.save_database()
            return True

        return False

    def update_by_rowid(self, rowid, command, action):
        res = self.cur.execute("SELECT 1 FROM bdd_moves WHERE ROWID = ?;", (str(rowid),))
        if res.fetchone() is None:
            return False

        self.cur.execute("UPDATE bdd_moves SET command = ?, action = ? WHERE ROWID = ?;", (str(command), str(action), str(rowid)))

        self.save_database()
        return True

    def get_all_actions(self):
        res = self.cur.execute("SELECT command, action, ROWID FROM bdd_moves")
        return res.fetchall()

    def get_specific_action(self, command):
        res = self.cur.execute("SELECT command, action FROM bdd_moves WHERE command = ?;", (str(command),))
        return res.fetchone()

    def delete_by_rowid(self, rowid):
        res = self.cur.execute("SELECT 1 FROM bdd_moves WHERE ROWID = ?;", (str(rowid),))
        if res.fetchone() is None:
            return False

        res = self.cur.execute("DELETE FROM bdd_moves WHERE ROWID = ?;", (str(rowid),))
        self.save_database()

        return True

    def destroy_table(self):
        self.cur.execute("DROP TABLE bdd_moves")
        self.save_database()


    def save_database(self):
        self.conn.commit()

# conn = sqlite3.connect("database.db")
# database = Database()
# print(database.get_all_actions())
# database.destroy_table()

# database = Database()
# print(database.get_all_actions())

# # database.save_database()

# database.insert_into_table("command123", "action")
# print(database.get_all_actions())
# print(database.delete_by_rowid(6))
# print(database.get_all_actions())

# database.insert_into_table("command2", "action3", "bdd_script4")
# # # # conn.commit()
# # database.save_database()
# print(database.get_all_actions())
# database.get_specific_action("click on link with text 'Tell me more'")
# database.get_specific_action("Given visiting site localhost:3000/button_with_redirect")
# print(database.get_specific_action("assert there is "))
# print(database.get_specific_action("command"))
# print(Database().destroy_table())
# database = Database()
# # # database.destroy_table()
# # # database.save_database()

# database.insert_into_table("command", "action")
# # database.insert_into_table("command2", "action3", "bdd_script4")
# # # # # conn.commit()
# # # database.save_database()
# # print(database.get_all_actions())
# print(database.get_specific_action("command"))