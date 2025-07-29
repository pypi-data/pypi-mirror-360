import hashlib


def get_file_hash(file_path, algorithm="sha256", chunk_size=8192, length=None):
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    if length:
        return hash_obj.hexdigest()[:length]
    return hash_obj.hexdigest()
