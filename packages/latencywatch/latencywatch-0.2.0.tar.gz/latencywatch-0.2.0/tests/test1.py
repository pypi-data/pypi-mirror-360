import time
from latency_watch import LatencyWatch


class DatabaseConnection:
    def connect(self):
        time.sleep(0.1)  # Simulate connection time
        
    def query(self, sql):
        time.sleep(0.05)  
        return "result"

class UserService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_user(self, user_id):
        self.db.connect()
        result = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return result

@LatencyWatch.watch
def main():
    service = UserService()
    user = service.get_user(123)
    print(f"Got user: {user}")

main()
print(LatencyWatch.get_last_report())