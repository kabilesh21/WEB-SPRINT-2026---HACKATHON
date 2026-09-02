/**
 * ============================================================================
 * KAYAK STUDIO / EDUPORTAL - CHARACTER RIGGING & SPRING PHYSICS ENGINE
 * ============================================================================
 */

class MonsterAnimationEngine {
  constructor() {
    this.stage = document.getElementById('monster-stage');
    this.isPasswordMode = false;
    this.isPasswordVisible = false;
    this.isCelebrating = false;
    this.currentFocusTarget = null;

    // Time tracking
    this.startTime = performance.now();
    this.lastFrameTime = performance.now();

    // Secondary impulse velocities for each character
    this.impulses = {
      pink: { y: 0, scaleY: 1, vy: 0, targetY: 0 },
      red: { y: 0, rot: 0, vy: 0, vrot: 0, targetY: 0, targetRot: 0 },
      teal: { y: 0, x: 0, vy: 0, vx: 0, targetY: 0, targetX: 0 },
      blue: { y: 0, scale: 1, vy: 0, vscale: 0, targetY: 0 }
    };

    // SVG Eye Centers in stage coordinates (viewBox 0 0 500 550)
    this.eyes = {
      pink: {
        x: 335,
        y: 225,
        maxRadius: 15,
        pupilEl: document.getElementById('pink-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      redLeft: {
        x: 128,
        y: 98,
        maxRadius: 9,
        pupilEl: document.getElementById('red-left-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      redRight: {
        x: 172,
        y: 98,
        maxRadius: 9,
        pupilEl: document.getElementById('red-right-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      tealLeft: {
        x: 126,
        y: 290,
        maxRadius: 10,
        pupilEl: document.getElementById('teal-left-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      tealRight: {
        x: 170,
        y: 290,
        maxRadius: 10,
        pupilEl: document.getElementById('teal-right-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      blueLeft: {
        x: 254,
        y: 328,
        maxRadius: 8.5,
        pupilEl: document.getElementById('blue-left-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      },
      blueRight: {
        x: 298,
        y: 328,
        maxRadius: 8.5,
        pupilEl: document.getElementById('blue-right-pupil'),
        currentX: 0,
        currentY: 0,
        targetX: 0,
        targetY: 0
      }
    };

    // Body & Head Elements for Rigging
    this.elements = {
      pinkMonster: document.getElementById('pink-monster'),
      pinkBody: document.getElementById('pink-body-root'),
      pinkHand: document.getElementById('pink-hand'),
      pinkEyeGroup: document.getElementById('pink-eye-group'),
      pinkPupil: document.getElementById('pink-pupil'),
      pinkClosedEye: document.getElementById('pink-closed-eye'),

      redMonster: document.getElementById('red-monster'),
      redHeadRoot: document.getElementById('red-head-root'),
      redLeftPupil: document.getElementById('red-left-pupil'),
      redRightPupil: document.getElementById('red-right-pupil'),
      redLeftBlink: document.getElementById('red-left-blink'),
      redRightBlink: document.getElementById('red-right-blink'),
      redMouthTeeth: document.getElementById('red-mouth-teeth'),
      redMouthClosed: document.getElementById('red-mouth-closed-cavity'),

      tealMonster: document.getElementById('teal-monster'),
      tealBodyRoot: document.getElementById('teal-body-root'),
      tealLeftPupil: document.getElementById('teal-left-pupil'),
      tealRightPupil: document.getElementById('teal-right-pupil'),
      tealLeftWink: document.getElementById('teal-left-wink'),
      tealRightWink: document.getElementById('teal-right-wink'),
      tealBlushLeft: document.getElementById('teal-blush-left'),
      tealBlushRight: document.getElementById('teal-blush-right'),
      tealMouthOpen: document.getElementById('teal-mouth-open'),

      blueMonster: document.getElementById('blue-monster'),
      blueBodyRoot: document.getElementById('blue-body-root'),
      blueHands: document.getElementById('blue-hands'),
      blueLeftClosed: document.getElementById('blue-left-closed'),
      blueRightClosed: document.getElementById('blue-right-closed'),
      blueLeftPupil: document.getElementById('blue-left-pupil'),
      blueRightPupil: document.getElementById('blue-right-pupil'),
      blueMouthOpen: document.getElementById('blue-mouth-open')
    };

    // Mouse coordinates
    this.mouseSvgX = 450;
    this.mouseSvgY = 340;

    this.init();
  }

  init() {
    this.bindEvents();
    this.startBlinkLoop();
    this.startRedTeethCycle();
    this.startRenderLoop();
    this.setupConfetti();
  }

  /**
   * Replays the choreographed entrance sequence:
   * 1. Sky Blue (Teal) drops from UP (t=0.05s)
   * 2. Pink & Blue rise from DOWN (t=0.35s - 0.45s)
   * 3. Red rises from DOWN LAST (t=0.95s)
   */
  replayToyDrop() {
    const sequence = [
      { id: 'teal-monster', cls: 'entrance-teal' },
      { id: 'pink-monster', cls: 'entrance-pink' },
      { id: 'blue-monster', cls: 'entrance-blue' },
      { id: 'red-monster', cls: 'entrance-red' }
    ];

    sequence.forEach(item => {
      const el = document.getElementById(item.id);
      if (el) {
        el.classList.remove(item.cls);
        void el.offsetWidth; // Trigger DOM reflow
        el.classList.add(item.cls);
      }
    });
  }

  /**
   * 3-Second Cycle for Red Monster Teeth / Mouth:
   * Mouth stays closed, opens teeth every 3 seconds, then closes after 1.2s
   */
  startRedTeethCycle() {
    const toggleTeeth = () => {
      if (this.elements.redMouthTeeth && this.elements.redMouthClosed) {
        // Open teeth
        this.elements.redMouthTeeth.style.opacity = '1';
        this.elements.redMouthClosed.style.opacity = '0';

        // After 1.2s, close teeth & show closed mouth
        setTimeout(() => {
          if (this.elements.redMouthTeeth && this.elements.redMouthClosed) {
            this.elements.redMouthTeeth.style.opacity = '0';
            this.elements.redMouthClosed.style.opacity = '1';
          }
        }, 1200);
      }
    };

    // Initial state: closed mouth
    if (this.elements.redMouthTeeth && this.elements.redMouthClosed) {
      this.elements.redMouthTeeth.style.opacity = '0';
      this.elements.redMouthClosed.style.opacity = '1';
    }

    // Trigger first opening at 3s, then every 3s
    setInterval(toggleTeeth, 3000);
  }

  bindEvents() {
    // Global mouse tracking
    window.addEventListener('mousemove', (e) => {
      if (!this.stage) return;
      const rect = this.stage.getBoundingClientRect();
      const scaleX = 500 / rect.width;
      const scaleY = 550 / rect.height;
      this.mouseSvgX = (e.clientX - rect.left) * scaleX;
      this.mouseSvgY = (e.clientY - rect.top) * scaleY;
    });

    // Touch support for mobile devices
    window.addEventListener('touchmove', (e) => {
      if (!this.stage || e.touches.length === 0) return;
      const touch = e.touches[0];
      const rect = this.stage.getBoundingClientRect();
      const scaleX = 500 / rect.width;
      const scaleY = 550 / rect.height;
      this.mouseSvgX = (touch.clientX - rect.left) * scaleX;
      this.mouseSvgY = (touch.clientY - rect.top) * scaleY;
    }, { passive: true });
  }

  /**
   * Trigger physical impulse bounce on character bodies
   */
  triggerKeystrokeImpulse() {
    this.impulses.blue.vy -= 4.2;
    this.impulses.teal.vy -= 3.0;
    this.impulses.teal.vx += (Math.random() - 0.5) * 2.2;
    this.impulses.red.vy -= 2.0;
    this.impulses.pink.vy -= 1.2;
  }

  /**
   * Set focus on text input to have monsters look at the user's input
   */
  setInputFocus(isFocused, inputElement = null) {
    this.currentFocusTarget = isFocused ? inputElement : null;
    this.isPasswordMode = false;
    this.updatePrivacyMode();

    if (isFocused) {
      this.impulses.blue.vy += 2.5;
      setTimeout(() => {
        this.impulses.blue.vy -= 4.5;
      }, 80);
      this.impulses.teal.vy -= 3.0;
    }
  }

  /**
   * Activate / Deactivate Password Privacy Blindfold Mode
   */
  setPasswordMode(isPassword, isVisible = false) {
    this.isPasswordMode = isPassword;
    this.isPasswordVisible = isVisible;
    this.updatePrivacyMode();
  }

  updatePrivacyMode() {
    if (this.isPasswordMode) {
      if (this.isPasswordVisible) {
        this.applyPeekAnimation();
      } else {
        this.applyShyAnimation();
      }
    } else {
      this.resetToNormalState();
    }
  }

  /**
   * SHY / BLINDFOLD MODE: ALL 4 TOYS CLOSE THEIR EYES
   */
  applyShyAnimation() {
    // 1. Blue Monster: Hands cover eyes & eyes close
    if (this.elements.blueHands) {
      this.elements.blueHands.style.transition = 'opacity 0.25s ease, transform 0.3s ease';
      this.elements.blueHands.style.opacity = '1';
      this.elements.blueHands.style.transform = 'translateY(0px)';
    }
    if (this.elements.blueLeftClosed && this.elements.blueRightClosed) {
      this.elements.blueLeftClosed.style.opacity = '1';
      this.elements.blueRightClosed.style.opacity = '1';
    }
    if (this.elements.blueLeftPupil && this.elements.blueRightPupil) {
      this.elements.blueLeftPupil.style.opacity = '0';
      this.elements.blueRightPupil.style.opacity = '0';
    }

    // 2. Teal Monster: Winks/Closes both eyes + blush
    if (this.elements.tealLeftWink && this.elements.tealRightWink) {
      this.elements.tealLeftWink.style.opacity = '1';
      this.elements.tealRightWink.style.opacity = '1';
    }
    if (this.elements.tealLeftPupil && this.elements.tealRightPupil) {
      this.elements.tealLeftPupil.style.opacity = '0';
      this.elements.tealRightPupil.style.opacity = '0';
    }
    if (this.elements.tealBlushLeft && this.elements.tealBlushRight) {
      this.elements.tealBlushLeft.style.opacity = '0.9';
      this.elements.tealBlushRight.style.opacity = '0.9';
    }

    // 3. Red Monster: Closes both eyes & tilts up innocently
    if (this.elements.redLeftBlink && this.elements.redRightBlink) {
      this.elements.redLeftBlink.style.opacity = '1';
      this.elements.redRightBlink.style.opacity = '1';
    }
    if (this.elements.redLeftPupil && this.elements.redRightPupil) {
      this.elements.redLeftPupil.style.opacity = '0';
      this.elements.redRightPupil.style.opacity = '0';
    }
    this.impulses.red.targetRot = -22;
    this.impulses.red.targetY = -8;

    // 4. Pink Monster: Hand covers cyclops eye & eye closes
    if (this.elements.pinkHand) {
      this.elements.pinkHand.style.transition = 'opacity 0.3s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
      this.elements.pinkHand.style.opacity = '1';
      this.elements.pinkHand.style.transform = 'translate(315px, 280px) scale(1.05)';
    }
    if (this.elements.pinkClosedEye) {
      this.elements.pinkClosedEye.style.opacity = '1';
    }
    if (this.elements.pinkPupil) {
      this.elements.pinkPupil.style.opacity = '0';
    }
  }

  /**
   * PEEK ANIMATION (When password eye toggle is visible)
   */
  applyPeekAnimation() {
    // Blue Monster peeks
    if (this.elements.blueHands) {
      this.elements.blueHands.style.opacity = '0.5';
      this.elements.blueHands.style.transform = 'translateY(12px)';
    }
    if (this.elements.blueLeftClosed && this.elements.blueRightClosed) {
      this.elements.blueLeftClosed.style.opacity = '0';
      this.elements.blueRightClosed.style.opacity = '0';
    }
    if (this.elements.blueLeftPupil && this.elements.blueRightPupil) {
      this.elements.blueLeftPupil.style.opacity = '1';
      this.elements.blueRightPupil.style.opacity = '1';
    }

    // Teal Monster peeks
    if (this.elements.tealLeftWink && this.elements.tealRightWink) {
      this.elements.tealLeftWink.style.opacity = '0';
      this.elements.tealRightWink.style.opacity = '1';
    }
    if (this.elements.tealLeftPupil && this.elements.tealRightPupil) {
      this.elements.tealLeftPupil.style.opacity = '1';
      this.elements.tealRightPupil.style.opacity = '0';
    }

    // Red Monster peeks
    if (this.elements.redLeftBlink && this.elements.redRightBlink) {
      this.elements.redLeftBlink.style.opacity = '0';
      this.elements.redRightBlink.style.opacity = '0';
    }
    if (this.elements.redLeftPupil && this.elements.redRightPupil) {
      this.elements.redLeftPupil.style.opacity = '1';
      this.elements.redRightPupil.style.opacity = '1';
    }
    this.impulses.red.targetRot = -6;
    this.impulses.red.targetY = -3;

    // Pink Monster peeks
    if (this.elements.pinkHand) {
      this.elements.pinkHand.style.opacity = '0.6';
      this.elements.pinkHand.style.transform = 'translate(315px, 320px) scale(0.95)';
    }
    if (this.elements.pinkClosedEye) {
      this.elements.pinkClosedEye.style.opacity = '0';
    }
    if (this.elements.pinkPupil) {
      this.elements.pinkPupil.style.opacity = '1';
    }
  }

  /**
   * RESET TO NORMAL STATE: All eyes open, hands away
   */
  resetToNormalState() {
    // Blue Monster
    if (this.elements.blueHands) {
      this.elements.blueHands.style.opacity = '0';
      this.elements.blueHands.style.transform = 'translateY(25px)';
    }
    if (this.elements.blueLeftClosed && this.elements.blueRightClosed) {
      this.elements.blueLeftClosed.style.opacity = '0';
      this.elements.blueRightClosed.style.opacity = '0';
    }
    if (this.elements.blueLeftPupil && this.elements.blueRightPupil) {
      this.elements.blueLeftPupil.style.opacity = '1';
      this.elements.blueRightPupil.style.opacity = '1';
    }

    // Teal Monster
    if (this.elements.tealLeftWink && this.elements.tealRightWink) {
      this.elements.tealLeftWink.style.opacity = '0';
      this.elements.tealRightWink.style.opacity = '0';
    }
    if (this.elements.tealLeftPupil && this.elements.tealRightPupil) {
      this.elements.tealLeftPupil.style.opacity = '1';
      this.elements.tealRightPupil.style.opacity = '1';
    }
    if (this.elements.tealBlushLeft && this.elements.tealBlushRight) {
      this.elements.tealBlushLeft.style.opacity = '0';
      this.elements.tealBlushRight.style.opacity = '0';
    }

    // Red Monster
    if (this.elements.redLeftBlink && this.elements.redRightBlink) {
      this.elements.redLeftBlink.style.opacity = '0';
      this.elements.redRightBlink.style.opacity = '0';
    }
    if (this.elements.redLeftPupil && this.elements.redRightPupil) {
      this.elements.redLeftPupil.style.opacity = '1';
      this.elements.redRightPupil.style.opacity = '1';
    }
    this.impulses.red.targetRot = 0;
    this.impulses.red.targetY = 0;

    // Pink Monster
    if (this.elements.pinkHand) {
      this.elements.pinkHand.style.opacity = '0';
      this.elements.pinkHand.style.transform = 'translate(320px, 360px)';
    }
    if (this.elements.pinkClosedEye) {
      this.elements.pinkClosedEye.style.opacity = '0';
    }
    if (this.elements.pinkPupil) {
      this.elements.pinkPupil.style.opacity = '1';
    }
  }

  /**
   * Random Blinking Loop when in normal mode
   */
  startBlinkLoop() {
    const doBlink = () => {
      if (!this.isPasswordMode) {
        if (this.elements.redLeftBlink && this.elements.redRightBlink) {
          this.elements.redLeftBlink.style.opacity = '1';
          this.elements.redRightBlink.style.opacity = '1';
          setTimeout(() => {
            if (!this.isPasswordMode && this.elements.redLeftBlink && this.elements.redRightBlink) {
              this.elements.redLeftBlink.style.opacity = '0';
              this.elements.redRightBlink.style.opacity = '0';
            }
          }, 140);
        }

        setTimeout(() => {
          if (!this.isPasswordMode && this.elements.blueLeftClosed && this.elements.blueRightClosed) {
            this.elements.blueLeftClosed.style.opacity = '1';
            this.elements.blueRightClosed.style.opacity = '1';
            setTimeout(() => {
              if (!this.isPasswordMode && this.elements.blueLeftClosed && this.elements.blueRightClosed) {
                this.elements.blueLeftClosed.style.opacity = '0';
                this.elements.blueRightClosed.style.opacity = '0';
              }
            }, 140);
          }
        }, 80);
      }

      const nextBlinkTime = 2500 + Math.random() * 3500;
      setTimeout(doBlink, nextBlinkTime);
    };

    setTimeout(doBlink, 2000);
  }

  /**
   * Main 60 FPS Render Loop: Spring Physics & Gaze Tracking
   */
  startRenderLoop() {
    const render = () => {
      const now = performance.now();
      const dt = Math.min((now - this.lastFrameTime) / 1000, 0.1);
      this.lastFrameTime = now;
      const t = (now - this.startTime) / 1000;

      // 1. Subtle idle organic breathing
      const pinkIdleY = Math.sin(t * 1.5) * 1.8;
      const redIdleY = Math.sin(t * 1.8 + 1) * 2.2;
      const redIdleRot = Math.cos(t * 1.4) * 1.5;
      const tealIdleY = Math.sin(t * 2.2 + 2) * 2.5;
      const blueIdleY = Math.sin(t * 1.6 + 3) * 2.0;

      // 2. Spring physics integration
      const springK = 70;
      const springDamp = 11;

      // Red Spring
      const redForceY = -springK * (this.impulses.red.y - this.impulses.red.targetY) - springDamp * this.impulses.red.vy;
      this.impulses.red.vy += redForceY * dt;
      this.impulses.red.y += this.impulses.red.vy * dt;

      const redForceRot = -springK * (this.impulses.red.rot - this.impulses.red.targetRot) - springDamp * this.impulses.red.vrot;
      this.impulses.red.vrot += redForceRot * dt;
      this.impulses.red.rot += this.impulses.red.vrot * dt;

      // Teal Spring
      const tealForceY = -springK * (this.impulses.teal.y - this.impulses.teal.targetY) - springDamp * this.impulses.teal.vy;
      this.impulses.teal.vy += tealForceY * dt;
      this.impulses.teal.y += this.impulses.teal.vy * dt;

      // Blue Spring
      const blueForceY = -springK * (this.impulses.blue.y - this.impulses.blue.targetY) - springDamp * this.impulses.blue.vy;
      this.impulses.blue.vy += blueForceY * dt;
      this.impulses.blue.y += this.impulses.blue.vy * dt;

      // 3. Apply Transforms to Bodies
      if (this.elements.pinkBody) {
        this.elements.pinkBody.setAttribute('transform', `translate(0, ${pinkIdleY})`);
      }

      if (this.elements.redHeadRoot) {
        const totalRedY = redIdleY + this.impulses.red.y;
        const totalRedRot = redIdleRot + this.impulses.red.rot;
        // Rotate around head center (155, 140) and keep clamped
        this.elements.redHeadRoot.setAttribute('transform', `rotate(${totalRedRot} 155 140) translate(0, ${totalRedY})`);
      }

      if (this.elements.tealBodyRoot) {
        const totalTealY = tealIdleY + this.impulses.teal.y;
        this.elements.tealBodyRoot.setAttribute('transform', `translate(0, ${totalTealY})`);
      }

      if (this.elements.blueBodyRoot) {
        const totalBlueY = blueIdleY + this.impulses.blue.y;
        this.elements.blueBodyRoot.setAttribute('transform', `translate(0, ${totalBlueY})`);
      }

      // 4. Update Eye Gaze Tracking
      if (!this.isPasswordMode) {
        let targetGx = this.mouseSvgX;
        let targetGy = this.mouseSvgY;

        if (this.currentFocusTarget) {
          targetGx = 450;
          targetGy = 340;
        }

        Object.keys(this.eyes).forEach(key => {
          const eye = this.eyes[key];
          if (!eye.pupilEl) return;

          const dx = targetGx - eye.x;
          const dy = targetGy - eye.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist > 0) {
            const angle = Math.atan2(dy, dx);
            const clampedDist = Math.min(dist * 0.08, eye.maxRadius);
            eye.targetX = Math.cos(angle) * clampedDist;
            eye.targetY = Math.sin(angle) * clampedDist;
          }

          // Smooth interpolation
          eye.currentX += (eye.targetX - eye.currentX) * 0.2;
          eye.currentY += (eye.targetY - eye.currentY) * 0.2;

          eye.pupilEl.setAttribute('transform', `translate(${eye.currentX.toFixed(2)}, ${eye.currentY.toFixed(2)})`);
        });
      }

      requestAnimationFrame(render);
    };

    requestAnimationFrame(render);
  }

  /**
   * Confetti Celebration for Login & Portal Actions
   */
  setupConfetti() {
    this.confettiCanvas = document.getElementById('confetti-canvas');
    if (!this.confettiCanvas) return;
    this.confettiCtx = this.confettiCanvas.getContext('2d');
    this.particles = [];

    const resize = () => {
      this.confettiCanvas.width = window.innerWidth;
      this.confettiCanvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();
  }

  celebrate() {
    if (!this.confettiCanvas || !this.confettiCtx) return;
    const colors = ['#2563eb', '#00d1d1', '#f59e0b', '#10b981', '#ef476f', '#fcaec7', '#298ef8'];
    const w = this.confettiCanvas.width;
    const h = this.confettiCanvas.height;

    for (let i = 0; i < 90; i++) {
      this.particles.push({
        x: w / 2 + (Math.random() - 0.5) * 200,
        y: h / 2 - 50,
        vx: (Math.random() - 0.5) * 16,
        vy: -Math.random() * 14 - 6,
        size: Math.random() * 8 + 5,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        vrot: (Math.random() - 0.5) * 10,
        alpha: 1.0
      });
    }

    if (!this.isCelebrating) {
      this.isCelebrating = true;
      this.renderConfetti();
    }
  }

  renderConfetti() {
    if (!this.confettiCtx) return;
    this.confettiCtx.clearRect(0, 0, this.confettiCanvas.width, this.confettiCanvas.height);

    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.4; // Gravity
      p.rotation += p.vrot;
      p.alpha -= 0.012;

      if (p.alpha <= 0 || p.y > this.confettiCanvas.height) {
        this.particles.splice(i, 1);
        continue;
      }

      this.confettiCtx.save();
      this.confettiCtx.globalAlpha = p.alpha;
      this.confettiCtx.translate(p.x, p.y);
      this.confettiCtx.rotate((p.rotation * Math.PI) / 180);
      this.confettiCtx.fillStyle = p.color;
      this.confettiCtx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      this.confettiCtx.restore();
    }

    if (this.particles.length > 0) {
      requestAnimationFrame(() => this.renderConfetti());
    } else {
      this.isCelebrating = false;
    }
  }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.monsterEngine = new MonsterAnimationEngine();
});
