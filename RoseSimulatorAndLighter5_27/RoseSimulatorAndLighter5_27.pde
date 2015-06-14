/*

  Rose Simulator and Lighter
  
  1. Simulator: draws rose shape on the monitor
  2. Lighter: sends data to the lights
  
  6/9/15
  
  Built on glorious Triangle Simulator
  
  x,y coordinates are p,d (petal, distance) coordinates.
  petal = axial, distance = radial. petal is 0-23, distance is 0-5.
  Turn on the coordinates to see the system.
    
*/


// Relative coordinates for the Big Roses
int[][] BigRoseCoord = {
  {0,0},
};

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

int NONE = 9999;  // hack: "null" for "int'

//
// Controller on the bottom of the screen
//
// Draw labels has 3 states:
// 0:LED number, 1:(x,y) coordinate, and 2:none
int DRAW_LABELS = 2;

// Tiling!
// true means draw all the Big Roses
// false means all Big Roses overlap
boolean TILING = true;

// number of roses and number of lights per rose
int numBigRose = 1;
int NUM_PIXELS = 144;

int BRIGHTNESS = 100;  // A percentage

int COLOR_STATE = 0;  // no enum types in processing. Messy

// Color buffers: [BigRose][Pixel][r,g,b]
// Two buffers permits updating only the lights that change color
// May improve performance and reduce flickering
int[][][] curr_buffer = new int[numBigRose][NUM_PIXELS][3];
int[][][] next_buffer = new int[numBigRose][NUM_PIXELS][3];

// Calculated pixel constants for simulator display
int SCREEN_SIZE = 400;  // square screen
float BORDER = 0.05; // How much edge between rose and screen
float DENSITY = 0.0005; // 'Dottiness' of rose lines. approaching 0 = full line.
int CORNER_X = 10; // bottom left corner position on the screen
int CORNER_Y = SCREEN_SIZE - 10; // bottom left corner position on the screen

// Lookup table to hasten the fill algorithm. Written once, read many times.
int[][] screen_map = new int[SCREEN_SIZE][SCREEN_SIZE];

// Grid model(s) of Big Roses
RoseForm[] roseGrid = new RoseForm[numBigRose];

void setup() {
  size(SCREEN_SIZE, SCREEN_SIZE + 50); // 50 for controls
  stroke(0);
  fill(255,255,0);
  
  frameRate(10); // default 60 seems excessive
  
  // Set up the Big Roses and stuff in the little Roses
  for (int i = 0; i < numBigRose; i++) {
    roseGrid[i] = makeRoseGrid(0,0,i);
  }
  
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  colorMode(RGB, 255);
  frameRate(60);
  prepareExitHandler();
  strips = registry.getStrips();  // Array of strips?
  
  initializeColorBuffers();  // Stuff with zeros (all black)
  
  _server = new Server(this, port);
  println("server listening:" + _server);
  
  background(200);  // gray
  
  drawBottomControls();
  drawGrids();   // need boundaries for flood fill in getScreenMap 
  getScreenMap();  // Map the leaves to the screen pixels to populate look-up table
}

void draw() {
  pollServer();        // Get messages from python show runner
  sendDataToLights();  // Dump data into lights
  //drawRoses();
  pushColorBuffer();   // Push the frame buffers
}

void drawRoses() {
  // Draw only in the Simulator all the leaves and labels
  for (int i = 0; i < numBigRose; i++) {
    roseGrid[i].draw();
  }
}

void drawGrids() {
  // Draw each big rose grid
  for (int i = 0; i < numBigRose; i++) {
    roseGrid[i].draw_grid();
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
  rect(0,SCREEN_SIZE,SCREEN_SIZE,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_SIZE,140,SCREEN_SIZE+40);
  line(290,SCREEN_SIZE,290,SCREEN_SIZE+40);
  line(470,SCREEN_SIZE,470,SCREEN_SIZE+40);
  
  // draw checkboxes
  stroke(0);
  fill(255);
  // Checkbox is always unchecked; it is 3-state
  rect(20,SCREEN_SIZE+10,20,20);  // label checkbox
  
  rect(200,SCREEN_SIZE+4,15,15);  // minus brightness
  rect(200,SCREEN_SIZE+22,15,15);  // plus brightness
  
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
  text("Toggle Labels", 50, SCREEN_SIZE+25);
  
  text("-", 190, SCREEN_SIZE+16);
  text("+", 190, SCREEN_SIZE+34);
  text("Brightness", 225, SCREEN_SIZE+25);
  textFont(f, 20);
  text(BRIGHTNESS, 150, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("None", 305, SCREEN_SIZE+16);
  text("All", 318, SCREEN_SIZE+34);
  text("Color", 430, SCREEN_SIZE+25);
  
  // scale font to size of Roses
  int font_size = 12;  // default size
  f = createFont("Helvetica", font_size, true);
  textFont(f, font_size);
}

void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // clicked draw labels button
    DRAW_LABELS = (DRAW_LABELS + 1) % 3;
    // Re-draw all the leaves and labels
    for (int i = 0; i < numBigRose; i++) {
      roseGrid[i].draw();
    }
   
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
   
    // Bright up checkbox
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
  
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
void floodFill(Coord coord, byte p, byte d, color newC, boolean mapping)
{
    int x = coord.x;
    int y = coord.y;
    floodFillUtil(x, y, p, d, get(x,y), newC, mapping);
}

// A recursive function to replace previous color 'prevC' at  '(x, y)' 
// and all surrounding pixels of (x, y) with new color 'newC' and
void floodFillUtil(int x, int y, byte p, byte d, color prevC, color newC, boolean mapping)
{
    int leaf = GetLightFromCoord(p,d,0);  //getLeafNum(p,d);
    
    // Base case
    if (x < 0 || x > SCREEN_SIZE || y < 0 || y > SCREEN_SIZE) return;
    if (get(x,y) != prevC) return;
 
    // Replace the color at (x,y)
    if (mapping) {
      screen_map[x][y] = leaf;      
    }
    stroke(newC);
    point(x,y);
 
    // Recur for north, east, south and west
    floodFillUtil(x+1, y, p, d, prevC, newC, mapping);
    floodFillUtil(x-1, y, p, d, prevC, newC, mapping);
    floodFillUtil(x, y+1, p, d, prevC, newC, mapping);
    floodFillUtil(x, y-1, p, d, prevC, newC, mapping);
}

//
// drawPixel
//
// Uses a recursive fill from the center of the leaf - slow
//
void drawPixel(byte p, byte d, color newColor, boolean mapping) {  
  floodFill(GetRoseOffset(p, d), p, d, newColor, mapping);
}

//
// drawLeaf
//
// Figures out which pixels on the screen correspond to the leaf
// and fills those
// Fast, but assumes a filled screen_map (see getScreenMap)
//
void drawLeaf(byte p, byte d, color c) {
  int leaf = getLeafNum(p,d);
  stroke(c);
  
  for (int x=0; x<SCREEN_SIZE; x++) {
    for (int y=0; y<SCREEN_SIZE; y++) {
      if (screen_map[x][y] == leaf) {
        point(x,y);
      }
    }
  }
}

//
// getLeafNum
//
int getLeafNum(byte p, byte d) {
  return (((p * 6) + d) % NUM_PIXELS);
}

//
// Get Rose Offset
//
// Returns the x,y coordinate of an offset point
// Petal is 0-23 number
// distance is 0-11 along the petal with 6 as the outside leaf
//
Coord GetRoseOffset(int petal, int distance) {
  petal = (((petal % 5) * 5) + (petal / 5)) % 24; // correct petals to line them up concurrently
  
  float t = PI * 7/12.0 * (petal + ((distance*7)+7)/100.0);
  float r = ((1-BORDER)*SCREEN_SIZE/2.0) * sin(12/7.0 * t);  // k/d = 12/7 = 1.7143
  float x = r * cos(t) + SCREEN_SIZE/2;
  float y = r * sin(t) + SCREEN_SIZE/2;
  //println(petal + " " + distance + " " + x + " " + y);
  // Polar to Cartesian conversion
  return (new Coord(int(x),int(y)));
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
  // Fill the screen_map with "empty" value (= NUM_PIXELS)
  fillScreen(NUM_PIXELS);
  
  for (byte p=0; p<24; p++) {
    for (byte d=0; d<6; d++) {
      drawPixel(p,d, color(255,0,0), true); // Mapping is on (true)
    }
  }
}

//
// fillScreen
//
// populate table with value
//
void fillScreen(int value) {
  for (int x=0; x<SCREEN_SIZE; x++) {
    for (int y=0; y<SCREEN_SIZE; y++) {
      screen_map[x][y] = value;
    }
  }
}

// makeRoseGrid
//
RoseForm makeRoseGrid(int big_x, int big_y, int big_num) {
  
  RoseForm form = new RoseForm();
  
  for (byte y=0; y<6; y++) {  // distance
    for (byte x=0; x<24; x++) {  // petals
      form.add(new Rose(x,y, big_num));
    }
  }
  return form;  
}

class RoseForm {
  ArrayList<Rose> roses;
  color[] pix_color = new color[NUM_PIXELS];
  
  RoseForm() {
    roses = new ArrayList<Rose>();
  }
  
  void add(Rose r) {
    int roseId = roses.size();
    roses.add(r);
  }
  
  int size() {
    return roses.size();
  }
  
  // Draws in the Simulator all the petals plus labels
  void draw() {
    bulk_draw();
    // Draws each leaf at a time
    /*
    for (Rose r : roses) {
      r.draw();
    }
    */
  }
  
  // Raster over the screen_map. Fill each pixel with the appropriate leaf color
  void bulk_draw() {
    int x,y,pixel;

    for (x = 0; x < SCREEN_SIZE; x++) {
      for (y = 0; y < SCREEN_SIZE; y++) {
        pixel = screen_map[x][y];
        if (pixel < NUM_PIXELS) {    // a leaf spot
          stroke(pix_color[pixel]);  // Look up the color for that leaf
          point(x,y);
        }
      }
    }
  }
  
  // Drawing the rose grid
  void draw_grid() {
    stroke(0);  // Black
    for(float t = 0; t <= 24*PI; t += DENSITY) {
      float r = ((1-BORDER)*SCREEN_SIZE/2.0) * cos(12/7.0 * t);  // k/d = 12/7
 
      // Polar to Cartesian conversion
      float x = r * cos(t) + SCREEN_SIZE/2;
      float y = r * sin(t) + SCREEN_SIZE/2;
      
      point(x,y);
      //rect(x, y, 2, 2);  // Chunky to prevent fill break-out
    }
  }
  
  // Reworked for iterative search (SD) XXX probably need a better API here!
  void setCellColor(color c, int i) {
    if (i >= roses.size()) {
      println("invalid offset for RoseForm.setColor: i only have " + roses.size() + " Roses");
      return;
    }
    pix_color[i] = c;
    for (Rose r : roses) {  // Search all 
      if (i == r.LED) {  // for the one that has the correct LED#
        r.setColor(c);
        return;
      }
    }
    println("Could not find LED #"+i);
  }
    
}

class Rose {
  String id = null; // "xcoord, ycoord"
  byte xcoord;  // x in the roseangle array (petal)
  byte ycoord;  // y in the roseangle array (distance)
  int big_num; // strip number
  int LED;     // LED number on the strand
  color c;
  
  Rose(byte xcoord, byte ycoord, int big_num) {
    this.xcoord = xcoord;
    this.ycoord = ycoord;
    this.big_num = big_num;
    this.LED = GetLightFromCoord(this.xcoord, this.ycoord, big_num);
    this.c = color(255,255,255);
    
    // str(xcoord + ", " + ycoord)
    int[] coords = new int[2];
    coords[0] = xcoord;
    coords[1] = ycoord;
    this.id = join(nf(coords, 0), ",");
  }

  void setId(String id) {
    this.id = id;
  }
  
  void setColor(color c) {
    // If back to individual-leaf colorings, remove the below comment
    //drawLeaf(this.xcoord, this.ycoord, c);  // Faster, lookup version
    //drawPixel(this.xcoord, this.ycoord, c, false);  // Slower, recursive version
    this.c = c;
  }

  void draw() {
    this.setColor(this.c);  // Fill in leaf - obliterate last letters if needed
    
    stroke(0);
    
    // toggle text label between light number and x,y coordinate
    String text = "";
    switch (DRAW_LABELS) {
      case 0:
        text = str(this.LED);
        break;
      case 1:
        text = this.id;  // (x,y) coordinate
        break;
      case 2:
        // no label
        break;
    }
    
    if (this.id != null) {
      Coord coord = GetRoseOffset(this.xcoord, this.ycoord);
      textAlign(CENTER);
      text(text, coord.x, coord.y);
    }
    noFill();
  }
}

//
// Get Light From Coord
//
// Algorithm to convert (petal,distance) coordinate into an LED number
int GetLightFromCoord(int p, int d, int grid) {
  p = (((p % 5) * 5) + (p / 5)) % 24; // correct petals to line them up concurrently
  
  int LED = (((5-d)/2)*48) + (p*2) + ((d+1)%2);
  
  if (d == 2 || d == 3) {  // Middle two rings of LEDs 48-95
    LED = LED+1;           // Shift the ring due to wiring
    if (LED >= 96) LED -= 48;
  }
  
  if (d <= 1) {   // Inner two rings of LEDs 96-143
    LED = LED+4;  // Shift the ring due to wiring
    if (LED >= 144) LED -= 48;
  }
  return LED;
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
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    println("ignoring input!");
    return;
  }
  int rose  = Integer.valueOf(m.group(1));
  int pix  = Integer.valueOf(m.group(2));
  int r    = Integer.valueOf(m.group(3));
  int g    = Integer.valueOf(m.group(4));
  int b    = Integer.valueOf(m.group(5));
  
  //println(String.format("setting pixel:%d,%d to r:%d g:%d b:%d", rose, pix, r, g, b));
  
  color correct = colorCorrect(r,g,b);
  
  r = adj_brightness(red(correct));
  g = adj_brightness(green(correct));
  b = adj_brightness(blue(correct));
  
  roseGrid[rose].setCellColor(color(r,g,b), pix);  // Simulator
  setPixelBuffer(rose, pix, r, g, b);  // Lights  
}

//
//  Routines to interact with the Lights
//

void sendDataToLights() {
  int BigRose, pixel;
  
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    List<Strip> strips = registry.getStrips();
    BigRose = 0;
    
    for (Strip strip : strips) {      
      for (pixel = 0; pixel < NUM_PIXELS; pixel++) {
         if (hasChanged(BigRose,pixel)) {
           strip.setPixel(getPixelBuffer(BigRose,pixel), pixel);
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

int adj_brightness(float value) {
  return (int)(value * BRIGHTNESS / 100);
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
  for (int t = 0; t < numBigRose; t++) {
    for (int p = 0; p < NUM_PIXELS; p++) {
      setPixelBuffer(t, p, 0,0,0);
    }
  }
  pushColorBuffer();
}

void setPixelBuffer(int BigRose, int pixel, int r, int g, int b) {
  BigRose = bounds(BigRose, 0, numBigRose-1);
  pixel = bounds(pixel, 0, NUM_PIXELS-1);
  
  next_buffer[BigRose][pixel][0] = r;
  next_buffer[BigRose][pixel][1] = g;
  next_buffer[BigRose][pixel][2] = b;
}

color getPixelBuffer(int BigRose, int pixel) {
  BigRose = bounds(BigRose, 0, numBigRose-1);
  pixel = bounds(pixel, 0, NUM_PIXELS-1);
  
  return color(next_buffer[BigRose][pixel][0],
               next_buffer[BigRose][pixel][1],
               next_buffer[BigRose][pixel][2]);
}

boolean hasChanged(int t, int p) {
  if (curr_buffer[t][p][0] != next_buffer[t][p][0] ||
      curr_buffer[t][p][1] != next_buffer[t][p][1] ||
      curr_buffer[t][p][2] != next_buffer[t][p][2]) {
        return true;
      } else {
        return false;
      }
}

void pushColorBuffer() {
  for (int t = 0; t < numBigRose; t++) {
    for (int p = 0; p < NUM_PIXELS; p++) {
      curr_buffer[t][p][0] = next_buffer[t][p][0];
      curr_buffer[t][p][1] = next_buffer[t][p][1];
      curr_buffer[t][p][2] = next_buffer[t][p][2]; 
    }
  }
}

int bounds(int value, int minimun, int maximum) {
  if (value < minimun) return minimun;
  if (value > maximum) return maximum;
  return value;
}
