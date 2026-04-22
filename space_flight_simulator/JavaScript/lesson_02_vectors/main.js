// ============================================================
//  LESSON 2: VECTORS — THE LANGUAGE OF MOVEMENT
//
//  Goals:
//    - Build a Vec3 class (used unchanged through Lesson 6)
//    - Understand add, sub, scale, length, normalize, dot, cross
//    - Use WASD to apply velocity to a ship (2D; z = 0 for now)
//    - Visualize velocity as an arrow and dot product in the HUD
// ============================================================


// ============================================================
//  VEC3 CLASS
// ============================================================

class Vec3 {
    constructor(x = 0, y = 0, z = 0) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    // ADD — combine two vectors component-by-component.
    // Example: position.add(velocity.scale(dt))  → new position
    add(v) {
        return new Vec3(this.x + v.x, this.y + v.y, this.z + v.z);
    }

    // SUBTRACT — vector FROM v TO this.
    // Example: planet.pos.sub(ship.pos)  → direction vector from ship to planet
    sub(v) {
        return new Vec3(this.x - v.x, this.y - v.y, this.z - v.z);
    }

    // SCALE — multiply every component by a scalar.
    // Example: velocity.scale(dt)  → displacement this frame
    //          direction.scale(-1) → reverse direction
    scale(s) {
        return new Vec3(this.x * s, this.y * s, this.z * s);
    }

    // LENGTH (MAGNITUDE) — the "size" of the vector.
    // From the 3D Pythagorean theorem: sqrt(x² + y² + z²)
    // Represents speed when applied to a velocity vector,
    // or distance when applied to a displacement vector.
    length() {
        return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
    }

    // LENGTH SQUARED — skips the sqrt, cheaper for comparisons.
    // Use when you only need to compare ("is A closer than B?"):
    //   a.lengthSquared() < b.lengthSquared()  — no sqrt needed
    lengthSquared() {
        return this.x * this.x + this.y * this.y + this.z * this.z;
    }

    // NORMALIZE — rescale so the vector has exactly length 1 (a "unit vector").
    // Strips out magnitude, leaving pure direction.
    // Example: (3, 4, 0) has length 5.  normalize() → (0.6, 0.8, 0) with length 1.
    // Use case: "move toward the planet" = direction.normalize().scale(speed)
    normalize() {
        const len = this.length();
        if (len === 0) return new Vec3(0, 0, 0);   // guard: can't normalize a zero vector
        return this.scale(1 / len);
    }

    // DOT PRODUCT — a.x·b.x + a.y·b.y + a.z·b.z
    //
    // When both vectors are unit vectors, result = cos(angle between them):
    //   dot =  1  → same direction       (0°)
    //   dot =  0  → perpendicular        (90°)
    //   dot = -1  → exactly opposite     (180°)
    //
    // Key uses:
    //   "Is the target ahead or behind me?"  → dot(myForward, toTarget) > 0 means ahead
    //   "How fast am I closing in?"          → dot(velocity, toTarget) (in units/sec)
    //   Lighting: cos(angle) between surface normal and light direction
    //   Camera transform: project a point onto each camera axis (Lessons 4-6)
    dot(v) {
        return this.x * v.x + this.y * v.y + this.z * v.z;
    }

    // CROSS PRODUCT — returns a NEW vector perpendicular to both a and b.
    // Direction follows the right-hand rule.
    // Magnitude = |a| * |b| * sin(angle) — zero when parallel.
    //
    // Key use: given "forward" and "right", find "up".
    //   up = forward.cross(right)  (or right.cross(forward), depending on convention)
    // We'll use this in Lesson 4 to build the camera's local coordinate frame.
    cross(v) {
        return new Vec3(
            this.y * v.z - this.z * v.y,   // x
            this.z * v.x - this.x * v.z,   // y
            this.x * v.y - this.y * v.x    // z
        );
    }

    toString(d = 1) {
        return `(${this.x.toFixed(d)}, ${this.y.toFixed(d)}, ${this.z.toFixed(d)})`;
    }
}


// ============================================================
//  WORLD SETUP
// ============================================================

const canvas = document.getElementById('canvas');
const ctx    = canvas.getContext('2d');

// Coordinate origin: canvas center (so our 2D "world" is centered).
// When drawing, we convert: screenX = cx + worldX,  screenY = cy - worldY
// The -worldY flip makes world-Y go UPWARD (like math), not downward (like screen).
const cx = canvas.width  / 2;
const cy = canvas.height / 2;

// Stars — static background
const NUM_STARS = 160;
const stars = [];
for (let i = 0; i < NUM_STARS; i++) {
    stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.2 + 0.3,
        a: Math.random() * 0.6 + 0.4
    });
}

// Planet colors sampled randomly from a nice palette
const PALETTE = ['#3a6fcc','#cc5533','#774422','#447755','#998833','#9944aa','#336688'];
function randomColor() { return PALETTE[Math.floor(Math.random() * PALETTE.length)]; }

// Planets — stored as Vec3 positions (z=0 in 2D)
const planets = [
    { pos: new Vec3(-220,  90, 0), radius: 42, color: '#3a6fcc', name: 'Hydra' },
    { pos: new Vec3( 190, -95, 0), radius: 28, color: '#cc5533', name: 'Ignis' },
    { pos: new Vec3( 260, 130, 0), radius: 55, color: '#774422', name: 'Magna' },
    { pos: new Vec3(-130,-150, 0), radius: 20, color: '#447755', name: 'Virid' },
];

// Ship state — position and velocity as Vec3.
// Everything is in "world units per second"; drawing maps world to screen.
const ship = {
    pos: new Vec3(0, 0, 0),
    vel: new Vec3(0, 0, 0),
};

// How strongly WASD adjusts velocity (units/sec added per second of keypress)
const THRUST = 130;

// Keyboard state — tracks which keys are currently held
const keysDown = new Set();
document.addEventListener('keydown', e => { keysDown.add(e.code); e.preventDefault(); });
document.addEventListener('keyup',   e => keysDown.delete(e.code));


// ============================================================
//  GAME LOOP
// ============================================================

let lastTime = -1;

function gameLoop(timestamp) {
    const dt = (lastTime < 0) ? 0 : (timestamp - lastTime) / 1000;
    lastTime = timestamp;
    update(dt);
    draw();
    requestAnimationFrame(gameLoop);
}

function update(dt) {

    // WASD: each held key modifies velocity (not position directly).
    // In Lesson 5 we'll make keys modify ACCELERATION instead — more realistic.
    if (keysDown.has('KeyW')) ship.vel.y += THRUST * dt;   // world-y up = positive
    if (keysDown.has('KeyS')) ship.vel.y -= THRUST * dt;
    if (keysDown.has('KeyA')) ship.vel.x -= THRUST * dt;
    if (keysDown.has('KeyD')) ship.vel.x += THRUST * dt;

    // Space: damp velocity toward zero (soft brake for convenience)
    if (keysDown.has('Space')) {
        ship.vel = ship.vel.scale(0.90);
    }

    // Integrate: position += velocity * dt
    // This is the fundamental physics step — same in every game engine.
    ship.pos = ship.pos.add(ship.vel.scale(dt));

    // Soft world boundary — bounce gently off the edges
    const BOUND = 320;
    if (ship.pos.x >  BOUND) { ship.pos.x =  BOUND; ship.vel.x *= -0.5; }
    if (ship.pos.x < -BOUND) { ship.pos.x = -BOUND; ship.vel.x *= -0.5; }
    if (ship.pos.y >  BOUND) { ship.pos.y =  BOUND; ship.vel.y *= -0.5; }
    if (ship.pos.y < -BOUND) { ship.pos.y = -BOUND; ship.vel.y *= -0.5; }
}


// ============================================================
//  DRAWING
// ============================================================

// Convert world (x, y) to screen pixel coordinates.
// World center (0,0) maps to canvas center (cx, cy).
// World +y is "up"; screen +y is "down" — so we negate wy.
function w2s(wx, wy) {
    return { sx: cx + wx, sy: cy - wy };
}

function draw() {

    // Clear
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Stars
    for (const s of stars) {
        ctx.fillStyle = `rgba(210, 225, 255, ${s.a})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
    }

    // Find nearest planet (for the direction-vector visualization)
    let nearest = null;
    let nearestDist = Infinity;
    for (const p of planets) {
        const d = p.pos.sub(ship.pos).length();
        if (d < nearestDist) { nearestDist = d; nearest = p; }
    }

    // Planets
    for (const planet of planets) {
        const { sx, sy } = w2s(planet.pos.x, planet.pos.y);

        ctx.fillStyle = planet.color;
        ctx.beginPath();
        ctx.arc(sx, sy, planet.radius, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = 'rgba(190,210,255,0.65)';
        ctx.font = '11px Courier New';
        ctx.textAlign = 'center';
        ctx.fillText(planet.name, sx, sy - planet.radius - 6);
    }

    const { sx: shipSX, sy: shipSY } = w2s(ship.pos.x, ship.pos.y);

    // Direction vector to nearest planet (dashed line)
    if (nearest) {
        const { sx: psx, sy: psy } = w2s(nearest.pos.x, nearest.pos.y);
        ctx.setLineDash([4, 7]);
        ctx.strokeStyle = 'rgba(180, 200, 255, 0.25)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(shipSX, shipSY);
        ctx.lineTo(psx, psy);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // Velocity arrow (yellow arrow from ship in the direction of movement)
    const VEL_SCALE = 0.14;   // visual scale factor — doesn't affect physics
    drawArrow(
        shipSX, shipSY,
        shipSX + ship.vel.x * VEL_SCALE,
        shipSY - ship.vel.y * VEL_SCALE,   // negate because screen y is down
        '#ffcc44',
        'velocity'
    );

    // Ship glow + core
    ctx.fillStyle = 'rgba(80, 180, 255, 0.18)';
    ctx.beginPath();
    ctx.arc(shipSX, shipSY, 10, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#70d8ff';
    ctx.beginPath();
    ctx.arc(shipSX, shipSY, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // HUD
    drawHUD(nearest);
}


// Draw an arrow from (x1,y1) to (x2,y2).
function drawArrow(x1, y1, x2, y2, color, label) {
    const dx  = x2 - x1;
    const dy  = y2 - y1;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 3) return;

    ctx.strokeStyle = color;
    ctx.lineWidth   = 1.5;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    // Arrowhead (small triangle at tip)
    const angle   = Math.atan2(dy, dx);
    const headLen = 8;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLen * Math.cos(angle - 0.42), y2 - headLen * Math.sin(angle - 0.42));
    ctx.lineTo(x2 - headLen * Math.cos(angle + 0.42), y2 - headLen * Math.sin(angle + 0.42));
    ctx.closePath();
    ctx.fill();

    if (label) {
        ctx.fillStyle   = color;
        ctx.font        = '10px Courier New';
        ctx.textAlign   = 'left';
        ctx.fillText(label, x2 + 5, y2 + 4);
    }
}


// Draw the HUD box in the top-left corner.
function drawHUD(nearest) {

    // Dot product of velocity-direction against direction-to-nearest-planet.
    // Positive → heading toward planet. Negative → heading away.
    let dotToNearest = 0;
    if (nearest && ship.vel.length() > 1) {
        const toTarget = nearest.pos.sub(ship.pos).normalize();
        const velDir   = ship.vel.normalize();
        dotToNearest   = toTarget.dot(velDir);
    }

    const pad   = 12;
    const lineH = 16;
    const lines = [
        { text: `pos:   ${ship.pos.toString(0)}`, color: '#8eb8e8' },
        { text: `vel:   ${ship.vel.toString(1)}`, color: '#ffcc44' },
        { text: `speed: ${ship.vel.length().toFixed(1)} u/s`, color: '#88ff88' },
        { text: `dot → nearest: ${dotToNearest.toFixed(2)}`, color: '#ff8888' },
        { text: `  (1=toward, -1=away)`, color: '#505870' },
    ];

    // Background
    ctx.fillStyle = 'rgba(4, 8, 18, 0.78)';
    ctx.fillRect(pad, pad, 258, lines.length * lineH + 14);

    ctx.font      = '11px Courier New';
    ctx.textAlign = 'left';
    for (let i = 0; i < lines.length; i++) {
        ctx.fillStyle = lines[i].color;
        ctx.fillText(lines[i].text, pad + 8, pad + 13 + i * lineH);
    }
}


// ---- START ----
requestAnimationFrame(gameLoop);
