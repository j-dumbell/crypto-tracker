from app.models import User


def gen_token(user_id):
    user = User.query.get(user_id)
    return user.encode_auth_token()
