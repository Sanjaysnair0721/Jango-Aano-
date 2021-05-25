# -*- coding: utf-8 -*-
"""Jango Classifier_training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SACK6wereq0TudWfF4EISUXM1WyJi86g
"""

from google.colab import drive
drive.mount('/content/drive')

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.functional import conv2d,max_pool2d,log_softmax,linear,relu,dropout2d,tanh
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
import matplotlib.pyplot as plt
import matplotlib.image as img
from PIL import Image, ImageDraw
import numpy as np
import os
import pandas as pd
import cv2

#loading trainimng data from drive
mean = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float)
std = torch.tensor([0.229, 0.224, 0.225], dtype=torch.float)
transform1 = transforms.Compose([
    transforms.Resize((32,32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std)])
train_data = ImageFolder(r'/content/drive/MyDrive/jackfruit_mango_classifier/training_new_trial/',transform = transform1)
print(train_data.classes)

#loading validatiuon data
valid_data = ImageFolder(r'/content/drive/MyDrive/jackfruit_mango_classifier/validation/',transform = transform1)
img,label= valid_data[0]
print(valid_data.classes)

# Create a Train DataLoader using Train Dataset
train_data_loader = torch.utils.data.DataLoader(
    dataset=train_data,
    batch_size=16,
    shuffle=False
    
)
# Create a Test DataLoader using Validation Dataset

val_data_loader = torch.utils.data.DataLoader(
    dataset = valid_data, 
    batch_size = 5, 
    shuffle=False
    
    )

#architecture based on Lenet5
class Net_jango(nn.Module):
    def __init__(self):
        super(Net_jango, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.maxpool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5) 
        self.fullyconnected1 = nn.Linear(16 * 5 * 5, 120)
        self.fullyconnected2 = nn.Linear(120, 84)
        self.fullyconnected3 = nn.Linear(84, 2)

    def forward(self, x):

        x = self.maxpool(F.relu(self.conv1(x)))
        x = self.maxpool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fullyconnected1(x))
        x = F.relu(self.fullyconnected2(x))
        x = self.fullyconnected3(x)
        return x

#model_initialisation and loading the trained model from drive for further training
model = Net_jango()
print(model)
model_save_name = 'jango_classifier.pt'
path_model = "/content/drive/MyDrive/jackfruit_mango_classifier/" + model_save_name
model.load_state_dict(torch.load(path_model))

#checking whether cuda available

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
device
if torch.cuda.is_available():
    model.cuda()
else:
    model.cpu()

#loss function and optimiser
epochs =50
batch_size = 5
learning_rate = 0.001
loss_f = torch.nn.NLLLoss()
loss_func =nn.CrossEntropyLoss()
optimise=torch.optim.Adam(model.parameters(),lr=0.001)

#training and testing
train_loss=[]
val_loss=[]
accuracy = []

for epoch in range(epochs):
  trainloss=0
  validloss=0

  model.train()
  for data,label in train_data_loader:
    data = data.to(device)
    label = label.to(device)
    #to clear gradients
    optimise.zero_grad()
    output = model(data)
    # print(output)
    loss = loss_func(output,label)
    loss.backward()
    optimise.step()
    trainloss += loss.item() #.item to convert to float
    train_loss.append(trainloss)
    

  model.eval()

  for data,label in val_data_loader:
    data = data.to(device)
    label = label.to(device)
    output = model(data)
    # print(output)
    loss = loss_func(output,label)
    validloss += loss.item() 
    val_loss.append(validloss)
    accuracy.append((label==torch.argmax(output.data,1)).sum().item() / label.shape[0])

  print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f} \t valid_accuracy: {:.2f}'.format(epoch, trainloss, validloss,sum(accuracy)/len(accuracy)))
    
  torch.save(model.state_dict(), '/content/drive/MyDrive/jackfruit_mango_classifier/model.ckpt')

model.eval()
i=0
accuracy=[]
with torch.no_grad():
  correct=0
  total=0
  for data,label in val_data_loader:
    data = data.to(device)
    label = label.to(device)
   # print("label=",label)
    i+=1
    output = model(data)
    #print("output",output.data)
    x,predicted = torch.max(output.data,1)
    accuracy.append((label==torch.argmax(output.data,1)).sum().item() / label.shape[0])
        
    print('Accuracy:'+ str(sum(accuracy)/len(accuracy)))
    #print(data,predicted)

#saving trained model to drive
model_save_name = 'jango_classifier.pt'
path_model = "/content/drive/MyDrive/jackfruit_mango_classifier/" + model_save_name
torch.save(model.state_dict(), path_model)

# Commented out IPython magic to ensure Python compatibility.
#visualise fitting
# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'

plt.plot(train_loss, label='Training loss')
plt.plot(val_loss, label='Validation loss')
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend(frameon=False)

#gettimg images from url and testing
urll = "https://thumbs.dreamstime.com/b/fruits-mango-scientific-name-mangifera-indica-anacardiaceae-ripened-fruit-piled-up-sale-thiruvananthapuram-kerala-india-48649430.jpg"

from imageio import imread
image1 = imread(urll,pilmode="RGB")
image1 = Image.fromarray(image1)
plt.imshow(image1)

model.eval()

class_list ={0:'chakka', 1:'maanga'}
detransform= transforms.Compose([
    transforms.Normalize(mean = -mean/std, std = 1./std),
    transforms.ToPILImage()
])
transform1 = transforms.Compose([                                                                                           
    transforms.Resize((32,32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std)])

image=transform1(image1)
image = image.unsqueeze(0).to(device)

with torch.no_grad():
        
        output = model(image)
        output = nn.Softmax(dim=1)(output)[0]*100
        print(output)
        max,id=torch.max(output,0)
        print(max,id,output[id])
        id = output.argmax().data.item()
        oclass = list(class_list.keys())[id]
        output = output.int().data.cpu().numpy()

        display(detransform(image.squeeze(0)))
        if(max>85):
          print(class_list[oclass], ':', output[id], '%')
        else:
          print("image not mango or jackfruit")