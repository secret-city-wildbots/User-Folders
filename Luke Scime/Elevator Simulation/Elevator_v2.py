# Author: Luke Scime
# Date: 2019-01-20
# Purpose: elevator simulation
#------------------------------------------------------------------------------

# Import libraries
from IPython import get_ipython; # needed to run magic commands
ipython = get_ipython(); # needed to run magic commands
import cv2;
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas;
from matplotlib.figure import Figure;
import numpy as np;
import matplotlib.pyplot as plt;
from PIL import ImageTk,Image,ImageDraw,ImageFont; # tk-integrated image display functionality 
import tkinter as tk; # file UI
import threading; # allows threads to be spawned

# Close previous windows
cv2.destroyAllWindows();
plt.close('all');

# Change Environment settings
ipython.magic('matplotlib qt'); # display figures in a separate window
plt.rcParams.update({'font.size': 24}); # change the default font size for plots
plt.rcParams.update({'figure.max_open_warning': False}); # disable warning about too opening too many figures - don't need that kind of negativity 

# GUI appearance settings
guiColor_background = '#%02x%02x%02x' % ((245,245,245)); # color for the GUI background
guiColor_live = '#%02x%02x%02x' % ((255,255,255)); # color for active input fields
guiColor_darkfont = '#%02x%02x%02x' % ((0,0,0)); # color for font on light backgrounds
guiColor_lightfont = '#%02x%02x%02x' % ((255,255,255)); # color for font on dark backgrounds
guiColor_enabled = '#%02x%02x%02x' % ((0,121,52)); # color for enabled buttons
guiColor_quit = '#%02x%02x%02x' % ((136,51,46)); # color for the "Quit" and "Return" buttons
guiFont_large = int(np.ceil(14)); # auto-scaled large font size
guiFont_pretty = 'Arial'; # standard font type

# Global variables
global theta_start;
global h_start;
theta_start =0;
h_start = 0;

#------------------------------------------------------------------------------

def actionExit(*args):
    
    guiwindow.quit();
    guiwindow.destroy();

#------------------------------------------------------------------------------

def actionMove():
    
    global theta_start,h_start;
    
    def tcallback():
        
        global theta_start,h_start;
        
        # Initialize
        flag_moving = True; 
        theta = theta_start;
        h = h_start;
        
        while(flag_moving):
        
            # Calculate the goal elevator and arm positions
            theta_goal = np.arccos((targetx - L1)/L2);
            h_goal = targety - L2*np.sin(theta_goal);
            print(theta_goal)
            
            # Modify the goal based on rules
            if(h_goal<h_min):
                theta_goal = -theta_goal;
                h_goal = targety - L2*np.sin(theta);
            h_goal = min(h_goal,h_max);
            h_goal = max(h_goal,h_min);
            
            
            
            
            
            
            # Calculate the position update
            theta += kp_theta*(theta_goal-theta);
            h += kp_h*(h_goal-h);
            
            # Calculate the arm display coordinates
            armx = np.array([0,(0+L1),L1+(L2*np.cos(theta))]);
            army = np.array([h,h,h+(L2*np.sin(theta))]);
        
            # Create the dummy figure
            h_fig = Figure(figsize=[5,5]);
            canvas = FigureCanvas(h_fig);
            ax = h_fig.gca();
            ax.imshow(mask_master);
#            ax.scatter(keepout_robot_x,keepout_robot_y,color='r');
#            ax.scatter(keepout_relative_x,keepout_relative_y,color='y');
            ax.scatter(targetx*scale,targety*scale,color='g');
            ax.plot(armx*scale,army*scale,color='b',ls='-',lw=4);
            ax.set_xlim(0,mask_master.shape[1]);
            ax.set_ylim(0,mask_master.shape[0]);
            ax.set_xlabel('x (in)');
            ax.set_ylabel('y (in)');
            h_fig.tight_layout();
            
            # Convert the dummy plot into an image
            canvas.draw(); # draw the canvas and cache the renderer
            armplot = np.fromstring(canvas.tostring_rgb(), dtype='uint8');
            
            # Reshape, resize, and recolor the background of the screenshot of the plot
            [width,height] = h_fig.get_size_inches()*h_fig.get_dpi();
            armplot = armplot.reshape(int(height),int(width),3);
            armplot[(armplot[:,:,0]==255)&(armplot[:,:,1]==255)&(armplot[:,:,2]==255)] = 245; # off-white background
            resizeFactor = min((graphicDisplaySize[1]/armplot.shape[1]),(graphicDisplaySize[0]/armplot.shape[0]));
            lossplot_small = cv2.resize(armplot,(int(armplot.shape[1]*resizeFactor),int(armplot.shape[0]*resizeFactor)));
            
            # Push the loss plot to the GUI
            I_lossplot = Image.fromarray(lossplot_small);
            I_lossplot = ImageTk.PhotoImage(I_lossplot,master=guiwindow);
            image_on_canvas = graphic1.create_image(0,0,anchor=tk.NW);
            graphic1.itemconfig(image_on_canvas,image=I_lossplot);
            graphic1.image = I_lossplot;
            guiwindow.update_idletasks();
            
            # Check for completion and apply time delay
            plt.pause(0.1);
            if((abs(h_goal-h)<1.0)&(abs(theta_goal-theta)<0.017)):
                flag_moving = False;
                
                
                
            
            
            
        # Update the start position
        theta_start = theta;
        h_start = h;

        # Unblock the GUI
        buttons[1].configure(bg=guiColor_enabled,state=tk.NORMAL);

    # Block the GUI
    buttons[1].configure(bg=guiColor_background,state=tk.DISABLED);
    
    # Robot dimensions
    L1 = 12; # [inches]
    L2 = 24; # [inches]
    theta_min = -np.pi/2; # [rad]
    theta_max = np.pi/2; # [rad]
    h_min = 7; # [inches]
    h_max = 84;  # [inches]
    y_min = 5; # [inches]
    
    # Motion settings
    kp_theta = 0.25;
    kp_h = 0.25;

    # Get the goal coordinates
    try: targetx = float(inputBoxes[0].get());
    except: targetx = 30;
    try: targety = float(inputBoxes[1].get());
    except: targety = 40;
    
    # Calculate reachable locations
    x_reach = [];
    y_reach = [];
    for i in np.linspace(h_min,h_max,100):
        for j in np.linspace(theta_min,theta_max,100):
            x = L1+L2*np.cos(j);
            y = i+L2*np.sin(j);
            if(y>y_min):
                x_reach.append(x);
                y_reach.append(y);
            
    # Remove unreachable positions (does NOT handle intermediate or bad arm positions)
    targetx = min(targetx,L1+L2);
    targetx = max(targetx,L1);
    targety = max(targety,y_min);
    theta = np.arccos((targetx - L1)/L2);
    h_max_eff = h_max+L2*np.sin(theta);
    targety = min(targety,h_max_eff);
    
    # Launch a thread
    t = threading.Thread(target=tcallback); # initialize thread
    t.start(); # spawn to a new thread

#------------------------------------------------------------------------------

# Scale
scale = 10; # [pixels/in]
    
# Robot dimensions
robotHeight = 96; # [inches]
L1 = 12; # [inches]
L2 = 24; # [inches]
theta_min = -0.5*np.pi; # [rad]
theta_max = 0.5*np.pi; # [rad]
h_min = 20; # [inches]
h_max = 80;  # [inches]

# Load the robot keep-out mask
img_robot = cv2.imread('keepout.png');
img_robot = cv2.cvtColor(img_robot,cv2.COLOR_BGR2RGB);
maskHeight = int(scale*robotHeight);
maskWidth = int((img_robot.shape[1]/img_robot.shape[0])*maskHeight);
img_robot = cv2.resize(img_robot,(maskWidth,maskHeight));
mask_robot_small = img_robot[:,:,1]!=255;
mask_robot = np.zeros((int(1.2*maskHeight),int(1.2*maskHeight)),bool);

# Initialize the master keep-out mask
mask_master = 255*np.ones((int(1.2*maskHeight),int(1.2*maskHeight),3),np.uint8);

# Shift the robot keep-out mask
mask_robot[(mask_master.shape[0]-maskHeight):mask_master.shape[0],0:maskWidth] = mask_robot_small;

# Calculate the relative keep-out mask
mask_relative = np.ones((mask_master.shape[0],mask_master.shape[1]),bool);
for i in range(0,mask_master.shape[1],1):
    for j in range(0,mask_master.shape[0],1):
        x = i/scale; # [in]
        y = (mask_master.shape[1] - j)/scale; # [in]
        try:
            theta = np.arccos((x - L1)/L2);
            if(np.isnan(theta)==False):
                h1 = y - L2*np.sin(theta);
                h2 = y - L2*np.sin(-theta);
                if((h1>h_min)&(h1<h_max)):
                    if(theta<theta_max):
                        mask_relative[j,i] = False;
                elif((h2>h_min)&(h2<h_max)):
                    if(-theta>theta_min):
                        mask_relative[j,i] = False;
        except: pass;

# Update the master keep-out mask
mask_master[mask_robot,1] = 0;
mask_master[mask_robot,2] = 0;
mask_master[mask_relative&(mask_robot==False),2] = 0;
mask_master = np.flip(mask_master,0);
#keepout_robot_x = np.where(mask_robot==True)[1]/scale;
#keepout_robot_y = (mask_master.shape[0]-np.where(mask_robot==True)[0])/scale;
#keepout_relative_x = np.where(mask_relative&(mask_robot==False)==True)[1]/scale;
#keepout_relative_y = (mask_master.shape[0]-np.where(mask_relative&(mask_robot==False)==True)[0])/scale;

#------------------------------------------------------------------------------

# Window sizes
scrnW = 1920; # [pixels] width of the computer monitor
scrnH = 1080; # [pixels] height of the computer monitor
winW =  0.5*scrnW;
winH = 0.5*scrnH;
    
# Open the GUI window
guiwindow = tk.Tk();
guiwindow.title('Deep Space - Elevator Simulator');
guiwindow.geometry(str(int(winW))+'x'+str(int(winH)));
guiwindow.configure(background=guiColor_background);
guiwindow.resizable(width=False, height=False);

# Set up the logos and graphics
graphicDisplaySize = np.array([500,500]);
graphic1 = tk.Canvas(guiwindow,width=graphicDisplaySize[0],height=graphicDisplaySize[1]);
I_graphic1 = Image.open('graphic_default.png');
I_graphic1 = I_graphic1.resize((int(graphicDisplaySize[1]),int(graphicDisplaySize[0])),Image.ANTIALIAS);
I_graphic1 = ImageTk.PhotoImage(I_graphic1,master=guiwindow);
graphic1.create_image(0,0,anchor=tk.NW,image=I_graphic1);

# Set up the dynamic text labels
dynamicLabels = [];
dynamicLabels.append(tk.Label(guiwindow,text='x (in)',fg=guiColor_darkfont,bg=guiColor_background,font=(guiFont_pretty,guiFont_large),height=1,width=25,anchor='w'));
dynamicLabels.append(tk.Label(guiwindow,text='y (in)',fg=guiColor_darkfont,bg=guiColor_background,font=(guiFont_pretty,guiFont_large),height=1,width=25,anchor='w'));

# Set up the main GUI buttons
buttons = [];
buttons.append(tk.Button(guiwindow,text='Exit',fg=guiColor_lightfont,bg=guiColor_quit,font=(guiFont_pretty,guiFont_large),height=1,width=10,command=actionExit));
buttons.append(tk.Button(guiwindow,text='Move',fg=guiColor_lightfont,bg=guiColor_enabled,font=(guiFont_pretty,guiFont_large),height=1,width=10,command=actionMove));

# Set up text entry boxes
inputBoxes = [];
inputBoxes.append(tk.Entry(guiwindow,fg=guiColor_darkfont,bg=guiColor_live,font=(guiFont_pretty,guiFont_large)));
inputBoxes.append(tk.Entry(guiwindow,fg=guiColor_darkfont,bg=guiColor_live,font=(guiFont_pretty,guiFont_large)));

# Place all active elements
graphic1.place(x=0.05*winW,y=0.05*winH);
buttons[0].place(x=0.85*winW,y=0.05*winH);
buttons[1].place(x=0.70*winW,y=0.46*winH);
dynamicLabels[0].place(x=0.70*winW,y=0.25*winH);
dynamicLabels[1].place(x=0.70*winW,y=0.35*winH);
inputBoxes[0].place(x=0.70*winW,y=0.30*winH);
inputBoxes[1].place(x=0.70*winW,y=0.40*winH);

# Run the GUI
guiwindow.mainloop();

#------------------------------------------------------------------------------