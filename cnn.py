import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data
import torchvision
import matplotlib.pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings('ignore')
 
torch.manual_seed(1)
 
EPOCH = 1
BATCH_SIZE = 50
LR = 0.001
DOWNLOAD_MNIST = True
 
# 获取训练集dataset
training_data = torchvision.datasets.MNIST(
             root='./MINST/', # dataset存储路径
             train=True, # True表示是train训练集，False表示test测试集
             transform=torchvision.transforms.ToTensor(), # 将原数据规范化到（0,1）区间
             download=DOWNLOAD_MNIST,
             )
training = training_data.train_data[:1000]
# 打印MNIST数据集的训练集及测试集的尺寸
print(training_data.train_data.size())
print(training_data.train_labels.size())
# torch.Size([60000, 28, 28])
# torch.Size([60000])
plt.imshow(training_data.train_data[0].numpy(), cmap='gray')
plt.title('%i' % training_data.train_labels[0])
plt.show()
 
# 通过torchvision.datasets获取的dataset格式可直接可置于DataLoader
train_loader = Data.DataLoader(dataset=training_data, batch_size=BATCH_SIZE,
                               shuffle=True)
                             
%%time
# 获取测试集dataset
test_data = torchvision.datasets.MNIST(root='../MINST/', train=False)
# 取前2000个测试集样本
test_x = Variable(torch.unsqueeze(test_data.test_data, dim=1),
                  volatile=True).type(torch.FloatTensor)[:2000]/255#torch.unsqueeze 在某一位置插入一维
print(test_x.size())
# (2000, 28, 28) to (2000, 1, 28, 28), in range(0,1)
test_y = test_data.test_labels[:2000]
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential( # (1,28,28)
                     nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5,
                               stride=1, padding=2), # (16,28,28)
        # 想要con2d卷积出来的图片尺寸没有变化, padding=(kernel_size-1)/2
                     nn.ReLU(),
                     nn.MaxPool2d(kernel_size=2) # (16,14,14)
                     )
        self.conv2 = nn.Sequential( # (16,14,14)
                     nn.Conv2d(16, 32, 5, 1, 2), # (32,14,14)
                     nn.ReLU(),
                     nn.MaxPool2d(2) # (32,7,7)
                     )
        self.out = nn.Linear(32*7*7, 10)
 
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        print(x.size())
        x = x.view(x.size(0), -1) # 将（batch，32,7,7）展平为（batch，32*7*7）
        output = self.out(x)
        return output


cnn = CNN()
print(cnn)
'''
CNN (
  (conv1): Sequential (
    (0): Conv2d(1, 16, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
    (1): ReLU ()
    (2): MaxPool2d (size=(2, 2), stride=(2, 2), dilation=(1, 1))
  )
  (conv2): Sequential (
    (0): Conv2d(16, 32, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
    (1): ReLU ()
    (2): MaxPool2d (size=(2, 2), stride=(2, 2), dilation=(1, 1))
  )
  (out): Linear (1568 -> 10)
)
'''
optimizer = torch.optim.SGD(cnn.parameters() ,momentum=0.9, lr=LR,nesterov = True)
loss_function = nn.CrossEntropyLoss()
 
for epoch in range(EPOCH):
      for step, (x, y) in enumerate(train_loader):
        b_x = Variable(x)
        b_y = Variable(y)
        print(b_x.size())
        output = cnn(b_x)
        loss = loss_function(output, b_y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if(step>10):
            break
        if step % 10 == 0:
            test_output = cnn(test_x)
            print(1,test_output.size())
            pred_y = torch.max(test_output, 1)[1].data.squeeze()
            target_y = test_y.numpy()
            pred_y = pred_y.numpy()
            accuracy = float((pred_y == target_y).astype(int).sum()) / float(target_y.size)
            print('Epoch:', epoch, '|Step:', step,
                  '|train loss:%.4f'%loss.data[0], '|test accuracy:%.4f'%accuracy)
test_output = cnn(test_x[:10])
  pred_y = torch.max(test_output, 1)[1].data.numpy().squeeze()
print(pred_y, 'prediction number')
