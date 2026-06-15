/* ================================================
   NETWOLF — Shared JavaScript
   Particle network background + intro animation
   Project: CS205 - Integrated Studio III
   Team: Josh (Backend) & Vishesh (Frontend)
   ================================================ */


// ================================================
// SECTION 1: PARTICLE NETWORK BACKGROUND
// Only runs if particleCanvas exists on the page
// ================================================

const canvas = document.getElementById('particleCanvas');

if (canvas) {

    const ctx = canvas.getContext('2d');

    // Set canvas to full window size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Resize canvas when window is resized
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    // --- Configuration ---
    const PARTICLE_COUNT = 80;
    const MAX_DISTANCE   = 150;

    const particles = [];

    // --- Particle Class ---
    class Particle {
        constructor() {
            this.x       = Math.random() * canvas.width;
            this.y       = Math.random() * canvas.height;
            this.vx      = (Math.random() - 0.5) * 0.8;
            this.vy      = (Math.random() - 0.5) * 0.8;
            this.radius  = Math.random() * 2.5 + 1;
            this.opacity = Math.random() * 0.5 + 0.3;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > canvas.width)  this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height)  this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 0, 0, ${this.opacity})`;
            ctx.fill();
        }
    }

    // Initialise particles
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }

    // Draw connecting lines between nearby particles
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx   = particles[i].x - particles[j].x;
                const dy   = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < MAX_DISTANCE) {
                    const opacity = (1 - dist / MAX_DISTANCE) * 0.4;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(255, 0, 0, ${opacity})`;
                    ctx.lineWidth   = 0.8;
                    ctx.stroke();
                }
            }
        }
    }

    // Animation loop — runs at ~60fps
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        requestAnimationFrame(animate);
    }

    animate();
}


// ================================================
// SECTION 2: INTRO SCREEN DISMISS
// Fades out intro and redirects to dashboard
// Only runs if introScreen exists (index.html only)
// ================================================

const introScreen = document.getElementById('introScreen');

if (introScreen) {
    setTimeout(() => {
        introScreen.classList.add('fade-out');

        // Redirect to dashboard after fade completes
        setTimeout(() => {
            window.location.href = 'pages/dashboard.html';
        }, 1000);
    }, 5000);
}