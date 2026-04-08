
import torch
import torchvision

def create_effnet_b0_model(num_classes:int=38,
                           seed:int=42):
    """
    Creates an Efficentnet_b0 feature extractor model and transforms.

    Args:
        num_classes(int, optional): number of classes in classifier head (DEFAULT:3)

        seed (int, optional) random seed value (DEFAULT:42) 

    Returns:
        model (torch.nn.Module): EffnetB0 model
        transforms (torchvision.transforms): EffnetB0 image transforms
    """

    # Creating effnet_b0 pretrained weights and transforms and model
    weights = torchvision.models.EfficientNet_B0_Weights.DEFAULT
    transforms = weights.transforms()
    model = torchvision.models.efficientnet_b0(weights=weights)

    # Freezing all the base layers
    for param in model.parameters():
        param.requires_grad = False
    
    # Changing the classifier head
    model.classifier = torch.nn.Sequential(
    torch.nn.Dropout(p=0.2, inplace=True),
    torch.nn.Linear(in_features=1280,
                    out_features=num_classes,
                    bias=True)
    )

    return model,transforms
    
