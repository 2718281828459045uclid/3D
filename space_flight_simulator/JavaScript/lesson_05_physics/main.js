// ============================================================
//  LESSON 5: THRUST AND PHYSICS
//
//  Goals:
//    - Give the camera a position that changes each frame
//    - WASD apply ACCELERATION (thrust) in camera-local directions
//    - Integrate: acceleration → velocity → position each frame
//    - Experience zero-gravity drift (no friction)
//    - HUD shows velocity and speed
//
//  NEW this lesson:
//    - camera.pos and camera.vel are Vec3 values
//    - worldToCamera() now subtracts camera.pos
//    - Physics update uses double-integration (Euler method)
// ============================================================


// ---- Vec3 ----
class Vec3 {
    constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
    add(v)      { return new Vec3(this.x + v.x, this.y + v.y, this.z + v.z); }
    sub(v)      { return new Vec3(this.x - v.x, this.y - v.y, this.z - v.z); }
    scale(s)    { return new Vec3(this.x * s,   this.y * s,   this.z * s  ); }
    dot(v)      { return this.x * v.x + this.y * v.y + this.z * v.z; }
    length()    { return Math.sqrt(this.x*this.x + this.y*this.y + this.z*this.z); }
    normalize() { const l = this.length(); return l === 0 ? new Vec3() : this.scale(1/l); }
    toString(d = 1) { return `(${this.x.toFixed(d)}, ${this.y.toFixed(d)}, ${this.z.toFixed(d)})`; }
}


// ---- CANVAS ----
const canvas = document.getElementById('canvas');
const ctx    = canvas.getContext('2d');
const CX     = canvas.width  / 2;
const CY     = canvas.height / 2;
const FOCAL_LENGTH = 500;
const NEAR_CLIP    = 1.0;


// ---- CAMERA ----
const camera = {
    pos:   new Vec3(0, 0, 0),   // world position — starts at origin
    vel:   new Vec3(0, 0, 0),   // velocity in world-space units/sec
    yaw:   0,                    // radians
    pitch: 0,                    // radians
};

// How much each thrust key accelerates the ship per second (units/sec²)
const THRUST_ACCEL = 80;
// How fast arrow keys rotate the camera (radians/sec)
const TURN_SPEED   = 1.2;


// ---- KEYBOARD ----
const keysDown = new Set();
document.addEventListener('keydown', e => { keysDown.add(e.code); e.preventDefault(); });
document.addEventListener('keyup',   e => keysDown.delete(e.code));


// ---- CAMERA BASIS VECTORS (same as Lesson 4) ----
function computeCameraVectors() {
    const cosP = Math.cos(camera.pitch);
    const sinP = Math.sin(camera.pitch);
    const cosY = Math.cos(camera.yaw);
    const sinY = Math.sin(camera.yaw);

    const forward = new Vec3(cosP * sinY,  sinP,        cosP * cosY);
    const right   = new Vec3(cosY,         0,           -sinY);
    const up      = new Vec3(-sinP * sinY, cosP,        -sinP * cosY);

    return { forward, right, up };
}


// ---- WORLD → CAMERA TRANSFORM ----
// NEW: subtracts camera.pos so the world moves relative to us.
function worldToCamera(worldPoint, camVec) {
    // rel = vector from camera position to the world point
    const rel = worldPoint.sub(camera.pos);

    return new Vec3(
        rel.dot(camVec.right),
        rel.dot(camVec.up),
        rel.dot(camVec.forward)
    );
}

function project(camPoint) {
    if (camPoint.z <= NEAR_CLIP) return null;
    return {
        sx:    (camPoint.x / camPoint.z) * FOCAL_LENGTH + CX,
        sy:   (-camPoint.y / camPoint.z) * FOCAL_LENGTH + CY,
        scale: FOCAL_LENGTH / camPoint.z,
    };
}


// ---- STARS ----
const NUM_STARS = 250;
const stars = [];
for (let i = 0; i < NUM_STARS; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    stars.push({
        dir:        new Vec3(Math.sin(phi)*Math.cos(theta), Math.sin(phi)*Math.sin(theta), Math.cos(phi)),
        brightness: Math.random() * 0.7 + 0.3,
        size:       Math.random() * 1.1 + 0.3,
    });
}

// ---- PLANETS ----
const COLORS = ['#3a6fcc','#cc5533','#774422','#447755','#998833','#9944aa','#336688','#aa6633'];
const NAMES  = ['Hydra','Ignis','Magna','Virid','Lutea','Ceres','Nebula','Ferro',
                'Glacis','Pyrex','Umbra','Solus','Terra','Argon','Noctis'];
const planets = [];
for (let i = 0; i < 15; i++) {
    planets.push({
        pos:    new Vec3(
            (Math.random() - 0.5) * 2000,
            (Math.random() - 0.5) * 1500,
            Math.random() * 3000 + 200
        ),
        radius: Math.random() * 60 + 15,
        color:  COLORS[i % COLORS.length],
        name:   NAMES[i % NAMES.length],
    });
}


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

    // 1. Compute camera orientation vectors (needed for thrust direction)
    const camVec = computeCameraVectors();

    // 2. Handle rotation (same as Lesson 4)
    if (keysDown.has('ArrowLeft'))  camera.yaw   -= TURN_SPEED * dt;
    if (keysDown.has('ArrowRight')) camera.yaw   += TURN_SPEED * dt;
    if (keysDown.has('ArrowUp'))    camera.pitch += TURN_SPEED * dt;
    if (keysDown.has('ArrowDown'))  camera.pitch -= TURN_SPEED * dt;

    const MAX_PITCH = Math.PI / 2 - 0.01;
    camera.pitch = Math.max(-MAX_PITCH, Math.min(MAX_PITCH, camera.pitch));

    // 3. Handle thrust — WASD keys apply ACCELERATION, not direct velocity change.
    //
    //   Newton's 2nd Law: F = m·a
    //   We assume mass = 1, so acceleration = force = THRUST_ACCEL.
    //
    //   Each frame: velocity += thrustDirection * THRUST_ACCEL * dt
    //
    //   Why multiply by dt?
    //   THRUST_ACCEL is in units/sec².  Multiplying by dt (seconds) gives
    //   the velocity change for this single frame (units/sec).
    //   Without dt, holding W longer at higher frame rate would give more speed.
    //
    //   Key difference from Lesson 2:
    //   Lesson 2 added directly to velocity (instant speed change).
    //   Now we add to velocity over time — gradual acceleration.  More realistic.
    if (keysDown.has('KeyW')) camera.vel = camera.vel.add(camVec.forward.scale( THRUST_ACCEL * dt));
    if (keysDown.has('KeyS')) camera.vel = camera.vel.add(camVec.forward.scale(-THRUST_ACCEL * dt));
    if (keysDown.has('KeyA')) camera.vel = camera.vel.add(camVec.right.scale(  -THRUST_ACCEL * dt));
    if (keysDown.has('KeyD')) camera.vel = camera.vel.add(camVec.right.scale(   THRUST_ACCEL * dt));

    // 4. Integrate position from velocity.
    //
    //   position += velocity * dt
    //
    //   This is Euler integration — the simplest numerical integration method.
    //   Combined with the velocity step above, we get:
    //
    //     velocity += acceleration * dt    (integrate acceleration → velocity)
    //     position += velocity    * dt    (integrate velocity    → position)
    //
    //   In zero gravity there is no force slowing us down, so velocity
    //   accumulates indefinitely.  That's Newton's 1st law: objects stay in
    //   motion unless acted on by a force.
    camera.pos = camera.pos.add(camera.vel.scale(dt));
}


// ============================================================
//  DRAWING (same pipeline as Lesson 4)
// ============================================================

function draw() {
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const camVec = computeCameraVectors();

    // Stars — transform direction into camera space, then project
    for (const star of stars) {
        const camDir = new Vec3(
            star.dir.dot(camVec.right),
            star.dir.dot(camVec.up),
            star.dir.dot(camVec.forward)
        );
        if (camDir.z <= 0) continue;
        const sx = (camDir.x / camDir.z) * FOCAL_LENGTH + CX;
        const sy = (-camDir.y / camDir.z) * FOCAL_LENGTH + CY;
        if (sx < -10 || sx > canvas.width + 10 || sy < -10 || sy > canvas.height + 10) continue;
        ctx.fillStyle = `rgba(210, 225, 255, ${star.brightness})`;
        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        ctx.fill();
    }

    // Planets
    const visible = [];
    for (const planet of planets) {
        const camPoint = worldToCamera(planet.pos, camVec);
        const proj     = project(camPoint);
        if (proj) visible.push({ planet, camPoint, proj });
    }
    visible.sort((a, b) => b.camPoint.z - a.camPoint.z);

    for (const { planet, proj } of visible) {
        const r = planet.radius * proj.scale;
        if (r < 0.5) continue;

        ctx.fillStyle = planet.color;
        ctx.beginPath();
        ctx.arc(proj.sx, proj.sy, r, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth   = 1;
        ctx.stroke();

        if (r > 8) {
            ctx.fillStyle = 'rgba(190,210,255,0.6)';
            ctx.font      = '11px Courier New';
            ctx.textAlign = 'center';
            ctx.fillText(planet.name, proj.sx, proj.sy - r - 5);
        }
    }

    // Crosshair
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(CX - 10, CY); ctx.lineTo(CX + 10, CY);
    ctx.moveTo(CX, CY - 10); ctx.lineTo(CX, CY + 10);
    ctx.stroke();

    // HUD
    drawHUD();
}

function drawHUD() {
    const speed   = camera.vel.length();
    const pad     = 12;
    const lineH   = 16;

    const lines = [
        { t: `pos:   ${camera.pos.toString(0)}`,     c: '#8eb8e8' },
        { t: `vel:   ${camera.vel.toString(1)}`,     c: '#ffcc44' },
        { t: `speed: ${speed.toFixed(1)} u/s`,       c: '#88ff88' },
        { t: `yaw:   ${(camera.yaw   * 180/Math.PI).toFixed(1)}°`, c: '#ff8888' },
        { t: `pitch: ${(camera.pitch * 180/Math.PI).toFixed(1)}°`, c: '#cc88ff' },
        { t: 'WASD=thrust  Arrows=rotate',            c: '#404860' },
    ];

    ctx.fillStyle = 'rgba(4,8,18,0.78)';
    ctx.fillRect(pad, pad, 280, lines.length * lineH + 14);
    ctx.font      = '11px Courier New';
    ctx.textAlign = 'left';
    for (let i = 0; i < lines.length; i++) {
        ctx.fillStyle = lines[i].c;
        ctx.fillText(lines[i].t, pad + 8, pad + 13 + i * lineH);
    }
}


// ---- START ----
requestAnimationFrame(gameLoop);
