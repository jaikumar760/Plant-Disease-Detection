### 1. Imports and class names setup ###
import torch
from PIL import Image
from python_scripts import effnet_b0_model

from timeit import default_timer as timer 
from typing import Tuple,Dict


# Setup the class_names as the list
with open("python_scripts/class_names.txt", "r") as f:
    class_names = [disease.strip() for disease in f.readlines()]

### 2. Model and transforms prepration ###

# create model
effnetb0, effnetbo_transforms = effnet_b0_model.create_effnet_b0_model(
    num_classes = len(class_names)
)

# Load saved model weight
effnetb0.load_state_dict(
    torch.load(
        f= "saved_models/efficient_net_1.pth",
        # map_location=torch.device("cpu") # load to cpu
    )
)

### 3. Predict functions ###

#Create the predict fn
def predict(img) -> Tuple[Dict, float]:
  """
  Transform ans performs a prediction on img and return prediction and time taken
  """
  # Opening image
#   img = Image.open(img)

  # Start the timer
  start_time = timer()

  # Transform the target_img and add batch dimension
  img = effnetbo_transforms(img).unsqueeze(0)

  # Put the model into evaluation model and turn on inference mode
  effnetb0.eval()
  with torch.inference_mode():
    # passing the transformed img through the model
    pred_probs = torch.softmax(effnetb0(img), dim=1)
  
  # Get the class with the highest probability
  highest_prob_class_idx = torch.argmax(pred_probs, dim=1).item()
  highest_prob = pred_probs[0][highest_prob_class_idx].item()
  
  # Create a dictionary with the highest probability class and its value
  prediction = {class_names[highest_prob_class_idx]: highest_prob}

  # Calculate the prediction time
  pred_time = round(timer() - start_time, 5)

  # return the prediction dictionary and prediction time
  return prediction, pred_time











