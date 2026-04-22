// ============================================================
//  LESSON 1: THE CANVAS AND COORDINATES
//
//  Goals:
//    - Get a canvas and drawing context
//    - Understand the 2D coordinate system
//    - Draw shapes (stars, planets, a ship)
//    - Run a game loop with requestAnimationFrame
//    - Use delta time for frame-rate independent movement
// ============================================================


// ---- CANVAS SETUP ----

// Grab the <canvas> element from the HTML.
const canvas = document.getElementById('canvas');

// getContext('2d') gives us the 2D drawing API.
// All drawing commands live on this object: fillRect, arc, stroke, etc.
// Alternative: getContext('webgl') would give raw GPU access — that's what Lesson 6
// could eventually grow into, but 2D canvas is perfect for learning the concepts.
const ctx = canvas.getContext('2d');


// ---- MOUSE TRACKING ----
// We'll display the mouse position so the student can see how coordinates work.
let mouseX = 0;
let mouseY = 0;

canvas.addEventListener('mousemove', function(event) {
    // getBoundingClientRect() gives the canvas position relative to the page.
    // Subtracting it converts the window-relative mouse position to canvas-relative.
    const rect = canvas.getBoundingClientRect();
    mouseX = Math.round(event.clientX - rect.left);
    mouseY = Math.round(event.clientY - rect.top);
});


// ---- STARS ----
// We create all stars once at startup and store them in an array.
// Creating them once (not every frame) is important for performance.
const NUM_STARS = 200;
const stars = [];

for (let i = 0; i < NUM_STARS; i++) {
    stars.push({
        x:          Math.random() * canvas.width,    // 0 to canvas width
        y:          Math.random() * canvas.height,   // 0 to canvas height
        radius:     Math.random() * 1.2 + 0.3,       // 0.3–1.5 px tiny dots
        brightness: Math.random() * 0.6 + 0.4        // 0.4–1.0 opacity
    });
}


// ---- PLANETS ----
// Placed by hand for this lesson.  In Lesson 3 we'll generate them randomly in 3D space.
const planets = [
    { x: 140, y: 180, radius: 44, color: '#3a6fcc', name: 'Hydra' },
    { x: 490, y: 130, radius: 28, color: '#cc5533', name: 'Ignis' },
    { x: 580, y: 350, radius: 62, color: '#774422', name: 'Magna' },
    { x: 240, y: 360, radius: 20, color: '#447755', name: 'Virid' },
    { x: 620, y: 220, radius: 15, color: '#998833', name: 'Lutea' },
];


// ---- SHIP ----
// The ship is a glowing dot.  It has a position (x, y) and a velocity (vx, vy).
// Velocity is measured in pixels per second.
const ship = {
    x:  350,   // starting x — roughly center of canvas
    y:  230,   // starting y
    vx:  55,   // 55 pixels/sec to the right
    vy:  20,   // 20 pixels/sec downward (remember: canvas y increases down)
};


// ---- GAME LOOP ----

// lastTime stores the browser timestamp of the previous frame.
// We start it at -1 as a sentinel meaning "no previous frame yet".
let lastTime = -1;

// gameLoop is called once per animation frame (~60 times/sec).
// The browser passes a 'timestamp' in milliseconds.
function gameLoop(timestamp) {

    // --- DELTA TIME ---
    // dt = seconds elapsed since the last frame.
    // Typical value at 60 fps: ~0.0167 seconds (1/60).
    // First frame: use 0 so nothing teleports.
    const dt = (lastTime < 0) ? 0 : (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    update(dt);
    draw();

    // Register for the NEXT frame.  This keeps the loop going.
    requestAnimationFrame(gameLoop);
}


// ---- UPDATE ----
// Move things forward by dt seconds.
function update(dt) {

    // Physics: new position = old position + velocity * time
    //
    //   position = position + velocity * dt
    //
    // If vx = 55 px/s and dt = 0.0167 s, we move 55 * 0.0167 ≈ 0.92 px this frame.
    // Over 60 frames (1 second) that totals to exactly 55 px — correct!
    ship.x += ship.vx * dt;
    ship.y += ship.vy * dt;

    // Wrap the ship around the canvas edges so it never disappears.
    if (ship.x > canvas.width)  ship.x -= canvas.width;
    if (ship.x < 0)             ship.x += canvas.width;
    if (ship.y > canvas.height) ship.y -= canvas.height;
    if (ship.y < 0)             ship.y += canvas.height;
}


// ---- DRAW ----
function draw() {

    // CLEAR — paint the whole canvas with our background color.
    // Without this, every frame stacks on top of the last, leaving trails.
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // --- Stars ---
    for (const star of stars) {
        // rgba(r, g, b, alpha) — alpha 0 = invisible, 1 = opaque.
        ctx.fillStyle = `rgba(210, 225, 255, ${star.brightness})`;

        // Drawing a circle:
        //   1. beginPath() — start a new shape definition
        //   2. arc(x, y, radius, startAngle, endAngle)
        //      angles in radians: 2*PI = full circle
        //   3. fill() — paint the interior
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    // --- Planets ---
    for (const planet of planets) {

        // Main colored disk
        ctx.fillStyle = planet.color;
        ctx.beginPath();
        ctx.arc(planet.x, planet.y, planet.radius, 0, Math.PI * 2);
        ctx.fill();

        // Faint white outline (stroke = draw the path edge, not the fill)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.14)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Name label above the planet
        ctx.fillStyle = 'rgba(190, 210, 255, 0.65)';
        ctx.font = '11px Courier New';
        ctx.textAlign = 'center';
        ctx.fillText(planet.name, planet.x, planet.y - planet.radius - 6);
    }

    // --- Ship ---
    // Layer 1: soft glow (large transparent circle)
    ctx.fillStyle = 'rgba(80, 180, 255, 0.18)';
    ctx.beginPath();
    ctx.arc(ship.x, ship.y, 10, 0, Math.PI * 2);
    ctx.fill();

    // Layer 2: bright core
    ctx.fillStyle = '#70d8ff';
    ctx.beginPath();
    ctx.arc(ship.x, ship.y, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // Ship position label
    ctx.fillStyle = '#70d8ff';
    ctx.font = '11px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText(`ship (${Math.round(ship.x)}, ${Math.round(ship.y)})`, ship.x + 12, ship.y + 4);

    // --- Coordinate Axis Diagram (bottom-left corner) ---
    drawAxisDiagram(30, 428);

    // --- Mouse Position Readout (top-left) ---
    ctx.fillStyle = 'rgba(180, 200, 255, 0.5)';
    ctx.font = '11px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText(`mouse: (${mouseX}, ${mouseY})`, 10, 18);
}


// Draw a small labeled X/Y axis diagram to illustrate the coordinate system.
function drawAxisDiagram(originX, originY) {
    const len = 40;
    ctx.lineWidth = 1.5;

    // X axis — points RIGHT (positive x = move right)
    ctx.strokeStyle = '#ff6666';
    ctx.beginPath();
    ctx.moveTo(originX, originY);
    ctx.lineTo(originX + len, originY);
    ctx.stroke();
    ctx.fillStyle = '#ff6666';
    ctx.font = '11px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText('x +', originX + len + 3, originY + 4);

    // Y axis — points DOWN (positive y = move down — opposite of math class!)
    ctx.strokeStyle = '#66ff88';
    ctx.beginPath();
    ctx.moveTo(originX, originY);
    ctx.lineTo(originX, originY + len);
    ctx.stroke();
    ctx.fillStyle = '#66ff88';
    ctx.textAlign = 'center';
    ctx.fillText('y +', originX, originY + len + 12);

    // Origin dot
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(originX, originY, 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = 'rgba(150, 170, 200, 0.55)';
    ctx.font = '10px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText('(0,0) top-left', originX + 6, originY - 5);
}


// ---- START ----
// Kick off the loop. The browser will call gameLoop every ~16ms.
requestAnimationFrame(gameLoop);
