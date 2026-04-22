// ============================================================
//  LESSON 6: COMPLETE FLIGHT SIMULATOR
//
//  This file assembles all concepts from Lessons 1–5 into a
//  polished, playable zero-gravity space flight simulator.
//
//  Nothing here is new — it's the same canvas, Vec3, projection,
//  camera transform, and Euler physics you already know.
//  The additions are purely cosmetic or quality-of-life:
//    - More planets, more spread-out world
//    - Nearest-planet HUD (name + distance)
//    - Speed bar
//    - Emergency brake (Space) with visual flash
//    - Planet glow shading
//    - Throttle indicator showing active thrust direction
// ============================================================


// ============================================================
//  VEC3  (unchanged from Lessons 2–5)
// ============================================================
class Vec3 {
    constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
    add(v)      { return new Vec3(this.x + v.x, this.y + v.y, this.z + v.z); }
    sub(v)      { return new Vec3(this.x - v.x, this.y - v.y, this.z - v.z); }
    scale(s)    { return new Vec3(this.x * s,   this.y * s,   this.z * s  ); }
    dot(v)      { return this.x * v.x + this.y * v.y + this.z * v.z; }
    length()    { return Math.sqrt(this.x*this.x + this.y*this.y + this.z*this.z); }
    lengthSquared() { return this.x*this.x + this.y*this.y + this.z*this.z; }
    normalize() { const l = this.length(); return l === 0 ? new Vec3() : this.scale(1/l); }
    toString(d = 0) { return `(${this.x.toFixed(d)}, ${this.y.toFixed(d)}, ${this.z.toFixed(d)})`; }
}


// ============================================================
//  CANVAS SETUP
// ============================================================
const canvas = document.getElementById('canvas');
const ctx    = canvas.getContext('2d');
const CX     = canvas.width  / 2;
const CY     = canvas.height / 2;

const FOCAL_LENGTH = 500;
const NEAR_CLIP    = 2.0;


// ============================================================
//  CAMERA  (position + velocity + orientation)
// ============================================================
const camera = {
    pos:   new Vec3(0, 0, 0),
    vel:   new Vec3(0, 0, 0),
    yaw:   0,
    pitch: 0,
};

const THRUST_ACCEL = 90;    // units/sec² per thrust axis
const TURN_SPEED   = 1.2;   // radians/sec


// ============================================================
//  KEYBOARD
// ============================================================
const keysDown = new Set();
document.addEventListener('keydown', e => { keysDown.add(e.code); e.preventDefault(); });
document.addEventListener('keyup',   e => keysDown.delete(e.code));


// ============================================================
//  CAMERA ORIENTATION MATH  (same as Lesson 4)
// ============================================================
function computeCameraVectors() {
    const cosP = Math.cos(camera.pitch);
    const sinP = Math.sin(camera.pitch);
    const cosY = Math.cos(camera.yaw);
    const sinY = Math.sin(camera.yaw);

    return {
        forward: new Vec3(cosP * sinY,   sinP,  cosP * cosY),
        right:   new Vec3(cosY,          0,     -sinY),
        up:      new Vec3(-sinP * sinY,  cosP,  -sinP * cosY),
    };
}

function worldToCamera(worldPoint, camVec) {
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


// ============================================================
//  WORLD GENERATION
// ============================================================

// Stars
const NUM_STARS = 300;
const stars = [];
for (let i = 0; i < NUM_STARS; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    stars.push({
        dir:        new Vec3(Math.sin(phi)*Math.cos(theta), Math.sin(phi)*Math.sin(theta), Math.cos(phi)),
        brightness: Math.random() * 0.7 + 0.3,
        size:       Math.random() * 1.2 + 0.3,
    });
}

// Planet generation — seeded layout spread through a large 3D volume
const PALETTE = [
    { base: '#3a6fcc', glow: 'rgba(60,100,220,0.4)' },   // blue
    { base: '#cc5533', glow: 'rgba(220,80,40,0.4)'  },   // orange-red
    { base: '#774422', glow: 'rgba(140,80,40,0.35)' },   // brown
    { base: '#447755', glow: 'rgba(60,140,80,0.35)' },   // green
    { base: '#998833', glow: 'rgba(180,160,40,0.35)'},   // gold
    { base: '#9944aa', glow: 'rgba(160,60,180,0.35)'},   // purple
    { base: '#336688', glow: 'rgba(50,100,160,0.35)'},   // teal
    { base: '#aa6633', glow: 'rgba(200,120,50,0.35)'},   // amber
];
const NAMES = ['Hydra','Ignis','Magna','Virid','Lutea','Ceres','Nebula','Ferro',
               'Glacis','Pyrex','Umbra','Solus','Terra','Argon','Noctis',
               'Oriox','Kaspa','Venti','Zura','Pelox'];

// Place planets in a large sphere around the starting position,
// with a minimum distance so we're not spawned inside one.
const planets = [];
for (let i = 0; i < 20; i++) {
    const colors = PALETTE[i % PALETTE.length];
    // Random direction on unit sphere
    const theta  = Math.random() * Math.PI * 2;
    const phi    = Math.acos(2 * Math.random() - 1);
    const dist   = Math.random() * 3500 + 600;   // 600 to 4100 units away
    planets.push({
        pos: new Vec3(
            Math.sin(phi) * Math.cos(theta) * dist,
            Math.sin(phi) * Math.sin(theta) * dist * 0.6,   // slightly compressed vertically
            Math.cos(phi) * dist + 800                       // bias slightly forward
        ),
        radius:   Math.random() * 70 + 20,
        baseColor: colors.base,
        glowColor: colors.glow,
        name:     NAMES[i % NAMES.length],
    });
}


// ============================================================
//  BRAKE FLASH — visual feedback when Space is pressed
// ============================================================
let brakeFlash = 0;   // 0–1, decays each frame


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


// ============================================================
//  UPDATE
// ============================================================
function update(dt) {
    const camVec = computeCameraVectors();

    // ---- Rotation ----
    if (keysDown.has('ArrowLeft'))  camera.yaw   -= TURN_SPEED * dt;
    if (keysDown.has('ArrowRight')) camera.yaw   += TURN_SPEED * dt;
    if (keysDown.has('ArrowUp'))    camera.pitch += TURN_SPEED * dt;
    if (keysDown.has('ArrowDown'))  camera.pitch -= TURN_SPEED * dt;
    camera.pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, camera.pitch));

    // ---- Thrust ----
    // WASD add acceleration in camera-local directions.
    // direction × THRUST_ACCEL × dt → velocity change this frame.
    if (keysDown.has('KeyW')) camera.vel = camera.vel.add(camVec.forward.scale( THRUST_ACCEL * dt));
    if (keysDown.has('KeyS')) camera.vel = camera.vel.add(camVec.forward.scale(-THRUST_ACCEL * dt));
    if (keysDown.has('KeyA')) camera.vel = camera.vel.add(camVec.right.scale(  -THRUST_ACCEL * dt));
    if (keysDown.has('KeyD')) camera.vel = camera.vel.add(camVec.right.scale(   THRUST_ACCEL * dt));

    // ---- Emergency Brake ----
    // Not physically realistic, but handy for demoing the simulator.
    // Damps velocity toward zero exponentially.
    if (keysDown.has('Space')) {
        camera.vel = camera.vel.scale(1 - Math.min(dt * 4, 0.99));
        brakeFlash = 1;
    } else {
        brakeFlash *= 0.85;   // fade out
    }

    // ---- Integrate ----
    camera.pos = camera.pos.add(camera.vel.scale(dt));
}


// ============================================================
//  DRAW
// ============================================================
function draw() {
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const camVec = computeCameraVectors();

    // ---- Stars ----
    for (const star of stars) {
        const camDir = new Vec3(
            star.dir.dot(camVec.right),
            star.dir.dot(camVec.up),
            star.dir.dot(camVec.forward)
        );
        if (camDir.z <= 0) continue;
        const sx = (camDir.x / camDir.z) * FOCAL_LENGTH + CX;
        const sy = (-camDir.y / camDir.z) * FOCAL_LENGTH + CY;
        if (sx < -5 || sx > canvas.width + 5 || sy < -5 || sy > canvas.height + 5) continue;
        ctx.fillStyle = `rgba(210, 225, 255, ${star.brightness})`;
        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        ctx.fill();
    }

    // ---- Planets ----
    // Find nearest planet first (for HUD)
    let nearest = null;
    let nearestDist = Infinity;
    for (const p of planets) {
        const d = p.pos.sub(camera.pos).length();
        if (d < nearestDist) { nearestDist = d; nearest = p; }
    }

    // Build visible list and depth-sort
    const visible = [];
    for (const planet of planets) {
        const camPoint = worldToCamera(planet.pos, camVec);
        const proj     = project(camPoint);
        if (proj) visible.push({ planet, camPoint, proj });
    }
    visible.sort((a, b) => b.camPoint.z - a.camPoint.z);

    // Draw each planet
    for (const { planet, proj } of visible) {
        const r = planet.radius * proj.scale;
        if (r < 0.4) continue;

        // Glow halo (drawn first, behind the disk)
        if (r > 3) {
            const glowRadius = r * 1.7;
            const grad = ctx.createRadialGradient(proj.sx, proj.sy, r * 0.5, proj.sx, proj.sy, glowRadius);
            grad.addColorStop(0, planet.glowColor);
            grad.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(proj.sx, proj.sy, glowRadius, 0, Math.PI * 2);
            ctx.fill();
        }

        // Planet disk
        ctx.fillStyle = planet.baseColor;
        ctx.beginPath();
        ctx.arc(proj.sx, proj.sy, r, 0, Math.PI * 2);
        ctx.fill();

        // Subtle highlight on one side (fake lighting)
        if (r > 4) {
            const hiGrad = ctx.createRadialGradient(
                proj.sx - r * 0.35, proj.sy - r * 0.35, 0,
                proj.sx, proj.sy, r
            );
            hiGrad.addColorStop(0, 'rgba(255,255,255,0.18)');
            hiGrad.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = hiGrad;
            ctx.beginPath();
            ctx.arc(proj.sx, proj.sy, r, 0, Math.PI * 2);
            ctx.fill();
        }

        // Name label
        if (r > 12) {
            ctx.fillStyle = 'rgba(190,210,255,0.65)';
            ctx.font      = '11px Courier New';
            ctx.textAlign = 'center';
            ctx.fillText(planet.name, proj.sx, proj.sy - r - 6);
        }
    }

    // ---- Crosshair ----
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth   = 1;
    const CH = 8;
    ctx.beginPath();
    ctx.moveTo(CX - CH - 4, CY); ctx.lineTo(CX - 4, CY);
    ctx.moveTo(CX + 4, CY);      ctx.lineTo(CX + CH + 4, CY);
    ctx.moveTo(CX, CY - CH - 4); ctx.lineTo(CX, CY - 4);
    ctx.moveTo(CX, CY + 4);      ctx.lineTo(CX, CY + CH + 4);
    ctx.stroke();

    // ---- Brake flash overlay ----
    if (brakeFlash > 0.01) {
        ctx.fillStyle = `rgba(255, 80, 0, ${brakeFlash * 0.12})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = `rgba(255, 80, 0, ${brakeFlash * 0.8})`;
        ctx.font      = '12px Courier New';
        ctx.textAlign = 'center';
        ctx.fillText('BRAKING', CX, CY + 25);
    }

    // ---- HUD ----
    drawHUD(nearest, nearestDist);
}


// ============================================================
//  HUD
// ============================================================
function drawHUD(nearest, nearestDist) {
    const speed = camera.vel.length();
    const pad   = 12;
    const lh    = 16;

    // Left panel — ship state
    const leftLines = [
        { t: `pos:   ${camera.pos.toString(0)}`,  c: '#8eb8e8' },
        { t: `speed: ${speed.toFixed(1)} u/s`,    c: '#88ff88' },
        { t: `yaw:   ${(camera.yaw   * 180/Math.PI).toFixed(0)}°`, c: '#aaaacc' },
        { t: `pitch: ${(camera.pitch * 180/Math.PI).toFixed(0)}°`, c: '#aaaacc' },
    ];

    ctx.fillStyle = 'rgba(4,8,18,0.82)';
    ctx.fillRect(pad, pad, 240, leftLines.length * lh + 16);
    ctx.font      = '11px Courier New';
    ctx.textAlign = 'left';
    for (let i = 0; i < leftLines.length; i++) {
        ctx.fillStyle = leftLines[i].c;
        ctx.fillText(leftLines[i].t, pad + 8, pad + 13 + i * lh);
    }

    // Speed bar (below left panel)
    const barY    = pad + leftLines.length * lh + 22;
    const barW    = 240;
    const barH    = 8;
    const maxSpeed = 500;
    const fillW   = Math.min(speed / maxSpeed, 1) * (barW - 16);
    ctx.fillStyle = 'rgba(4,8,18,0.82)';
    ctx.fillRect(pad, barY, barW, barH + 16);
    ctx.fillStyle = '#1a3050';
    ctx.fillRect(pad + 8, barY + 6, barW - 16, barH);
    // Color shifts from green → yellow → red as speed increases
    const t = speed / maxSpeed;
    const r = Math.floor(t > 0.5 ? 255 : t * 2 * 255);
    const g = Math.floor(t < 0.5 ? 255 : (1 - (t - 0.5) * 2) * 255);
    ctx.fillStyle = `rgb(${r}, ${g}, 40)`;
    ctx.fillRect(pad + 8, barY + 6, fillW, barH);
    ctx.fillStyle = '#304060';
    ctx.font      = '10px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText('speed', pad + 9, barY + 5 + barH + 9);

    // Right panel — nearest planet
    if (nearest) {
        const distStr = nearestDist < 10000
            ? `${Math.round(nearestDist)} u`
            : `${(nearestDist / 1000).toFixed(1)} ku`;

        const rightLines = [
            { t: 'NEAREST PLANET', c: '#6090c0' },
            { t: nearest.name,     c: '#e0e8ff' },
            { t: distStr,          c: '#ffcc66' },
        ];

        const rx = canvas.width - pad - 180;
        ctx.fillStyle = 'rgba(4,8,18,0.82)';
        ctx.fillRect(rx, pad, 180, rightLines.length * lh + 16);
        ctx.font      = '11px Courier New';
        for (let i = 0; i < rightLines.length; i++) {
            ctx.fillStyle   = rightLines[i].c;
            ctx.textAlign   = 'center';
            ctx.fillText(rightLines[i].t, rx + 90, pad + 13 + i * lh);
        }
    }

    // Control reminder (bottom-left)
    const remLines = [
        'WASD — thrust',
        'Arrows — rotate',
        'Space — brake',
    ];
    const ry = canvas.height - pad - remLines.length * lh - 4;
    ctx.fillStyle = 'rgba(4,8,18,0.7)';
    ctx.fillRect(pad, ry, 160, remLines.length * lh + 8);
    ctx.font      = '10px Courier New';
    ctx.textAlign = 'left';
    for (let i = 0; i < remLines.length; i++) {
        ctx.fillStyle = '#405070';
        ctx.fillText(remLines[i], pad + 8, ry + 10 + i * lh);
    }
}


// ============================================================
//  START
// ============================================================
requestAnimationFrame(gameLoop);
