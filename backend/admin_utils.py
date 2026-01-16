"""
Utility script to manage admin users
"""
from sqlmodel import Session, select
from models import User
from database import engine
import argparse
import sys


def promote_user_to_admin(email_or_username: str):
    """
    Promote a user to admin by email or username
    """
    with Session(engine) as session:
        # Find user by email or username
        user = session.exec(select(User).where(
            (User.email == email_or_username) | (User.username == email_or_username)
        )).first()

        if not user:
            print(f"User with email/username '{email_or_username}' not found.")
            return False

        # Update user to admin
        user.is_admin = True
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"User '{user.username}' ({user.email}) has been promoted to admin.")
        return True


def demote_admin_to_user(email_or_username: str):
    """
    Demote an admin user to regular user by email or username
    """
    with Session(engine) as session:
        # Find user by email or username
        user = session.exec(select(User).where(
            (User.email == email_or_username) | (User.username == email_or_username)
        )).first()

        if not user:
            print(f"User with email/username '{email_or_username}' not found.")
            return False

        # Update user to non-admin
        user.is_admin = False
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"User '{user.username}' ({user.email}) has been demoted from admin.")
        return True


def list_admin_users():
    """
    List all admin users
    """
    with Session(engine) as session:
        admin_users = session.exec(select(User).where(User.is_admin == True)).all()

        if not admin_users:
            print("No admin users found.")
        else:
            print(f"Found {len(admin_users)} admin user(s):")
            for user in admin_users:
                print(f"- {user.username} ({user.email})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Admin user management utility")
    parser.add_argument("action", choices=["promote", "demote", "list"],
                       help="Action to perform: promote, demote, or list admin users")
    parser.add_argument("--identifier", help="Email or username of the user (required for promote/demote)")

    args = parser.parse_args()

    if args.action == "promote":
        if not args.identifier:
            print("Error: --identifier is required for promote action")
            sys.exit(1)
        promote_user_to_admin(args.identifier)
    elif args.action == "demote":
        if not args.identifier:
            print("Error: --identifier is required for demote action")
            sys.exit(1)
        demote_admin_to_user(args.identifier)
    elif args.action == "list":
        list_admin_users()