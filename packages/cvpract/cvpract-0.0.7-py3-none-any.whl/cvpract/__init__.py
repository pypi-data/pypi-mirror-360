def show():
    print(r"""
PRACTICAL 1
Program 1: To show the image: 
import cv2 
img = cv2.imread("bheem.jpg") cv2.imshow("Output Image", img) 
 

Program 2: To convert rgb image to grayscale image: 
Method 1: 
import cv2 
img = cv2.imread("bheem.jpg") 
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) cv2.imshow("Original Image", img) cv2.imshow("Grayscale Image", gray_image) 
 

Method 2: 
import cv2 
img = cv2.imread("bheem.jpg") 
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) cv2.imshow("Original Image", img) 
converted_image = cv2.imread("bheem.jpg", cv2.IMREAD_GRAYSCALE) cv2.imshow("Converted Image", converted_image) 
 

Program 3: To display multiple images on same screen: 
import cv2 
import matplotlib.pyplot as plt img = cv2.imread("bheem.jpg") 
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
#cv2.imshow("Original Image", img) 
#cv2.imshow("GrayScale Image", gray_image) 
#Image1 
plt.figure(figsize = (10,5)) plt.subplot(1,2,2) plt.imshow(img) 
#plt.imshow(img, cmap = 'gray') plt.title('Original Image') plt.axis('off') 
#Image2 
plt.subplot(1,2,1) plt.imshow(gray_image) 
#plt.imshow(gray_image, cmap = 'gray') plt.title('GrayScale Image') plt.axis('off') plt.show() 




PRACTICAL 2 

TO CONVERT ORIGINAL IMAGE TO BRIGHTENED, DARK, ROTATE AND TRANSLATE

import cv2 
from scipy import ndimage import matplotlib.pyplot as plt import numpy as np 
#Load the image 
image = cv2.imread("C:/Users/admin/Desktop/Nupur/flower.jpg")  
#Increase Brightness 
image_float = image.astype(float)  
# Increase the brightness (values greater than 1 between 2 to 5) brightness_factor = 2.5  # Increase or decrease this value as needed brightened_image = image_float * brightness_factor  
#Decrease the Brightness (values between 0 and 1) 
brightness_factor1 = 0.4  # Increase or decrease this value as needed dark_image = image_float * brightness_factor1  
# Clip the pixel values to the valid range [0, 255] brightened_image = np.clip(brightened_image, 0, 255) dark_image = np.clip(dark_image, 0, 255)  
# Convert the image back to unsigned 8-bit integers brightened_image = brightened_image.astype(np.uint8) dark_image = dark_image.astype(np.uint8)  
# Image Rotation 
image_rotate = ndimage.rotate(image,45)  
#Image translation 
height, width = image.shape[:2] #Store height and Weight T = np.float32([[1, 0, 100], [0, 1, 200]]) img_trans = cv2.warpAffine(image, T, (width, height))  
#Show images 
#cv2.imshow("Original Image",image) 
#cv2.imshow("Brightened image",brightened_image) 
#cv2.imshow("Dark image",dark_image) 
#cv2.imshow("Rotated image",image_rotate) 
#cv2.imshow("Translated image",img_trans) 
plt.figure(figsize = (10,5)) 
#Image1 
plt.subplot(2,3,1) plt.imshow(image) plt.title('Original Image') plt.axis('off') 
#Image2 
plt.subplot(2,3,2) plt.imshow(brightened_image) plt.title('Brightened Image') plt.axis('off')  
#Image3 
plt.subplot(2,3,3) plt.imshow(dark_image) plt.title('Dark Image') plt.axis('off') 
#Image4 
plt.subplot(2,3,4) plt.imshow(image_rotate) plt.title('Rotated Image') plt.axis('off') 
#Image5 
plt.subplot(2,3,5) plt.imshow(img_trans) plt.title('Translated Image') plt.axis('off') plt.show() 
#cv2.waitKey(0) 
#cv2.destroyAllWindows() 


HISTOGRAM POLTTING

import cv2 import matplotlib.pyplot as plt 
# Step 2: Read the image 
image = cv2.imread("C:/Users/admin/Desktop/Nupur/sunset.jpg") 
# Step 3: Convert to grayscale (optional) gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
# Step 4: Calculate the histogram 
hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256]) 
# Step 5: Plot the histogram (optional) plt.plot(hist) 
plt.title('Histogram of Grayscale Image') plt.xlabel('Pixel Intensity') plt.ylabel('Frequency') plt.show() 


HISTOGRAM EQUALIZATIONN

#import required Libraries import cv2 from scipy import ndimage import numpy as np import matplotlib.pyplot as plt 
#Load the image 
image = cv2.imread("C:/Users/admin/Desktop/Nupur/sunset.jpg") 
#Convert to Grayscale 
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
#Perform Histogram Equalization equalized_img = cv2.equalizeHist(gray) 
#cv2.imshow("Original Gray Image",gray) 
#cv2.imshow("Histogram Equalized Image",equalized_img) 
plt.figure(figsize = (10,5)) 
#Image1 
plt.subplot(2,2,1) plt.imshow(gray, cmap = 'gray') plt.title('Original Gray Image') plt.axis('off') 
#Image2 
plt.subplot(2,2,2) 
plt.imshow(equalized_img, cmap = 'gray') 
plt.title('Histogram Equalized Image') plt.axis('off') plt.show() 
#cv2.waitKey(0) 
#cv2.destroyAllWindows() 




PRACTICAL 3

LOW FILTER IMAGE
 
import cv2 import numpy as np import matplotlib.pyplot as plt  
def apply_average_filter(image_path, kernel_size): 
    # Read the image 
    image = cv2.imread(image_path) 
    # Apply the average filter 
filtered_image = cv2.blur(image, (kernel_size, kernel_size)) 
    return filtered_image 
if __name__ == "__main__": 
    # Input image path and kernel size 
    input_image_path = "C:/Users/admin/Desktop/Nupur/scenery.jpg"     kernel_size = 10  # You can adjust the kernel size as needed. 
    # Apply the average filter 
    filtered_image = apply_average_filter(input_image_path, kernel_size) 
    # Display the original and filtered images 
    #cv2.imshow("Original Image", cv2.imread(input_image_path)) 
    #cv2.imshow("Filtered Image", filtered_image)
    #Image1     plt.figure(figsize = (10,5))     plt.subplot(1,2,2) 
    #plt.imshow(cv2.imread(input_image_path))     plt.imshow(cv2.imread(input_image_path), cmap = 'gray')     plt.title('Original Image')     plt.axis('off') 
    #Image2     plt.subplot(1,2,1)     #plt.imshow(filtered_image)     plt.imshow(filtered_image, cmap = 'gray')     plt.title('Filtered Image')     plt.axis('off')     plt.show() 
    # Wait for a key press and then close the windows     cv2.waitKey(0) 
cv2.destroyAllWindows() 
 



GAUSSIAN FILTER 
 
import cv2 
import matplotlib.pyplot as plt 
def apply_weighted_average_filter(image_path, kernel_size, sigmaX): 
    # Read the image     image = cv2.imread(image_path) 
    # Apply the weighted average filter (Gaussian blur) 
    filtered_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX):
    return filtered_image   
if __name__ == "__main__": 
    # Input image path, kernel size, and sigmaX (standard deviation in X direction)     input_image_path = "C:/Users/admin/Desktop/Nupur/scenery.jpg"     kernel_size = 5  # You can adjust the kernel size as needed. 
    sigmaX = 4  # You can adjust the sigmaX value for the Gaussian kernel. 
    # Apply the weighted average filter 
    filtered_image = apply_weighted_average_filter(input_image_path, kernel_size, sigmaX) 
    # Display the original and filtered images 
    #cv2.imshow("Original Image", cv2.imread(input_image_path)) 
    #cv2.imshow("Filtered Image", filtered_image) 
    #Image1 
    plt.figure(figsize = (10,5))     plt.subplot(1,2,2) 
    #plt.imshow(cv2.imread(input_image_path))    
 plt.imshow(cv2.imread(input_image_path), cmap = 'gray')
 plt.title('Original Image') 
    plt.axis('off') 
    #Image2     plt.subplot(1,2,1)    
 #plt.imshow(filtered_image)   
  plt.imshow(filtered_image, cmap = 'gray')    
 plt.title('Filtered Image')     
plt.axis('off')    
 plt.show() 
    # Wait for a key press and then close the windows     cv2.waitKey(0)     cv2.destroyAllWindows() 


 
MEDIAN FILTER 

 
import cv2 import numpy as np import matplotlib.pyplot as plt   
# Load the image 
image_path = "C:/Users/admin/Desktop/Nupur/scenery.jpg" original_image = cv2.imread(image_path) 
# Apply median filter with specified kernel size kernel_size = 3  # Adjust this value to change the filter size median_filtered_image = cv2.medianBlur(original_image, kernel_size) 
# Display the original and filtered images 
#cv2.imshow('Original Image', original_image) 
#cv2.imshow('Median Filtered Image', median_filtered_image) 
#Image1 
plt.figure(figsize = (10,5)) plt.subplot(1,2,2) plt.imshow(original_image) 
#plt.imshow(original_image, cmap = 'gray') plt.title('Original Image') plt.axis('off') 
#Image2 
plt.subplot(1,2,1) 
plt.imshow(median_filtered_image) 
#plt.imshow(median_filtered_image, cmap = 'gray') plt.title('Median Filtered Image') plt.axis('off') plt.show() 
# Wait for a key press and close the windows cv2.waitKey(0) cv2.destroyAllWindows() 



PRACTICAL 3B


SOBEL FILTER 
 
import cv2 import numpy as np import matplotlib.pyplot as plt   
# Load the image 
image_path = 'C:/Users/admin/Desktop/Nupur (M.Sc.IT)/CV Practical/Practical 4/Flower.jpg' original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) 
# Check if the image was loaded successfully if original_image is None: 
    print("Error loading the image.") else: 
    # Apply Sobel filter in the x and y directions 
    sobel_x = cv2.Sobel(original_image, cv2.CV_64F, 1, 0, ksize=3)     sobel_y = cv2.Sobel(original_image, cv2.CV_64F, 0, 1, ksize=3) 
    # Convert the results to absolute values and then to 8-bit     sobel_x = cv2.convertScaleAbs(sobel_x)     sobel_y = cv2.convertScaleAbs(sobel_y) 
    # Combine the Sobel images to get the gradient magnitude     gradient_magnitude = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0) 
    # Display the original image and the gradient magnitude 
    #cv2.imshow('Original Image', original_image) 
    #cv2.imshow('Gradient Magnitude', gradient_magnitude) 
    #Image1 
    plt.figure(figsize = (10,5))    
 plt.subplot(1,2,2) 
    #plt.imshow(original_image)     
plt.imshow(original_image, cmap = 'gray')     
plt.title('Original Image')    
 plt.axis('off') 
    #Image2    
 plt.subplot(1,2,1) 
    #plt.imshow(gradient_magnitude)     
plt.imshow(gradient_magnitude, cmap = 'gray')    
 plt.title('Gradient Magnitude')    
 plt.axis('off')    
 plt.show() 
    # Wait for a key press and close the windows     cv2.waitKey(0)     cv2.destroyAllWindows() 



 PREWIT FILTER 
 
import numpy as np import cv2 
import matplotlib.pyplot as plt  
def apply_prewitt_filter(image_path): 
    # Read the image in grayscale 
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)     if img is None: 
        print("Error: Unable to load image.")         return 
    # Define Prewitt operator kernels 
    prewitt_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)     prewitt_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32) 
    # Apply filters 
    grad_x = cv2.filter2D(img, -1, prewitt_x)     grad_y = cv2.filter2D(img, -1, prewitt_y) 
    # Combine gradients 
    gradient_magnitude = cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32)) 
    gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8) 
    # Display results     plt.figure(figsize=(10, 5)) 
    plt.subplot(1, 3, 1), plt.imshow(img, cmap='gray'), plt.title('Original Image')     plt.subplot(1, 3, 2), plt.imshow(grad_x, cmap='gray'), plt.title('Prewitt X')     plt.subplot(1, 3, 3), plt.imshow(grad_y, cmap='gray'), plt.title('Prewitt Y')     plt.figure(figsize=(5, 5)) 
    plt.imshow(gradient_magnitude, cmap='gray'), plt.title('Gradient Magnitude')     plt.show() 
# Example usage 
apply_prewitt_filter('C:/Users/admin/Desktop/Nupur (M.Sc.IT)/CV Practical/Practical 4/Flower.jpg') 
 


LAPLACIAN FILTER
 
import cv2 import numpy as np import matplotlib.pyplot as plt   
# Read the image in grayscale 
image = cv2.imread('C:/Users/admin/Desktop/Nupur (M.Sc.IT)/CV Practical/Practical 4/Flower.jpg', cv2.IMREAD_GRAYSCALE) 
# Apply the Laplacian filter 
laplacian = cv2.Laplacian(image, cv2.CV_64F) 
# Convert the result to uint8 
laplacian = np.uint8(np.absolute(laplacian)) 
# Display the original and filtered images plt.figure(figsize=(10, 5)) plt.subplot(1, 2, 1) plt.title("Original Image") plt.imshow(image, cmap='gray') plt.axis('off') 
plt.subplot(1, 2, 2) 
plt.title("Laplacian Filtered Image") plt.imshow(laplacian, cmap='gray') plt.axis('off') 
 plt.show() 




PRACTICAL 4

RGB IMAGE TO BINARY IMAGE

import cv2 import numpy as np import matplotlib.pyplot as plt  
# Load the grayscale image 
image = cv2.imread('cartoon.jpeg', cv2.IMREAD_GRAYSCALE) 
total=np.sum(image) w,h=image.shape avg=int(total/(w*h)) 
# Apply thresholding 
threshold_value = avg  # You can adjust this value 
_, thresholded_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY) 
# Display the thresholded image 
#cv2.imshow('Thresholded Image', thresholded_image) 
#Image1  
plt.figure(figsize = (10,5))  plt.subplot(1,2,2)  #plt.imshow(image)  plt.imshow(image, cmap = 'gray')  plt.title('Original Image')  plt.axis('off')  
#Image2  plt.subplot(1,2,1)  
#plt.imshow(thresholded_image)  plt.imshow(thresholded_image, cmap = 'gray')  plt.title('Thresholded Image')  plt.axis('off')  plt.show() 
cv2.waitKey(0) cv2.destroyAllWindows() 



 PRACTICAL 6

MORPHOLOGICAL OPERATIONS

import cv2 import numpy as np 
from skimage.morphology import skeletonize import matplotlib.pyplot as plt 
# Read the image 
image = cv2.imread("doraemon.jpg") 
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
gray_image = cv2.imread("doraemon.jpg", cv2.IMREAD_GRAYSCALE) 
_,binary_image = cv2.threshold(rgb_image, 127, 255, cv2.THRESH_BINARY) 
# Create a kernel 
kernel = np.ones((5,5), np.uint8) 
# Apply morphological operations 
erosion = cv2.erode(rgb_image, kernel, iterations=1) 
dilation = cv2.dilate(rgb_image, kernel, iterations=1) 
opening = cv2.dilate(erosion, kernel, iterations=1)
 closing = cv2.erode(dilation, kernel, iterations=1) 
binary = binary_image // 255  # Normalize to 0 and 1 skeleton = skeletonize(binary)  # Apply thinning 
# Convert back to uint8 (0 and 255) skeleton = (skeleton * 255).astype(np.uint8) 
#Image1  
plt.figure(figsize = (10,5))  
plt.subplot(2,4,1)  plt.imshow(rgb_image)  
#plt.imshow(image, cmap = 'gray')  plt.title('Original Image')  plt.axis('off') 
#Image2 
plt.subplot(2,4,2)  #plt.imshow(gray_image)  plt.imshow(gray_image, cmap = 'gray')  plt.title('GrayScale Image')  plt.axis('off') 
#Image3 
plt.subplot(2,4,3)  plt.imshow(binary_image)  
#plt.imshow(binary_image, cmap = 'gray') 
plt.title('Binary Image') 
 plt.axis('off') 
#Image4 
plt.subplot(2,4,4) 
 plt.imshow(erosion)  
#plt.imshow(erosion, cmap = 'gray') 
 plt.title('Eroded Image') 
 plt.axis('off') 
#Image5   
plt.subplot(2,4,5)  
plt.imshow(dilation)  #plt.imshow(dilation, cmap = 'gray')  plt.title('Dilated Image')  plt.axis('off') 
#Image6 
plt.subplot(2,4,6)  plt.imshow(opening)  #plt.imshow(opening, cmap = 'gray')  plt.title('Opening Image')  plt.axis('off') 
#Image7 
plt.subplot(2,4,7)  plt.imshow(closing)  #plt.imshow(closing, cmap = 'gray')  plt.title('Closing Image')  plt.axis('off') 
#Image8 
plt.subplot(2,4,8)  plt.imshow(skeleton)  
#plt.imshow(skeleton, cmap = 'gray')  plt.title('SKeleton Image')  plt.axis('off') plt.show() 



PRACTICAL 7


Shift Invariant Fourier Transform (SIFT) 

import cv2 
# Load two images 
image1 = cv2.imread("scenery_1.jpg") 
image2 = cv2.imread("scenery_2.jpg") 
# Convert images to grayscale 
gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY) 
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY) 
# Initialize SIFT detector sift = cv2.SIFT_create() 
# Detect keypoints and compute descriptors for both images keypoints1, 
descriptors1 = sift.detectAndCompute(gray1, None) keypoints2,
 descriptors2 = sift.detectAndCompute(gray2, None) 
# Initialize a Brute Force Matcher 
bf = cv2.BFMatcher() 
# Match descriptors between the two images matches = bf.knnMatch(descriptors1, descriptors2, k=2) 
# Apply ratio test to filter good matches
 good_matches = [] for m, n in matches:    
 if m.distance < 0.5 * n.distance:        
 good_matches.append(m) 
# Draw matches 
matched_image = cv2.drawMatches(image1, keypoints1, image2, keypoints2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS) 
# Display the matched image 
cv2.imshow('Key Point Matches', matched_image)
 cv2.waitKey(0) cv2.destroyAllWindows() 
 

PRACTICAL 8 

IMAGE STITCHING

import cv2 
 
image_paths=["img1.jpg","img2.jpg","img3.jpg","img4.jpg"] 
 
# initialized a list of images  imgs = [] 
for i in range(len(image_paths)):  
    imgs.append(cv2.imread(image_paths[i]))      imgs[i]=cv2.resize(imgs[i],(0,0),fx=0.4,fy=0.4) 
     
# showing the original pictures  cv2.imshow('1',imgs[0])  cv2.imshow('2',imgs[1]) cv2.imshow('3',imgs[2]) cv2.imshow('4',imgs[3]) stitchy=cv2.Stitcher.create()  
(dummy,output)=stitchy.stitch(imgs) 
 
if dummy != cv2.STITCHER_OK:  
  # checking if the stitching procedure is successful       print("stitching ain't successful")  else:   
    print('Your Panorama is ready!!!')  
# final output  
cv2.imshow('final result',output)  cv2.waitKey(0) 


PRACTICAL 9 

2D TO 3D VERSION 

from PIL import Image  import numpy as np 
def shift_image(img, depth_img, shift_amount=10):  
 	# Ensure base image has alpha   	img = img.convert("RGBA")   	data = np.array(img) 
 	# Ensure depth image is grayscale (for single value)   	depth_img = depth_img.convert("L")   	depth_data = np.array(depth_img)  
 	deltas = ((depth_data / 255.0) * float(shift_amount)).astype(int)  	# This creates the transparent resulting image.  
 	# For now, we're dealing with pixel data.  
 	shifted_data = np.zeros_like(data) 
 	height, width, _ = data.shape 
 	for y, row in enumerate(deltas):   	 	for x, dx in enumerate(row):   	 	 	if x + dx < width and x + dx >= 0:   	 	 	 	shifted_data[y, x + dx] = data[y, x]
 	# Convert the pixel data to an image.  
 	shifted_image = Image.fromarray(shifted_data.astype(np.uint8)) 
 	return shifted_image 
img = Image.open("2D_1.jpeg")  depth_img = Image.open("2D_2.jpeg")  
shifted_img = shift_image(img, depth_img, shift_amount=10)  shifted_img.show() 




PRACTICAL 10 


OBJECT DETECTION 

from ultralytics import YOLO import cv2 import math  
# start webcam cap = cv2.VideoCapture(0) cap.set(3, 640) cap.set(4, 480) 
# model 
model = YOLO("yolo-Weights/yolov8n.pt") 
# object classes 
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", 
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", 
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", 
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", 
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", 
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", 
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", 
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", 
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",               "teddy bear", "hair drier", "toothbrush" 
              ] 
while True: 
    success, img = cap.read()     results = model(img, stream=True) 
    # coordinates     for r in results:         boxes = r.boxes         for box in boxes:             # bounding box             x1, y1, x2, y2 = box.xyxy[0] 
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values 
            # put box in cam 
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3) 
            # confidence 
            confidence = math.ceil((box.conf[0]*100))/100             print("Confidence --->",confidence) 
            # class name             cls = int(box.cls[0]) 
            print("Class name -->", classNames[cls]) 
            # object details             org = [x1, y1] 
            font = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1             color = (255, 0, 0)             thickness = 2 
            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness) 
    cv2.imshow('Webcam', img)     if cv2.waitKey(1) == ord('q'): 
        break 
cap.release() cv2.destroyAllWindows() 





PRACTICAL 11

CAMERA CALIBRATION 

# Import required modules  import cv2  import numpy as np  import os  import glob 
  
# Define the dimensions of checkerboard  
CHECKERBOARD = (6, 9) 
  
# stop the iteration when specified  
# accuracy, epsilon, is reached or  
# specified number of iterations are completed.  
criteria = (cv2.TERM_CRITERIA_EPS + 
 	 	 	cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) 
  
# Vector for 3D points  threedpoints = [] 
  
# Vector for 2D points  twodpoints = [] 
  
# 3D points real world coordinates  objectp3d = np.zeros((1, CHECKERBOARD[0]  
 	 	 	 	 	* CHECKERBOARD[1],   	 	 	 	 	3), np.float32)  
objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],  
 	 	 	 	 	 	 	0:CHECKERBOARD[1]].T.reshape(-1, 2)  prev_img_shape = None 
  
# Extracting path of individual image stored  
# in a given directory. Since no path is  
# specified, it will take current directory  
# jpg files alone  images = glob.glob('*.jpg') 
  
for filename in images:  
 	image = cv2.imread(filename)  
 	grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
  
 	# Find the chess board corners  
 	# If desired number of corners are   	# found in the image then ret = true   	ret, corners = cv2.findChessboardCorners(  
 	 	 	 	 	grayColor, CHECKERBOARD,   	 	 	 	 	cv2.CALIB_CB_ADAPTIVE_THRESH   	 	 	 	 	+ cv2.CALIB_CB_FAST_CHECK +  	 	 	 	 	cv2.CALIB_CB_NORMALIZE_IMAGE) 
  
 	# If desired number of corners can be detected then,  
 	# refine the pixel coordinates and display  
 	# them on the images of checker board  
 	if ret == True:  
 	 	threedpoints.append(objectp3d) 
  
 	 	# Refining pixel coordinates   	 	# for given 2d points.  
 	 	corners2 = cv2.cornerSubPix(  
 	 	 	grayColor, corners, (11, 11), (-1, -1), criteria) 
  
 	 	twodpoints.append(corners2) 
  
 	 	# Draw and display the corners  
 	 	image = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, ret) 
  
 	cv2.imshow('img', image)   	cv2.waitKey(0) 
  
cv2.destroyAllWindows() 
  
h, w = image.shape[:2] 
  
# Perform camera calibration by  
# passing the value of above found out 3D points (threedpoints)  
# and its corresponding pixel coordinates of the  
# detected corners (twodpoints)  
ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(   	threedpoints, twodpoints, grayColor.shape[::-1], None, None) 
  
# Displaying required output  print(" Camera matrix:")  print(matrix) 
  
print("\n Distortion coefficient:")  print(distortion) 
  
print("\n Rotation Vectors:")  print(r_vecs) 





PRACTICAL 12 

IMAGE COLORIZATION 

import cv2 import os import numpy as np 
 
# Paths to load the model 
DIR = r"C:\Users\admin\Desktop\Nupur (M.Sc.IT)\CV Practical\Practical 12" 
PROTOTXT = os.path.join(DIR, r"colorization_deploy_v2.prototxt") 
POINTS = os.path.join(DIR, r"pts_in_hull.npy") 
MODEL = os.path.join(DIR, r"colorization_release_v2.caffemodel") 
  
# Load the Model print("Load model") 
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL) pts = np.load(POINTS) 
  
# Load centers for ab channel quantization used for rebalancing class8 = net.getLayerId("class8_ab") conv8 = net.getLayerId("conv8_313_rh") pts = pts.transpose().reshape(2, 313, 1, 1) net.getLayer(class8).blobs = [pts.astype("float32")] net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")] 
  
# Load the input image image = cv2.imread("car.jpg") scaled = image.astype("float32") / 255.0 lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB) 
  
resized = cv2.resize(lab, (224, 224)) 
L = cv2.split(resized)[0] 
L -= 50 
  
print("Colorizing the image") net.setInput(cv2.dnn.blobFromImage(L)) ab = net.forward()[0, :, :, :].transpose((1, 2, 0)) 
  
ab = cv2.resize(ab, (image.shape[1], image.shape[0])) 
  
L = cv2.split(lab)[0] 
colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2) 
  
colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR) colorized = np.clip(colorized, 0, 1) 
  
colorized = (255 * colorized).astype("uint8") 
  
cv2.imshow("Original", image) cv2.imshow("Colorized", colorized) cv2.waitKey(0) 
""")

