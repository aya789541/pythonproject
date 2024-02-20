import secrets
import hashlib
import hmac

symmetric_key = secrets.token_hex(32)


def generate_node_key(node_id):
    if node_id % 20 == 0:
        return bytes.fromhex('3a5b6c7d8e9fa0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7b8c9d0a1b2c3d4e5')
    else:
        key = secrets.token_bytes(32)  # Génère une clé de 256 bits (32 octets)
        key =  hashlib.sha256(key).digest()  # Renvoie la clé hashée (32 octets)
        node_key = key.hex()
        return node_key


rA = secrets.token_bytes(16) # générer un nombre pseudo-aléatoire de 16 octets
print(rA)
bytes_symmetric_key = bytes.fromhex(symmetric_key)
mac1 = hmac.new(bytes_symmetric_key, rA, hashlib.sha256).digest() # calculer le HMAC du message avec la clé secrète
print("mac1", mac1)
mac2 = hmac.new(bytes_symmetric_key, rA, hashlib.sha256).digest() # calculer le HMAC du message avec la clé secrète
print("mac2", mac2)









