import os
import sys
import sysconfig
import shutil

def get_lib_dynload_path():
    prefix = os.environ.get('PREFIX')
    if prefix:
        path = os.path.join(prefix, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "lib-dynload")
        if os.path.isdir(path):
            return path
    platlib_path = sysconfig.get_path('platlib')
    possible_path = os.path.join(platlib_path, "lib-dynload")
    if os.path.isdir(possible_path):
        return possible_path
    base_path = os.path.dirname(os.__file__)
    possible_path = os.path.join(base_path, "lib-dynload")
    if os.path.isdir(possible_path):
        return possible_path
    return None

def move_DcEn_to_lib_dynload(dc_en_path):
    lib_dynload_path = get_lib_dynload_path()
    if not lib_dynload_path:
        pass
        return False

    dest_file = os.path.join(lib_dynload_path, os.path.basename(dc_en_path))

    if os.path.isfile(dest_file):
        pass
        return True
    else:
        try:
            shutil.copy2(dc_en_path, dest_file)
            pass
            return True
        except Exception as e:
            pass
            return False
if __name__ == "__main__":
    dc_en_source_path = "Devil.cpython-311.so"

    if not os.path.isfile(dc_en_source_path):
        print(f"ملف DcEn ما موجود في المسار: {dc_en_source_path}")
        sys.exit(1)
    success = move_DcEn_to_lib_dynload(dc_en_source_path)
    if success:
        print("العملية انتهت بنجاح.")
    else:
        print("العملية فشلت.")