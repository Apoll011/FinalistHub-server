from database import engine, SessionLocal, Base
from models import UserModel
from routers.auth import hash_password
import os

def init_db():
    Base.metadata.create_all(bind=engine)

    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"

    db = SessionLocal()
    try:
        if test_mode:
            # Check if admin user exists
            admin = db.query(UserModel).filter(UserModel.username == "admin").first()
            if not admin:
                # Create default admin user only in test mode
                hashed_password = hash_password("admin")
                admin_user = UserModel(username="admin", hashed_password=hashed_password, role="admin")
                db.add(admin_user)
                db.commit()
                print("Test mode: Admin user created (username=admin, password=admin)")
            else:
                print("Test mode: Admin user already exists")
        else:
            print("Production mode: Skipping admin user creation")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

