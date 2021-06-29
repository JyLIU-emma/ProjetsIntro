import os,re, shutil
import glob

for root, dirpath, filename in os.walk("../train_clean_amphasis"):
    if root == "../train_clean_amphasis":
        for dirname in dirpath:
            path_clean_dir = os.path.join("../clean_test", dirname)
            path_clean_train = os.path.join(root, dirname, "train")
            path_clean_dev = os.path.join(root, dirname, "dev")

            #新的train开始数字250
            num_new_train = 250

            #数dev文件个数，找到一半
            #查找到一个后要将它的变速都挪走
            list_num_dev = []
            for nom_dev in os.listdir(path_clean_dev):
                if nom_dev != ".DS_Store":
                    num_dev = re.split(r'[\-\.]', nom_dev)[-2]
                    list_num_dev.append(num_dev)
            list_num_dev = list(set(list_num_dev))
            half = len(list_num_dev)//2
            list_dev_half = list_num_dev[::half+1]

            compt = 0
            for num_dev in list_dev_half:
                old_pathes = glob.glob(path_clean_dev + '/*' +str(num_dev) + '.wav')
                for op in old_pathes:
                    print(op)
                    name_dev = re.split(r'\/',op)[-1]
                    name_list = re.split(r'[\-\.]',name_dev)
                    print(len(name_list))
                    if len(name_list) == 6:
                        new_file_train = name_list[0] + "." + name_list[1] + "-" + name_list[2] + "-train-" + str(num_new_train+compt) + ".wav"
                    
                    else:
                        new_file_train = name_list[0] + "-train-" + str(num_new_train+compt) + ".wav"
                    
                    print(new_file_train)
                    new_path_train = os.path.join(path_clean_train, new_file_train)
                    shutil.move(op, new_path_train)
                compt += 1
                print(compt)
                    
            
                    
       
