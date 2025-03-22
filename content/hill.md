Title: When's the best time to surge when cycling up a hill?
Date: 2025-03-21
Category: Physics
Tags: cycling, physics, simulation, chart.js
Slug: surge-cycling-up-a-hill
Authors: François Leblanc
Summary: A simple cycling simulator that calculates the time it takes to cycle up a hill with a surge of power.

![Cycling uphill](img/12_percent_hill.jpg)

## The Physics of Cycling Uphill
My wife and I recently upgraded from our late 80s steel bikes to more modern ones, and purchased an erg-enabled indoor trainer. I've been spending a surprising number of hours on Zwift, and turns out... it's great fun! I consider myself an all-round athlete, so it was to my great dismay to discover that what I thought was being in OK shape is &mdash; as far as comparison with other indoor cyclists goes &mdash; relatively poor performance! This of course, was very exciting. I love a good training challenge.

I've participated in a few races and noticed many different strategies being used when tackling hills. Having tried various approaches myself, I could definitely feel that some were much better than others. But was that due to luck and good timing on my part, or actually a good strategy? The good news is, cycling is mostly "basic" physics, and we can simulate it!

When cycling, several forces affect your motion:

1. **Propulsive Force**: The power you generate divided by your velocity
2. **Gravity**: Pulls you down, making climbs harder. The heavier you are, the more power you need to climb.
3. **Rolling Resistance**: Friction between tires and road, linear with velocity.
4. **Air Resistance**: Increases with the square of your velocity

The simulation below models a 1,200 m route with a hill in the middle. We're keeping things simple: you can apply a single surge of power, and the simulation calculates the time it takes to cross the finish line for various surge starting points, to see when it's most effective.

## When Should You Surge?

The key question: **When is the optimal time to apply a short power surge to
minimize your total time?**

- On the flat sections?
- At the beginning of the climb?
- In the middle of the climb?
- Near the top of the climb?
- During the descent?

Use the simulator below to find out!


<!-- Input controls with better styling -->
<div style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px;">
  <h3>Simulation Parameters</h3>
  
  <!-- Primary parameters -->
  <div style="margin-bottom: 20px;">
    <h4>Power Settings</h4>
    <div style="display: flex; flex-wrap: wrap; gap: 15px;">
      <div style="min-width: 200px;">
        <label for="normal_power" style="display: block; margin-bottom: 5px; font-weight: bold;">Normal Power (W):</label>
        <input type="range" id="normal_power_slider" min="100" max="400" value="200" style="width: 100%;">
        <input type="number" id="normal_power" value="200" style="width: 100px;">
      </div>
      <div style="min-width: 200px;">
        <label for="surge_power" style="display: block; margin-bottom: 5px; font-weight: bold;">Surge Power (W):</label>
        <input type="range" id="surge_power_slider" min="200" max="800" value="400" style="width: 100%;">
        <input type="number" id="surge_power" value="400" style="width: 100px;">
      </div>
      <div style="min-width: 200px;">
        <label for="surge_duration" style="display: block; margin-bottom: 5px; font-weight: bold;">Surge Duration (s):</label>
        <input type="range" id="surge_duration_slider" min="5" max="60" value="20" style="width: 100%;">
        <input type="number" id="surge_duration" value="20" style="width: 100px;">
      </div>
    </div>
  </div>
  
  <!-- Advanced parameters (initially hidden) -->
  <div>
    <details>
      <summary style="cursor: pointer; font-weight: bold; padding: 10px 0;">Advanced Parameters</summary>
      <div style="margin-top: 10px; padding: 15px; background: #eee; border-radius: 5px;">
        <div style="display: flex; flex-wrap: wrap; gap: 15px;">
          <div style="min-width: 200px;">
            <label for="cyclist_mass" style="display: block; margin-bottom: 5px; font-weight: bold;">Cyclist + Bike Mass (kg):</label>
            <input type="range" id="cyclist_mass_slider" min="50" max="100" value="70" style="width: 100%;">
            <input type="number" id="cyclist_mass" value="70" style="width: 100px;">
          </div>
          <div style="min-width: 200px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
              <label for="drag_coefficient" style="font-weight: bold; margin-right: 5px;">Drag Coefficient:</label>
              <div class="tooltip" style="position: relative; display: inline-block; cursor: help;">
                <span style="display: inline-block; width: 16px; height: 16px; background: #666; color: white; border-radius: 50%; text-align: center; line-height: 16px; font-size: 12px;">i</span>
                <div style="visibility: hidden; width: 250px; background-color: #555; color: #fff; text-align: left; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-weight: normal; line-height: 1.4;">
                  The drag coefficient affects air resistance. Lower values mean less drag.
                  <br><br>
                  <strong>Examples:</strong>
                  <br>• 0.5: Drafting behind another cyclist
                  <br>• 0.9: Racing position on drops
                  <br>• 1.2: Upright position
                </div>
              </div>
            </div>
            <input type="range" id="drag_coefficient_slider" min="0.5" max="1.5" step="0.1" value="0.9" style="width: 100%;">
            <input type="number" id="drag_coefficient" value="0.9" step="0.1" style="width: 100px;">
          </div>
          <div style="min-width: 200px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
              <label for="frontal_area" style="font-weight: bold; margin-right: 5px;">Frontal Area (m²):</label>
              <div class="tooltip" style="position: relative; display: inline-block; cursor: help;">
                <span style="display: inline-block; width: 16px; height: 16px; background: #666; color: white; border-radius: 50%; text-align: center; line-height: 16px; font-size: 12px;">i</span>
                <div style="visibility: hidden; width: 250px; background-color: #555; color: #fff; text-align: left; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-weight: normal; line-height: 1.4;">
                  The frontal area is the cyclist's cross-sectional area facing the wind.
                  <br><br>
                  <strong>Typical values:</strong>
                  <br>• 0.36 m²: Pro cyclist in aero position
                  <br>• 0.5 m²: Recreational cyclist on hoods
                  <br>• 0.6 m²: Upright position
                </div>
              </div>
            </div>
            <input type="range" id="frontal_area_slider" min="0.3" max="0.7" step="0.01" value="0.42" style="width: 100%;">
            <input type="number" id="frontal_area" value="0.42" step="0.01" style="width: 100px;">
          </div>
        </div>
      </div>
    </details>
  </div>
  
  <button id="plot_button" style="margin-top: 15px; padding: 8px 16px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Run Simulation</button>
</div>

<!-- Container for the elevation profile -->
<div style="margin: 20px 0;">
  <h3>Elevation Profile</h3>
  <div style="position: relative; height: 40vh; min-height: 200px;">
    <canvas id="elevation_chart"></canvas>
  </div>
</div>

<!-- Container for the results chart -->
<div style="margin: 20px 0;">
  <h3>Total Time vs. Surge Start Position</h3>
  <div style="position: relative; height: 60vh; min-height: 350px;">
    <canvas id="results_chart"></canvas>
  </div>
</div>

<!-- Container for optimal result -->
<div id="optimal_result" style="margin: 20px 0; padding: 15px; background: #e8f5e9; border-radius: 8px; display: none;">
  <h3>Optimal Surge Zone</h3>
  <p id="optimal_text"></p>
  <p><em>Note: The time curve typically has a "flat spot" where multiple surge points yield similar results. This shows the entire range of surge start times that achieve the fastest overall time (within 0.1 seconds of minimum).</em></p>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Constants for the simulation
const g = 9.81; // gravity in m/s^2
const C_r = 0.005; // rolling resistance coefficient
const rho = 1.2; // air density in kg/m^3
const total_distance = 1200; // total distance in meters
const dt = 0.1; // time step in seconds

// Variables that can be modified through UI
let m = 70; // mass of cyclist + bike in kg
let C_d = 0.9; // drag coefficient
let A = 0.42; // frontal area in m^2

// Route profile: segments with start/end distances and slope in degrees
const route = [
  {start: 0, end: 100, slope: 0}, // flat
  {start: 100, end: 600, slope: 10}, // uphill
  {start: 600, end: 1100, slope: -10}, // downhill
  {start: 1100, end: 1200, slope: 0} // flat
];

// Calculate elevation profile
function calculateElevationProfile() {
  const points = [];
  let elevation = 0;
  
  for (let x = 0; x <= total_distance; x += 10) {
    let theta = getTheta(x);
    // If moving 1 meter horizontally at this slope, how much vertical change?
    let vertical_change = Math.tan(theta) * 10;
    
    if (points.length > 0) {
      elevation += vertical_change;
    }
    
    points.push({x: x, y: elevation});
  }
  
  return points;
}

// Get slope angle in radians based on position
function getTheta(x) {
  for (let segment of route) {
    if (x >= segment.start && x < segment.end) {
      return segment.slope * Math.PI / 180; // convert degrees to radians
    }
  }
  return 0; // default to flat if beyond segments
}

// Get segment description based on position
function getSegmentDescription(x) {
  if (x < 100) return "starting flat";
  if (x < 600) return "climbing uphill";
  if (x < 1100) return "descending";
  return "final flat section";
}

// Calculate steady-state speed on flat ground for a given power
function calculateSteadyStateSpeed(power) {
  // On flat ground, steady-state means acceleration = 0
  // F_power + F_roll + F_drag = 0
  // power/v - C_r*m*g - 0.5*C_d*A*rho*v^2 = 0
  
  // Use iterative approach to find the velocity where net force is zero
  let v = 5; // starting guess
  const maxIterations = 50;
  const tolerance = 0.001;
  
  for (let i = 0; i < maxIterations; i++) {
    let F_power = power / v;
    let F_roll = -C_r * m * g;
    let F_drag = -0.5 * C_d * A * rho * v * v;
    let F_net = F_power + F_roll + F_drag;
    
    if (Math.abs(F_net) < tolerance) {
      break;
    }
    
    // Use simple proportional update to converge to solution
    // If F_net is positive, we need to increase v
    // If F_net is negative, we need to decrease v
    v = v * (1 + 0.1 * Math.sign(F_net) * Math.min(1, Math.abs(F_net)));
  }
  
  return v;
}

// Simulate the ride and return total time
function simulate(normal_power, surge_power, surge_duration, t_surge_start) {
  let t = 0; // time in seconds
  let x = 0; // position in meters
  let v = calculateSteadyStateSpeed(normal_power); // start at steady-state speed for normal power
  
  // For tracking position at surge start/end
  let surge_start_pos = 0;
  let surge_end_pos = 0;
  
  // Data points for this simulation
  const timePoints = [];
  const speedPoints = [];
  const powerPoints = [];
  const positionPoints = [];
  
  while (x < total_distance) {
    let theta = getTheta(x);
    
    // Apply surge power if within surge interval, else normal power
    let P = (t >= t_surge_start && t < t_surge_start + surge_duration) ? surge_power : normal_power;
    
    // Track surge position
    if (t >= t_surge_start && surge_start_pos === 0) {
      surge_start_pos = x;
    }
    if (t >= t_surge_start + surge_duration && surge_end_pos === 0) {
      surge_end_pos = x;
    }
    
    // Calculate forces
    let F_power = P / (v + 1e-6); // avoid division by zero
    let F_gravity = -m * g * Math.sin(theta);
    let F_roll = -C_r * m * g * Math.cos(theta);
    let F_drag = -0.5 * C_d * A * rho * v * v;
    let F_net = F_power + F_gravity + F_roll + F_drag;
    
    let a = F_net / m; // acceleration
    v += a * dt; // update velocity
    if (v < 0) v = 0; // prevent negative velocity
    x += v * dt; // update position
    t += dt; // increment time
    
    // Save data point every second
    if (Math.round(t) === t) {
      timePoints.push(t);
      speedPoints.push(v);
      powerPoints.push(P);
      positionPoints.push(x);
    }
  }
  
  return {
    total_time: t,
    surge_start_pos: surge_start_pos,
    surge_end_pos: surge_end_pos,
    data: {
      time: timePoints,
      speed: speedPoints,
      power: powerPoints,
      position: positionPoints
    }
  };
}

// Draw the elevation profile
function drawElevationProfile(optimalStartPos = null, optimalEndPos = null, isOptimalZone = false) {
  const elevationData = calculateElevationProfile();
  
  // Create chart
  const ctx = document.getElementById('elevation_chart').getContext('2d');
  
  if (window.elevationChart) {
    window.elevationChart.destroy();
  }
  
  const datasets = [{
    label: 'Elevation Profile',
    data: elevationData,
    borderColor: '#8BC34A',
    borderWidth: 3,
    fill: true,
    backgroundColor: 'rgba(139, 195, 74, 0.2)',
    tension: 0.4
  }];
  
  // Add optimal surge markers if provided
  if (optimalStartPos !== null && optimalEndPos !== null) {
    // Find the y-values (elevation) for the start and end positions
    let startElevation = 0;
    let endElevation = 0;
    
    for (const point of elevationData) {
      if (point.x >= optimalStartPos) {
        startElevation = point.y;
        break;
      }
    }
    
    for (const point of elevationData) {
      if (point.x >= optimalEndPos) {
        endElevation = point.y;
        break;
      }
    }
    
    // If this is showing an optimal zone (flat spot) rather than a single optimal point
    if (isOptimalZone) {
      // Add a highlighted zone for the optimal surge
      datasets.push({
        label: 'Optimal Surge Zone',
        data: [
          {x: optimalStartPos, y: startElevation},
          {x: optimalEndPos, y: endElevation}
        ],
        backgroundColor: 'rgba(76, 175, 80, 0.3)',
        borderColor: 'rgba(76, 175, 80, 0.8)',
        borderWidth: 3,
        fill: false,
        pointRadius: 6,
        pointHoverRadius: 8
      });
      
      // Find elevation points within the optimal zone to create a filled area
      const zonePoints = [];
      for (const point of elevationData) {
        if (point.x >= optimalStartPos && point.x <= optimalEndPos) {
          zonePoints.push(point);
        }
      }
      
      // Add the filled area if we have points
      if (zonePoints.length > 0) {
        datasets.push({
          label: 'Optimal Zone',
          data: zonePoints,
          backgroundColor: 'rgba(76, 175, 80, 0.2)',
          borderColor: 'rgba(76, 175, 80, 0.5)',
          borderWidth: 0,
          fill: true,
          pointRadius: 0
        });
      }
    } else {
      // Add start marker
      datasets.push({
        label: 'Surge Start',
        data: [{x: optimalStartPos, y: startElevation}],
        backgroundColor: '#FF5722',
        borderColor: '#FF5722',
        pointRadius: 8,
        pointHoverRadius: 10
      });
      
      // Add end marker
      datasets.push({
        label: 'Surge End',
        data: [{x: optimalEndPos, y: endElevation}],
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0',
        pointRadius: 8,
        pointHoverRadius: 10
      });
      
      // Add a line connecting them
      datasets.push({
        label: 'Optimal Surge',
        data: [
          {x: optimalStartPos, y: startElevation},
          {x: optimalEndPos, y: endElevation}
        ],
        backgroundColor: 'rgba(255, 87, 34, 0.3)',
        borderColor: '#FF5722',
        borderWidth: 5,
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0
      });
    }
  }
  
  window.elevationChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              if (context.dataset.label === 'Surge Start') {
                return `Surge starts here: ${Math.round(context.parsed.x)}m, Elevation: ${Math.round(context.parsed.y)}m`;
              } else if (context.dataset.label === 'Surge End') {
                return `Surge ends here: ${Math.round(context.parsed.x)}m, Elevation: ${Math.round(context.parsed.y)}m`;
              } else {
                return `Elevation: ${Math.round(context.parsed.y)}m, Distance: ${context.parsed.x}m`;
              }
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          title: {
            display: true,
            text: 'Distance (m)'
          },
          ticks: {
            callback: function(value) {
              return value + 'm';
            }
          },
          // Force consistent range on all devices
          min: 0,
          max: total_distance // 1200m
        },
        y: {
          title: {
            display: true,
            text: 'Elevation (m)'
          },
          ticks: {
            callback: function(value) {
              return Math.round(value) + 'm';
            },
            // Force integer values only
            stepSize: 10
          },
          // Ensure reasonable range but not too tall
          min: function(context) {
            const elevationValues = elevationData.map(p => p.y);
            const minElevation = Math.min(...elevationValues);
            return Math.floor(minElevation / 10) * 10; // Round down to nearest 10
          },
          max: function(context) {
            const elevationValues = elevationData.map(p => p.y);
            const minElevation = Math.min(...elevationValues);
            const maxElevation = Math.max(...elevationValues);
            // Ensure at least 30 meters of range (but not more than needed)
            const range = maxElevation - minElevation;
            return Math.ceil((minElevation + Math.max(range, 30)) / 10) * 10; // Round up to nearest 10
          }
        }
      }
    }
  });
}

// Run simulations and plot the results
function plot() {
  // Get user inputs for power
  let normal_power = parseFloat(document.getElementById('normal_power').value);
  let surge_power = parseFloat(document.getElementById('surge_power').value);
  let surge_duration = parseFloat(document.getElementById('surge_duration').value);
  
  // Get advanced parameters if they exist
  m = parseFloat(document.getElementById('cyclist_mass').value);
  C_d = parseFloat(document.getElementById('drag_coefficient').value);
  A = parseFloat(document.getElementById('frontal_area').value);
  
  // Debug: Log current values to console to verify
  console.log("Current simulation parameters:", {
    normalPower: normal_power,
    surgePower: surge_power, 
    surgeDuration: surge_duration,
    mass: m,
    dragCoefficient: C_d,
    frontalArea: A
  });
  
  // Simulate for different surge start times
  let data = [];
  let min_time = Infinity;
  let optimal_start = 0;
  let optimal_result = null;
  
  // Calculate a large number of evenly-spaced time points with high granularity
  const timePoints = [];
  // Use 0.5 second intervals throughout the entire range for higher precision
  for (let t = 0; t <= 500; t += 0.5) {
    timePoints.push(t);
  }
  
  // Sort and remove duplicates
  const uniqueTimePoints = [...new Set(timePoints)].sort((a, b) => a - b);
  
  // Store both time-based and position-based results
  const timeBasedData = [];
  const positionBasedData = [];
  
  for (let t_surge_start of uniqueTimePoints) {
    let result = simulate(normal_power, surge_power, surge_duration, t_surge_start);
    timeBasedData.push({x: t_surge_start, y: result.total_time, pos: result.surge_start_pos});
    positionBasedData.push({x: result.surge_start_pos, y: result.total_time, time: t_surge_start});
    
    if (result.total_time < min_time) {
      min_time = result.total_time;
      optimal_start = t_surge_start;
      optimal_result = result;
    }
  }
  
  // Sort position-based data by x (position)
  positionBasedData.sort((a, b) => a.x - b.x);
  
  // Use position-based data for our chart
  data = positionBasedData;
  
  // Find the flat spot (optimal surge zone)
  // First, find the minimum time
  let min_time_value = Math.min(...data.map(point => point.y));
  
  // Find all points within 0.1 seconds of the minimum time (flat spot)
  const tolerance = 0.1; // seconds
  let optimalZone = data.filter(point => point.y <= min_time_value + tolerance);
  let optimalStartPos = Math.min(...optimalZone.map(point => point.x));
  let optimalEndPos = Math.max(...optimalZone.map(point => point.x));
  
  // Also keep track of corresponding times for the optimal zone
  let optimalStartTime = timeBasedData.find(p => p.pos >= optimalStartPos)?.x || optimal_start;
  let optimalEndTime = timeBasedData.find(p => p.pos >= optimalEndPos)?.x || (optimal_start + surge_duration);
  
  // Create chart
  const ctx = document.getElementById('results_chart').getContext('2d');
  
  if (window.resultsChart) {
    window.resultsChart.destroy();
  }
  
  window.resultsChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [{
        label: 'Total Time',
        data: data,
        borderColor: '#2196F3',
        borderWidth: 3,
        pointRadius: 0,
        pointHoverRadius: 5,
        fill: false
      },
      {
        label: 'Optimal Zone',
        data: optimalZone,
        backgroundColor: 'rgba(76, 175, 80, 0.3)',
        borderColor: 'rgba(76, 175, 80, 0.8)',
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const point = context.raw;
              return `Surge at ${point.x.toFixed(0)}m (${point.time?.toFixed(1) || '?'}s) → Time: ${context.parsed.y.toFixed(1)}s`;
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          title: {
            display: true,
            text: 'Surge Start Position (m)'
          },
          ticks: {
            callback: function(value) {
              return value + 'm';
            }
          },
          // Limit x-axis to total distance
          min: 0,
          max: total_distance
        },
        y: {
          title: {
            display: true,
            text: 'Total Time (s)'
          },
          ticks: {
            callback: function(value) {
              return Math.round(value) + 's';
            }
          },
          // Set fixed limits with reasonable padding to avoid excessive decimal values
          suggestedMin: function(context) {
            const minTime = Math.min(...data.map(point => point.y));
            return Math.floor(minTime - 1); // 1 second below, rounded down
          },
          suggestedMax: function(context) {
            const minTime = Math.min(...data.map(point => point.y));
            const maxTime = Math.max(...data.map(point => point.y));
            // Ensure we show at least a 5 second range, but not more than needed
            return Math.ceil(Math.max(minTime + 5, maxTime)); // Round up
          }
        }
      },
      animation: {
        duration: 1000
      }
    }
  });
  
  // Show optimal result
  const optimalResultElement = document.getElementById('optimal_result');
  const optimalTextElement = document.getElementById('optimal_text');
  
  // Determine where the surge is happening on the route
  let surgeStartSegment = getSegmentDescription(optimal_result.surge_start_pos);
  let surgeEndSegment = getSegmentDescription(optimal_result.surge_end_pos);
  
  // Calculate speeds for display
  const normalSpeed = calculateSteadyStateSpeed(normal_power);
  const surgeSpeed = calculateSteadyStateSpeed(surge_power);
  
  optimalTextElement.innerHTML = `
    <strong>Fastest time:</strong> ${min_time.toFixed(1)} seconds<br>
    <strong>Optimal surge start:</strong> ${optimal_start.toFixed(1)} seconds into the ride<br>
    <strong>Location:</strong> Surge applied at ${optimal_result.surge_start_pos.toFixed(0)}m (${surgeStartSegment}) to ${optimal_result.surge_end_pos.toFixed(0)}m (${surgeEndSegment})<br>
    <strong>Speeds:</strong> Normal power: ${normalSpeed.toFixed(1)} m/s (${(normalSpeed*3.6).toFixed(1)} km/h), Surge power: ${surgeSpeed.toFixed(1)} m/s (${(surgeSpeed*3.6).toFixed(1)} km/h)
  `;
  
  optimalResultElement.style.display = 'block';
  
  window.resultsChart.update();
  
  // We already have optimalStartPos and optimalEndPos directly from the position-based data

  // Find the corresponding times for these positions for the result text
  const startTimeData = timeBasedData.find(d => Math.abs(d.pos - optimalStartPos) < 1);
  const endTimeData = timeBasedData.find(d => Math.abs(d.pos - optimalEndPos) < 1);
  const startTimeText = startTimeData ? startTimeData.x.toFixed(1) : '?';
  const endTimeText = endTimeData ? endTimeData.x.toFixed(1) : '?';
  
  // Update the optimal result text to show the range
  optimalTextElement.innerHTML = `
    <strong>Fastest time:</strong> ${min_time_value.toFixed(1)} seconds<br>
    <strong>Optimal surge zone:</strong> ${optimalStartPos.toFixed(0)}m to ${optimalEndPos.toFixed(0)}m<br>
    <strong>Time equivalent:</strong> ${startTimeText}s to ${endTimeText}s into the ride<br>
    <strong>Speeds:</strong> Normal power: ${normalSpeed.toFixed(1)} m/s (${(normalSpeed*3.6).toFixed(1)} km/h), Surge power: ${surgeSpeed.toFixed(1)} m/s (${(surgeSpeed*3.6).toFixed(1)} km/h)
  `;
  
  // Update the elevation profile with the optimal zone
  drawElevationProfile(optimalStartPos, optimalEndPos, true);
}

// Initialize
window.onload = function() {
  // Link sliders and number inputs
  const normalPowerSlider = document.getElementById('normal_power_slider');
  const normalPowerInput = document.getElementById('normal_power');
  const surgePowerSlider = document.getElementById('surge_power_slider');
  const surgePowerInput = document.getElementById('surge_power');
  const surgeDurationSlider = document.getElementById('surge_duration_slider');
  const surgeDurationInput = document.getElementById('surge_duration');
  
  // Advanced parameters
  const cyclistMassSlider = document.getElementById('cyclist_mass_slider');
  const cyclistMassInput = document.getElementById('cyclist_mass');
  const dragCoefficientSlider = document.getElementById('drag_coefficient_slider');
  const dragCoefficientInput = document.getElementById('drag_coefficient');
  const frontalAreaSlider = document.getElementById('frontal_area_slider');
  const frontalAreaInput = document.getElementById('frontal_area');
  
  // Helper function to link a slider and input
  function linkInputs(slider, input) {
    slider.addEventListener('input', function() {
      input.value = this.value;
    });
    
    input.addEventListener('input', function() {
      slider.value = this.value;
    });
  }
  
  // Link all input pairs
  linkInputs(normalPowerSlider, normalPowerInput);
  linkInputs(surgePowerSlider, surgePowerInput);
  linkInputs(surgeDurationSlider, surgeDurationInput);
  linkInputs(cyclistMassSlider, cyclistMassInput);
  linkInputs(dragCoefficientSlider, dragCoefficientInput);
  linkInputs(frontalAreaSlider, frontalAreaInput);
  
  // Draw initial elevation profile without markers
  drawElevationProfile(null, null);
  
  // Attach plot function to button click
  document.getElementById('plot_button').addEventListener('click', plot);
  
  // Setup tooltips
  const tooltipContainers = document.querySelectorAll('.tooltip');
  tooltipContainers.forEach(container => {
    const tooltipText = container.querySelector('div');
    
    container.addEventListener('mouseenter', () => {
      tooltipText.style.visibility = 'visible';
      tooltipText.style.opacity = '1';
    });
    
    container.addEventListener('mouseleave', () => {
      tooltipText.style.visibility = 'hidden';
      tooltipText.style.opacity = '0';
    });
  });
  
  // Initial plot
  plot();
};
</script>

### Understanding the Results
The simulation identifies the zone where your time will be minimized. There might be slight wobbles in some sections: this is just a result of the simulation's granularity. Any spot on the hill between where your "momentum is spent" and before your "surge would be applied downhill" is a good spot to surge.

Let's look at some general conclusions. Of course, this isn't real life! A good cyclist will be able to determine how long and how hard to push for a given hill, in a way that allows them to recover before the next hill or attack.

### Don't surge downhill!
This is the main takeaway from the simulation. Surging downhill is a waste of
energy, as you're already moving quickly and air resistance is high. The best
time to surge is when you're moving slowly, that is, on the uphill section.

I am very guilty of this in real life... and in fact thinking about it is why I
wrote this article in the first place!

### Don't surge before the climb!
I often do this, telling myself I'll "spread the load" a bit before so that the
peak power during the ascent is lower. But in most simulations, you'll find
that the time is dramatically slower if the surge is applied before the climb.
This is because all the extra power is "wasted" by accelerating on flat ground
where air resistance is the dominant force.

### Don't surge before your momentum is spent!
You'll also notice that the first optimal surge point is not exactly as the
start of the climb. This is because the surge is most effective when the rider
is at their slowest speed. And as we're carrying some momentum from the flat
section, the optimal surge point is a bit into the climb. Depending on the
settings, this might be 20-40 meters into the climb.

### Race Dynamics - surge at the bottom, or the crest?
In real racing, optimal surge timing can depend on tactical considerations
beyond pure physics. This simulation doesn't model drafting, but in a race, a
surge would be more effective at dropping riders when drafting is most useful,
i.e. at higher speeds in the downhill section.

This is why you will often see surges applied near the crest of a climb in
professional cycling - it's a strategic move to break away from competitors!
