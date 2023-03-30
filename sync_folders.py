import os
import shutil
import time
import argparse
import hashlib

parser = argparse.ArgumentParser(prog='Sync folders',
                                 description='Synchronize two folders options',
                                 epilog='End Explination')
parser.add_argument("source", help="Source folder path")
parser.add_argument("replica", help="Replica folder path")
parser.add_argument("interval", type=int, help="Period when refreshed (s)")
parser.add_argument("log_file", help="Log file")
args = parser.parse_args()


def md5(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()

def sync_folders(source, replica, log_file_path):
    with open(log_file_path, "a") as log_file:
        log_file.write(f"Sync started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for root, dirs, files in os.walk(source):
            
            for file in files:
                source_file_path = os.path.join(root, file)
                replica_file_path = os.path.join(replica, os.path.relpath(source_file_path, source))
                source_file_md5 = md5(source_file_path)

                if os.path.exists(replica_file_path):
                    replica_file_md5 = md5(replica_file_path)
                else:
                    replica_file_md5 = None

                if source_file_md5 != replica_file_md5:
                    log_file.write(f"Copying {source_file_path} to {replica_file_path}\n")
                    shutil.copy2(source_file_path, replica_file_path)

            for dir in dirs:
                source_dir_path = os.path.join(root, dir)
                replica_dir_path = os.path.join(replica, os.path.relpath(source_dir_path, source))

                if not os.path.exists(replica_dir_path):
                    log_file.write(f"Creating folder {replica_dir_path}\n")
                    os.makedirs(replica_dir_path)

        for root, dirs, files in os.walk(replica, topdown=False):
            for file in files:
                replica_file_path = os.path.join(root, file)
                source_file_path = os.path.join(source, os.path.relpath(replica_file_path, replica))

                if not os.path.exists(source_file_path):
                    log_file.write(f"Removing {replica_file_path}\n")
                    os.remove(replica_file_path)

            for dir in dirs:
                replica_dir_path = os.path.join(root, dir)
                source_dir_path = os.path.join(source, os.path.relpath(replica_dir_path, replica))
                if not os.path.exists(source_dir_path):
                    log_file.write(f"Removing directory {replica_dir_path}\n")
                    os.rmdir(replica_dir_path)
        log_file.write(f"Sync completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")



while True:
    sync_folders(args.source, args.replica, args.log_file)
    time.sleep(args.interval)
