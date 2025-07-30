import argparse
from models import User
from database import SessionLocal
import subprocess

def update_admin(email):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_admin = 1 # type:ignore
        db.commit()
        print("User promoted to admin.")
        db.close()
    else:
        print("User not found.")

def main():
    parser = argparse.ArgumentParser(description="Tools used for administrating the Nyxbox backend.")
    parser.add_argument("--promote", action="store_true", help="Promote a user to admin status")
    parser.add_argument("--remove", action="store_true", help="Remove database (DANGER!!)")
    parser.add_argument("email", nargs="?", help="User email address")
    args = parser.parse_args()
    if args.promote:
        if not args.email:
            print("Error: Email is required when using --promote")
            return
        update_admin(args.email)
    elif args.remove:
        # Add your remove database logic here
        result = subprocess.run("rm -rf database.db", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Command executed successfully")
        else:
            print(f"Command failed: {result.stderr}")
    else:
        parser.print_help()
