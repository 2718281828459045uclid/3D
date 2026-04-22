// ============================================================
//  LESSON 3: 3D PERSPECTIVE PROJECTION
//
//  Goals:
//    - Place planets at 3D positions (x, y, z)
//    - Project them onto a 2D canvas using perspective math
//    - Depth-sort with the painter's algorithm
//    - Understand focalLength (field of view) and apparent radius
//
//  Camera is fixed at origin (0, 0, 0), looking in the +Z direction.
//  We'll add rotation in Lesson 4.
// ============================================================


// ---- Vec3 (same class as Lesson 2 — full docs there) ----
class Vec3 {
    constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
    add(v)    { return new Vec3(this.x + v.x, this.y + v.y, this.z + v.z); }
    sub(v)    { return new Vec3(this.x - v.x, this.y - v.y, this.z - v.z); }
    scale(s)  { return new Vec3(this.x * s,   this.y * s,   this.z * s  ); }
    dot(v)    { return this.x * v.x + this.y * v.y + this.z * v.z; }
    length()  { return Math.sqrt(this.x*this.x + this.y*this.y + this.z*this.z); }
    normalize() {
        const l = this.length();
        return l === 0 ? new Vec3() : this.scale(1 / l);
    }
}


// ---- CANVAS SETUP ----
const canvas = document.getElementById('canvas');
const ctx    = canvas.getContext('2d');

// Canvas center — the "principal point" of our camera.
// The projection puts the center of the view here.
const CX = canvas.width  / 2;
const CY = canvas.height / 2;

// FOCAL LENGTH — controls the field of view.
//
//   fov (angle) and focalLength are related by:
//     focalLength = CX / tan(halfFOV)
//
//   A typical 60° horizontal FOV means halfFOV = 30°:
//     focalLength = 350 / tan(30°) ≈ 606
//
//   Larger focalLength → narrower FOV (telephoto: things look bigger, less peripheral vision)
//   Smaller focalLength → wider FOV  (wide-angle: more visible, more distortion at edges)
//
//   We pick 500 here — a moderate FOV, easy to adjust and experiment with.
const FOCAL_LENGTH = 500;


// ---- STARS ----
// Stars are treated as points at "infinite" distance in random directions.
// We store them as unit-direction Vec3s.  To draw: project the direction directly
// (no position offset since they're infinitely far — depth = direction.z effectively).
// For this lesson the camera is fixed, so stars just sit at fixed screen positions.
const NUM_STARS = 220;
const stars = [];
for (let i = 0; i < NUM_STARS; i++) {
    // Random point on a sphere surface: use spherical coordinates
    const theta = Math.random() * Math.PI * 2;          // azimuth 0…2π
    const phi   = Math.acos(2 * Math.random() - 1);     // polar  0…π  (uniform distribution)
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
// Each planet lives in 3D world space.  The camera is at (0,0,0),
// so planets must have z > 0 to appear in front of the camera.
const PLANET_COLORS = ['#3a6fcc','#cc5533','#774422','#447755','#998833','#9944aa','#336688','#aa6633'];
const PLANET_NAMES  = ['Hydra','Ignis','Magna','Virid','Lutea','Ceres','Nebula','Ferro',
                       'Glacis','Pyrex','Umbra','Solus','Terra','Argon','Noctis'];

function makePlanet(i) {
    return {
        pos:    new Vec3(
            (Math.random() - 0.5) * 900,   // x: -450 to 450
            (Math.random() - 0.5) * 700,   // y: -350 to 350  (world y = up)
            Math.random() * 2000 + 80      // z: 80 to 2080  (always in front of camera)
        ),
        radius: Math.random() * 45 + 8,    // world-space radius: 8 to 53
        color:  PLANET_COLORS[i % PLANET_COLORS.length],
        name:   PLANET_NAMES[i % PLANET_NAMES.length],
    };
}

const planets = [];
for (let i = 0; i < 15; i++) planets.push(makePlanet(i));


// ============================================================
//  PERSPECTIVE PROJECTION
//
//  This function converts a 3D world point to a 2D screen position.
//
//  The math:
//    screenX = (worldX / worldZ) * FOCAL_LENGTH + CX
//    screenY = (−worldY / worldZ) * FOCAL_LENGTH + CY
//
//  Why dividing by Z gives perspective:
//    Imagine the canvas is a window 1 unit in front of you.
//    A point at world position (wx, wy, wz) projects through
//    that window at (wx/wz, wy/wz).  The farther away (larger wz),
//    the closer to center that projection lands — things shrink.
//
//  Why −worldY:
//    World Y increases upward.  Screen Y increases downward.
//    Negating flips the axis so "up in the world" = "up on screen".
//
//  Returns null if the point is behind the camera (z ≤ nearClip).
// ============================================================
const NEAR_CLIP = 1.0;   // don't draw anything closer than 1 unit

function project(worldPos) {
    const z = worldPos.z;
    if (z <= NEAR_CLIP) return null;   // behind camera — skip

    return {
        sx:    (worldPos.x / z) * FOCAL_LENGTH + CX,   // screen x
        sy:   (-worldPos.y / z) * FOCAL_LENGTH + CY,   // screen y (y flipped)
        scale: FOCAL_LENGTH / z,                         // how large things appear at this depth
    };
}


// ============================================================
//  GAME LOOP
// ============================================================

let lastTime = -1;

function gameLoop(timestamp) {
    const dt = (lastTime < 0) ? 0 : (timestamp - lastTime) / 1000;
    lastTime = timestamp;
    // No update() this lesson — camera and planets are all static.
    draw();
    requestAnimationFrame(gameLoop);
}


function draw() {
    ctx.fillStyle = '#050810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // --- Stars ---
    // Camera is fixed, so just project each star's direction as-is.
    // Stars with dir.z ≤ 0 are "behind" us — skip them.
    for (const star of stars) {
        if (star.dir.z <= 0) continue;
        const proj = project(star.dir);  // direction treated as position at unit depth
        if (!proj) continue;
        const sx = (star.dir.x / star.dir.z) * FOCAL_LENGTH + CX;
        const sy = (-star.dir.y / star.dir.z) * FOCAL_LENGTH + CY;
        ctx.fillStyle = `rgba(210, 225, 255, ${star.brightness})`;
        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        ctx.fill();
    }

    // --- Planets ---
    // PAINTER'S ALGORITHM: sort by depth (z) descending, draw farthest first.
    // Each new planet paints over whatever is behind it.
    // This works perfectly for convex objects like spheres.
    const sorted = [...planets].sort((a, b) => b.pos.z - a.pos.z);

    for (const planet of sorted) {
        const proj = project(planet.pos);
        if (!proj) continue;    // behind camera

        // Apparent radius on screen.
        // A planet of world-radius R at depth z looks like a circle of radius R/z * FOCAL_LENGTH.
        // Same division-by-depth logic as the position projection.
        const apparentRadius = planet.radius * proj.scale;
        if (apparentRadius < 0.5) continue;   // too small to see — skip

        // Draw planet disk
        ctx.fillStyle = planet.color;
        ctx.beginPath();
        ctx.arc(proj.sx, proj.sy, apparentRadius, 0, Math.PI * 2);
        ctx.fill();

        // Faint edge highlight
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth   = 1;
        ctx.stroke();

        // Name label — only if the planet is large enough to read
        if (apparentRadius > 10) {
            ctx.fillStyle   = 'rgba(190,210,255,0.6)';
            ctx.font        = '11px Courier New';
            ctx.textAlign   = 'center';
            ctx.fillText(planet.name, proj.sx, proj.sy - apparentRadius - 5);
        }

        // Depth label (shows the z distance — good teaching aid)
        if (apparentRadius > 5) {
            ctx.fillStyle   = 'rgba(130,160,190,0.4)';
            ctx.font        = '10px Courier New';
            ctx.textAlign   = 'center';
            ctx.fillText(`z=${Math.round(planet.pos.z)}`, proj.sx, proj.sy + apparentRadius + 12);
        }
    }

    // --- Crosshair (center of camera view) ---
    const len = 10;
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(CX - len, CY); ctx.lineTo(CX + len, CY);
    ctx.moveTo(CX, CY - len); ctx.lineTo(CX, CY + len);
    ctx.stroke();

    // --- Corner label ---
    ctx.fillStyle = 'rgba(180,200,255,0.4)';
    ctx.font      = '11px Courier New';
    ctx.textAlign = 'left';
    ctx.fillText(`camera at (0, 0, 0) · focalLength=${FOCAL_LENGTH}`, 10, 18);
}


// ---- START ----
requestAnimationFrame(gameLoop);
