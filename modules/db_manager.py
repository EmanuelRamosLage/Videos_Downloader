import sqlite3 as sql
from pathlib import Path

class database:
    def __init__(self) -> None:
        pass

    def open_db(self) -> None:
        self.file = Path('./storage.db')
        self.connection = sql.connect(str(self.file))
        self.cursor = self.connection.cursor()

        self.cursor.execute('CREATE TABLE IF NOT EXISTS videos(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT NOT NULL UNIQUE, size INTEGER NOT NULL, video_id TEXT UNIQUE)')
        self.connection.commit()

    def read_db(self) -> list[tuple[int, str, str, int, str]]:
        '''Returns database entries in a list of tuple: (key, title, link, size)'''
        response = self.cursor.execute("SELECT * FROM videos ORDER BY size")
        
        return response.fetchall()

    def add_link(self, link: str, title: str = 'Nothing', size: int = 0, video_id: str | None = None) -> None:
        '''Add new link to the database, if it already existis update it.'''
        data = title, link, size, video_id
        try:
            self.cursor.execute("INSERT INTO videos(title, link, size, video_id) VALUES(?, ?, ?, ?)", data)
        except sql.IntegrityError:
            data = title, size, video_id, link
            self.cursor.execute("UPDATE videos SET title = ?, size = ?, video_id = ? WHERE link = ?", data)

    # def update(self, link: str, new_title: str = 'Nothing', new_size: int = 0, video_id: str = 'Nothing') -> None:
    #     data = new_title, new_size, video_id, link
    #     self.cursor.execute("UPDATE videos SET title = ?, size = ?, video_id = ? WHERE link = ?", data)

    def rm_link(self, link: str) -> None:
        self.cursor.execute("DELETE FROM videos WHERE link = ?", (link,))

    def save_db(self) -> None:
        self.connection.commit()

    def close_db(self) -> None:
        self.connection.commit()
        self.connection.close()

    def __len__(self) -> int:
        response = self.cursor.execute("SELECT id FROM videos")

        return len(response.fetchall())