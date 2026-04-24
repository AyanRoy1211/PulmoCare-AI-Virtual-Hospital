
from torchvision.models import resnet18,resnet34,resnet50
from torchvision.models import ResNet50_Weights, ResNet34_Weights,ResNet18_Weights
from torchsummary import summary
import torch.nn as nn
import torch


def resnetmodel18(input,device='cpu', parallel=True, pretrain = True):

    if pretrain:
        resnet_model = resnet18(weights=ResNet18_Weights.DEFAULT)
    else:
        resnet_model = resnet18(weights= None)

    # print(resnet_model)
    resnet_model.fc = nn.Sequential(nn.Dropout(0.5),nn.Linear(512,128),nn.ReLU(inplace=True),nn.Dropout(0.5),nn.Linear(128,1))
    resnet_model.conv1 = nn.Conv2d(input, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3,3), bias=False)
    
    if parallel:
        resnet_model = nn.DataParallel(resnet_model)
    resnet_model = resnet_model.to(device)

    return resnet_model

def resnetmodel34(input,device='cpu', parallel=True, pretrain = True):
    
    if pretrain:
        resnet_model = resnet34(weights=ResNet34_Weights.DEFAULT)
    else:
        resnet_model = resnet34(weights= None)
   
    resnet_model.fc = nn.Sequential(nn.Dropout(0.5),nn.Linear(512,128),nn.ReLU(inplace=True),nn.Dropout(0.5),nn.Linear(128,1))
    resnet_model.conv1 = nn.Conv2d(input, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3,3), bias=False)
    
    if parallel:
        resnet_model = nn.DataParallel(resnet_model)
    resnet_model = resnet_model.to(device)

    return resnet_model

def resnetmodel50(input,device='cpu', parallel=True, pretrain = True):

    if pretrain:
        resnet_model = resnet50(weights=ResNet50_Weights.DEFAULT)
    else:
        resnet_model = resnet50(weights= None)
    # print(resnet_model)
    resnet_model.fc = nn.Sequential(nn.Dropout(0.5),nn.Linear(512,128),nn.ReLU(inplace=True),nn.Dropout(0.5),nn.Linear(128,1))
    resnet_model.conv1 = nn.Conv2d(input, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3,3), bias=False)
    
    if parallel:
        resnet_model = nn.DataParallel(resnet_model)
    resnet_model = resnet_model.to(device)

    return resnet_model


def lr_layers_different(model, x, lr1, lr2):
    lr1 = lr1
    lr2 = lr2

    if x == 'onlyfc':
        for name, param in model.named_parameters():
    
            if not 'fc' in name:
                param.requires_grad = False
        
    elif x == 'allayers':
        
        #all layers with decreasing rates
        layer_names = []
        for idx, (name, param) in enumerate(model.named_parameters()):
            layer_names.append(name)
            print(f'{idx}: {name}')
        
        layer_names.reverse()
        print(layer_names)
        lr      = 1e-2
        lr_mult = 0.9

            # placeholder
        parameters      = []
        prev_group_name = layer_names[0].split('.')[0]

        # store params & learning rates
        for idx, name in enumerate(layer_names):
            
            # parameter group name
            cur_group_name = name.split('.')[0]
            
            # update learning rate
            if cur_group_name != prev_group_name:
                lr *= lr_mult
            prev_group_name = cur_group_name
            
            # display info
            print(f'{idx}: lr = {lr:.6f}, {name}')
            
            # append layer parameters
            parameters += [{'params': [p for n, p in model.named_parameters() if n == name and p.requires_grad],
                            'lr':     lr}]

            #different groups with different rates
    elif x == 'subgroups':

        group1 = ['fc']
        group2 =  ['conv','bn','layer1','layer2','layer3','layer4']
        parameters = []
        for n,p in model.named_parameters():
            #print(n)
            if any(x in n for x in group1):
                #print('grp1',n)
                parameters +=[{'params': p,
                            'lr':     lr1}]
            elif any(x in n for x in group2):
                #print('grp2',n)
                #p.requires_grad = False
                parameters +=[{'params': p,
                            'lr':     lr2}]         
    
    return parameters
    
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = resnetmodel50(1,device, parallel=False, pretrain = True)
    params = lr_layers_different(model,'subgroups',0.01,0.01)

    model =resnetmodel18(1,device, parallel=False, pretrain = True)
    model.fc = nn.Sequential(nn.Dropout(0.5),nn.Linear(512,128),nn.ReLU(inplace=False),nn.Dropout(0.5),nn.Linear(128,1))
    names = []
    for name, module in model.named_modules():
        if hasattr(module, 'relu'):
            module.relu = nn.ReLU(inplace=False)
   
            
    print(model)   
    model.eval()
    
    


