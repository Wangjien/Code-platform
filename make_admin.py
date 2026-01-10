import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Promote an existing user to admin')
    parser.add_argument('--email', type=str, help='User email')
    parser.add_argument('--username', type=str, help='Username')
    args = parser.parse_args()

    if not args.email and not args.username:
        print('Please provide --email or --username')
        return 2

    project_root = Path(__file__).resolve().parent
    backend_dir = project_root / 'backend'
    sys.path.insert(0, str(backend_dir))

    from app import app  # noqa: E402
    from models import db  # noqa: E402
    from models.user import User  # noqa: E402

    with app.app_context():
        if args.email:
            user = User.query.filter_by(email=args.email).first()
        else:
            user = User.query.filter_by(username=args.username).first()

        if not user:
            print('User not found')
            return 1

        user.role = 'admin'
        if hasattr(user, 'is_active'):
            user.is_active = True

        db.session.commit()
        print(f'OK: {user.username} ({user.email}) is now admin')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
