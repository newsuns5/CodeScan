'''
Simple code for Barcode Decoding Test 
'''


import cv2
import zxingcpp
from scipy import ndimage
import math

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

def rotate_image(img,angle=0) :
    
    #rotation angle in degree
    rotated = ndimage.rotate(img, angle)
    return rotated

def draw_angled_rec(x0, y0, width, height, angle, img):

    _angle = angle * math.pi / 180.0
    b = math.cos(_angle) * 0.5
    a = math.sin(_angle) * 0.5
    pt0 = (int(x0 - a * height - b * width),
           int(y0 + b * height - a * width))
    pt1 = (int(x0 + a * height - b * width),
           int(y0 - b * height - a * width))
    pt2 = (int(2 * x0 - pt0[0]), int(2 * y0 - pt0[1]))
    pt3 = (int(2 * x0 - pt1[0]), int(2 * y0 - pt1[1]))

    cv2.line(img, pt0, pt1, (0, 0, 255), 3)
    cv2.line(img, pt1, pt2, (0, 0, 255), 3)
    cv2.line(img, pt2, pt3, (0, 0, 255), 3)
    cv2.line(img, pt3, pt0, (0, 0, 255), 3)


def bnc_control(img,alpha,beta) :
    # define the alpha and beta
    # alpha = 1.5 # Contrast control
    # beta = 10 # Brightness control

    # call convertScaleAbs function 
    adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return adjusted_img

font = cv2.FONT_HERSHEY_SIMPLEX
path = 'C:/PythonWorkSpace/CodeScanVenv/'
file_name = 'test_img_original3_crop.png'
img = cv2.imread(path+file_name)

nAngle = 0

alpha = 0.5 # Contrast control
beta = 50 # Brightness control        

# B&C control
img = bnc_control(img,alpha,beta)

#Rotate image
while nAngle < 90 :
         
    print("processing Angle : ",nAngle)
    rotated_img = rotate_image(img, nAngle)
    results = zxingcpp.read_barcodes(rotated_img)
    # cv2.imwrite(path+file_name+'_'+str(nAngle)+'_rotated.jpg',rotated_img)


    for result in results:
        x,y,w,h = convert_position(result.position)
        # draw_angled_rec(w,y,w,h,nAngle,img)
        img2 = cv2.rectangle(rotated_img, (x, y), (w, h), (0, 0, 255), 4)
        print("Found barcode:\n Text:    '{}'\n Format:   {}\n Position: {}"
            .format(result.text, result.format, result.position))

        if results :
            rotateback_img = rotate_image(img2,-nAngle)
            cv2.putText(rotateback_img, result.text, (x , y + 20), font, 1, (0, 0, 255),4)
            resize = cv2.resize(rotateback_img, dsize=None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
            # cv2.imshow('result',rotateback_img)
            # cv2.waitKey(0)
            cv2.imwrite(path+file_name+'_'+str(nAngle)+'_result.jpg',resize)

        elif len(results) == 0 :
            
            print("Could not find any barcode.")

    nAngle += 5



