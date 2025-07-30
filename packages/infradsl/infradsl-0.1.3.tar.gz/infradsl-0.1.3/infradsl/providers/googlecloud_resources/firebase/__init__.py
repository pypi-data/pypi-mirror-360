"""
Firebase Resources Package
"""

# Use the new modular implementations
from .firebase_auth_new import FirebaseAuth
from .firestore_new import Firestore
from .firebase_functions_new import FirebaseFunctions
from .firebase_hosting_new import FirebaseHosting
from .firebase_storage_new import FirebaseStorage

__all__ = [
    'FirebaseHosting',
    'FirebaseAuth',
    'Firestore',
    'FirebaseFunctions',
    'FirebaseStorage',
]
