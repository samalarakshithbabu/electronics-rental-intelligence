"""
Password Migration Script
Migrates plaintext passwords to bcrypt hashes
"""
from security.hashing import hash_password
from database.connection import db

# Get all users
users = db.execute('SELECT id, email, password_hash FROM users')
for user in users:
    old_hash = user['password_hash']
    # Check if already bcrypt (starts with $2)
    if not old_hash.startswith('$2'):
        new_hash = hash_password(old_hash)
        db.execute_update('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user['id']))
        print(f'Migrated user: {user["email"]}')
    else:
        print(f'User {user["email"]} already using bcrypt')

print('\nPassword migration complete!')