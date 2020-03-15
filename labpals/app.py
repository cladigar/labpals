from labpals import app, db
from labpals.models import User, Post, Result, Group, Role, Permission


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Result': Result, 'Group': Group,
            'Role': Role, 'Permission': Permission}
