import hashlib
import zlib

class GitSimulator:
    def __init__(self):
        self.objects = {}
        self.refs = {}

    def hash_object(self, data):
        sha1 = hashlib.sha1(data.encode()).hexdigest()
        self.objects[sha1] = data
        return sha1

    def commit(self, changes):
        # Basic commit functionality
        commit_hash = self.hash_object(str(changes))
        self.refs['HEAD'] = commit_hash
        return commit_hash

    def get_object(self, obj_hash):
        return self.objects.get(obj_hash)

class OptimizedGitSimulator(GitSimulator):
    def __init__(self):
        super().__init__()
        self.chunk_size = 1024 * 1024  # 1MB chunks

    def commit(self, changes):
        # Improved commit process with chunked delta compression
        previous_commit = self.refs.get('HEAD')
        if previous_commit:
            previous_data = self.get_object(previous_commit)
            delta = self.create_delta(previous_data, changes)
            commit_hash = self.hash_object(delta)
        else:
            commit_hash = self.hash_object(changes)

        self.refs['HEAD'] = commit_hash
        return commit_hash

    def create_delta(self, old_data, new_data):
        delta = []
        for i in range(0, len(new_data), self.chunk_size):
            chunk = new_data[i:i+self.chunk_size]
            if chunk in old_data:
                # Store reference to existing chunk
                delta.append(f"REF:{old_data.index(chunk)}:{len(chunk)}")
            else:
                # Compress and store new chunk
                compressed = zlib.compress(chunk.encode())
                delta.append(f"NEW:{len(compressed)}:{compressed.decode('latin1')}")
        return "|".join(delta)

    def get_object(self, obj_hash):
        data = super().get_object(obj_hash)
        if data.startswith("REF:") or data.startswith("NEW:"):
            # This is a delta, need to reconstruct
            return self.reconstruct_delta(data)
        return data

    def reconstruct_delta(self, delta):
        chunks = delta.split("|")
        reconstructed = ""
        for chunk in chunks:
            if chunk.startswith("REF:"):
                _, start, length = chunk.split(":")
                start, length = int(start), int(length)
                previous_commit = self.get_object(self.refs['HEAD'])
                reconstructed += previous_commit[start:start+length]
            elif chunk.startswith("NEW:"):
                _, length, data = chunk.split(":", 2)
                decompressed = zlib.decompress(data.encode('latin1'))
                reconstructed += decompressed.decode()
        return reconstructed

# Example usage
git = OptimizedGitSimulator()

# First commit
first_commit = git.commit("Initial content of a large file.")
print(f"First commit: {first_commit}")

# Second commit with changes
second_commit = git.commit("Initial content of a large file. Some changes here.")
print(f"Second commit: {second_commit}")

# Retrieve the content of the second commit
content = git.get_object(second_commit)
print(f"Content of the second commit: {content}")