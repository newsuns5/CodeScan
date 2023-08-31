'''
Simple code for Barcode Decoding Test 
'''


import cv2
import zxingcpp


font = cv2.FONT_HERSHEY_SIMPLEX
path = 'C:/PythonWorkSpace/CodeScanVenv/'
file_name = 'test_img_original3_crop.png'
img = cv2.imread(path+file_name)
results = zxingcpp.read_barcodes(img)
# zxing 좌표 컨버팅 as x,y,w,h
def convert_position(data) :
    
    t = str(data)
    # t = "394x108 406x360 166x362 153x115"
    t_cvt = t[:-1]
    t_split = t_cvt.split()
    # print('t_split : ',t_split)

    t_split_xy = t_split[0]
    t_split_wh = t_split[2]
    # print('t_split_xy :',t_split_xy)
    # print('t_split_wh :',t_split_wh)

    t_split_xy = t_split_xy.split('x')
    t_split_wh = t_split_wh.split('x')
    x = t_split_xy[0]
    y = t_split_xy[1]
    w = t_split_wh[0]
    h = t_split_wh[1]

    x,y,w,h = int(x),int(y),int(w),int(h)
  
    return x,y,w,h


for result in results:
	x,y,w,h = convert_position(result.position)
	cv2.rectangle(img, (x, y), (w, h), (0, 0, 255), 4)
	cv2.putText(img, result.text, (x , y + 20), font, 1, (0, 0, 255),4)
	print("Found barcode:\n Text:    '{}'\n Format:   {}\n Position: {}"
		.format(result.text, result.format, result.position))

if results :
    resize = cv2.resize(img, dsize=None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
    cv2.imshow('result',resize)
    cv2.waitKey(0)
    # cv2.imwrite(path+file_name+'_result.jpg',img)
	
elif len(results) == 0 :
	print("Could not find any barcode.")