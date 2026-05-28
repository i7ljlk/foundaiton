document.addEventListener('DOMContentLoaded', () => {
    // Initialize VanillaTilt for 3D card effect
    if (typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(document.querySelectorAll("[data-tilt]"), {
            max: 10,
            speed: 400,
            glare: true,
            "max-glare": 0.2,
            scale: 1.02
        });
    }

    // Canvas Particles for background effect
    const canvas = document.getElementById('particles');
    const ctx = canvas.getContext('2d');
    
    let width, height, particles;
    
    function init() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        particles = [];
        
        const numParticles = Math.min(width / 15, 80); // Responsive particle count
        
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * 2 + 1,
                vx: Math.random() * 0.5 - 0.25,
                vy: Math.random() * 0.5 - 0.25,
                alpha: Math.random() * 0.5 + 0.1
            });
        }
    }
    
    function draw() {
        ctx.clearRect(0, 0, width, height);
        
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            
            // Bounce off edges
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(59, 130, 246, ${p.alpha})`;
            ctx.fill();
        });
        
        // Draw lines between nearby particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    const opacity = 1 - (dist / 120);
                    ctx.strokeStyle = `rgba(59, 130, 246, ${opacity * 0.2})`;
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(draw);
    }
    
    init();
    draw();
    
    window.addEventListener('resize', () => {
        init();
    });
});
