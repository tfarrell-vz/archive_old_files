import hashlib
import os
import shutil
import sys
import time

SAFE_MODE = True

def archive_it(archive_time_limit, target):
    if time.time() - os.path.getmtime(target) < archive_time_limit:
        return False
    else:
        return True

def gen_hash(src_path):
    _hash = hashlib.md5()
    with open(src_path, 'rb') as src_file:
        buf = src_file.read()
        _hash.update(buf)
    return _hash

def main():
    ARCHIVE_TIME = 0.0 # 31556952 # seconds = 365.2425 days

    archive_store = sys.argv[2]
    cur_dir = sys.argv[1]
    old_path, root = os.path.split(cur_dir)
    archive_root = os.path.join(archive_store, root)
    os.mkdir(archive_root)

    print("The (old) path prior to the directory to be archived %s" % old_path)
    print("Current directory: %s" % cur_dir)
    print("Archives are stored in: %s" % archive_store)
    print("Archive root for the present archival process: %s" % archive_root)

    walk = os.walk(cur_dir)

    for step in walk:
        dirpath, dirnames, filenames = step[0], step[1], step[2]
        cur_arch_dir = archive_store + dirpath[len(old_path):]

        # Make the directories seen in this level of the walk.
        for dir in dirnames:
            os.mkdir(os.path.join(cur_arch_dir, dir))

        # Check for old files, and archive them if necessary.
        for _file in filenames:
            src = os.path.join(dirpath, _file)
            if archive_it(ARCHIVE_TIME, src):
                dst = os.path.join(cur_arch_dir, _file)
                shutil.copy(src, dst)

                src_hash = gen_hash(src)
                dst_hash = gen_hash(dst)

                if src_hash.hexdigest() == dst_hash.hexdigest() and not SAFE_MODE:
                    os.remove(src)

if __name__ == '__main__':
    main()
