// ============================================================
//  LESSON 4: CAMERA ORIENTATION — PITCH AND YAW
//
//  Goals:
//    - Represent camera rotation with two Euler angles
//    - Derive the camera's local forward / right / up vectors
//    - Transform world-space points into camera space
//    - Arrow keys control the camera; planets and stars move as we look
//
//  NEW this lesson:
//    - computeCameraVectors()  — yaw/pitch → forward, right, up
//    - worldToCamera()         — world point → camera-local coordinates
//    - Stars now rotate correctly when you look around
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
}


// ---- CANVAS ----
const canvas = document.getElementById('canvas');
const ctx    = canvas.getContext('2d');
const CX     = canvas.width  / 2;
const CY     = canvas.height / 2;
const FOCAL_LENGTH = 500;
const NEAR_CLIP    = 1.0;


// ---- CAMERA STATE ----
// The camera sits at the world origin.  Its orientation is described by two angles.
const camera = {
    // YAW: rotation around the world Y axis (left and right).
    //   yaw = 0   → facing +Z direction
    //   yaw = π/2 → facing +X direction
    yaw: 0,

    // PITCH: tilt up or down.
    //   pitch = 0    → level (horizon)
    //   pitch = +π/2 → looking straight up
    //   pitch = -π/2 → looking straight down
    //   We clamp pitch to ±89° so the camera never flips upside down.
    pitch: 0,
};

const TURN_SPEED = 1.1;   // radians per second

// ---- KEYBOARD ----
const keysDown = new Set();
document.addEventListener('keydown', e => { keysDown.add(e.code); e.preventDefault(); });
document.addEventListener('keyup',   e => keysDown.delete(e.code));


// ============================================================
//  CAMERA BASIS VECTORS
//
//  From yaw and pitch we derive three mutually perpendicular unit vectors
//  that define the camera's local coordinate frame:
//
//    forward — where the camera is pointing
//    right   — 90° to the right of forward (stays horizontal, no pitch)
//    up      — perpendicular to both, points "toward the sky"
//
//  These are derived by rotating the default axes (0,0,1), (1,0,0), (0,1,0)
//  first by yaw around Y, then by pitch around the local X (right) axis.
//
//  Equivalently: this IS the rotation matrix, just expressed as three column
//  vectors instead of a 3×3 matrix. Real engines store this as a matrix.
// ============================================================
function computeCameraVectors() {

    const cosP = Math.cos(camera.pitch);
    const sinP = Math.sin(camera.pitch);
    const cosY = Math.cos(camera.yaw);
    const sinY = Math.sin(camera.yaw);

    // FORWARD — the direction the camera points.
    //   Start with (0,0,1) (looking down +Z).
    //   Yaw rotates it in the XZ plane; pitch tilts it up/down.
    const forward = new Vec3(
        cosP * sinY,    // x component
        sinP,           // y component — pitch lifts the nose up
        cosP * cosY     // z component
    );

    // RIGHT — 90° to the right of forward, in the horizontal plane.
    //   We intentionally ignore pitch here (ry = 0) so strafing stays horizontal.
    //   This is the same as rotating (1,0,0) by yaw only.
    const right = new Vec3(
         cosY,   // x
         0,      // y — always horizontal
        -sinY    // z
    );

    // UP — perpendicular to both forward and right, pointing "sky-ward".
    //   Mathematically: up = right × forward  (or: computed directly from angles).
    //   We use the direct formula to avoid accumulated floating-point error.
    const up = new Vec3(
        -sinP * sinY,   // x
         cosP,          // y — when pitch=0, up is purely (0,1,0) = world up ✓
        -sinP * cosY    // z
    );

    return { forward, right, up };
}


// ============================================================
//  WORLD → CAMERA TRANSFORM
//
//  Given a point P in world space and the camera's current basis,
//  return P expressed in camera-local coordinates.
//
//  Steps:
//    1. Subtract camera position to get a vector from camera to P.
//       (Camera is at origin here, so this is just P itself for now.)
//    2. Dot-product with each camera axis to project onto that axis.
//       This is equivalent to multiplying by the inverse view matrix.
//
//  After this transform:
//    camPoint.x = how far right the point is from camera center
//    camPoint.y = how far up the point is from camera center
//    camPoint.z = how far forward the point is (depth)
// ============================================================
function worldToCamera(worldPoint, camVec) {
    // In Lesson 4 the camera position is always the origin (0,0,0),
    // so rel = worldPoint.  In Lesson 5 we subtract camera.pos.
    const rel = worldPoint;

    return new Vec3(
        rel.dot(camVec.right),    // camera-local x
        rel.dot(camVec.up),       // camera-local y
        rel.dot(camVec.forward)   // camera-local z (depth)
    );
}

// Project a camera-space point to screen coordinates.
// Returns null if the point is behind the camera.
function project(camPoint) {
    if (camPoint.z <= NEAR_CLIP) return null;
    return {
        sx:    (camPoint.x / camPoint.z) * FOCAL_LENGTH + CX,
        sy:   (-camPoint.y / camPoint.z) * FOCAL_LENGTH + CY,
        scale: FOCAL_LENGTH / camPoint.z,
    };
}


// ---- STARS ----
// Stored as unit-direction vectors in world space.
// When we look around, we transform each star direction by the camera rotation,
// then project — so they appear to surround us in all directions correctly.
const NUM_STARS = 250;
const stars = [];
for (let i = 0; i < NUM_STARS; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    stars.push({
        dir: new Vec3(
            Math.sin(phi) * Math.cos(theta),
            Math.sin(phi) * Math.sin(theta),
            Math.cos(phi)
        ),
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
            (Math.random() - 0.5) * 1000,
            (Math.random() - 0.5) * 800,
            Math.random() * 2000 + 80
        ),
        radius: Math.random() * 45 + 8,
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
    // Arrow keys rotate the camera
    if (keysDown.has('ArrowLeft'))  camera.yaw   -= TURN_SPEED * dt;
    if (keysDown.has('ArrowRight')) camera.yaw   += TURN_SPEED * dt;
    if (keysDown.has('ArrowUp'))    camera.pitch += TURN_SPEED * dt;
    if (keysDown.has('ArrowDown'))  camera.pitch -= TURN_SPEED * dt;

    // Clamp pitch to ±89° — prevents the camera from flipping upside down.
    const MAX_PITCH = Math.PI / 2 - 0.01;
    camera.pitch = Math.max(-MAX_PITCH, Math.min(MAX_PITCH, camera.pitch));
}

function draw() {
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Recompute camera basis once per frame
    const camVec = computeCameraVectors();

    // --- Stars ---
    // Transform each star's world-space direction into camera space, then project.
    // Stars are at "infinite distance" so we skip the position offset.
    for (const star of stars) {
        // camDir = camera-local direction to this star
        const camDir = new Vec3(
            star.dir.dot(camVec.right),
            star.dir.dot(camVec.up),
            star.dir.dot(camVec.forward)
        );
        if (camDir.z <= 0) continue;   // behind camera

        const sx = (camDir.x / camDir.z) * FOCAL_LENGTH + CX;
        const sy = (-camDir.y / camDir.z) * FOCAL_LENGTH + CY;
        // Clip to canvas bounds before drawing
        if (sx < 0 || sx > canvas.width || sy < 0 || sy > canvas.height) continue;

        ctx.fillStyle = `rgba(210, 225, 255, ${star.brightness})`;
        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        ctx.fill();
    }

    // --- Planets ---
    // Transform each planet from world space to camera space, then project.
    const visible = [];
    for (const planet of planets) {
        const camPoint = worldToCamera(planet.pos, camVec);
        const proj     = project(camPoint);
        if (proj) visible.push({ planet, camPoint, proj });
    }

    // Painter's algorithm: draw farthest first (largest camPoint.z)
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

        if (r > 10) {
            ctx.fillStyle = 'rgba(190,210,255,0.6)';
            ctx.font      = '11px Courier New';
            ctx.textAlign = 'center';
            ctx.fillText(planet.name, proj.sx, proj.sy - r - 5);
        }
    }

    // --- Crosshair ---
    const len = 10;
    ctx.strokeStyle = 'rgba(255,255,255,0.35)';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(CX - len, CY); ctx.lineTo(CX + len, CY);
    ctx.moveTo(CX, CY - len); ctx.lineTo(CX, CY + len);
    ctx.stroke();

    // --- HUD ---
    drawHUD(camVec);
}

function drawHUD(camVec) {
    const pad   = 12;
    const lineH = 16;
    const lines = [
        { t: `yaw:   ${(camera.yaw   * 180 / Math.PI).toFixed(1)}°`, c: '#8eb8e8' },
        { t: `pitch: ${(camera.pitch * 180 / Math.PI).toFixed(1)}°`, c: '#ffcc44' },
        { t: `forward: ${vecStr(camVec.forward)}`, c: '#88ff88' },
        { t: `right:   ${vecStr(camVec.right)}`,   c: '#ff8888' },
        { t: `up:      ${vecStr(camVec.up)}`,       c: '#cc88ff' },
        { t: 'Arrow keys to look around', c: '#404860' },
    ];
    ctx.fillStyle = 'rgba(4,8,18,0.78)';
    ctx.fillRect(pad, pad, 270, lines.length * lineH + 14);
    ctx.font      = '11px Courier New';
    ctx.textAlign = 'left';
    for (let i = 0; i < lines.length; i++) {
        ctx.fillStyle = lines[i].c;
        ctx.fillText(lines[i].t, pad + 8, pad + 13 + i * lineH);
    }
}

function vecStr(v) {
    return `(${v.x.toFixed(2)}, ${v.y.toFixed(2)}, ${v.z.toFixed(2)})`;
}


// ---- START ----
requestAnimationFrame(gameLoop);
