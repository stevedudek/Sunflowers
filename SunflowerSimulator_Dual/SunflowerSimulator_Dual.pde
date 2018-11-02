/*

  Sunflower Simulator and Lighter
  
  1. Simulator: draws sunflower shape on the monitor
  2. Lighter: sends data to the lights
  
  DUAL SHOWS - Works!
  
  HSV colors (not RGB) for better interpolation
  
  11/1/18
  
  Built on glorious Rose + Triangle Simulator
  
  (s,i) coordinates are (s,i) = (sunflower,pixel) coordinates.
  s = 0 - 3; i = 0 - 272
  
  Turn on the coordinates to see the system.
    
*/

byte NUM_SUNFLOWERS = 3;  // Number of Big Sunflowers
int NUM_LEDS = 273;
int SPIRAL_COUNT = 21;
int MAX_DIST = 14; // 17 with clipping
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

int NUM_CHANNELS = 2;  // Dual shows

// network vars
int port = 4444;
Server[] _servers = new Server[NUM_CHANNELS];  // For dual shows 
StringBuffer[] _bufs = new StringBuffer[NUM_CHANNELS];  // separate buffers

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
int DRAW_LABELS = 2;  // enumerated type: 0=(p,d) label, 1=(strip,pixel), 2=labels off
boolean TOP_UP = true;  // Whether to draw sunflower as concave or convex
int BRIGHTNESS = 100;  // A percentage
int COLOR_STATE = 0;  // no enum types in processing. Messy

// Color buffers: [s][i][hsv color]
color[][][] curr_buffer = new color[NUM_CHANNELS][NUM_SUNFLOWERS][NUM_LEDS];
color[][][] next_buffer = new color[NUM_CHANNELS][NUM_SUNFLOWERS][NUM_LEDS];
color[][][] morph_buffer = new color[NUM_CHANNELS][NUM_SUNFLOWERS][NUM_LEDS];  // blend of curr + next
color[][] interp_buffer = new color[NUM_SUNFLOWERS][NUM_LEDS];  // combine two channels here

// Timing variables needed to control regular morphing
// Doubled for 2 channels
int[] delay_time = { 10000, 10000 };  // delay time length in milliseconds (dummy initial value)
long[] start_time = { millis(), millis() };  // start time point (in absolute time)
long[] last_time = { start_time[0], start_time[1] };
short[] channel_intensity = { 255, 0 };  // Off = 0, All On = 255 


// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = true;  // turn false for LED-only updates
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

boolean track_flag = false;  // Needed for animation debugging

PFont font_sun = createFont("Helvetica", 12, true);

//
// Setup
//
// Calculate just once the screen position of all petals,
// the conversion of (s,p,d) petals coordinates to (strip, pixel) LEDs   
// 
void setup() {
  
  size(SCREEN_WIDTH, SCREEN_HEIGHT);
  stroke(0);
  fill(255,255,0);
  
  frameRate(20);
  
  // Pixel Pusher stuff
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  prepareExitHandler();
  strips = registry.getStrips();
  
  colorMode(HSB, 255);  // HSB colors (not RGB)
  
  for (int i = 0; i < NUM_CHANNELS; i++) {
    _bufs[i] = new StringBuffer();
    _servers[i] = new Server(this, port + i);
    println("server " + i + " listening: " + _servers[i]);
  }
  
  initializeColorBuffers();  // Stuff curr/next/morph frames with zeros (all black)
  
  background(0, 0, 200);  // gray
  
  sunGrid = new SunForm();  // Set up the Big Sunflowers and stuff in petals
  
  drawBottomControls();
}

//
// Draw - Main function
//
void draw() {
  pollServer();          // Get messages from python show runner
  update_morph();        // Morph between current frame and next frame 
  interpChannels();    // Update the visualizer
  if (UPDATE_VISUALIZER) {
    sunGrid.draw();        // Draw all the petals
    sunGrid.drawLabels();  // Labels need to drawn on top of petals
  }
  sendDataToLights();    // Turn on all lights
}

//
// Bottom Control functions
//
void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-21) {
    
    // Draw labels button
    DRAW_LABELS = (DRAW_LABELS + 1) % 3;  // 0-1-2 state
  
  }  else if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    
    // Invert button  
    if (TOP_UP) {
      TOP_UP = false;
    } else {
      TOP_UP = true;
    }
     
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT-46 && mouseY < SCREEN_HEIGHT-21) {
    
    // Bright up checkbox
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
   
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT-28 && mouseY < SCREEN_HEIGHT-13) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
  
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
  fill(0,0,255);
  rect(0,SCREEN_HEIGHT-50,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_HEIGHT-50,140,SCREEN_HEIGHT+10);
  line(290,SCREEN_HEIGHT-50,290,SCREEN_HEIGHT+10);
  line(470,SCREEN_HEIGHT-50,470,SCREEN_HEIGHT+10);
  
  // draw checkboxes
  stroke(0);
  fill(255);
  
  drawCheckbox(20,SCREEN_HEIGHT-46,15, color(0,0,255), false);  // label checkbox
  drawCheckbox(20,SCREEN_HEIGHT-28,15, color(0,0,255), false);  // invert checkbox
  
  rect(200,SCREEN_HEIGHT-46,15,15);  // minus brightness
  rect(200,SCREEN_HEIGHT-28,15,15);  // plus brightness
  
  drawCheckbox(340,SCREEN_HEIGHT-46,15, color(255,255,255), COLOR_STATE == 1);
  drawCheckbox(340,SCREEN_HEIGHT-28,15, color(255,255,255), COLOR_STATE == 4);
  drawCheckbox(360,SCREEN_HEIGHT-46,15, color(87,255,255), COLOR_STATE == 2);
  drawCheckbox(360,SCREEN_HEIGHT-28,15, color(87,255,255), COLOR_STATE == 5);
  drawCheckbox(380,SCREEN_HEIGHT-46,15, color(175,255,255), COLOR_STATE == 3);
  drawCheckbox(380,SCREEN_HEIGHT-28,15, color(175,255,255), COLOR_STATE == 6);
  
  drawCheckbox(400,SCREEN_HEIGHT-40,20, color(0,0,255), COLOR_STATE == 0);
    
  // draw text labels in 12-point Helvetica
  fill(0);
  textAlign(LEFT);
  textFont(font_sun, 12);  
  text("Labels", 50, SCREEN_HEIGHT-34);
  text("Invert", 50, SCREEN_HEIGHT-16);
  
  text("+", 190, SCREEN_HEIGHT-34);
  text("-", 190, SCREEN_HEIGHT-16);
  text("Brightness", 225, SCREEN_HEIGHT-25);
  textFont(font_sun, 20);
  text(BRIGHTNESS, 150, SCREEN_HEIGHT-22);
  
  textFont(font_sun, 12);
  text("None", 305, SCREEN_HEIGHT-34);
  text("All", 318, SCREEN_HEIGHT-16);
  text("Color", 430, SCREEN_HEIGHT-25);
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
// holds all the petals as a [s][i] array of Petal objects
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
    if (DRAW_LABELS == 2) {  // 2 = No Label
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
    this.p = get_spiral_order(i % 21); // spiral_order[i % 21];  //  Re-order the spiral arms here
    this.d = int(i / 21);
    this.petal = i;
    this.xy = calc_xy(this.s, this.petal);
    this.rtheta = calc_rtheta(this.s, this.petal);
    //this.angle = (  float(this.petal+1) * golden_angle  ) + ( PI / 2);
    this.strip_led = calc_led(this.s, p, this.d);
    this.p_d_id = get_p_d_id(p, this.d);
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
    return join(nf(coords, 0), ",");
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
        text = this.strip_led_id;
        break;
      case 1:
        text = this.p_d_id;
        break;
      case 2:
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
  
  Coord_int calc_led(byte sunflower, int p, int d) {
    // convert (s, p, d) coordinates into (strip, LED)
    int led = 0;
    int s = sunflower * 2;
    p = 20 - p; // flip orientation
    if ((p < 10) || (p == 10 && d > 6))  {
      led = (p / 2) * 27;
      
      if (p % 2 == 0) {
        led += (12 - d);
      } else {
        led += (13 + d);
      }
    } else {
      s += 1;
      p = 20 - p;
      led = (p / 2) * 27;
      
      if (p % 2 == 0) {
        led += d;
      } else {
        led += (26 - d);
      }
    }
    Coord_int coord = new Coord_int(s, led);
    return coord;
  }
  
  int get_petal_num(int p, int d) {
    return p + (d * SPIRAL_COUNT);
  }
  
  int get_spiral_order(int p) {
    return ((20 - p) * 13) % 21;
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
  // Read 2 different server ports into 2 buffers - keep channels separated
  for (int i = 0; i < NUM_CHANNELS; i++) {
    try {
      Client c = _servers[i].available();
      // append any available bytes to the buffer
      if (c != null) {
        _bufs[i].append(c.readString());
      }
      // process as many lines as we can find in the buffer
      int ix = _bufs[i].indexOf("\n");
      while (ix > -1) {
        String msg = _bufs[i].substring(0, ix);
        msg = msg.trim();
        processCommand(msg);
        _bufs[i].delete(0, ix+1);
        ix = _bufs[i].indexOf("\n");
      }
    } catch (Exception e) {
      println("exception handling network command");
      e.printStackTrace();
    }
  }  
}

//
// With DUAL shows: 
// 1. all commands must start with either a '0' or '1'
// 2. Followed by either
//     a. X = Finish a morph cycle (clean up by pushing the frame buffers)
//     b. D(int) = delay for int milliseconds (but keeping morphing)
//     c. I(short) = channel intensity (0 = off, 255 = all on)
//     d. Otherwise, process 5 integers as (s,i, r,g,b)
//
//
void processCommand(String cmd) {
  if (cmd.length() < 2) { return; }  // Discard erroneous stub characters
  byte channel = (cmd.charAt(0) == '0') ? (byte)0 : (byte)1 ;  // First letter indicates Channel 0 or 1
  cmd = cmd.substring(1, cmd.length());  // Strip off first-letter Channel indicator
  
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle(channel);
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time[channel] = Integer.valueOf(cmd.substring(1, cmd.length()));
  } else if (cmd.charAt(0) == 'I') {  // Get the intensity
    channel_intensity[channel] = Integer.valueOf(cmd.substring(1, cmd.length())).shortValue();
  } else {  
    processPixelCommand(channel, cmd);  // Pixel command
  }
}

// 5 comma-separated numbers for triangle, pixel, h, s, v
Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

void processPixelCommand(byte channel, String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    //println(cmd);
    println("ignoring input for " + cmd);
    return;
  }
  byte sun  =    Byte.valueOf(m.group(1));
  int i     = Integer.valueOf(m.group(2));
  int h     = Integer.valueOf(m.group(3));
  int s     = Integer.valueOf(m.group(4));
  int v     = Integer.valueOf(m.group(5));
  
  next_buffer[channel][sun][i] = color( (short)h, (short)s, (short)v );  
//  println(String.format("setting channel %d pixel:%d,%d to h:%d, s:%d, v:%d", channel, s, i, h, s, v));
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by morphing to the max and pushing the frame buffer
void finishCycle(byte channel) {
  morph_frame(channel, 1.0);  // May work after all
  pushColorBuffer(channel);
  start_time[channel] = millis();  // reset the clock
}

//
// Update Morph
//
void update_morph() {
  // Fractional morph over the span of delay_time
  for (byte channel = 0; channel < NUM_CHANNELS; channel++) {
    last_time[channel] = millis();  // update clock
    float fract = (last_time[channel] - start_time[channel]) / (float)delay_time[channel];
    if (is_channel_active(channel) && fract <= 1.0) {
      morph_frame(channel, fract);
    }
  }
}

//
// Is Channel Active
//
boolean is_channel_active(int channel) {
  return (channel_intensity[channel] > 0);
}

//
// Interpolate Channels
//
// Interpolate between the 2 channels
// Push the interpolated results on to the simulator 
//
void interpChannels() {
  if (!is_channel_active(0)) {
    pushOnlyOneChannel(1);
  } else if (!is_channel_active(1)) {
    pushOnlyOneChannel(0);
  } else {
    float fract = (float)channel_intensity[0] / (channel_intensity[0] + channel_intensity[1]);
    morphBetweenChannels(fract);
  }
}

//
// pushOnlyOneChannel - push the morph_channel to the simulator
//
void pushOnlyOneChannel(int channel) {
  color col;
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      col = adjColor(morph_buffer[channel][s][i]);
      sunGrid.setCellColor(s, i, col);
      interp_buffer[s][i] = col;
    }
  }
}

//
// morphBetweenChannels - interpolate the morph_channel on to the simulator
//
void morphBetweenChannels(float fract) {
  color col;
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      col = adjColor(interp_color(morph_buffer[1][s][i], morph_buffer[0][s][i], fract));
      sunGrid.setCellColor(s, i, col);
      interp_buffer[s][i] = col;
    }
  }
}

// Adjust color for brightness and hue
color adjColor(color c) {
  return adj_brightness(colorCorrect(c));
}

// Convert hsb color (0-255) to hsb (0-1.0) and then to rgb (0-255)
//   warning: it's messy
color hsb_to_rgb(color c) {
  int color_int = Color.HSBtoRGB(hue(c) / 255.0,  // 255?
                                 saturation(c) / 255.0, 
                                 brightness(c) / 255.0);
  return color((color_int & 0x00FF0000) >> 16, 
               (color_int & 0x0000FF00) >> 8, 
               (color_int & 0x000000FF));
}

/////  Routines to interact with the Lights

void sendDataToLights() {
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
  
    int strip_num = 0;
    int pixel;
    Coord_int strip_led;
    
    List<Strip> strip_list = registry.getStrips();
    
    for (Strip strip : strip_list) {
      if (strip_num < (NUM_SUNFLOWERS * 2) && strip_num < strip_array.length) {
        strip_array[strip_num] = strip;
        strip_num++;
      }
    }
    
    for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
      for (short i = 0; i < NUM_LEDS; i++) {
        strip_led = sunGrid.petals[s][i].get_strip_led();
        strip_num = strip_led.c1;
        pixel = strip_led.c2;
        
        if (strip_num < strip_array.length) {
          strip_array[strip_num].setPixel(hsb_to_rgb(interp_buffer[s][i]), pixel);
        } else {
          println("Strip " + strip_num + " is out of bounds for " + strip_array.length + " strips");
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
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0 - 1.0 fraction towards the next frame
//
void morph_frame(byte c, float fract) {
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (short i = 0; i < NUM_LEDS; i++) {
      morph_buffer[c][s][i] = interp_color(curr_buffer[c][s][i], next_buffer[c][s][i], fract);   
    }
  }
}

color adj_brightness(color c) {
  // Adjust only the 3rd brightness channel
  return color(hue(c), saturation(c), brightness(c) * BRIGHTNESS / 100);
}

color colorCorrect(color c) {
  short new_hue;
  
  switch(COLOR_STATE) {
    case 1:  // no red
      new_hue = map_range(hue(c), 40, 200);
      break;
    
    case 2:  // no green
      new_hue = map_range(hue(c), 120, 45);
      break;
    
    case 3:  // no blue
      new_hue = map_range(hue(c), 200, 120);
      break;
    
    case 4:  // all red
      new_hue = map_range(hue(c), 200, 40);
      break;
    
    case 5:  // all green
      new_hue = map_range(hue(c), 40, 130);
      break;
    
    case 6:  // all blue
      new_hue = map_range(hue(c), 120, 200);
      break;
    
    default:  // all colors
      new_hue = (short)hue(c);
      break;
  }
  return color(new_hue, saturation(c), brightness(c));
}

//
// map_range - map a hue (0-255) to a smaller range (start-end)
//
short map_range(float hue, int start, int end) {
  int range = (end > start) ? end - start : (end + 256 - start) % 256 ;
  return (short)((start + ((hue / 255.0) * range)) % 256);
}

void initializeColorBuffers() {
  for (int c = 0; c < NUM_CHANNELS; c++) {
    fill_black_one_channel(c);
  }
}

void fill_black_one_channel(int c) {
  color black = color(0,0,0); 
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (short i = 0; i < NUM_LEDS; i++) {
      curr_buffer[c][s][i] = black;
      next_buffer[c][s][i] = black;
    }
  }
}

void pushColorBuffer(byte c) {
  for (byte s = 0; s < NUM_SUNFLOWERS; s++) {
    for (short i = 0; i < NUM_LEDS; i++) {
      curr_buffer[c][s][i] = next_buffer[c][s][i];
    }
  }
}

void print_memory_usage() {
  long maxMemory = Runtime.getRuntime().maxMemory();
  long allocatedMemory = Runtime.getRuntime().totalMemory();
  long freeMemory = Runtime.getRuntime().freeMemory();
  int inUseMb = int(allocatedMemory / 1000000);
  
  if (inUseMb > 80) {
    println("Memory in use: " + inUseMb + "Mb");
  }  
}

color interp_color(color c1, color c2, float fract) {
 // standard lerpColor interpolation does not work well
 // for HSV colors if one color is black
 if (is_black(c1) && is_black(c2)) {
   return c1;
 } else if (is_black(c1)) {
  return color(hue(c2), saturation(c2), brightness(c2) * fract);
 } else if (is_black(c2)) {
  return color(hue(c1), saturation(c1), brightness(c1) * (1.0 - fract));
 } else {
   return color(lerp(hue(c1), hue(c2), fract),
                lerp(saturation(c1), saturation(c2), fract),
                lerp(brightness(c1), brightness(c2), fract));
 }
} 

boolean is_black(color c) {
  return (hue(c) == 0 && saturation(c) == 0 && brightness(c) == 0);
} 
