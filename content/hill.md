Title: Cycling up a hill
Date: 2025-03-21
Category: Physics
Tags: cycling, physics, simulation, chart.js
Slug: cycling-up-a-hill
Authors: François Leblanc
Summary: A simple cycling simulator that calculates the time it takes to cycle up a hill with a surge of power.

## The Physics of Cycling Uphill

When cycling, several forces affect your motion:

1. **Propulsive Force**: The power you generate divided by your velocity
2. **Gravity**: Pulls you down, making climbs harder. The heavier you are, the more power you need to climb.
3. **Rolling Resistance**: Friction between tires and road, linear with velocity.
4. **Air Resistance**: Increases with the square of your velocity

The simulation below models a 1.2km route with a hill in the middle. You can
apply a power surge at different points to see when it's most effective.

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
        <input type="range" id="surge_power_slider" min="200" max="800" value="350" style="width: 100%;">
        <input type="number" id="surge_power" value="350" style="width: 100px;">
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
            <input type="range" id="frontal_area_slider" min="0.3" max="0.7" step="0.01" value="0.36" style="width: 100%;">
            <input type="number" id="frontal_area" value="0.36" step="0.01" style="width: 100px;">
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
  <canvas id="elevation_chart" width="800" height="200"></canvas>
</div>

<!-- Container for the results chart -->
<div style="margin: 20px 0;">
  <h3>Total Time vs. Surge Start Time</h3>
  <canvas id="results_chart" width="800" height="400"></canvas>
</div>

<!-- Container for optimal result -->
<div id="optimal_result" style="margin: 20px 0; padding: 15px; background: #e8f5e9; border-radius: 8px; display: none;">
  <h3>First Optimal Surge Point</h3>
  <p id="optimal_text"></p>
  <p><em>Note: The time curve may have flat spots where other surge points yield similar results. This shows the first point that provides the minimum time.</em></p>
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
let A = 0.36; // frontal area in m^2

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
function drawElevationProfile(optimalStartPos = null, optimalEndPos = null) {
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
  
  window.elevationChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: datasets
    },
    options: {
      responsive: true,
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
          }
        },
        y: {
          title: {
            display: true,
            text: 'Elevation (m)'
          },
          ticks: {
            callback: function(value) {
              return value + 'm';
            }
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
  
  // Simulate for different surge start times
  let data = [];
  let min_time = Infinity;
  let optimal_start = 0;
  let optimal_result = null;
  
  // Calculate time points based on route to ensure we sample the key segments well
  const timePoints = [];
  for (let t = 0; t <= 200; t += 10) {
    timePoints.push(t);
  }
  
  // Add more granular points around the uphill section
  for (let t = 10; t <= 150; t += 2) {
    timePoints.push(t);
  }
  
  // Sort and remove duplicates
  const uniqueTimePoints = [...new Set(timePoints)].sort((a, b) => a - b);
  
  for (let t_surge_start of uniqueTimePoints) {
    let result = simulate(normal_power, surge_power, surge_duration, t_surge_start);
    data.push({x: t_surge_start, y: result.total_time});
    
    if (result.total_time < min_time) {
      min_time = result.total_time;
      optimal_start = t_surge_start;
      optimal_result = result;
    }
  }
  
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
      }]
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Surge at ${context.parsed.x.toFixed(1)}s → Time: ${context.parsed.y.toFixed(1)}s`;
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
            text: 'Surge Start Time (s)'
          },
          ticks: {
            callback: function(value) {
              return value + 's';
            }
          },
          // Limit x-axis to 200 seconds
          min: 0,
          max: 200
        },
        y: {
          title: {
            display: true,
            text: 'Total Time (s)'
          },
          ticks: {
            callback: function(value) {
              return value + 's';
            }
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
  
  // Mark the optimal point on the chart
  window.resultsChart.data.datasets.push({
    label: 'Optimal Point',
    data: [{x: optimal_start, y: min_time}],
    backgroundColor: '#F44336',
    pointRadius: 8,
    pointHoverRadius: 10
  });
  
  window.resultsChart.update();
  
  // Update the elevation profile with markers for the optimal surge
  drawElevationProfile(optimal_result.surge_start_pos, optimal_result.surge_end_pos);
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
The simulation identifies the **first** optimal time to apply your power surge.
Due to the physics of cycling, there may be multiple points where surging
provides similar time benefits - this creates flat spots in the time curve.

But here, let's look at some general conclusions.

### Don't surge before the climb!
In most simulations, you'll find that the time is dramatically slower if the
surge is applied before the climb. This is because all the extra power is
"wasted" by accelerating on flat ground where air resistance is the dominant
force.

### Don't surge before your momentum is lost!
You'll also notice that the first optimal surge point is not exactly as the
start of the climb. This is because the surge is most effective when the rider
is at their slowest speed, just before the climb starts.

### Race Dynamics - surge at the bottom, or the crest?
In real racing, optimal surge timing can depend on tactical considerations
beyond pure physics. This simulation doesn't model drafting, but in a race, a
surge would be more effective at dropping riders when drafting is most useful,
i.e. at higher speeds in the downhill section.

This is why you will often see surges applied near the crest of a climb in
professional cycling - it's a strategic move to break away from competitors!
