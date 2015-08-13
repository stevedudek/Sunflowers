/*

  Rose Simulator and Lighter
  
  1. Simulator: draws rose shape on the monitor
  2. Lighter: sends data to the lights
  
  8/2/15
  
  A. Movies
  B. Multiple roses
  
  Built on glorious Triangle Simulator
  
  x,y coordinates are p,d (petal, distance) coordinates.
  petal = axial, distance = radial. petal is 0-23, distance is 0-5.
  Turn on the coordinates to see the system.
    
*/

int numBigRose = 3;  // Number of Big Triangles

// Relative coordinates for the Big Roses
int[][] BigRoseCoord = {
  {0,0},  // Strip 1
  {1,0},  // Strip 2
  {2,0},  // Strip 3
};

import com.heroicrobot.dropbit.registry.*;
import com.heroicrobot.dropbit.devices.pixelpusher.Pixel;
import com.heroicrobot.dropbit.devices.pixelpusher.Strip;
import com.heroicrobot.dropbit.devices.pixelpusher.PixelPusher;
import com.heroicrobot.dropbit.devices.pixelpusher.PusherCommand;

import processing.net.*;
import java.util.*;
import java.util.regex.*;
import processing.video.*;  // For video

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
char NUM_PIXELS = 144;

int BRIGHTNESS = 100;  // A percentage

int COLOR_STATE = 0;  // no enum types in processing. Messy

// Color buffers: [BigRose][Pixel][r,g,b]
// Two buffers permits updating only the lights that change color
// May improve performance and reduce flickering
int[][][] curr_buffer = new int[numBigRose][NUM_PIXELS][3];
int[][][] next_buffer = new int[numBigRose][NUM_PIXELS][3];
int[][][] morph_buffer = new int[numBigRose][NUM_PIXELS][3];
boolean morph_complete = true;

// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = false;  // turn false for LED-only updates
int SCREEN_SIZE = 200;  // square screen
float BORDER = 0.05; // How much fractional edge between rose and screen
int BORDER_PIX = int(SCREEN_SIZE * BORDER); // Edge in pixels
int ROSE_DIAM = int(SCREEN_SIZE * (1.0 - (2 * BORDER)));  // Rose size
float DENSITY = 0.0005; // 'Dottiness' of rose lines. approaching 0 = full line.
int CORNER_X = 10; // bottom left corner position on the screen
int CORNER_Y = SCREEN_SIZE - 10; // bottom left corner position on the screen

// Lookup table to hasten the fill algorithm. Written once, read many times.
char[][] screen_map = new char[ROSE_DIAM][ROSE_DIAM];

//
// Video variables
//
PImage movieFrame;            // The current movie frame
boolean VIDEO_STATE = false;  // Whether video is playing
Movie myMovie;                // The current animated gif
int movie_number;             // current movie number
int PIX_DENSITY = 10;  // How many pixels wide is each little triangle
float[] movie_speeds = { 0.0, 0.2, 0.4, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0 };
String[] movie_titles = { "eye", "Earth", "bluedot" };

// Grid model(s) of Big Roses
RoseForm[] roseGrid = new RoseForm[numBigRose];

//
// Pixel Array routines for Images
//

class RGBColor {
  public float r, g, b;
  
  RGBColor(float r, float g, float b) {
    this.r = r;
    this.g = g;
    this.b = b;
  }
}

class Pixel {
  public int numitems;
  public RGBColor pixcolor;
  
  Pixel() {
    this.numitems = 0;
    pixcolor = new RGBColor(0,0,0);
  }
  
  void Empty() {
    this.numitems = 0;
    pixcolor = new RGBColor(0,0,0);
  }
}

class PixelArray {
  public char array_length;
  public Pixel[] Pixels;
  
  PixelArray(char array_length) {  // x,y=p,d
    this.array_length = array_length;
    this.Pixels = new Pixel[array_length];
    
    for (char i = 0; i < array_length; i++) {
      Pixels[i] = new Pixel();
    }
  }
  
  boolean IsValidCoord(int i) {
    if (i < 0 || i >= this.array_length) {
      return false;
    } else {
      return true;
    }
  }
  
  void EmptyAllPixels() {
    for (char i = 0; i < array_length; i++) {
      Pixels[i].Empty();
    }
  }
  
  RGBColor GetPixelColor(char i) {
    if (IsValidCoord(i)) {
      return Pixels[i].pixcolor;
    } else {
      RGBColor black = new RGBColor(0,0,0);
      return black;
    }
  }
     
  void StuffPixelWithColor(char i, RGBColor rgb) {
    if (!IsValidCoord(i)) return;  // Out of range
    
    int numdata = Pixels[i].numitems;
    if (numdata == 0) {  // First value in pixel. Stuff all of it.
      this.Pixels[i].pixcolor = new RGBColor(rgb.r, rgb.g, rgb.b);
    } else {  // Already values in pixel. Do a weighted average with the new value.
      this.Pixels[i].pixcolor = new RGBColor(
        (rgb.r + (this.Pixels[i].pixcolor.r*numdata))/(numdata+1),
        (rgb.g + (this.Pixels[i].pixcolor.g*numdata))/(numdata+1),
        (rgb.b + (this.Pixels[i].pixcolor.b*numdata))/(numdata+1));
    }
    this.Pixels[i].numitems++;
  }
}

// Buffer that holds pixels
PixelArray pixelarray;

void setup() {
  
  size(SCREEN_SIZE, SCREEN_SIZE + 50); // 50 for controls
  stroke(0);
  fill(255,255,0);
  
  frameRate(10); // 10? default 60 seems excessive
  
  // Set up the Big Roses and stuff in the little Roses
  for (byte i = 0; i < numBigRose; i++) {
    roseGrid[i] = makeRoseGrid(getBigX(i), getBigY(i),i);
  }
  
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  colorMode(RGB, 255);
  frameRate(60);
  prepareExitHandler();
  strips = registry.getStrips();  // Array of strips?
  
  initializeColorBuffers();  // Stuff with zeros (all black)
  
  // Image handling
  pixelarray = new PixelArray(NUM_PIXELS);
  
  movieFrame = createImage(ROSE_DIAM, ROSE_DIAM, RGB);
  movie_number = int(random(movie_titles.length));  // Initial movie
  
  _server = new Server(this, port);
  println("server listening:" + _server);
  
  background(200);  // gray
  
  drawGrids();   // need boundaries for flood fill in getScreenMap 
  getScreenMap();  // Map the leaves to the screen pixels to populate look-up table
}

void draw() {
  drawBottomControls();
  pollServer();        // Get messages from python show runner
  
  if (VIDEO_STATE) {  // Is video on?
    DumpMovieIntoPixels();
    movePixelsToBuffer();
    pixelarray.EmptyAllPixels();
  }
}

void drawRoses() {
  // Draw only in the Simulator all the leaves and labels
  roseGrid[0].draw();
  /*
  for (int i = 0; i < numBigRose; i++) {
    roseGrid[i].draw();
  }
  */
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
  line(630,SCREEN_SIZE,630,SCREEN_SIZE+40);
  
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
  
  drawCheckbox(480,SCREEN_SIZE+10,20, color(255,255,255), VIDEO_STATE); // Video
  rect(600,SCREEN_SIZE+10,20,20);  // next gif box
    
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
  text("Video", 505, SCREEN_SIZE+25);
  text("Next", 565, SCREEN_SIZE+16);
  text("gif", 570, SCREEN_SIZE+32);
  
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
  
  }  else if (mouseX > 480 && mouseX < 500 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // clicked video button
    VIDEO_STATE = !VIDEO_STATE;
    if (VIDEO_STATE) {
      turnOnMovie();
    } else {
      myMovie.stop();
    }
   
  } else if (mouseX > 600 && mouseX < 620 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // clicked next gif button
    if (VIDEO_STATE) nextMovie();
  }
}

//
// Movies
//

void DumpMovieIntoPixels() {
  movieFrame.loadPixels();
  //image(movieFrame, 0, 0);
  // Iterate over background/main image pixel-by-pixel
  // For each pixel, determine the triangular coordinate
  // Width/height ratio is already properly scaled
  
  for (int j = 0; j < movieFrame.height; j++) {
    for (int i = 0; i < movieFrame.width; i++) {
      char pix = screen_map[i][j];
      
      if (pix >= NUM_PIXELS) continue;  // outside the rose shape, so blank
      
      // Pull pixel location and color from picture
      int imageloc = i + j*movieFrame.width;
      RGBColor rgb = new RGBColor(red(movieFrame.pixels[imageloc]),
                                 green(movieFrame.pixels[imageloc]),
                                blue(movieFrame.pixels[imageloc]));
                                
      pixelarray.StuffPixelWithColor(pix, rgb);
    }
  }
}

void movieEvent(Movie m) {
  boolean width_dominate = true;
  
  m.read();        // Get the next movie frame
  m.loadPixels();  // Load frame into memory
  
  // Black out movieFrame - May need to restore this
  /*
  for (int i=0; i < movieFrame.pixels.length; i++) {
    movieFrame.pixels[i] = color(0,0,0);
  }
  */
  
  // Is the "m" movie too narrow?
  if (m.width < m.height) {
    int new_height = m.width;
    
    movieFrame.copy(m,0,0,m.width,m.height, // (src,sx,sy,sw,sh
      0, (movieFrame.height-new_height)/2,  // dx,dy
      movieFrame.width,new_height);         // dw,dh) 

  } else {  // No - make height the dominate value
    int new_width = m.height;
    
    movieFrame.copy(m,0,0,m.width,m.height, // (src,sx,sy,sw,sh
      (movieFrame.width-new_width)/2, 0,    // dx,dy 
      new_width,movieFrame.height);         // dw,dh)
  }
}

void turnOnMovie() {
  String movieName = movie_titles[movie_number] + ".mov";
  println("Starting " + movieName);
  myMovie = new Movie(this, movieName);
  myMovie.loop();
}

void nextMovie() {
  myMovie.stop();
  movie_number = (movie_number + 1) % movie_titles.length;
  turnOnMovie();
}

void movePixelsToBuffer() {
  for (int i = 0; i < NUM_PIXELS; i++) {
    RGBColor rgb = pixelarray.GetPixelColor((char)i);
    int r = (int)rgb.r;
    int g = (int)rgb.g;
    int b = (int)rgb.b;
    
    for (int rose = 0; rose < numBigRose; rose++) {
      sendColorOut(rose, i, r, g, b, false);
    }
  }
}

// Get helper functions
//
// Makes code more readable
// No out-of-bounds error handling. Make sure grid# is valid!
int getBigX(int grid) { return (BigRoseCoord[grid][0]); }
int getBigY(int grid) { return (BigRoseCoord[grid][1]); }

//
// minBigX
//
// Smallest BigX value
int minBigX() {
  int min_x = getBigX(0);
  for (int i=1; i<numBigRose; i++) {
    if (getBigX(i) < min_x) min_x = getBigX(i);
  }
  return min_x;
}

//
// minBigY
//
// Smallest BigY value
int minBigY() {
  int min_y = getBigY(0);
  for (int i=1; i<numBigRose; i++) {
    if (getBigY(i) < min_y) min_y = getBigY(i);
  }
  return min_y;
}

//
// grid_width
//
// How many roses across is the big grid?
float grid_width() {
  
  int min_x = getBigX(0);
  int max_x = min_x;
  int new_x;
  
  for (int i=1; i<numBigRose; i++) {
    new_x = getBigX(i);
    if (new_x < min_x) min_x = new_x;
    if (new_x > max_x) max_x = new_x;
  }
  return (max_x - min_x);
}

//
// grid_height
//
// How many rose high is the big grid?
int grid_height() {
  
  if (TILING == false) return 1;
  
  int min_y = getBigY(0);
  int max_y = min_y;
  int new_y;
  
  for (int i=1; i<numBigRose; i++) {
    new_y = getBigY(i);
    if (new_y < min_y) min_y = new_y;
    if (new_y > max_y) max_y = new_y;
  }
  return (max_y - min_y + 1);
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
    floodFillUtil(x, y, p, d, getColor(x,y), newC, mapping);
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
void floodFillUtil(int x, int y, byte p, byte d, color prevC, color newC, boolean mapping)
{
    byte big_grid = 0;
    char leaf = GetLightFromCoord(p,d,big_grid);
    
    // Base case
    if (x < 0 || x >= ROSE_DIAM || y < 0 || y >= ROSE_DIAM) return;
    if (getColor(x,y) != prevC) return;
 
    // Replace the color at (x,y)
    if (mapping) {
      screen_map[x][y] = leaf;      
    }
    putColor(x,y,newC);
 
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
  
  for (int x=0; x<ROSE_DIAM; x++) {
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
int getLeafNum(byte p, byte d) {
  return (((p * 6) + d) % NUM_PIXELS);
}

//
// Get Rose Offset
//
// Returns the x,y coordinate of an offset point
// Need to add the screen border for actual offset
// Petal is 0-23 number
// distance is 0-11 along the petal with 6 as the outside leaf
//
Coord GetRoseOffset(int petal, int distance) {
  petal = (((petal % 5) * 5) + (petal / 5)) % 24; // correct petals to line them up concurrently
  
  float t = PI * 7/12.0 * (petal + ((distance*7)+7)/100.0);
  float r = (ROSE_DIAM/2.0) * sin(12/7.0 * t);  // k/d = 12/7 = 1.7143
  float x = r * cos(t) + ROSE_DIAM/2;
  float y = r * sin(t) + ROSE_DIAM/2;
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
void fillScreen(char value) {
  for (int x=0; x<ROSE_DIAM; x++) {
    for (int y=0; y<ROSE_DIAM; y++) {
      screen_map[x][y] = value;
    }
  }
}

// makeRoseGrid
//
RoseForm makeRoseGrid(int big_x, int big_y, byte big_num) {
  
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
    // Draws each leaf at a time - may be slower
    /*
    for (Rose r : roses) {
      r.draw();
    }
    */
  }
  
  // Raster over the screen_map. Fill each pixel with the appropriate leaf color
  void bulk_draw() {
    int x,y;
    char pixel;
    for (x = 0; x < ROSE_DIAM; x++) {
      for (y = 0; y < ROSE_DIAM; y++) {
        pixel = screen_map[x][y];
        if (pixel < NUM_PIXELS) {    // a leaf spot
          putColor(x,y, pix_color[pixel]);
        }
      }
    }
  }
  
  // Drawing the rose grid
  void draw_grid() {
    color black = color(0,0,0);
    for(float t = 0; t <= 24*PI; t += DENSITY) {
      float r = (ROSE_DIAM/2.0) * cos(12/7.0 * t);  // k/d = 12/7
 
      // Polar to Cartesian conversion
      int x = int(r * cos(t) + ROSE_DIAM/2);
      int y = int(r * sin(t) + ROSE_DIAM/2);
      
      putColor(x,y,black);
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
  byte big_num; // strip number
  char LED;     // LED number on the strand
  color c;
  
  Rose(byte xcoord, byte ycoord, byte big_num) {
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
char GetLightFromCoord(byte p, byte d, byte grid) {
  int LED = (((5-d)/2)*48) + (p*2) + ((d+1)%2);
  
  if (d == 2 || d == 3) {  // Middle two rings of LEDs 48-95
    LED = LED+1;           // Shift the ring due to wiring
    if (LED >= 96) LED -= 48;
  }
  
  if (d <= 1) {   // Inner two rings of LEDs 96-143
    LED = LED+4;  // Shift the ring due to wiring
    if (LED >= 144) LED -= 48;
  }
  return char(LED);
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
  // morphing
  if (cmd.charAt(0) == 'M') {
    goMorphing(Integer.valueOf(cmd.substring(1, cmd.length())));
  
  // video 
  } else if (cmd.charAt(0) == 'V') {
    startVideo(cmd.substring(1, cmd.length()));
  
  // Pixel command
  } else {  
    processPixelCommand(cmd);
  }
}
  
void processPixelCommand(String cmd) {
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
  
  sendColorOut(rose, pix, r, g, b, false);
  
  //println(String.format("setting pixel:%d,%d to r:%d g:%d b:%d", rose, pix, r, g, b));
  
  if (VIDEO_STATE) {  // Video is running - need to turn it off
    myMovie.stop();
    println("Stopping movie");
    VIDEO_STATE = false;
  }
}

// Process a morph command
void goMorphing(int morph) {
  morph_frame(morph);
  sendDataToLightsAndScreen();
  if (morph == 10) {
    pushColorBuffer();   // Push the frame buffers: next -> current
  }
}

// Start a movie
void startVideo(String movie) {
  String movieName = movie + ".mov";
  println("Starting " + movieName);
  myMovie = new Movie(this, movieName);
  myMovie.loop();
  VIDEO_STATE = true;
}

// Make the screen and lights go!
void sendDataToLightsAndScreen() {
  sendDataToLights();  // Dump data into lights
  if (UPDATE_VISUALIZER) drawRoses();  // Update visualizer  
}

// Send a corrected color to a rose pixel on screen and in lights
void sendColorOut(int rose, int pix, int r, int g, int b, boolean morph) {
  color correct = colorCorrect(r,g,b);
  
  r = adj_brightness(red(correct));
  g = adj_brightness(green(correct));
  b = adj_brightness(blue(correct));
  
  roseGrid[rose].setCellColor(color(r,g,b), pix);  // Simulator
  setPixelBuffer(rose, pix, r, g, b, morph);  // Lights: sets next-frame  
}

//
//  Fractional morphing between current and next frame
//
//  morph is an integer representation morph/10 fraction towards the next fram
//
void morph_frame(int morph) {
  int r,g,b;
  int rose,pix;
  float fract = morph / 10.0;
  
  for (rose = 0; rose < numBigRose; rose++) {
    for (pix = 0; pix < NUM_PIXELS; pix++) {
      if (hasChanged(rose, pix)) {
        r = interp(curr_buffer[rose][pix][0], next_buffer[rose][pix][0], fract);
        g = interp(curr_buffer[rose][pix][1], next_buffer[rose][pix][1], fract);
        b = interp(curr_buffer[rose][pix][2], next_buffer[rose][pix][2], fract);
        
        sendColorOut(rose, pix, r, g, b, true);
      }
    }
  }
}  

int interp(int a, int b, float fract) {
  return (int(a + (fract * (b-a))));
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
      setPixelBuffer(t, p, 0,0,0, false);
    }
  }
  pushColorBuffer();
}

void setPixelBuffer(int BigRose, int pixel, int r, int g, int b, boolean morph) {
  BigRose = bounds(BigRose, 0, numBigRose-1);
  pixel = bounds(pixel, 0, NUM_PIXELS-1);
  
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

color getPixelBuffer(int BigRose, int pixel) {
  BigRose = bounds(BigRose, 0, numBigRose-1);
  pixel = bounds(pixel, 0, NUM_PIXELS-1);
  
  return color(morph_buffer[BigRose][pixel][0],
               morph_buffer[BigRose][pixel][1],
               morph_buffer[BigRose][pixel][2]);
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
