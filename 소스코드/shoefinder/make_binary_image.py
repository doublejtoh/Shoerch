from PIL import Image
import numpy as np
import os

input_rel_path = 'data/TIMBERLAND/test'
output_rel_path = '/tmp/TIMBERLAND_data/TIMBERLAND-batches-bin'
filenames = os.listdir(input_rel_path)
if '.DS_Store' in filenames:
    filenames.remove('.DS_Store')
image_nums = len(filenames)
print(image_nums)
split_file_num = 1 # data_batch_1.bin, data_batch_2, ..., data_batch_5

splitted_filenames = [filenames[i:i + int(image_nums / split_file_num)] for i in range(0, len(filenames), int(image_nums / split_file_num))]

print(splitted_filenames)

for i, filenames in enumerate(splitted_filenames):
    out = None
    for filename in filenames:
        ### reshape image if necessary ###
        im = Image.open(os.path.join(input_rel_path, filename))
        im = im.resize((500, 500))
        im = (np.array(im))

        r = im[:, :, 0].flatten()
        g = im[:, :, 1].flatten()
        b = im[:, :, 2].flatten()

        ### label parsing ###
        start_index = filename.rfind('_')
        end_index = filename.rfind('.')
        label = [int(filename[start_index+1: end_index])-1]
        if out == None:
            out = list(label) + list(r) + list(g) + list(b)
        else:
            out = out + list(label) + list(r) + list(g) + list(b)
        print("end for")
    out = np.array(out, np.uint8)
    print("fout >>>")
    #out.tofile(os.path.join(output_rel_path, 'data_batch_%d.bin' % (i+1,)))
    out.tofile(os.path.join(output_rel_path, 'test_batch.bin'))




# im = Image.open(os.path.join(rel_path, filenames[1]))
#
# ### reshape image if necessary ###
# im = im.resize((500, 500))
# im = (np.array(im))
#
# r = im[:, :, 0].flatten()
# print(len(r))
# g = im[:, :, 1].flatten()
# b = im[:, :, 2].flatten()
# ### label parsing ###
# start_index = filenames[1].rfind('_')
# end_index = filenames[1].rfind('.')
# label = [int(filenames[1][start_index+1: end_index])]
#
#
# out = np.array(list(label) + list(r) + list(g) + list(b), np.uint8)
# print(len(out))
# out.tofile("data/binary_input/data_batch_1.bin")
# print(out)
