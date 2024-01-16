# 목적 : 파일의 날짜를 판단해서 업데이트 하는 로직을 피하기 위해서 제작한 스크립트
# 용량 및 crc가 다른 파일 복사/삭제하는 동기화 스크립트

import sys
import os
import shutil
import zlib
import copy

def crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def get_file_list(path):
    print("get file list - 다음 디렉토리에서 하위 포함 전체 파일을 리스트화 - " + path)
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            relative_path = fp.replace(path, "")
            file_list.append([fp, f, relative_path])

    return file_list

def get_file_size(file_path):
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        return file_size

    return 0

def get_file_info_map(path):
    print("get file info - size, crc, fullname, path")
    fullpath = 0
    filename = 1
    relative_path = 2
    file_dict = {}
    file_list = get_file_list(path)
    for file_info in file_list:
        calc_crc = crc(file_info[fullpath])
        file_dict[file_info[relative_path]] = {'size' : get_file_size(file_info[fullpath]), 'fullpath' : file_info[fullpath], 'filename' : file_info[filename], 'crc' : calc_crc}
    
    print(file_dict)
    return file_dict

def get_diff(map1, map2):
    print("get diff - 두 디렉토리에서 crc 및 용량이 다른 파일 찾기")
    diff_list : list = []
    delete_map : dict = copy.deepcopy(map2)
    for key in map1:
        data1 = map1[key]
        if key in delete_map:
            delete_map.pop(key) # 지우지 않을 개체는 삭제 맵에서 제거
        if key in map2:
            data2 = map2[key]
            if data1['size'] != data2['size']:
                print("파일 사이즈가 틀려서 추가함 : " + key)
                diff_list.append([data1['fullpath'], data1['filename']])
            elif data1['crc'] != data2['crc']:
                print("파일 crc가 틀려서 추가함 : " + key)
                diff_list.append([data1['fullpath'], data1['filename']])
        else:
            diff_list.append([data1['fullpath'], data1['filename']])
            print("대상 폴더에 없어서 추가함 : " + key)
    return diff_list, delete_map

def copy_from_map(file_list, src_path, dest_path):
    if len(file_list) == 0:
        print("복사할 파일이 없습니다")
        return

    print("파일 복사 시작")
    fullpath = 0
    print(file_list)
    for path_pair in file_list:
        make_path = dest_path + "/" + path_pair[fullpath].replace(src_path, '')
        os.makedirs(os.path.dirname(make_path), exist_ok=True)
        print("Copy file : " + path_pair[fullpath] + " to " + make_path)
        shutil.copy2(path_pair[fullpath], make_path)

def delete_from_map(delete_map : dict):
    if len(delete_map) == 0:
        print("삭제할 파일이 없습니다")
        return

    print("도착지점의 원본 파일과 다른 파일 삭제")
    for key in delete_map:
        target_file = delete_map[key]["fullpath"]
        print("Delete file : " + target_file)
        os.remove(target_file)
    
    

def main(arg1 : str , arg2: str):
    if len(sys.argv) == 3:
        path1 = sys.argv[1]
        path2 = sys.argv[2]
    else:
        if not arg1 or not arg2:
            sys.exit()
        else:
            path1 = arg1
            path2 = arg2

    # for debug test
    # path1 = "C:\src_dir"
    # path2 = "C:\dest_dir"

    file_dict1 = get_file_info_map(path1)
    file_dict2 = get_file_info_map(path2)

    diff_list, delete_map = get_diff(file_dict1, file_dict2)
    if len(diff_list) != 0:
        print("변경된 파일 리스트")
        print(diff_list)

    delete_from_map(delete_map)
    copy_from_map(diff_list, path1, path2)

if __name__ == "__main__":
    # for debug test
    #main("C:\src_dir", "C:\dest_dir")
    main()
     
