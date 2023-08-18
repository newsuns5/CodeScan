import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import cv2
from datetime import datetime
from PIL import Image, ImageTk
import zxingcpp
import configparser
from time import strftime
import os
import logging
import torch
import sys



class LoggerFactory(object) :
    _LOGGER = None

    @staticmethod
    def create_logger():
        #루트 로거 생성
        LoggerFactory._LOGGER = logging.getLogger()
        LoggerFactory._LOGGER.setLevel(logging.INFO)

        #Log 폴더 없을시 생성
        if (os.path.exists('./log') == False) :
            os.makedirs('./log')

        #로드 포멧 생성
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(funcName)s:%(lineno)s] >> %(message)s') 

        #핸들러
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        file_handler = logging.FileHandler('./log/' + 'CodeScan_' + datetime.now().strftime('%Y%m%d') + '.log')
        file_handler.setFormatter(formatter)
        LoggerFactory._LOGGER.addHandler(stream_handler)
        LoggerFactory._LOGGER.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls):
        return cls._LOGGER
        

class CodeScannerApp:
    def __init__(self, root):
        self.root = root
        LoggerFactory.create_logger()
        self.logger = LoggerFactory.get_logger()
        # self.load_config_values
        self.config_file_path = "./code_config.ini"
        self.nStatus = tk.IntVar(value=0)
        self.nMode = tk.IntVar()  # Default mode is 1 (1 Reel Mode)
        self.destPath=tk.StringVar()
        self.model_path = tk.StringVar()
        self.config = configparser.ConfigParser()
        self.version = "1.2"
        self.verify_config() # config.ini 확인
        self.camera_number, self.flip, self.destPath, self.width, self.height, self.yolov5_path, self.model_path, self.MLconf = self.load_config_values()     
        self.fps = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cap = cv2.VideoCapture(self.camera_number)  # Initialize video capture
        self.txt_Box = None
        self.frame_temp = None
        self.nDOReultStatus = tk.BooleanVar()
        
        self.create_widgets()
        self.logger.info(f"\n\n\nCode Scan Version : {self.version}\nCode Scan Main Window executed successfully!\n")
        # self.ML_load()
        # self.logger.info(f"ML_data Loaded successfully!\n")
        
    
    def ML_load(self,frame) :
        
        # yolov5_path = os.path.join(os.getcwd(),'yolov5')
        # sys.path.append(yolov5_path)
        yolov5_path = os.path.abspath(self.config.get('ML SETTING', 'yolov5_path'))
        model_path = os.path.abspath(self.config.get('ML SETTING', 'model_path'))
        model = torch.hub.load(yolov5_path, 'custom', model_path, source='local',force_reload=True)
        # model = model.autoshape()
        # frame = ImageGrab.grab()
        model.conf = self.MLconf
        results = model(frame)
        
        return results

    # CONFIG.INI 파일이나 만들어 볼꽈~py
    def config_generator(self):
     
        self.config = configparser.ConfigParser()
        
 

        # 설정파일 오브젝트 만들기
        self.config['SYSTEM'] = {}
        self.config['SYSTEM']['title'] = 'Mr.Tak Code Scan'
        self.config['SYSTEM']['version'] = self.version
        self.config['SYSTEM']['update'] = strftime('%Y-%m-%d %H:%M:%S')

        self.config['SETTING'] = {}
        self.config['SETTING']['width'] = str(4000) # configparser 는 string 만 받는데
        self.config['SETTING']['height'] = str(3000)
        self.config['SETTING']['flip_option'] = str(-1)
        self.config['SETTING']['camera_number'] = str(2)
        self.config['SETTING']['image path'] = str(os.getcwd())

        self.config['ML SETTING'] = {}

        # yolov5 경로 받아오기 
        self.yolov5_path = os.path.join(os.getcwd(),'yolov5')
        sys.path.append(self.yolov5_path)

        self.config['ML SETTING']['yolov5_path'] = str(self.yolov5_path)
        self.config['ML SETTING']['model_path'] = str(self.yolov5_path)
        self.config['ML SETTING']['model_conf'] = str(0.5)

        

        # 설정파일 저장
        with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        self.logger.info("[Configure]"+f"{self.config_file_path}"+" is generated!\n")

    def save_config(self):
        # Update the config object with the new values from the entry fields
        self.width = int(self.width_entry.get())
        self.height = int(self.height_entry.get())
        self.camera_number = int(self.camera_number_entry.get())
        self.flip = int(self.flip_entry.get())
        save_location = self.saveLocationEntry.get()
        save_MLdataPath = self.saveMLdataLocationEntry.get()
        self.MLconf = float(self.entry_config_MLconf.get())


        # Save config values to config.ini
        if 'SETTING' not in self.config:
            self.config['SETTING'] = {}
        
        self.config['SYSTEM']['update'] = strftime('%Y-%m-%d %H:%M:%S')
        
        self.config['SETTING']['width'] = str(self.width)
        self.config['SETTING']['height'] = str(self.height)
        self.config['SETTING']['camera_number'] = str(self.camera_number)
        self.config['SETTING']['flip_option'] = str(self.flip)
        self.config['SETTING']['image path'] = save_location

        self.config['ML SETTING']['yolov5_path'] = self.yolov5_path
        self.config['ML SETTING']['model_path'] = save_MLdataPath
        self.config['ML SETTING']['model_conf'] = str(self.MLconf)
        

        with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        self.txt_Box.insert(tk.END,f"[Configure] Configure has been saved.\n")
        self.logger.info("[Configure] Configure has been saved.\n")

    def load_config_values(self) :

        print("Loading config values")
        self.logger.info("[Configure] Load"+f"{self.config_file_path}\n")
        # 설정파일 읽기
        self.config = configparser.ConfigParser()    
        self.config.read(self.config_file_path, encoding='utf-8') 
        
        print(self.config.items('SETTING'))
        
        return_camera_no = int(self.config.get('SETTING','camera_number'))
        return_flip_option = int(self.config.get('SETTING','flip_option'))
        return_image_path  = self.config.get('SETTING','image path')
        return_width = int(self.config.get('SETTING','width'))
        return_height = int(self.config.get('SETTING','height'))
        return_yolov5_path = self.config.get('ML SETTING','yolov5_path')
        retrun_MLpath = self.config.get('ML SETTING','model_path')
        retrun_MLconf = float(self.config.get('ML SETTING','model_conf'))

        return return_camera_no, return_flip_option, return_image_path, return_width, return_height, return_yolov5_path, retrun_MLpath, retrun_MLconf 

            
    def verify_config(self) :
        
        if os.path.isfile(self.config_file_path) :           
            print("config file is exist")

        else :
            self.config_generator()
            print("config file is generated")

    def config_read(self):
    
        # 설정파일 읽기
        self.config = configparser.ConfigParser()    
        self.config.read(self.config_file_path, encoding='utf-8') 

        # 설정파일의 색션 확인
        self.INI_read_test(self.config)

    # 설정파일 잘 불러오는지 테스트용 메소드
    def INI_read_test(self,config) :
        current_working_dir = os.getcwd() # 폴더 어디임?
        ver = config['SYSTEM']['version']
        title = config['SYSTEM']['title']
        width = config['SETTING']['width']
        height = config['SETTING']['height']
        flip_option = config['SETTING']['flip_option']
        camera_number = config['SETTING']['camera_number']
        print(title,ver)
        print("Camera Resolution : {0}x{1}".format(width,height))
        print("Camera Number : {0}".format(camera_number))
        print("Flip Option : ", flip_option)
        print("Working_DIR : ",current_working_dir) # 폴더 여기임~

    def convert_position(self, data):
        
        t = str(data)
        # t = "394x108 406x360 166x362 153x115"
        # t_cvt = t[:-1]
        # t_split = t_cvt.split()
        t_split = t.split()
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

    def Capture_CodeScan(self) :
        self.logger.info("[Barcode Scan] Capture_CodeScan method called\n")
        self.mode_value = self.nMode.get()
        print("Selected Mode:", self.mode_value)
        global frame_temp

        current_time = datetime.now()
        image_date = datetime.now().strftime('%Y%m%d_%H%M%S')

        if self.destPath == '':
            tk.messagebox.showerror("ERROR", "NO DIRECTORY SELECTED")
            self.logger.info("[Barcode Scan] Save Path is empty\n")
            return
        # 이미지 저장경로가 있으면    
        else:
            image_path = self.destPath
            imgName = image_path + '/' + image_date + ".jpg"

        flip_temp = cv2.flip(frame_temp,self.flip)
        cv2.imwrite(imgName, flip_temp)

        self.logger.info("[Barcode Scan] Original Image write\n")
        result = self.read_frame_simple(flip_temp)

        if result is not None :

            self.logger.info(f"[Barcode Scan] {result[2]} Code read Successfully\n")

        elif result is None :
            self.logger.info("[Barcode Scan] Barcode detection failed.\n")
            self.txt_Box.insert(tk.END,"[Barcode Scan] Barcode detection failed.\n")
            return
        
        success_result_frame, barcode_index, barcode_data = result
        resize_success_result_frame = cv2.resize(success_result_frame, dsize=None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)  

        cv2.imshow('Result', resize_success_result_frame)
        self.logger.info("[Barcode Scan] Show result View successfully\n")
        


        # if resize_success_result_frame.any() :
        #     self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"index : "+f"{barcode_index}"+" :: "+f"{barcode_data}"+f" is saved successfuly.\n")

    def Capture(self, frame, barcode_data, barcode_index):
        current_time = datetime.now()
        image_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        
      
        image_path = self.destPath
        
        if self.mode_value == 1 :
            imgName = image_path + '/' + image_date + '_' + '0' + '_' + barcode_data + ".jpg" 
        elif self.mode_value == 4:
            imgName = image_path + '/' + image_date + '_' + str(barcode_index) + '_' + barcode_data + ".jpg" 
    
        # 이미지 저장
        success = cv2.imwrite(imgName, frame)

        # 성공하면 logging
        if success :
            if self.mode_value == 1 :
                self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"1 Reel Mode"+" :: "+f"{barcode_data}"+" is saved successfuly.\n")
                self.logger.info("1 Reel Mode"+" :: "+f"{barcode_data}"+" is saved successfuly.\n")
            elif self.mode_value == 4 :
                self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"4 Reel Mode"+" :: "+f"{barcode_index}"+" :: "+f"{barcode_data}"+" is saved successfuly.\n")
                self.logger.info("4 Reel Mode"+" :: "+f"{barcode_index}"+" :: "+f"{barcode_data}"+" is saved successfuly.\n")


    def barcode_pos_compare(self, barcode_pos):
         # x coordinate check
        if barcode_pos[0] <= self.width / 2 :
            barcode_index_x = 0   
        else : 
            barcode_index_x = 1
        # y coordinate check
        if barcode_pos[1] <= self.height / 2 :
            barcode_index_y = 0
        else :
            barcode_index_y = 1
        # x,y check
        if barcode_index_x == 0 and barcode_index_y == 0:
            barcode_index = 0
        elif barcode_index_x == 1 and barcode_index_y == 0:
            barcode_index = 1
        elif barcode_index_x == 0 and barcode_index_y == 1:
            barcode_index = 2
        else:
            barcode_index = 3

        return barcode_index
    
    def read_frame_simple(self, frame):
        current_time = datetime.now()
        try:

            barcodes = zxingcpp.read_barcodes(frame) 

            for barcode in barcodes :
                x, y, w, h = self.convert_position(barcode.position)
                barcode_result = barcode.text
                barcode_pos = [x,y,w,h]
                barcode_index = self.barcode_pos_compare(barcode_pos)
                cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 8)
                cv2.putText(frame, barcode_result, (x , y + 20), self.font, 1, (0, 0, 255),4)

                # print('nMode : ',self.nMode,type(self.nMode))
                # print('mode_value : ',self.mode_value,type(self.mode_value))
                
                if self.mode_value == 1 :
                    self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"index : 0"+" :: "+f"{barcode.format}"+" :: "+f"{barcode_result}\n")
                    self.logger.info("1 Reel Mode"+" :: "+f"{barcode_result}"+" is read.\n")
                elif self.mode_value == 4 :
                    self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"index : "+f"{barcode_index}"+" :: "+f"{barcode.format}"+" :: "+f"{barcode_result}\n")
                    self.logger.info("4 Reel Mode"+" :: "+f"{barcode_index}"+f"{barcode_result}"+" is read.\n")
                else :
                    self.txt_Box.insert(tk.END,"Barcode Mode or Code error")
                    self.logger.error("[Barcode Scan] Barcode Mode or Code error\n")
                
                self.Capture(frame,barcode_result,barcode_index)

            return frame, barcode_index, barcode_result
        
        
        except Exception as e:
            self.logger.error(f"[Barcode Scan] {e} \n")
            print(e)

        # else : # 2 번 camera view mode
                
        #     return frame, None, None    
        
    def ShowFeed(self):
        global width, height, nStatus, nMode, frame_temp
        width_4reel = self.width / 2
        height_4reel = self.height / 2

        # camera mode 확인
        if self.nMode.get() == 1 : # 0 : Camera View Mode

            # 실행 내역 및 프레임 가져오기
            ret, frame = self.cap.read()
            frame_temp = frame # code decoding 및 save용 temp frame
            # 실행 내역이 true이면 프레임 출력
            if ret: 

                #이미지 미러링
                mirror_image = cv2.flip(frame,self.flip)

                # <<<여기다 object detection 
                
                # 시간 txt 이미지에 삽입
                cv2.putText(mirror_image, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (400,100), cv2.FONT_HERSHEY_TRIPLEX, 3, (0,255,0))
                # Convert image from one color space to other
                opencv_image = cv2.cvtColor(mirror_image, cv2.COLOR_BGR2RGBA)
                resize_frame = cv2.resize(opencv_image, (960,540), interpolation=cv2.INTER_CUBIC)

                # Capture the latest frame and transform to image
                captured_image = Image.fromarray(resize_frame)
                    
                # Convert captured image to photoimage
                photo_image = ImageTk.PhotoImage(image=captured_image)

                # Displaying photoimage in the label
                self.webcam_label.photo_image = photo_image
                # Configure image in the label
                self.webcam_label.configure(image=photo_image)
                
                self.webcam_label.after(20, self.ShowFeed)
               
            
            else :
                    self.webcam_label.configure(image='')  

        if self.nMode.get() == 4 : # Real time Code Detection 이면
            
            ret, frame = self.cap.read()
            frame_temp = frame
        
            if ret: 

                    # 이미지 미러링
                    mirror_image = cv2.flip(frame,self.flip)
                    # x,y 분할선 추가
                    x_line_image = cv2.line(mirror_image,(0,int(self.height/2)),(int(self.width),int(self.height/2)),(0,255,0),thickness=8)
                    y_line_image = cv2.line(x_line_image,(int(self.width/2),0),(int(self.width/2),int(self.height)),(0,255,0),thickness=8)
                    # 시간 txt 이미지에 삽입
                    cv2.putText(y_line_image, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (400,100), cv2.FONT_HERSHEY_TRIPLEX, 3, (0,255,0))

                    # decode_image = self.read_frame(y_line_image)
                    # Convert image from one color space to other
                    opencv_image = cv2.cvtColor(y_line_image, cv2.COLOR_BGR2RGBA)
                    resize_frame = cv2.resize(opencv_image, (960,540), interpolation=cv2.INTER_CUBIC)

                    # Capture the latest frame and transform to image
                    captured_image = Image.fromarray(resize_frame)
                        
                    # Convert captured image to photoimage
                    photo_image = ImageTk.PhotoImage(image=captured_image)

                    # Displaying photoimage in the label
                    self.webcam_label.photo_image = photo_image
                    # Configure image in the y
                    self.webcam_label.configure(image=photo_image)
                    
                    self.webcam_label.after(20, self.ShowFeed)

            else :
                    self.webcam_label.configure(image='')   

    def CameraOn(self):
        
        self.btn_manual_capture.config(state=tk.NORMAL)
        # Creating object of class VideoCapture with webcam index
        self.cap = cv2.VideoCapture(self.camera_number)

        width, height = self.width,self.height
        focus_val = 255
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(28,focus_val)

        #get original camera resolution
        width_original_size  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height_original_size = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float `height`
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.logger.info("Camera On Button Clicked\n")
        self.ShowFeed() 

    def CameraOff(self):
        self.logger.info("Camera Off Button Clicked\n")
        self.cap.release()
        self.webcam_label.config(text="Vision Window",width=800,height=600, borderwidth=1, relief="solid")
        # capture disable
        self.btn_manual_capture.config(state=tk.DISABLED) 

    def destimgBrowse(self):

        self.destDirectory = filedialog.askdirectory(initialdir=os.getcwd(), parent=self.menu_config)
        
        self.saveLocationEntry.delete(0, tk.END)
        self.saveLocationEntry.insert(0, self.destDirectory)
        # self.saveLocationEntry = tk.Entry(self.menu_config, width=20, textvariable=tk.StringVar(value=return_dest_path))
        # # Displaying the directory in the directory textbox
        # if destDirectory:
        #     self.destPath.set(destDirectory)
        #     self.root.focus_force()

    def destMLtrainBrowse(self) :
        self.destMLdataPath = filedialog.askopenfilename(initialdir=os.getcwd(), \
                                                         title="Select ML Train data",\
                                                         filetypes=(("PT files", "*.pt"), ("All files", "*.*")), \
                                                         parent=self.menu_config)
        
        if self.destMLdataPath == '' :
            tk.messagebox.showwarning("warning","Please Select the file")
        else :
            self.saveMLdataLocationEntry.delete(0, tk.END)
            self.saveMLdataLocationEntry.insert(0, self.destMLdataPath)
    
    def ObjectDetection(self) :
        
        global frame_temp

        current_time = datetime.now()
        image_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.destPath == '':
            # messagebox.showerror("ERROR", "NO DIRECTORY SELECTED")
            return
        # 이미지 저장경로가 있으면    
        else:
            image_path = self.destPath
            
        imgName = image_path + '/' + image_date + ".jpg" 

        # 이미지 저장
        success = cv2.imwrite(imgName, frame_temp)
        self.logger.info(f"[Object Detection]{imgName} is saved successfully.\n")

        # 성공하면 logging
        if success :
            self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"index : "+f" Image is saved successfully.\n")

                      
            # Train 적용
            ML_result = self.ML_load(frame_temp)

            print(type(ML_result))
            print(ML_result)
            self.logger.info(f"[Object Detection] Machine Learing data mounted successfully.\n")

            # Result View Option is checked!!!
            if self.nDOReultStatus.get() == True : 

                ML_result.show() # 화면 뿌리기
                self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+f"{ML_result}\n")
            else : 
                self.logger.info(f"[Object Detection] {ML_result} :: Show the result successfully.\n")
                self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+f"{ML_result}\n")
                tk.messagebox.showinfo(title="Object Detection Result", message=f"{ML_result}")


        else :
            print("ML routine is not working.")
            self.logger.error(f"[Object Detection] {current_time} Machine Learning data is not loaded.\n")

    def manual_capture(self):

        global frame_temp

        current_time = datetime.now()
        image_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.destPath == '':
            # messagebox.showerror("ERROR", "NO DIRECTORY SELECTED")
            return
        # 이미지 저장경로가 있으면    
        else:
            image_path = self.destPath
            
        imgName = image_path + '/' + image_date + ".jpg" 

        # 이미지 저장
        success = cv2.imwrite(imgName, frame_temp)

        # 성공하면 logging
        if success :
            self.txt_Box.insert(tk.END,f"{current_time}"+" -> "+"index : "+f" Image is saved successfuly.\n")
            
        else :
            print("Image Capture is failed.")

    def clear(self):
        self.txt_Box.delete(1.0,tk.END)    

    def TestBtn(self):
    
        global fps
        global width,height
        global nMode

        return_camera_no, return_flip_option, return_image_path, return_width, return_height, return_mlpath, return_mlconf = self.load_config_values()
        # 현재 선택된 모드를 가져오기
        selected_mode = self.nMode.get()
        
        # self.txt_Box.insert(tk.END,f"x : {width_original_size}, y : {height_original_size}\n")
        # self.txt_Box.insert(tk.END,f"focus : {cv2.CAP_PROP_FOCUS}\n")
        # self.txt_Box.insert(tk.END,f"fps : {self.fps}\n")
        self.txt_Box.insert(tk.END,f"Reel Mode : {selected_mode}\n")
        self.txt_Box.insert(tk.END,f"Camera Number : {return_camera_no}\n")
        self.txt_Box.insert(tk.END,f"width : {return_width}, height : {return_height}\n" )
        self.txt_Box.insert(tk.END,f"Flip_Option : {return_flip_option}\n")
        self.txt_Box.insert(tk.END,f"Save Dir : {return_image_path}\n")
        self.txt_Box.insert(tk.END,f"ML path : {return_mlpath}\n")
        self.txt_Box.insert(tk.END,f"ML conf : {return_mlconf}\n")

        self.config_read()

        self.txt_Box.insert(tk.END,f"Result View Option : {self.nDOReultStatus.get()}\n")


    def version_info(self):
        #도움말
        menu_help = tk.Toplevel(self.root)
        menu_help.geometry("300x200+600+300")
        menu_help.title("버전정보")
        ver_info = tk.Label(menu_help, text="TECHVALLEY INTELIGENT VISION SYSTEM",font=('고딕체',10,'bold'))
        ver_info.place(x=12,y=20)
        ver_no = tk.Label(menu_help, text="Version : {0}".format(self.version),font=('고딕체',9,'bold'))
        ver_no.place(x=110,y=70)
        website = tk.Label(menu_help, text="www.techvalley.co.kr",font=('고딕체',9,'bold'))
        website.place(x=90,y=120)
    
    def config_menu(self) :
        self.menu_config = tk.Toplevel(self.root)
        self.menu_config.geometry("800x400+600+300")
        self.menu_config.title("설정")

        # Set the initial values to the Entry widgets
        return_camera_no, return_flip_option, return_dest_path, return_width, return_height,return_yolov5_path,return_mlpath,return_mlconf = self.load_config_values()

        # Camera Flip Entry
        config_flip_label = tk.Label(self.menu_config, text="Camera Flip", font=('고딕체',10))
        config_flip_label.place(x=10,y=20)
        self.flip_entry = tk.Entry(self.menu_config, width=4, textvariable=tk.StringVar(value=return_flip_option))
        self.flip_entry.place(x=140, y=20)

        # Camera Number Entry
        config_camera_number = tk.Label(self.menu_config, text="Camera Number", font=('고딕체',10))
        config_camera_number.place(x=10,y=50)
        self.camera_number_entry = tk.Entry(self.menu_config, width=4, textvariable=tk.StringVar(value=return_camera_no))
        self.camera_number_entry.place(x=140,y=50)

        # Width Entry
        config_width_label = tk.Label(self.menu_config, text="Width", font=('고딕체', 10))
        config_width_label.place(x=10, y=80)
        self.width_entry = tk.Entry(self.menu_config, width=6, textvariable=tk.StringVar(value=self.width))
        self.width_entry.place(x=140, y=80)

     
        # Height Entry
        config_height_label = tk.Label(self.menu_config, text="Height", font=('고딕체', 10))
        config_height_label.place(x=10, y=110)
        self.height_entry = tk.Entry(self.menu_config, width=6, textvariable=tk.StringVar(value=self.height))
        self.height_entry.place(x=140, y=110)

        # Browse and Entry for Save Image Path
        label_imageSavePath = tk.Label(self.menu_config, text="Save Image Path")
        label_imageSavePath.place(x=10, y=144)
        
        self.saveLocationEntry = tk.Entry(self.menu_config, width=20)
        self.saveLocationEntry.place(x=10, y=164)
        self.saveLocationEntry.insert(0, return_dest_path)

        btn_imagePathBrowse = tk.Button(self.menu_config, width=8, height=1, text="Browse", command=self.destimgBrowse)
        btn_imagePathBrowse.place(x=160, y=160)

        # ML load Configure
        label_mlDataPath = tk.Label(self.menu_config, text="ML Train Data Path")
        label_mlDataPath.place(x=10, y=194)

        self.saveMLdataLocationEntry = tk.Entry(self.menu_config, width=20)
        self.saveMLdataLocationEntry.place(x=10, y=214)
        self.saveMLdataLocationEntry.insert(0, return_mlpath)

        btn_mldataBrowse = tk.Button(self.menu_config, width=8, height=1, text="Browse", command=self.destMLtrainBrowse) 
        btn_mldataBrowse.place(x=160,y=210)

        label_config_MLconf = tk.Label(self.menu_config, text="Conf", font=('고딕체', 10))
        label_config_MLconf.place(x=10, y=250)
        self.entry_config_MLconf = tk.Entry(self.menu_config, width=6, textvariable=tk.StringVar(value=return_mlconf))
        self.entry_config_MLconf.place(x=140, y=250)

        # Save & Close Button
        btn_config_save = tk.Button(self.menu_config, text="Save", width=10, height=2, command=self.save_config)
        btn_config_save.place(x=200, y=350)

        btn_config_close = tk.Button(self.menu_config,text="Close", width=10, height=2, command=self.menu_config.destroy)
        btn_config_close.place(x=300,y=350)


    def create_widgets(self):
        main_menu = tk.Menu(self.root)
        self.root.config(menu=main_menu)

        # File Menu
        file_menu = tk.Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Config Menu
        config_menu = tk.Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="Configure", menu=config_menu)
        config_menu.add_command(label="Configuration", command=self.config_menu)

        # Help Menu
        help_menu = tk.Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Version", command=self.version_info)

        # Mode Selection Combobox
        # cmb_mode = ttk.Combobox(self.root, height=3, textvariable=self.nStatus)
        # cmb_mode.config(values=('Camera View Mode', 'Real-Time Code Detection'))
        # cmb_mode.place(x=10, y=10)
        # cmb_mode.bind("<<ComboboxSelected>>", self.display_selected_item_index)

        # Vision View Label
        self.webcam_label = tk.Label(self.root, text="Vision Window", width=800, height=600, borderwidth=1, relief="solid")
        self.webcam_label.place(x=240, y=20, width=800, height=600)
      

        # Mode Radio Buttons
        radio_mode_1 = tk.Radiobutton(self.root, text="1 Reel", value=1, variable=self.nMode)
        radio_mode_1.select()
        radio_mode_4 = tk.Radiobutton(self.root, text="4 Reel", value=4, variable=self.nMode)
        radio_mode_1.place(x=10, y=40)
        radio_mode_4.place(x=80, y=40)

        # Camera On/Off Buttons
        btn_cameraOn = tk.Button(self.root, text="Camera On", width=10, height=2, command=self.CameraOn)
        btn_cameraOn.place(x=10, y=70)

        btn_cameraOff = tk.Button(self.root, text="Camera Off", width=10, height=2, command=self.CameraOff)
        btn_cameraOff.place(x=100, y=70)

        # Code Scan Button
        btn_code_scan = tk.Button(self.root, text="Barcode Scan",width=22, height=2, command=self.Capture_CodeScan)
        btn_code_scan.place(x=12, y=120)

        # Object Detection Button
        btn_ObjectDetecion = tk.Button(self.root, text="Object Detection", width=22, height=2, command=self.ObjectDetection)
        btn_ObjectDetecion.place(x=12, y=170)

        # Object Detection Result Checkbutton
        # label_ODResult = tk.Label(self.root, text="Result View Option")
        # label_ODResult.place(x=12, y=220)
        chkbtn_ODReult = tk.Checkbutton(self.root, text="Result View Option")
        chkbtn_ODReult.config(variable=self.nDOReultStatus)
        chkbtn_ODReult.place(x=12, y=220)


        # Manual Capture Button
        self.btn_manual_capture = tk.Button(self.root, text="Manual Capture", width=15, height=2, state=tk.NORMAL, command=self.manual_capture)
        self.btn_manual_capture.place(x=10, y=260)

        # Clear Button
        btn_clear = tk.Button(self.root, text="Clear", width=15, height=2, command=self.clear)
        btn_clear.place(x=12, y=320)

        # Test Button
        btn_test = tk.Button(self.root, text="Test", width=10, height=1, command=self.TestBtn)
        btn_test.place(x=10, y=380)

        # Text Box
        self.txt_Box = tk.Text(self.root, width=100, height=14)
        self.txt_Box.insert(tk.END, "Code Scan Test\n")
        self.txt_Box.place(x=240, y=650, width=800, height=240)

        

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x900+300+50")
    app = CodeScannerApp(root)
    root.title("Mr.Tak Code Scan"+"  version : {}".format(app.version))
    root.mainloop()