/*

  Sunflower Simulator and Lighter
  
  1. Simulator: draws sunflower shape on the monitor
  2. Lighter: sends data to the lights
  
  4/21/17 
  
  Built on glorious Rose + Triangle Simulator
  
  (n,x,y) coordinates are (s,p,d) = (sunflower,petal, distance) coordinates.
  sunflower = large display, petal = spiral arm, distance = radial
  s = 0 (for now); p = 0-21; d = 0-17
  
  software handles clipped pixels and won't show them,
  so assume a full matrix from (0,0,0) to (0,20,16)
  Turn on the coordinates to see the system.
    
*/

byte NUM_SUNFLOWERS = 1;  // Number of Big Sunflowers
int NUM_LEDS = 288;
int SPIRAL_COUNT = 21;  // spiral_count in Tom's code
int MAX_DIST = 13; // 17 with clipping
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
// End Pixel pusher stuff
//

// TILING
// true: show all sunflowers and let each sunflower act differently
// false: show only one sunflower (0) and force all sunflowers to act the same way
boolean TILING = true;  // Tiling!
int DRAW_LABELS = 2;  // enumerated type: 0=(p,d) label, 1=(strip,pixel), 2=labels off
boolean TOP_UP = true;  // Whether to draw sunflower as concave or convex
int BRIGHTNESS = 100;  // A percentage
int COLOR_STATE = 0;  // no enum types in processing. Messy

// Color buffers: [s][p][d][r,g,b]
// Several buffers permits updating only the lights that change color
byte[][][][] curr_buffer = new byte[NUM_SUNFLOWERS][SPIRAL_COUNT][MAX_DIST][3];
byte[][][][] next_buffer = new byte[NUM_SUNFLOWERS][SPIRAL_COUNT][MAX_DIST][3];
byte[][][][] morph_buffer = new byte[NUM_SUNFLOWERS][SPIRAL_COUNT][MAX_DIST][3];

// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = true;  // turn false for LED-only updates
int SCREEN_SIZE = 500;  // This is the value to change for Screen Size
int SCREEN_WIDTH = SCREEN_SIZE * NUM_SUNFLOWERS;
float BORDER = 0.1; // How much fractional edge between sunflower and screen
int CONTROL_HEIGHT = 50; // Height on the bottom control bar
float SUNFLOWER_RAD = SCREEN_SIZE * (1.0 - (2 * BORDER)) / 2;  // Sunflower size
float PETAL_RAD = SUNFLOWER_RAD * 0.08;  // Size of a petal
float Z_MAX = SUNFLOWER_RAD;

// holy of holies
float phi = ( sqrt( 5) + 1) / 2;  
float golden_angle = ( 3 - sqrt( 5)) * PI;

// Petal Clipping to prevent crowding in the center
// Each item in th following array is a spiral arm
// Each number is how many to clip off the arm from the center
// List must add up to 16 long * 21 spiral_arms = 357 - 288 LEDs = 69 clipped pixels
int[] clip_list = { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 };

//int[] clip_list = { 0, 3, 1, 2, 0,
//                    3, 1, 2, 4, 4,
//                    4, 5, 4, 5, 4,
//                    4, 6, 4, 3, 6,
//                    4               };

// Change the "random" order of spiral arms into sequential
int[] spiral_order = { 12, 20, 7, 15, 2, 10, 18, 5, 13, 0, 8, 16, 3, 11, 19, 6, 14, 1, 9, 17, 4 };

SunForm sunGrid;  // Grid model of Sunflower holds all the Petal objects

// Timing variables needed to control regular morphing
int delay_time = 10000;  // delay time length in milliseconds (dummy initial value)
int start_time = millis();  // start time point (in absolute time)
int last_time = start_time;

//
// Setup
//
// Calculate just once the screen position of all petals,
// the conversion of (s,p,d) petals coordinates to (strip, pixel) LEDs   
// 
void setup() {
  
  size(SCREEN_WIDTH, SCREEN_SIZE + CONTROL_HEIGHT, P3D); // 50 for controls
  stroke(0);
  fill(255,255,0);
  
  frameRate(10); // 10? default 60 seems excessive
  
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
  
  drawBottomControls();
}

//
// Draw - Main function
//
void draw() {
  background( 255);
  camera(width/2, 0, 1.5 * height, 
    width/2, height/2, 0, 0, 1, 0);
  rotateX( 1 * PI / 4);
  
  pollServer();          // Get messages from python show runner
  update_morph();        // Morph between current frame and next frame 
  sunGrid.draw();        // Draw all the petals
  sunGrid.drawLabels();  // Labels need to drawn on top of petals
}

//
// Bottom Control functions
//
void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Draw labels button
    DRAW_LABELS = (DRAW_LABELS + 1) % 3;  // 0-1-2 state
  
  }  else if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    // Invert button  
    if (TOP_UP) {
      TOP_UP = false;
    } else {
      TOP_UP = true;
    }
     
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
   
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    // Bright up checkbox
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
  drawBottomControls();
}

void drawBottomControls() {
  rectMode( CORNER);
  
  // draw a bottom white region
  fill(255,255,255);
  rect(0,SCREEN_SIZE,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_SIZE,140,SCREEN_SIZE+40);
  line(290,SCREEN_SIZE,290,SCREEN_SIZE+40);
  line(470,SCREEN_SIZE,470,SCREEN_SIZE+40);
  
  // draw checkboxes
  stroke(0);
  fill(255);
  
  drawCheckbox(20,SCREEN_SIZE+4,15, color(255,255,255), false);  // label checkbox
  drawCheckbox(20,SCREEN_SIZE+22,15, color(255,255,255), false);  // invert checkbox
  
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
  text("Labels", 50, SCREEN_SIZE+16);
  text("Invert", 50, SCREEN_SIZE+34);
  
  text("-", 190, SCREEN_SIZE+16);
  text("+", 190, SCREEN_SIZE+34);
  text("Brightness", 225, SCREEN_SIZE+25);
  textFont(f, 20);
  text(BRIGHTNESS, 150, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("None", 305, SCREEN_SIZE+16);
  text("All", 318, SCREEN_SIZE+34);
  text("Color", 430, SCREEN_SIZE+25);
  
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
// SunForm class
//
// holds all the petals as a [s][p][d] array of Petal objects
//
class SunForm {
  Petal[][][] petals;
  Coord_int[] petal_order;  // Lookup list of the (p,d) coordinate order to draw petals 
  
  SunForm() {
    // Sets up a new SunForm and stuffs in all the petals
    this.petals = new Petal[NUM_SUNFLOWERS][SPIRAL_COUNT][MAX_DIST];
    this.petal_order = new Coord_int[NUM_PETALS];
    
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      for (int p = 0; p < SPIRAL_COUNT; p++) {
        for (int d = 0; d < MAX_DIST; d++) {
          Petal new_petal = new Petal(s, p, d);
          this.petals[s][p][d] = new_petal;  // Add one petal at a time
          this.petal_order[new_petal.petal] = new Coord_int(p,d);  // Store its position in order
        }
      }
    }
  }
  
  boolean is_visible(int p, int d) {
    return this.petals[0][p][d].visible;  // Don't draw clipped petals
  }
  
  byte get_strip(byte s, int p, int d) {
    return byte(this.petals[s][p][d].strip_led.c1);
  }
  
  int get_led(int p, int d) {
    return this.petals[0][p][d].strip_led.c2;
  }
  
  void draw() {
    // Draw function for the overall SunGrid
    draw_black_circle();  // Clipping exposes some background that should be blackened
    
    // Draw all petals in  order using the petal_order lookup table
    if (TOP_UP) {
      for (int i = NUM_PETALS-1; i >= 0; i--) {
        draw_all_petals_num(i);
      }
    } else {
      for (int i = 0; i < NUM_PETALS; i++) {
        draw_all_petals_num(i);
      }
    }
  }
  
  void draw_all_petals_num( int i) {
    // Draw petals numbered i for all sunflowers
    int p = this.petal_order[i].c1;
    int d = this.petal_order[i].c2;
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      petals[s][p][d].draw();  // Have each petal draw itself
    }
  }
  
  void drawLabels() {
    // Draw all the numbered labels
    // Labels should stick out more (Tom?)
    if (DRAW_LABELS == 2) {  // 2 = No Label
      return;
    }
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      for (int p = 0; p < SPIRAL_COUNT; p++) {
        for (int d = 0; d < MAX_DIST; d++) {
          petals[s][p][d].drawLabel();  // Have each petal draw its own label
        }
      }
    }
  }
  
  void setCellColor(int s, int p, int d, color c) {
    petals[s][p][d].setColor(c);  // Have each petal store its own color
  }
  
  void draw_black_circle() {
    // Draw a black background circle underneath the sunflower
    fill(0,0,0);
    stroke(0);
    ellipse((width / 2), ((height - CONTROL_HEIGHT) / 2), SUNFLOWER_RAD*2, SUNFLOWER_RAD*2);
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
  float z;
  Coord rtheta;  // screen r, theta (floats)
  Coord_int strip_led; // (strip, led) coordinate
  String p_d_id; // label of "p, d"
  String strip_led_id; // label of "strip, led"
  boolean visible;  // false = clipped off
  color c;  // (r, g, b)
  
  Petal(byte s, int p, int d) {
    this.s = s;
    this.p = spiral_order[p];  //  Re-order the spiral arms here
    this.d = d;
    this.petal = get_petal_num(this.p, this.d);
    this.xy = calc_xy(this.s, this.petal);
    this.z = calc_z(this.s, this.petal);
    this.rtheta = calc_rtheta(this.s, this.petal);
    //this.angle = (  float(this.petal+1) * golden_angle  ) + ( PI / 2);
    this.strip_led = calc_led(this.s, this.p, this.d);
    this.p_d_id = get_p_d_id(p, this.d);
    this.strip_led_id = get_strip_led_id(this.strip_led);
    this.visible = valid_petal(this.p, this.d);  // boolean: true = draw petal
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
    return join(nf(coords, 0), ",");
  }
  
  boolean valid_petal( int p, int d) {
    if (d >= clip_list[p]) {
      return true;
    } else {
      return false;
    }
  }
  
  void setColor(color c) {
    this.c = c;
  }
  
  void drawLabel() {
    if (this.visible == false) {
      return;  // not visible, so just return
    }
    
    // toggle text label between light number and x,y coordinate
    String text = "";
    switch (DRAW_LABELS) {
      case 0:
        text = this.strip_led_id;
        break;
      case 1:
        text = this.p_d_id;
        break;
      case 2:
        break;
    }
    rectMode( RADIUS);
    fill( 0, 0, 255, 255);
    text( text, this.xy.c1, this.xy.c2);
  }
  
  void draw() {
    // Draw just the petal - all this is from Thomas T. Landers
    if (this.visible == false) {
      return;  // not visible, so just return
    }
    float x = this.xy.c1;
    float y = this.xy.c2;
    float z = this.z;
    float orient = this.rtheta.c2;
    float radius = PETAL_RAD;
    
    fill(this.c);
    smooth();
    noStroke();
//    stroke(0);
    
    rectMode( RADIUS);

    pushMatrix();
    translate( x, y, z);
    rotateZ( orient ); // 3D
    rotateX( - (PI / 2) + ( this.petal * ( 0.0018 * PI)) );

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
  
  Coord calc_xy(int sunflower, int i) {
    // Calculate the x,y-screen position for the petal
    // sunflower (s) not used yet, but will be used in later versions
    float ratio =  float(i+1) / float( NUM_PETALS);
    float angle = (  float(i+1) * golden_angle  ) - ( PI / 2);
    float spiral_rad = ratio * SUNFLOWER_RAD;
    float x = (width / 2) + cos( angle) * spiral_rad;
    float y = ((height - CONTROL_HEIGHT) / 2) + sin( angle) * spiral_rad;
    Coord coord = new Coord(x,y);
    return coord;
  }
  
  float calc_z(int sunflower, int i) {
    float ratio =  float(i+1) / float( NUM_PETALS);
    float spiral_rad = ratio * SUNFLOWER_RAD;
    float z = Z_MAX - 9 * sqrt(spiral_rad);
    return z;
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
  
  Coord_int calc_led(byte s, int p, int d) {
    // Incredibly complicated look-up table (not yet - need wiring plan first)
    // to convert (s,p,d) coordinates into (strip, LED)
    Coord_int dummy_coord = new Coord_int(s, get_petal_num(p,d));
    return dummy_coord;
  }
  
  int get_petal_num(int p, int d) {
    return p + (d * SPIRAL_COUNT);
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

Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

//
// 2 wildcard commands:
//
// X=Finish a morph cycle (clean up by pushing the frame buffers)
// D(int) means delay for int milliseconds (but keeping morphing)
//
// Otherwise, process 6 integers as (s,p,d, r,g,b)
//
void processCommand(String cmd) {
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle();
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time = Integer.valueOf(cmd.substring(1, cmd.length())) + 10;  // 20 is a buffer
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
  int p     = Integer.valueOf(m.group(2));
  int d     = Integer.valueOf(m.group(3));
  int r     = Integer.valueOf(m.group(4));
  int g     = Integer.valueOf(m.group(5));
  int b     = Integer.valueOf(m.group(6));
  
  sendColorOut(s, p, d, byte(r), byte(g), byte(b), false);  
//  println(String.format("setting pixel:%d,%d,%d to r:%d g:%d b:%d", s, p, d, r, g, b));
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by morphing to the max and pushing the frame buffer
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
  // Fractional morph over the span of delay_time
  morph_frame((last_time - start_time) / (float)delay_time); 
}

// Send a corrected color to a sunflower pixel on screen and in lights
void sendColorOut(byte s, int p, int d, byte r, byte g, byte b, boolean morph) {
  color correct = colorCorrect(r,g,b);  // all-red, all-blue, etc.
  
  r = adj_brightness(red(correct));
  g = adj_brightness(green(correct));
  b = adj_brightness(blue(correct));
  
  if (TILING) {
    sunGrid.setCellColor(s, p, d, color(r,g,b));  // Simulator
    setPixelBuffer(s, p, d, r, g, b, morph);  // Lights: sets next-frame buffer (doesn't turn them on)
  } else {
    if (s == 0) {
      for (byte s_num = 0; s_num < NUM_SUNFLOWERS; s_num++) {
        sunGrid.setCellColor(s_num, p, d, color(r,g,b));  // Simulator
        setPixelBuffer(s, p, d, r, g, b, morph);  // Lights: sets next-frame buffer (doesn't turn them on)
      }
    }
  }
}

//
//  Routines to interact with the Lights
//
void sendDataToLights() {
  byte strip;
  
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    // may need to move this into the loop, as the can registry change while populating lights
    List<Strip> strips = registry.getStrips();  
    
    // THIS MAY NOT WORK - won't know until we get a working LED sunflower
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {      
      for (int p = 0; p < SPIRAL_COUNT; p++) {
        for (int d = 0; d < MAX_DIST; d++) {
          if ((hasChanged(s, p, d)) && (sunGrid.is_visible(p, d))) {
            strip = sunGrid.get_strip(s, p, d);
            if (strip < strips.size()) { 
              strips.get(strip).setPixel(getPixelBuffer(s, p, d), sunGrid.get_led(p, d));
            }
          }
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
      for (int i=0; i < 100000; i++)
        Thread.yield();
    }
  }
  ));
}

//
//  Routines for the strip buffer
//
byte adj_brightness(float value) {
  return (byte)(value * BRIGHTNESS / 100);
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
  byte empty = 0;
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int p = 0; p < SPIRAL_COUNT; p++) {
      for (int d = 0; d < MAX_DIST; d++) {
        setPixelBuffer(s, p, d, empty,empty,empty, false);
      }
    }
  }
  pushColorBuffer();
}

//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0-1.0 fraction towards the next frame
//
void morph_frame(float fract) {
  byte r,g,b;
  
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int p = 0; p < SPIRAL_COUNT; p++) {
      for (int d = 0; d < MAX_DIST; d++) {
        if (hasChanged(s, p, d)) {
          r = interp(curr_buffer[s][p][d][0], next_buffer[s][p][d][0], fract);
          g = interp(curr_buffer[s][p][d][1], next_buffer[s][p][d][1], fract);
          b = interp(curr_buffer[s][p][d][2], next_buffer[s][p][d][2], fract);
          
          sendColorOut(s,p,d, r,g,b, true);
        }
      }
    }
  }
}  

byte interp(byte a, byte b, float fract) {
  return (byte(a + (fract * (b-a))));
}

void setPixelBuffer(byte s, int p, int d, byte r, byte g, byte b, boolean morph) {
  if (morph) {
    morph_buffer[s][p][d][0] = r;
    morph_buffer[s][p][d][1] = g;
    morph_buffer[s][p][d][2] = b;
  } else {
    next_buffer[s][p][d][0] = r;
    next_buffer[s][p][d][1] = g;
    next_buffer[s][p][d][2] = b;
  }
}

color getPixelBuffer(byte s, int p, int d) {
  return color(morph_buffer[s][p][d][0],
               morph_buffer[s][p][d][1],
               morph_buffer[s][p][d][2]);
}

boolean hasChanged(byte s, int p, int d) {
  if (curr_buffer[s][p][d][0] != next_buffer[s][p][d][0] ||
      curr_buffer[s][p][d][1] != next_buffer[s][p][d][1] ||
      curr_buffer[s][p][d][2] != next_buffer[s][p][d][2]) {
        return true;
      } else {
        return false;
      }
}

void pushColorBuffer() {
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int p = 0; p < SPIRAL_COUNT; p++) {
      for (int d = 0; d < MAX_DIST; d++) {
        curr_buffer[s][p][d][0] = next_buffer[s][p][d][0];
        curr_buffer[s][p][d][1] = next_buffer[s][p][d][1];
        curr_buffer[s][p][d][2] = next_buffer[s][p][d][2];
      }
    }
  }
}

