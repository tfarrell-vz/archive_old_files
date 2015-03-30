import hashlib
import os
import sys
import time
import win32file
import win32security

SAFE_MODE = True

def archive_it(archive_time_limit, target):
    if time.time() - os.path.getmtime(target) < archive_time_limit:
        return False
    else:
        return True

def days_to_seconds(days):
    return 24.0 * 60.0 * 60.0 * days

def clean_empty_dirs(archive_root):
    walk = os.walk(archive_root, topdown=False)
    for step in walk:
        dirpath, dirnames, filenames = step[0], step[1], step[2]
        if len(dirnames) == 0:
            os.rmdir(dirpath)

def gen_hash(src_path):
    _hash = hashlib.md5()
    with open(src_path, 'rb') as src_file:
        buf = src_file.read()
        _hash.update(buf)
    return _hash

def main():
    archive_time = days_to_seconds(float(sys.argv[3]))
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

        print(dirpath)
        # Make the directories seen in this level of the walk.
        for dir in dirnames:
            if dir == 'DfsrPrivate':
                del(dirnames[dirnames.index(dir)])
            else:
                os.mkdir(os.path.join(cur_arch_dir, dir))

        # Check for old files, and archive them if necessary.
        for _file in filenames:
            if _file == 'thumbs.db':
                pass
            else:
                src = os.path.join(dirpath, _file)
                if archive_it(archive_time, src):
                    dst = os.path.join(cur_arch_dir, _file)
                    acl = win32security.GetFileSecurity(src, win32security.DACL_SECURITY_INFORMATION)
                    win32file.CopyFile(src, dst, 0)
                    win32security.SetFileSecurity(dst, win32security.DACL_SECURITY_INFORMATION, acl)

                    src_hash = gen_hash(src)
                    dst_hash = gen_hash(dst)

                    if src_hash.hexdigest() == dst_hash.hexdigest() and not SAFE_MODE:
                        os.remove(src)

    # Clean up empty directories in the archive.
    clean_empty_dirs(archive_root)

if __name__ == '__main__':
    main()
