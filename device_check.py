import torch
import torchvision
from tensorflow.python.client import device_lib


print("cuda available : ",torch.cuda.is_available())
print("torch version : ",torch.__version__)
print("torchvision version : ",torchvision.__version__)


# print(device_lib.list_local_devices())


# GPU 이름 체크(cuda:0에 연결된 그래픽 카드 기준)
device_name = torch.cuda.current_device()
print("GPU index : ",torch.cuda.current_device()) # 'NVIDIA TITAN X (Pascal)'
print("GPU name : ",torch.cuda.get_device_name(device_name))

# 사용 가능 GPU 개수 체크
print("사용가능 GPU 수 : ",torch.cuda.device_count()) 


device = 'cuda'
boxes = torch.tensor([[0., 1., 2., 3.]]).to(device)
scores = torch.randn(1).to(device)
iou_thresholds = 0.5
print(torchvision.ops.nms(boxes,scores,iou_thresholds))