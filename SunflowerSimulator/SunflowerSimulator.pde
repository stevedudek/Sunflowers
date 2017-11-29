/*

  Sunflower Simulator and Lighter
  
  FOR THE EXPLORATORIUM
  
  1. Simulator: draws sunflower shape on the monitor
  2. Lighter: sends data to the lights
  
  11/27/17 
  
  Built on glorious Rose + Triangle Simulator
  
  (s,i) coordinates are (s,i) = (sunflower,pixel) coordinates.
  s = 0 - 3; i = 0 - 272
  
  Includes hsb interpolation of colors
  
  Turn on the coordinates to see the system.
    
*/

byte NUM_SUNFLOWERS = 2;  // Number of Big Sunflowers
int NUM_LEDS = 273;
int SPIRAL_COUNT = 21;  // spiral_count in Tom's code
int MAX_DIST = 14;
int NUM_PETALS = SPIRAL_COUNT * MAX_DIST;

//
// Pixel pusher stuff
//
import com.heroicrobot.dropbit.registry.*;
import com.heroicrobot.dropbit.devices.pixelpusher.Pixel;
import com.heroicrobot.dropbit.devices.pixelpusher.Strip;
import com.heroicrobot.dropbit.devices.pixelpusher.PixelPusher;
import com.heroicrobot.dropbit.devices.pixelpusher.PusherCommand;

import processing.net.*;
import java.util.*;
import java.util.regex.*;

import java.awt.Color;

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
Strip[] strip_array = new Strip[NUM_SUNFLOWERS * 2];

//
// End Pixel pusher stuff
//

// TILING
// true: show all sunflowers and let each sunflower act differently
// false: show only one sunflower (0) and force all sunflowers to act the same way
boolean TILING = true;  // Tiling!
byte[] big_x = { 1,2,3,2 };
byte[] big_y = { 1,1,1,2 };
int DRAW_LABELS = 0;  // enumerated type: 0=(p,d) label, 1=(strip,pixel), 2=labels off
boolean TOP_UP = true;  // Whether to draw sunflower as concave or convex
int BRIGHTNESS = 80;  // A percentage
int COLOR_STATE = 0;  // no enum types in processing. Messy

// Color buffers: [s][i][r,g,b]
// Several buffers permits updating only the lights that change color
short[][][] curr_buffer = new short[NUM_SUNFLOWERS][NUM_LEDS][3];
short[][][] next_buffer = new short[NUM_SUNFLOWERS][NUM_LEDS][3];
short[][][] morph_buffer = new short[NUM_SUNFLOWERS][NUM_LEDS][3];

// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = false;  // turn false for LED-only updates
int SPIRAL_SIZE = 500;  // This is the value to change for Screen Size
int CONTROL_HEIGHT = 50; // Height on the bottom control bar
int SCREEN_WIDTH = SPIRAL_SIZE * big_x[NUM_SUNFLOWERS-1];
int SCREEN_HEIGHT = (SPIRAL_SIZE * big_y[NUM_SUNFLOWERS-1]) + CONTROL_HEIGHT;
float BORDER = 0.1; // How much fractional edge between sunflower and screen
float SUNFLOWER_RAD = SPIRAL_SIZE * (1.0 - (2 * BORDER)) / 2;  // Sunflower size
float PETAL_RAD = SUNFLOWER_RAD * 0.08;  // Size of a petal

// holy of holies
float phi = ( sqrt( 5) + 1) / 2;  
float golden_angle = ( 3 - sqrt( 5)) * PI;

SunForm sunGrid;  // Grid model of Sunflower holds all the Petal objects

// Timing variables needed to control regular morphing
int delay_time = 10000;  // delay time length in milliseconds (dummy initial value)
long start_time = millis();  // start time point (in absolute time)
long last_time = start_time;

// Brute-force arrays of strip and pixel for each i
byte[] SPIRAL_ORDER = {
  12, 20, 7, 15, 2, 10, 18, 5, 13, 0, 8, 16, 3, 11, 19, 6, 14, 1, 9, 17, 4 };

byte[] led_lookup_strip = {
  1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,
  1,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1,1,
  0,1,0,0,1,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,0,1,0,0,
  1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,
  0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,0,0,
  1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,
  0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,
  1,0,0,1,0,1,0,0 };
  
int[] led_lookup_pixel = {
  80,94,0,108,66,53,121,13,81,93,26,134,40,54,120,12,107,67,27,135,39,79,95,
  1,109,65,52,122,14,82,92,25,133,41,55,119,11,106,68,28,136,38,78,96,2,110,
  64,51,123,15,83,91,24,132,42,56,118,10,105,69,29,137,37,77,97,3,111,63,50,
  124,16,84,90,23,131,43,57,117,9,104,70,30,138,36,76,98,4,112,62,49,125,17,
  85,89,22,130,44,58,116,8,103,71,31,139,35,75,99,5,113,61,48,126,18,86,88,
  21,129,45,59,115,7,102,72,32,140,34,74,100,6,114,60,47,127,19,87,87,20,128,
  46,60,114,6,101,73,33,141,33,73,101,7,115,59,46,128,20,88,86,19,127,47,61,
  113,5,100,74,34,140,32,72,102,8,116,58,45,129,21,89,85,18,126,48,62,112,4,
  99,75,35,139,31,71,103,9,117,57,44,130,22,90,84,17,125,49,63,111,3,98,76,
  36,138,30,70,104,10,118,56,43,131,23,91,83,16,124,50,64,110,2,97,77,37,137,
  29,69,105,11,119,55,42,132,24,92,82,15,123,51,65,109,1,96,78,38,136,28,68,
  106,12,120,54,41,133,25,93,81,14,122,52,66,108,0,95,79,39,135,27 };

//
// Setup
//
// Calculate just once:
// 1. The screen position of all petals, indexed by (i),
// 2. The conversion of (s,p,d) petals coordinates to (strip, pixel) LEDs   
// 
void setup() {
  
  size(SCREEN_WIDTH, SCREEN_HEIGHT);
  stroke(0);
  fill(255,255,0);
  
  frameRate(40); // 10? default 60 seems excessive
  
  // Pixel Pusher stuff
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  colorMode(RGB, 255);
  prepareExitHandler();
  strips = registry.getStrips();
  
  _server = new Server(this, port);
  println("server listening:" + _server);
  
  initializeColorBuffers();  // Stuff curr/next/morph frames with zeros (all black)
  
  background(200);  // gray
  
  sunGrid = new SunForm();  // Set up the Big Sunflowers and stuff in petals
  sunGrid.draw();        // Draw all the petals
  drawBottomControls();
}

//
// Draw - Main function
//
void draw() {
  pollServer();          // Get messages from python show runner
  update_morph();        // Morph between current frame and next frame 
  sunGrid.draw();        // Draw all the petals
  sunGrid.drawLabels();  // Labels need to drawn on top of petals
  sendDataToLights();    // Turn on all lights
}

//
// Bottom Control functions
//
void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-21) {
    
    // Draw labels button
    DRAW_LABELS = (DRAW_LABELS + 1) % 4;  // 0-1-2 state
  
  }  else if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    
    // Invert button  
    if (TOP_UP) {
      TOP_UP = false;
    } else {
      TOP_UP = true;
    }
     
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-21) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
   
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    
    // Bright up checkbox
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
  
  }  else if (mouseX > 400 && mouseX < 420 && mouseY > SCREEN_HEIGHT-40 && mouseY < SCREEN_HEIGHT-20) {
    // No color correction  
    COLOR_STATE = 0;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-21) {
    // None red  
    COLOR_STATE = 1;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    // All red  
    COLOR_STATE = 4;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-31) {
    // None blue  
    COLOR_STATE = 2;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    // All blue  
    COLOR_STATE = 5;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-31) {
    // None green  
    COLOR_STATE = 3;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    // All green  
    COLOR_STATE = 6;
  
  }
  drawBottomControls();
}

void drawBottomControls() {
  rectMode( CORNER);
  
  // draw a bottom white region
  fill(255,255,255);
  rect(0,SCREEN_HEIGHT-50,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_HEIGHT-50,140,SCREEN_HEIGHT+10);
  line(290,SCREEN_HEIGHT-50,290,SCREEN_HEIGHT+10);
  line(470,SCREEN_HEIGHT-50,470,SCREEN_HEIGHT+10);
  
  // draw checkboxes
  stroke(0);
  fill(255);
  
  drawCheckbox(20,SCREEN_HEIGHT-46,15, color(255,255,255), false);  // label checkbox
  drawCheckbox(20,SCREEN_HEIGHT-28,15, color(255,255,255), false);  // invert checkbox
  
  rect(200,SCREEN_HEIGHT-46,15,15);  // minus brightness
  rect(200,SCREEN_HEIGHT-28,15,15);  // plus brightness
  
  drawCheckbox(340,SCREEN_HEIGHT-46,15, color(255,0,0), COLOR_STATE == 1);
  drawCheckbox(340,SCREEN_HEIGHT-28,15, color(255,0,0), COLOR_STATE == 4);
  drawCheckbox(360,SCREEN_HEIGHT-46,15, color(0,255,0), COLOR_STATE == 2);
  drawCheckbox(360,SCREEN_HEIGHT-28,15, color(0,255,0), COLOR_STATE == 5);
  drawCheckbox(380,SCREEN_HEIGHT-46,15, color(0,0,255), COLOR_STATE == 3);
  drawCheckbox(380,SCREEN_HEIGHT-28,15, color(0,0,255), COLOR_STATE == 6);
  
  drawCheckbox(400,SCREEN_HEIGHT-40,20, color(255,255,255), COLOR_STATE == 0);
    
  // draw text labels in 12-point Helvetica
  fill(0);
  textAlign(LEFT);
  PFont f = createFont("Helvetica", 12, true);
  textFont(f, 12);  
  text("Labels", 50, SCREEN_HEIGHT-34);
  text("Invert", 50, SCREEN_HEIGHT-16);
  
  text("-", 190, SCREEN_HEIGHT-34);
  text("+", 190, SCREEN_HEIGHT-16);
  text("Brightness", 225, SCREEN_HEIGHT-25);
  textFont(f, 20);
  text(BRIGHTNESS, 150, SCREEN_HEIGHT-22);
  
  textFont(f, 12);
  text("None", 305, SCREEN_HEIGHT-34);
  text("All", 318, SCREEN_HEIGHT-16);
  text("Color", 430, SCREEN_HEIGHT-25);
  
  int font_size = 12;  // default size
  f = createFont("Helvetica", font_size, true);
  textFont(f, font_size);
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

//
// SunForm class - holds all the petals as a [s][i] array of Petal objects
//
class SunForm {
  Petal[][] petals;  // (s,i)
  int[] petal_order;  // Lookup list of the i-coordinate order to draw petals 
  
  SunForm() {
    // Sets up a new SunForm and stuffs in all the petals
    this.petals = new Petal[NUM_SUNFLOWERS][NUM_LEDS];
    this.petal_order = new int[NUM_LEDS];
    
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      for (int i = 0; i < NUM_LEDS; i++) {
          Petal new_petal = new Petal(s, i);
          this.petals[s][i] = new_petal;  // Add one petal at a time
          this.petal_order[i] = i;  // Store its position in order
      }
    }
  }
  
  byte get_strip(byte s, int i) {
    return byte(this.petals[s][i].strip_led.c1);
  }
  
  int get_led(int i) {
    return this.petals[0][i].strip_led.c2;
  }
  
  float get_dist(int i1, int i2) {
    float x1 = this.petals[0][this.petal_order[i1]].xy.c1;
    float y1 = this.petals[0][this.petal_order[i1]].xy.c2;
    float x2 = this.petals[0][this.petal_order[i2]].xy.c1;
    float y2 = this.petals[0][this.petal_order[i2]].xy.c2;
    
    return sqrt(sq(x2 - x1) + sq(y2 - y1));
  }
  
  void draw() {
    // Draw all petals in  order using the petal_order lookup table
    if (TOP_UP) {
      for (int i = NUM_LEDS-1; i >= 0; i--) {
        draw_all_petals_num(i);
      }
    } else {
      for (int i = 0; i < NUM_LEDS; i++) {
        draw_all_petals_num(i);
      }
    }
  }
  
  void draw_all_petals_num( int i) {
    // Draw petals numbered i for all sunflowers
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      petals[s][this.petal_order[i]].draw();  // Have each petal draw itself
    }
  }
  
  void drawLabels() {
    // Draw all the numbered labels
    if (DRAW_LABELS == 4) {  // 4 = No Label
      return;
    }
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      for (int i = 0; i < NUM_LEDS; i++) {
        petals[s][i].drawLabel();  // Have each petal draw its own label
      }
    }
  }
  
  void setCellColor(int s, int i, color c) {
    petals[s][i].setColor(c);  // Have each petal store its own color
  }
}

//
// Petal class - holds a ton of information about each petal
//
// A lot of calculations are done just once when the petal is created
//
class Petal {
  int petal;  // petal number on the sunflower
  byte s;  // which large sunflower
  int p;  // angular petal coordinate
  int d;  // radial distance coordinate
  Coord xy;  // screen x, y (floats)
  Coord rtheta;  // screen r, theta (floats)
  Coord_int strip_led; // (strip, led) coordinate
  String p_d_id; // label of "p, d"
  String strip_led_id; // label of "strip, led"
  color c;  // (r, g, b)
  
  Petal(byte s, int i) {
    this.s = s;
    this.p = get_spiral_order(i % 21); //  Re-order the spiral arms here
    this.d = int(i / 21);
    this.petal = i;
    this.xy = calc_xy(this.s, this.petal);
    this.rtheta = calc_rtheta(this.s, this.petal);
    //this.angle = (  float(this.petal+1) * golden_angle  ) + ( PI / 2);
    this.strip_led = calc_led(this.s, this.petal);
    this.p_d_id = get_p_d_id(this.p, this.d);
    this.strip_led_id = get_strip_led_id(this.strip_led);
    this.c = color(255,255,255);  // Start white
  }
  
  String get_p_d_id(int p, int d) {
    int[] coords = new int[2];
    coords[0] = p;
    coords[1] = d;
    return join(nf(coords, 0), ",");
  }
  
  String get_strip_led_id(Coord_int strip_led) {
    int[] coords = new int[2];
    coords[0] = strip_led.c1;
    coords[1] = strip_led.c2;;
    return join(nf(coords, 0), "-");
  }
  
  Coord_int get_strip_led() {
    return this.strip_led;
  }
  
  void setColor(color c) {
    this.c = c;
  }
  
  void drawLabel() {
    // toggle text label between light number and x,y coordinate
    String text = "";
    switch (DRAW_LABELS) {
      case 0:  
        break;
      case 1:
        text = this.p_d_id;
        break;
      case 2:
        text = str(this.petal);
        break;
      case 3:
        text = this.strip_led_id;
        break;
    }
    rectMode( RADIUS);
    textAlign( CENTER);
    
    pushMatrix();
    translate( this.xy.c1, this.xy.c2);
    rotate( this.rtheta.c2 );
    translate( 0, -1.8 * PETAL_RAD);
    fill( 0, 0, 255, 255);
    text( text, 0, 0);
    popMatrix();
    
  }
  
  void draw() {
    // Draw just the petal - all this is from Thomas T. Landers
    float x = this.xy.c1;
    float y = this.xy.c2;
    float orient = this.rtheta.c2;
    float radius = PETAL_RAD;
    
    fill(this.c);
    smooth();
    stroke(0);
    
    rectMode( RADIUS);

    pushMatrix();
    translate( x, y);
    rotate( orient );

    beginShape();
    vertex( 0 + radius, 0 - 2*radius); // top right
    vertex( 0 + radius, 0); // bottom right
    vertex( 0 - radius, 0); // bottom left
    vertex( 0 - radius, 0 - 2*radius); // top left
    curveVertex( 0 - radius, 0 );             // FCP
    curveVertex( 0 - radius, 0 - 2*radius);   // FDP starting from top left
    curveVertex( 0 - radius/2, 0 - (( 2.8 ) * radius));
    curveVertex( 0, 0 - 3*radius);            // midpoint
    curveVertex( 0 + radius/2, 0 - (( 2.8 ) * radius));
    curveVertex( 0 + radius, 0 - 2*radius);   // LDP
    curveVertex( 0 + radius, 0 );             //LCP

    endShape();
    popMatrix();
  } // end drawPetal
  
  Coord calc_xy(byte sunflower, int i) {
    // Calculate the x,y-screen position for the petal
    float ratio =  float(i+1) / float( NUM_PETALS);
    float angle = (  float(i+1) * golden_angle  ) - ( PI / 2);
    float spiral_rad = ratio * SUNFLOWER_RAD;
    float x = calc_x_offset(sunflower) + cos( angle) * spiral_rad;
    float y = calc_y_offset(sunflower) + sin( angle) * spiral_rad;
    Coord coord = new Coord(x,y);
    return coord;
  }
  
  float calc_x_offset(byte sunflower) { 
    byte x_offset = big_x[NUM_SUNFLOWERS-1];
    float fract_x = float(((sunflower % x_offset) * 2) + 1) / (2 * x_offset);
    return fract_x * width;
  }
   
  float calc_y_offset(int sunflower) {
    float fract_y = 0.5;  // default
    if (NUM_SUNFLOWERS == 4) {
      fract_y = (((sunflower / 2) * 2) + 1) / 4.0;
    }
    return fract_y * (SCREEN_HEIGHT - 50);
  }
  
  Coord calc_rtheta(int sunflower, int i) {
    // Calculate the r,theta-screen position for the petal
    // sunflower (s) not used yet, but will be used in later versions
    float ratio =  float(i+1) / float( NUM_PETALS);
    float angle = float(i+1) * golden_angle;
    float spiral_rad = ratio * SUNFLOWER_RAD;
    Coord coord = new Coord(spiral_rad, angle);
    return coord;
  }
  
  Coord_int calc_led(byte sunflower, int i) {
    // convert (s, i) coordinates into (strip, pixel) with lookup tables
    int s = (sunflower * 2) + led_lookup_strip[i];
    int pixel = led_lookup_pixel[i];
    Coord_int coord = new Coord_int(s, pixel);
    return coord;
  }
  
  int get_petal_num(int p, int d) {
    return p + (d * SPIRAL_COUNT);
  }
  
  int get_spiral_order(int p) {
//    return ((20 - p) * 13) % 21;
    return SPIRAL_ORDER[(24 - p) % 21];
  }
}

//
// Two Coord classes to enable function returns of 2 values (either int's or float's) 
//
class Coord {
  public float c1, c2;
  
  Coord(float c1, float c2) {
    this.c1 = c1;
    this.c2 = c2;
  }
}

class Coord_int {
  public int c1, c2;
  
  Coord_int(int c1, int c2) {
    this.c1 = c1;
    this.c2 = c2;
  }
}

//
//  Server Routines - How to convert streaming ASCII into commands
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
//      println(msg);
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

//
// 2 wildcard commands:
//
// X = Finish a morph cycle (clean up by pushing the frame buffers)
// D(int) means delay for int milliseconds (but keeping morphing)
//
// Otherwise, process 5 integers as (s,i, r,g,b)
//
void processCommand(String cmd) {
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle();
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time = Integer.valueOf(cmd.substring(1, cmd.length()));
  } else {  
    processPixelCommand(cmd);  // Pixel command
  }
}
  
void processPixelCommand(String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    //println(cmd);
    println("ignoring input!");
    return;
  }
  byte s    =    Byte.valueOf(m.group(1));
  int i     = Integer.valueOf(m.group(2));
  int r     = Integer.valueOf(m.group(3));
  int g     = Integer.valueOf(m.group(4));
  int b     = Integer.valueOf(m.group(5));
  
  sendColorOut(s, i, (short)r, (short)g, (short)b, false);  
//  println(String.format("setting pixel:%d,%d to r:%d, g:%d, b:%d", s, i, r, g, b));
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by morphing to the max and pushing the frame buffer
//
void finishCycle() {
//  morph_frame(1.0);  // Causes jerky animations (removed)
  pushColorBuffer();
  start_time = last_time;  // = millis(); // reset the clock
}

//
// Update Morph
//
void update_morph() {
  last_time = millis();  // update clock
  // Fractional morph over the span of delay_time
  morph_frame((last_time - start_time) / (float)delay_time); 
}

// Send a corrected color to a sunflower pixel on screen and in lights
void sendColorOut(byte s, int i, short r, short g, short b, boolean morph) {
  color correct = colorCorrect(r,g,b);  // all-red, all-blue, etc.
  
  r = (short)red(correct);
  g = (short)green(correct);
  b = (short)blue(correct);
  
  if (TILING) {
    sunGrid.setCellColor(s, i, color(r,g,b));  // Simulator
    setPixelBuffer(s, i, r, g, b, morph);  // Lights: sets next-frame buffer (doesn't turn them on)
  } else {
    if (s == 0) {
      for (byte s_num = 0; s_num < NUM_SUNFLOWERS; s_num++) {
        sunGrid.setCellColor(s_num, i, color(r,g,b));  // Simulator
        setPixelBuffer(s, i, r, g, b, morph);  // Lights: sets next-frame buffer (doesn't turn them on)
      }
    }
  }
}

//
//  Routines to interact with the Lights
//
void sendDataToLights() {
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(10);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    int strip_num, pixel, brightness;     
    Coord_int strip_led;
    
    List<Strip> strip_list = registry.getStrips();
    
    strip_num = 0;
    for (Strip strip : strip_list) {
      if (strip_num < strip_array.length) {
        strip_array[strip_num] = strip;
        strip_num++;
      }
    }
    
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      brightness = calcBrightness(s);
      for (short i = 0; i < NUM_LEDS; i++) {
        strip_led = sunGrid.petals[s][i].get_strip_led();
        strip_num = strip_led.c1;
        pixel = strip_led.c2;
        
        if (strip_num < strip_array.length && strip_array[strip_num] != null) {
          strip_array[strip_num].setPixel(adj_brightness(getPixelBuffer(s,i), brightness), pixel);
        }
      }
    }
  }
}

private void prepareExitHandler () {

  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {

    public void run () {

      System.out.println("Shutdown hook running");

      List<Strip> strips = registry.getStrips();
      for (Strip strip : strips) {
        for (int i = 0; i < strip.getLength(); i++)
          strip.setPixel(#000000, i);
      }
      for (int i=0; i < 100000; i++) {
        Thread.yield();
      }
    }
  }
  ));
}

//
//  Routines for the strip buffer
//
color adj_brightness(color c, int brightness) {
  if (brightness == 100) {
    return c;  // No adjustment needed at full brightness
  }
  return color(  red(c) * brightness / 100.0,
               green(c) * brightness / 100.0,
                blue(c) * brightness / 100.0);
}

int calcBrightness(byte s) {
  if (BRIGHTNESS == 100) {
    return BRIGHTNESS;  // No calculation needed at full brightness
  }
  
  color c;
  long total = 0;
  
  for (short i = 0; i < NUM_LEDS; i++) {
    c = getPixelBuffer(s,i);
    total += (red(c) + green(c) + blue(c));
  }
  
  int power_fract = (int)(total * 100 / (NUM_LEDS * 255 * 3));
  
  if (power_fract > BRIGHTNESS) {
    return BRIGHTNESS;
  } else {
    return 100;
  }
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
  short empty = 0;
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      setPixelBuffer(s, i, empty,empty,empty, false);
    }
  }
  pushColorBuffer();
}

//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0 - 1.0 fraction towards the next frame
//
void morph_frame(float fract) {
  color c1, c2, interp;
  short r,g,b;
  
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      c1 = color(curr_buffer[s][i][0], curr_buffer[s][i][1], curr_buffer[s][i][2]);
      c2 = color(next_buffer[s][i][0], next_buffer[s][i][1], next_buffer[s][i][2]);      
      
      interp = lerpColor(c1, c2, fract);
      
      r = (short)(interp >> 16 & 0xFF);
      g = (short)(interp >> 8 & 0xFF);
      b = (short)(interp & 0xFF);
      
      sendColorOut(s,i, r,g,b, true);
    }
  }
}

/*  COMPLEX RGB-HSV MORPHING CODE (deprecated)
//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0 - 1.0 fraction towards the next frame
//
//  Check several simple base cases before doing full rgb <-> hsb interpolation
//
void morph_frame(float fract) {
  short r,g,b;
  short r1,g1,b1;
  short r2,g2,b2;
  
  float[] hsb_c1 = { 0, 0, 0 };
  float[] hsb_c2 = { 0, 0, 0 };
  float[] hsb_inter = { 0, 0, 0 };
  
  Color c;
  
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      r1 = curr_buffer[s][i][0];
      g1 = curr_buffer[s][i][1];
      b1 = curr_buffer[s][i][2];
      
      r2 = next_buffer[s][i][0];
      g2 = next_buffer[s][i][1];
      b2 = next_buffer[s][i][2];
                
      if (fract <= 0) {
        r = r1; g = g1; b = b1;  // Fract = 0; Send back 1st color
      } else if (fract >= 1) {
        r = r2; g = g2; b = b2;  // Fract = 1; Send back 2nd color
      } else if (r1 == r2 && g1 == g2 && b1 == b2) {
        r = r1; g = g1; b = b1;  // Same color; Send back 1st color
      } else if (isBlack(r1, g1, b1) || isBlack(r2, g2, b2)) {  // Blacks. do RGB interp.
        r = interp(curr_buffer[s][i][0], next_buffer[s][i][0], fract);
        g = interp(curr_buffer[s][i][1], next_buffer[s][i][1], fract);
        b = interp(curr_buffer[s][i][2], next_buffer[s][i][2], fract);
      } else {
        // Need to hsb-interpolate between colors
        hsb_c1 = Color.RGBtoHSB((int)r1, (int)g1, (int)b1, null);
        hsb_c2 = Color.RGBtoHSB((int)r2, (int)g2, (int)b2, null);
        
        hsb_inter[0] = interpolate_wrap(hsb_c1[0], hsb_c2[0], fract);  // h
        hsb_inter[1] =     interp_float(hsb_c1[1], hsb_c2[1], fract);  // s
        hsb_inter[2] =     interp_float(hsb_c1[2], hsb_c2[2], fract);  // b
        
        c = Color.getHSBColor(hsb_inter[0], hsb_inter[1], hsb_inter[2]);
        
        r = (short)(c.getRed());
        g = (short)(c.getGreen());
        b = (short)(c.getBlue());
      }
      sendColorOut(s,i, r,g,b, true);
    }
  }
}
*/

/*  SIMPLIFIED RGB-only MORPHING CODE (deprecated)
//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0-1.0 fraction towards the next frame
//
//  Simple RGB-interpolation (no hsb)
//
void morph_frame(float fract) {
  short r,g,b;
  
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      r = interp(curr_buffer[s][i][0], next_buffer[s][i][0], fract);
      g = interp(curr_buffer[s][i][1], next_buffer[s][i][1], fract);
      b = interp(curr_buffer[s][i][2], next_buffer[s][i][2], fract);
      
      sendColorOut(s,i, r,g,b, true);
    }
  }
}


short interp(short a, short b, float fract) {
  return (short)(a + (fract * (b-a)));
}

float interp_float(float a, float b, float fract) {
  return a + (fract * (b-a));
}

float interpolate_wrap(float a, float b, float fract)
{
  float distCCW, distCW;

  if (a >= b) {
    distCW = 1 + b - a;
    distCCW = a - b; 
  } else {
    distCW = b - a;
    distCCW = 1 + a - b;
  }
  if (distCW <= distCCW) {
    return a + interp_float(0, distCW, fract);
  } else {
    return a - interp_float(0, distCCW, fract);
  }
}

*/

void setPixelBuffer(byte s, int i, short r, short g, short b, boolean morph) {
  if (morph) {
    morph_buffer[s][i][0] = r;
    morph_buffer[s][i][1] = g;
    morph_buffer[s][i][2] = b;
  } else {
    next_buffer[s][i][0] = r;
    next_buffer[s][i][1] = g;
    next_buffer[s][i][2] = b;
  }
}

color getPixelBuffer(byte s, int i) {
  return color(morph_buffer[s][i][0],
               morph_buffer[s][i][1],
               morph_buffer[s][i][2]);
}

boolean hasChanged(byte s, int i) {
  if (curr_buffer[s][i][0] != next_buffer[s][i][0] ||
      curr_buffer[s][i][1] != next_buffer[s][i][1] ||
      curr_buffer[s][i][2] != next_buffer[s][i][2]) {
    return true;
  } else {
    return false;
  }
}

void pushColorBuffer() {
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      curr_buffer[s][i][0] = next_buffer[s][i][0];
      curr_buffer[s][i][1] = next_buffer[s][i][1];
      curr_buffer[s][i][2] = next_buffer[s][i][2];
    }
  }
}

boolean isBlack(short r, short g, short b) {
  return (r==0 && g==0 && b==0);
}

