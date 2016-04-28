/*

  Rose Simulator and Lighter
  
  1. Simulator: draws rose shape on the monitor
  2. Lighter: sends data to the lights
  
  4/20/16
  
  A. Multiple roses that can be individually addressed
  B. Massive Simplification! Removed Rose and RoseForm class
  C. Removed Video
  D. Better morphing included only in the Processing component
  E. Rotations 
  
  Built on glorious Triangle Simulator
  
  x,y coordinates are p,d (petal, distance) coordinates.
  petal = axial, distance = radial. petal is 0-23, distance is 0-5.
  Turn on the coordinates to see the system.
    
*/

byte numBigRose = 3;  // Number of Big Roses

import com.heroicrobot.dropbit.registry.*;
import com.heroicrobot.dropbit.devices.pixelpusher.Pixel;
import com.heroicrobot.dropbit.devices.pixelpusher.Strip;
import com.heroicrobot.dropbit.devices.pixelpusher.PixelPusher;
import com.heroicrobot.dropbit.devices.pixelpusher.PusherCommand;

import processing.net.*;
import java.util.*;
import java.util.regex.*;

// network vars
int port = 4444;
Server _server; 
StringBuffer _buf = new StringBuffer();

class TestObserver implements Observer {
  public boolean hasStrips = false;
  public void update(Observable registry, Object updatedDevice) {
    println("Registry changed!");
    if (updatedDevice != null) {
      println("Device change: " + updatedDevice);
    }
    this.hasStrips = true;
  }
}

TestObserver testObserver;

// Physical strip registry
DeviceRegistry registry;
List<Strip> strips = new ArrayList<Strip>();

//
// Controller on the bottom of the screen
//
boolean DRAW_LABELS = false;

// TILING
// true: show all roses and let each rose act differently
// false: show only one rose (0) and force all roses to act the same way
boolean TILING = true;  // Tiling!

// number of roses and number of lights per rose
char NUM_PIXELS = 144;
char EMPTY = 999;

int BRIGHTNESS = 100;  // A percentage
int SATURATION = 0;  // 0 - 255
int COLOR_STATE = 0;  // no enum types in processing. Messy

boolean DO_ROTATE = true;  // Turn rotation on
float rotation = 0;       // Amount of rotation (0 - 23.99)
float rotation_inc = 1.0; // Amount each time rotation increases (variable)
float FRACT_MAX_ROTATE = 0.75; // 0 - 1.0. Higher the value (closer to 1) and the more disc will rotate (duty cycle)
float FRACT_MIN_ROTATE = 0.5; // 0 - 1.0. Higher the value (closer to 1) and the less disc will rotate (duty cycle)
float MAX_ROTATE_INC = 1.0;  // Maximum rotation speed
int rotation_delay = 100; // duration in milliseconds between rotation increments (smaller = faster rotation)
int rotation_time = millis();
int rotation_period = 6000000;  // 6 million ms = 10 minutes

int delay_time = 10000;  // delay time length in milliseconds (dummy initial value)
int start_time = millis();  // start time point (in absolute time)
int last_time = start_time;

// Color buffers: [BigRose][Pixel][r,g,b]
// Several buffers permits updating only the lights that change color
// May improve performance and reduce flickering
char[][][] curr_buffer = new char[numBigRose][NUM_PIXELS][3];
char[][][] next_buffer = new char[numBigRose][NUM_PIXELS][3];
char[][][] morph_buffer = new char[numBigRose][NUM_PIXELS][3];
char[][][] rotate_buffer = new char[numBigRose][NUM_PIXELS][3];
char[] shift_array = new char[NUM_PIXELS];
color[][] pix_color = new color[numBigRose][NUM_PIXELS];

// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = false;  // turn false for LED-only updates
int SCREEN_SIZE = 300;  // This is the value to change for Screen Size
int SCREEN_WIDTH = SCREEN_SIZE + getBigXoffset(numBigRose-1);
float BORDER = 0.05; // How much fractional edge between rose and screen
int BORDER_PIX = int(SCREEN_SIZE * BORDER); // Edge in pixels
int ROSE_DIAM = int(SCREEN_SIZE * (1.0 - (2 * BORDER)));  // Rose size
int ROSE_MAP_WIDTH = ROSE_DIAM + getBigXoffset(numBigRose-1);
float DENSITY = 0.0005; // 'Dottiness' of rose lines. approaching 0 = full line.

// Lookup table to hasten the fill algorithm. Written once, read many times.
char[][] screen_map = new char[ROSE_MAP_WIDTH][ROSE_DIAM];

//
//  Setup
// 
void setup() {
  
  size(900,350);
  stroke(0);
  fill(255,255,0);
  
  frameRate(20); // 10? default 60 seems excessive
  
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  colorMode(RGB, 255);
  prepareExitHandler();
  strips = registry.getStrips();
  
  initializeColorBuffers();  // Stuff with zeros (all black)
  
  _server = new Server(this, port);
  println("server listening:" + _server);
  
  background(200);  // gray
  
  //drawGrids();   // need boundaries for flood fill in getScreenMap 
  //getScreenMap();  // Map the leaves to the screen pixels to populate look-up table
  setUpShiftArray();  // Set up rotation map
}

void draw() {
  drawBottomControls();
  pollServer();        // Get messages from python show runner
  update_morph();
  if (DO_ROTATE) checkRotation();
}

void drawGrids() {
  // Draw each big rose grid
  if (TILING) {
    for (int i = 0; i < numBigRose; i++) {
      draw_grid(i);
    }
  } else {
    draw_grid(0);
  }
}

// Drawing the rose grid
void draw_grid(int rose_num) {
  color black = color(0,0,0);
  for(float t = 0; t <= 24*PI; t += DENSITY) {
    float r = (ROSE_DIAM/2.0) * cos(12/7.0 * t);  // k/d = 12/7
 
    // Polar to Cartesian conversion
    int x = int(r * cos(t) + ROSE_DIAM/2);
    int y = int(r * sin(t) + ROSE_DIAM/2);
    
    putColor(x + getBigXoffset(rose_num), y, black);
  }
}

int getBigXoffset(int rose_num) {
  if (TILING) {
    return (rose_num * SCREEN_SIZE);
  } else {
    return (0);
  }
} 

void drawCheckbox(int x, int y, int size, color fill, boolean checked) {
  stroke(0);
  fill(fill);  
  rect(x,y,size,size);
  if (checked) {    
    line(x,y,x+size,y+size);
    line(x+size,y,x,y+size);
  }  
}

void drawBottomControls() {
  // draw a bottom white region
  fill(255,255,255);
  rect(0,SCREEN_SIZE,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_SIZE,140,SCREEN_SIZE+40);
  line(290,SCREEN_SIZE,290,SCREEN_SIZE+40);
  line(470,SCREEN_SIZE,470,SCREEN_SIZE+40);
  line(610,SCREEN_SIZE,620,SCREEN_SIZE+40);
  
  // draw checkboxes
  stroke(0);
  fill(255);
  
  drawCheckbox(20,SCREEN_SIZE+10,20, color(255,255,255), DRAW_LABELS);  // label checkbox
  
  rect(200,SCREEN_SIZE+4,15,15);  // minus brightness
  rect(200,SCREEN_SIZE+22,15,15);  // plus brightness
  
  rect(520,SCREEN_SIZE+4,15,15);  // minus saturation
  rect(520,SCREEN_SIZE+22,15,15);  // plus saturation
  
  drawCheckbox(340,SCREEN_SIZE+4,15, color(255,0,0), COLOR_STATE == 1);
  drawCheckbox(340,SCREEN_SIZE+22,15, color(255,0,0), COLOR_STATE == 4);
  drawCheckbox(360,SCREEN_SIZE+4,15, color(0,255,0), COLOR_STATE == 2);
  drawCheckbox(360,SCREEN_SIZE+22,15, color(0,255,0), COLOR_STATE == 5);
  drawCheckbox(380,SCREEN_SIZE+4,15, color(0,0,255), COLOR_STATE == 3);
  drawCheckbox(380,SCREEN_SIZE+22,15, color(0,0,255), COLOR_STATE == 6);
  
  drawCheckbox(400,SCREEN_SIZE+10,20, color(255,255,255), COLOR_STATE == 0);
    
  // draw text labels in 12-point Helvetica
  fill(0);
  textAlign(LEFT);
  PFont f = createFont("Helvetica", 12, true);
  textFont(f, 12);  
  text("Labels", 50, SCREEN_SIZE+25);
  
  text("-", 190, SCREEN_SIZE+16);
  text("+", 190, SCREEN_SIZE+34);
  text("Brightness", 225, SCREEN_SIZE+25);
  textFont(f, 20);
  text(BRIGHTNESS, 150, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("-", 510, SCREEN_SIZE+16);
  text("+", 510, SCREEN_SIZE+34);
  text("Saturation", 545, SCREEN_SIZE+25);
  textFont(f, 20);
  text(SATURATION, 480, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("None", 305, SCREEN_SIZE+16);
  text("All", 318, SCREEN_SIZE+34);
  text("Color", 430, SCREEN_SIZE+25);
  
  int font_size = 12;  // default size
  f = createFont("Helvetica", font_size, true);
  textFont(f, font_size);
}

void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // clicked draw labels button
    DRAW_LABELS = !DRAW_LABELS;
   
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
   
    // Bright up checkbox
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
  
  }  else if (mouseX > 520 && mouseX < 545 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    SATURATION -= 10;
    if (SATURATION < 0) SATURATION = 1;
   
    // Bright up checkbox
  } else if (mouseX > 520 && mouseX < 545 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    SATURATION += 10;
    if (SATURATION > 255) SATURATION = 255;
  
  }  else if (mouseX > 400 && mouseX < 420 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // No color correction  
    COLOR_STATE = 0;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None red  
    COLOR_STATE = 1;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All red  
    COLOR_STATE = 4;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None blue  
    COLOR_STATE = 2;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All blue  
    COLOR_STATE = 5;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None green  
    COLOR_STATE = 3;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All green  
    COLOR_STATE = 6;
  
  }
}


// Coord class

class Coord {
  public int x, y;
  
  Coord(int x, int y) {
    this.x = x;
    this.y = y;
  }
}

// Fill the coord with a color
void floodFill(Coord coord, byte r, byte p, byte d, color newC, boolean mapping)
{
    int x = coord.x;
    int y = coord.y;
    floodFillUtil(x, y, r, p, d, getColor(x,y), newC, mapping);
}

// Return the color of the x,y pixel
// Adjust for the border
color getColor(int x, int y) {
  return get(x+BORDER_PIX, y+BORDER_PIX);
}

// Adds a point of color at x,y
// Adjust for the border
void putColor(int x, int y, color c) {
  stroke(c);
  point(x+BORDER_PIX, y+BORDER_PIX);
}

// A recursive function to replace previous color 'prevC' at  '(x, y)' 
// and all surrounding pixels of (x, y) with new color 'newC' and
void floodFillUtil(int x, int y, byte r, byte p, byte d, color prevC, color newC, boolean mapping)
{
    char leaf = GetLightFromCoord(r,p,d);
    
    // Base case
    if (x < 0 || x >= ROSE_MAP_WIDTH || y < 0 || y >= ROSE_DIAM) return;
    if (getColor(x,y) != prevC) return;
 
    // Replace the color at (x,y)
    if (mapping) {
      screen_map[x][y] = leaf;      
    }
    putColor(x,y,newC);
 
    // Recur for north, east, south and west
    floodFillUtil(x+1, y, r, p, d, prevC, newC, mapping);
    floodFillUtil(x-1, y, r, p, d, prevC, newC, mapping);
    floodFillUtil(x, y+1, r, p, d, prevC, newC, mapping);
    floodFillUtil(x, y-1, r, p, d, prevC, newC, mapping);
}

//
// drawPixel
//
// Uses a recursive fill from the center of the leaf - slow
//
void drawPixel(byte r, byte p, byte d, color newColor, boolean mapping) {  
  floodFill(GetRoseOffset(r, p, d), r, p, d, newColor, mapping);
}

//
// drawLeaf
//
// Figures out which pixels on the screen correspond to the leaf
// and fills those
// Fast, but assumes a filled screen_map (see getScreenMap)
//
void drawLeaf(byte r, byte p, byte d, color c) {
  int leaf = getLeafNum(r,p,d);
  stroke(c);
  
  for (int x=0; x<ROSE_MAP_WIDTH; x++) {
    for (int y=0; y<ROSE_DIAM; y++) {
      if (screen_map[x][y] == leaf) {
        putColor(x,y,c);
      }
    }
  }
}

//
// getLeafNum
//
int getLeafNum(byte r, byte p, byte d) {
  return ((r * NUM_PIXELS) + (((p * 6) + d) % NUM_PIXELS));
}

//
// Get Rose Offset
//
// Returns the x,y coordinate of an offset point
// Need to add the screen border for actual offset
// Petal is 0-23 number
// distance is 0-11 along the petal with 6 as the outside leaf
//
Coord GetRoseOffset(byte rose, int petal, int distance) {
  petal = (((petal % 5) * 5) + (petal / 5)) % 24; // correct petals to line them up concurrently
  
  float t = PI * 7/12.0 * (petal + ((distance*7)+7)/100.0);
  float r = (ROSE_DIAM/2.0) * sin(12/7.0 * t);  // k/d = 12/7 = 1.7143
  float x = r * cos(t) + ROSE_DIAM/2;
  float y = r * sin(t) + ROSE_DIAM/2;
  // Polar to Cartesian conversion
  return (new Coord(int(x) + getBigXoffset(rose), int(y)));
}

//
// getScreenMap
//
// Recursive flood fill is too memory intensive
// for fast use in the visualizer
//
// Instead, calculate once in set-up and store in a look-up table
// which leaf belongs to each screen pixel 
//
void getScreenMap() {
  byte maxRose;
  
  // Fill the screen_map with "empty" value
  fillScreen(EMPTY);
  
  if (TILING) {
    maxRose = numBigRose;
  } else {
    maxRose = 1;
  }
  for (byte r=0; r<numBigRose; r++) {
    for (byte p=0; p<24; p++) {
      for (byte d=0; d<6; d++) {
        drawPixel(r,p,d, color(255,0,0), true); // Mapping is on (true)
      }
    }
  }
}

//
// fillScreen
//
// populate table with value
//
void fillScreen(char value) {
  for (int x=0; x<ROSE_MAP_WIDTH; x++) {
    for (int y=0; y<ROSE_DIAM; y++) {
      screen_map[x][y] = value;
    }
  }
}

// Raster over the screen_map. Fill each pixel with the appropriate leaf color
// This one-time fill of the screen may be the computationally fastest approach 
void drawRoses() {
  int x,y;
  char pixel;
  
  for (x = 0; x < ROSE_MAP_WIDTH; x++) {
    for (y = 0; y < ROSE_DIAM; y++) {
      pixel = screen_map[x][y];
      if (pixel != EMPTY) {    // a leaf spot
        putColor(x,y, pix_color[pixel/NUM_PIXELS][pixel%NUM_PIXELS]);
      }
    }
  }
}
   
void setCellColor(color c, byte r, int i) {
  if (i >= NUM_PIXELS) {
    println("invalid LED number: i only have " + NUM_PIXELS + " LEDs");
    return;
  }
  if (r >= numBigRose) {
    println("invalid rose number: i only have " + numBigRose + " Roses");
    return;
  }
  pix_color[r][i] = c;
}

//
// drawLabels
//
void drawLabels() {
  if (TILING) {
    for (byte i = 0; i < numBigRose; i++) {
      draw_label(i);
    }
  } else {
    draw_label(byte(0));
  }
}

// Drawing the rose grid
void draw_label(byte r) {
  if (!DRAW_LABELS) return;
  
  String text_coord;
  Coord coord;
  
  fill(127);  // Gray
  textAlign(CENTER);
  PFont f = createFont("Helvetica", 8, true);
  textFont(f, 8); 
  
  for (int p = 0; p < 24; p++) {
    for (int d = 0; d < 6; d++) {
      text_coord = String.format("%d,%d", p, d);
      coord = GetRoseOffset(r,p,d);
      text(text_coord, coord.x + BORDER_PIX, coord.y + BORDER_PIX);
    }
  }
}

//
// Get Light From Coord
//
// Algorithm to convert (petal,distance) coordinate into an LED number
char GetLightFromCoord(byte r, byte p, byte d) {
  int LED = (((5-d)/2)*48) + (p*2) + ((d+1)%2);
  
  if (d == 2 || d == 3) {  // Middle two rings of LEDs 48-95
    LED = LED+1;           // Shift the ring due to wiring
    if (LED >= 96) LED -= 48;
  }
  
  if (d <= 1) {   // Inner two rings of LEDs 96-143
    LED = LED+4;  // Shift the ring due to wiring
    if (LED >= 144) LED -= 48;
  }
  return char(LED + (r * NUM_PIXELS));  // Overloading LED with Big Rose
}

//
// Rotation Routines
//
void setUpShiftArray() {
  byte r = 0;
  byte shifted;
  for (byte p = 0; p < 24; p++) {
    for (byte d = 0; d < 6; d++) {
      shifted = (byte)((p+1) % 24);
      shift_array[GetLightFromCoord(r, p, d)] = GetLightFromCoord(r, shifted, d);
    }
  } 
}

void checkRotation() {
  // Rotate disc
  if (millis() - rotation_time > rotation_delay) {
    rotation_time = millis();
    if (rotation_inc > 0) {
      rotation += rotation_inc;
    } else {
      rotation = round(rotation);  // Make static disc stay on a whole petal
    }
    if (rotation >= 24.0) {
      rotation -= 24.0;
    }
    rotation_inc = setRotationSpeed();
  }
}

float setRotationSpeed() {
  float value = sin(3.1415 * (millis() % rotation_period) / rotation_period);  // sin(0 - pi) = 0 to 1
  if (value < FRACT_MIN_ROTATE) {
    return 0;
  } else if (value < FRACT_MAX_ROTATE) {
    return MAX_ROTATE_INC;
  }
  return MAX_ROTATE_INC * (value - FRACT_MIN_ROTATE) / (FRACT_MAX_ROTATE - FRACT_MIN_ROTATE);
}
  
void rotateFrame() {
  byte rose;
  char r,g,b;
  char pix, left_pix, right_pix;
  float fract = rotation - floor(rotation);
  
  for (rose = 0; rose < numBigRose; rose++) {
    for (pix = 0; pix < NUM_PIXELS; pix++) {
      left_pix = shiftPix(pix, floor(rotation));
      right_pix = shift_array[left_pix];
      
      r = interp(morph_buffer[rose][left_pix][0], morph_buffer[rose][right_pix][0], fract);
      g = interp(morph_buffer[rose][left_pix][1], morph_buffer[rose][right_pix][1], fract);
      b = interp(morph_buffer[rose][left_pix][2], morph_buffer[rose][right_pix][2], fract);
      
      setCellColor(color(r,g,b), rose, pix);  // Simulator
      
      rotate_buffer[rose][pix][0] = r;
      rotate_buffer[rose][pix][1] = g;
      rotate_buffer[rose][pix][2] = b;
    }
  }
}

char shiftPix(char pix, int shift_amount) {
  char new_pix = pix;
  for (int i = 0; i < shift_amount; i++) {
    new_pix = shift_array[new_pix];
  }
  return new_pix;
}

//
//  Server Routines
//
void pollServer() {
  try {
    Client c = _server.available();
    // append any available bytes to the buffer
    if (c != null) {
      _buf.append(c.readString());
    }
    // process as many lines as we can find in the buffer
    int ix = _buf.indexOf("\n");
    while (ix > -1) {
      String msg = _buf.substring(0, ix);
      msg = msg.trim();
      //println(msg);
      processCommand(msg);
      _buf.delete(0, ix+1);
      ix = _buf.indexOf("\n");
    }
  } catch (Exception e) {
    println("exception handling network command");
    e.printStackTrace();
  }  
}


Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

void processCommand(String cmd) {
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle();
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time = Integer.valueOf(cmd.substring(1, cmd.length())) + 20;  // 20 is a buffer
  } else {  
    processPixelCommand(cmd);  // Pixel command
  }
}
  
void processPixelCommand(String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    println("ignoring input!");
    return;
  }
  byte rose  = Byte.valueOf(m.group(1));
  int pix    = Integer.valueOf(m.group(2));
  int r     = Integer.valueOf(m.group(3));
  int g     = Integer.valueOf(m.group(4));
  int b     = Integer.valueOf(m.group(5));
  
  setPixelBuffer(rose, pix, (char)r, (char)g, (char)b, false); 
//  println(String.format("setting pixel:%d,%d to r:%d g:%d b:%d", rose, pix, r, g, b));
}

// Send a corrected color to a rose pixel on screen and in lights
void sendColorOut(byte rose, int pix, char r, char g, char b) {
  color correct = colorCorrect(r,g,b);
  
  r = adj_brightness(red(correct));
  g = adj_brightness(green(correct));
  b = adj_brightness(blue(correct));
  
  if (TILING) {
    //if (r+g+b > 0) println(rose, pix, r, g, b);
    setCellColor(color(r,g,b), rose, pix);  // Simulator
    setPixelBuffer(rose, pix, r, g, b, true);  // Lights: sets next-frame buffer (doesn't turn them on)
  } else {
    if (rose == 0) {
      for (byte rose_num = 0; rose_num < numBigRose; rose_num++) {
        setCellColor(color(r,g,b), rose_num, pix);  // Simulator
        setPixelBuffer(rose_num, pix, r, g, b, true);  // Lights: sets next-frame buffer (doesn't turn them on)
      }
    }
  }
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by:
void finishCycle() {
  morph_frame(1.0);
  pushColorBuffer();
  start_time = millis();  // reset the clock
}

//
// Update Morph
//
void update_morph() {
  if ((last_time - start_time) > delay_time) {
    return;  // Already finished all morphing - waiting for next command 
  }
  last_time = millis();  // update clock
  morph_frame((last_time - start_time) / (float)delay_time); 
}
  
//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0-1.0 fraction towards the next frame
//
void morph_frame(float fract) {
  byte rose;
  char r,g,b;
  int pix;
  
  for (rose = 0; rose < numBigRose; rose++) {
    for (pix = 0; pix < NUM_PIXELS; pix++) {
      if (hasChanged(rose, pix)) {
        r = interp(curr_buffer[rose][pix][0], next_buffer[rose][pix][0], fract);
        g = interp(curr_buffer[rose][pix][1], next_buffer[rose][pix][1], fract);
        b = interp(curr_buffer[rose][pix][2], next_buffer[rose][pix][2], fract);
        
        sendColorOut(rose, pix, r, g, b);  // Update individual light and simulator
      }
    }
  }
  if (DO_ROTATE) rotateFrame(); // Rotate!
  sendDataToLights();  // Turn on all lights
  if (UPDATE_VISUALIZER) {
    drawRoses();  // Update all displays
    drawLabels();
  }
}  

char interp(char a, char b, float fract) {
  return (char)(a + (fract * (b-a)));
}

//
//  Routines to interact with the Lights
//
void sendDataToLights() {
  byte BigRose;
  int pixel;
  
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    List<Strip> strips = registry.getStrips();
    BigRose = 0;
    
    for (Strip strip : strips) {      
      for (pixel = 0; pixel < NUM_PIXELS; pixel++) {
         if (DO_ROTATE || hasChanged(BigRose, pixel)) {
           strip.setPixel(getPixelBuffer(BigRose, pixel), pixel);
         }
      }
      BigRose++;
      if (BigRose >=numBigRose) break;  // Prevents buffer overflow
    }
  }
}

private void prepareExitHandler () {

  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {

    public void run () {

      System.out.println("Shutdown hook running");

      List<Strip> strips = registry.getStrips();
      for (Strip strip : strips) {
        for (int i=0; i<strip.getLength(); i++)
          strip.setPixel(#000000, i);
      }
      for (int i=0; i<100000; i++)
        Thread.yield();
    }
  }
  ));
}

//
//  Routines for the strip buffer
//
char adj_brightness(float value) {
  return (char)(value * BRIGHTNESS / 100);
}

color colorCorrect(int r, int g, int b) {
  switch(COLOR_STATE) {
    case 1:  // no red
      if (r > 0) {
        if (g == 0) {
          g = r;
          r = 0;
        } else if (b == 0) {
          b = r;
          r = 0;
        }
      }
      break;
    
    case 2:  // no green
      if (g > 0) {
        if (r == 0) {
          r = g;
          g = 0;
        } else if (b == 0) {
          b = g;
          g = 0;
        }
      }
      break;
    
    case 3:  // no blue
      if (b > 0) {
        if (r == 0) {
          r = b;
          b = 0;
        } else if (g == 0) {
          g = b;
          b = 0;
        }
      }
      break;
    
    case 4:  // all red
      if (r == 0) {
        if (g > b) {
          r = g;
          g = 0;
        } else {
          r = b;
          b = 0;
        }
      }
      break;
    
    case 5:  // all green
      if (g == 0) {
        if (r > b) {
          g = r;
          r = 0;
        } else {
          g = b;
          b = 0;
        }
      }
      break;
    
    case 6:  // all blue
      if (b == 0) {
        if (r > g) {
          b = r;
          r = 0;
        } else {
          b = g;
          g = 0;
        }
      }
      break;
    
    default:
      break;
  }
  return color(r,g,b);   
}

void initializeColorBuffers() {
  char empty = 0;
  for (byte r = 0; r < numBigRose; r++) {
    for (int p = 0; p < NUM_PIXELS; p++) {
      setPixelBuffer(r, p, empty,empty,empty, false);
    }
  }
  pushColorBuffer();
}

void setPixelBuffer(byte BigRose, int pixel, char r, char g, char b, boolean morph) {
  BigRose = byte(BigRose % numBigRose);
  pixel = int(pixel % NUM_PIXELS);
  
  if (morph) {
    morph_buffer[BigRose][pixel][0] = r;
    morph_buffer[BigRose][pixel][1] = g;
    morph_buffer[BigRose][pixel][2] = b;
  } else {
    next_buffer[BigRose][pixel][0] = r;
    next_buffer[BigRose][pixel][1] = g;
    next_buffer[BigRose][pixel][2] = b;
  }
}

color getPixelBuffer(byte BigRose, int pixel) {
  //BigRose = byte(BigRose % numBigRose);
  pixel = int(pixel % NUM_PIXELS);
  
  if (DO_ROTATE) {
    return color(rotate_buffer[BigRose][pixel][0],
                 rotate_buffer[BigRose][pixel][1],
                 rotate_buffer[BigRose][pixel][2]);
  } else {
    return color(morph_buffer[BigRose][pixel][0],
                 morph_buffer[BigRose][pixel][1],
                 morph_buffer[BigRose][pixel][2]);
  }
}

boolean hasChanged(byte r, int p) {
  if (curr_buffer[r][p][0] != next_buffer[r][p][0] ||
      curr_buffer[r][p][1] != next_buffer[r][p][1] ||
      curr_buffer[r][p][2] != next_buffer[r][p][2]) {
        return true;
      } else {
        return false;
      }
}

void pushColorBuffer() {
  for (byte r = 0; r < numBigRose; r++) {
    for (int p = 0; p < NUM_PIXELS; p++) {
      curr_buffer[r][p][0] = next_buffer[r][p][0];
      curr_buffer[r][p][1] = next_buffer[r][p][1];
      curr_buffer[r][p][2] = next_buffer[r][p][2];
    }
  }
}