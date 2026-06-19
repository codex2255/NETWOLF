const canvas = document.getElementById('particleCanvas');

if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('resize', function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    var particles = [];
    var total = 80;
    var maxDist = 150;

    function makeParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.8,
            vy: (Math.random() - 0.5) * 0.8,
            radius: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.3
        };
    }

    for (var i = 0; i < total; i++) {
        particles.push(makeParticle());
    }

    function updateParticle(p) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    }

    function drawParticle(p) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 0, 0,' + p.opacity + ')';
        ctx.fill();
    }

    function drawLines() {
        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var dx = particles[i].x - particles[j].x;
                var dy = particles[i].y - particles[j].y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < maxDist) {
                    var opacity = (1 - dist / maxDist) * 0.4;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = 'rgba(255, 0, 0,' + opacity + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (var i = 0; i < particles.length; i++) {
            updateParticle(particles[i]);
            drawParticle(particles[i]);
        }
        drawLines();
        requestAnimationFrame(animate);
    }

    animate();
}

var intro = document.getElementById('introScreen');

if (intro) {
    setTimeout(function() {
        intro.classList.add('fade-out');
        setTimeout(function() {
            window.location.href = 'pages/dashboard.html';
        }, 1000);
    }, 5000);
}