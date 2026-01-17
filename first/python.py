<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>星际战机 - 经典打飞机</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #050505;
            color: white;
            font-family: 'Microsoft YaHei', sans-serif;
            overflow: hidden; /* 防止滚动 */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        #game-wrapper {
            position: relative;
            width: 100%;
            max-width: 450px;
            height: 100vh;
            max-height: 800px;
            box-shadow: 0 0 50px rgba(0, 150, 255, 0.3);
        }

        canvas {
            background: #000;
            display: block;
            width: 100%;
            height: 100%;
        }

        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none; /* 让鼠标事件穿透到canvas */
        }

        .score-box {
            position: absolute;
            top: 20px;
            left: 20px;
            font-size: 24px;
            font-weight: bold;
            color: #00d2ff;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
        }

        #menu, #game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            background: rgba(0, 0, 0, 0.85);
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #00d2ff;
            pointer-events: auto;
            min-width: 200px;
        }

        #game-over { display: none; }

        button {
            background: #00d2ff;
            border: none;
            padding: 12px 30px;
            font-size: 18px;
            color: black;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 20px;
        }

        button:hover {
            background: #fff;
            box-shadow: 0 0 20px #00d2ff;
        }

        h1 { margin-top: 0; color: #00d2ff; }
    </style>
</head>
<body>

<div id="game-wrapper">
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div class="score-box">分数: <span id="scoreVal">0</span></div>
        
        <!-- 开始菜单 -->
        <div id="menu">
            <h1>星际战机</h1>
            <p>移动鼠标或触摸屏幕控制</p>
            <button onclick="initGame()">开始战斗</button>
        </div>

        <!-- 游戏结束 -->
        <div id="game-over">
            <h1 style="color: #ff4b2b;">战机坠毁</h1>
            <p>最终得分: <span id="finalScore">0</span></p>
            <button onclick="initGame()">重新出击</button>
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreVal = document.getElementById('scoreVal');
    const finalScore = document.getElementById('finalScore');
    const menu = document.getElementById('menu');
    const gameOverScreen = document.getElementById('game-over');

    // 游戏配置
    let gameActive = false;
    let score = 0;
    let player, bullets, enemies, particles, stars;

    // 屏幕适配
    function resize() {
        const wrapper = document.getElementById('game-wrapper');
        canvas.width = wrapper.clientWidth;
        canvas.height = wrapper.clientHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    // 背景星星
    class Star {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speed = Math.random() * 3 + 1;
        }
        draw() {
            ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
        update() {
            this.y += this.speed;
            if (this.y > canvas.height) {
                this.y = 0;
                this.x = Math.random() * canvas.width;
            }
        }
    }

    // 玩家战机
    class Player {
        constructor() {
            this.w = 40;
            this.h = 45;
            this.x = canvas.width / 2;
            this.y = canvas.height - 80;
        }
        draw() {
            // 绘制机身
            ctx.fillStyle = '#00d2ff';
            ctx.beginPath();
            ctx.moveTo(this.x, this.y - 20);
            ctx.lineTo(this.x - 20, this.y + 20);
            ctx.lineTo(this.x + 20, this.y + 20);
            ctx.closePath();
            ctx.fill();
            // 引擎火光
            ctx.fillStyle = '#ff9d00';
            ctx.fillRect(this.x - 5, this.y + 20, 10, 5);
        }
    }

    // 子弹
    class Bullet {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.speed = 10;
            this.r = 3;
        }
        draw() {
            ctx.fillStyle = '#ffff00';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fill();
        }
        update() { this.y -= this.speed; }
    }

    // 敌机
    class Enemy {
        constructor() {
            this.w = 30 + Math.random() * 20;
            this.h = 30;
            this.x = Math.random() * (canvas.width - this.w) + this.w/2;
            this.y = -50;
            this.speed = 2 + (score / 500); // 随分数增加速度
            this.color = `hsl(${Math.random() * 360}, 70%, 50%)`;
        }
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.moveTo(this.x, this.y + 20);
            ctx.lineTo(this.x - 15, this.y - 10);
            ctx.lineTo(this.x + 15, this.y - 10);
            ctx.closePath();
            ctx.fill();
        }
        update() { this.y += this.speed; }
    }

    // 爆炸粒子
    class Particle {
        constructor(x, y, color) {
            this.x = x; this.y = y; this.color = color;
            this.size = Math.random() * 3;
            this.speedX = (Math.random() - 0.5) * 6;
            this.speedY = (Math.random() - 0.5) * 6;
            this.life = 1;
        }
        draw() {
            ctx.globalAlpha = this.life;
            ctx.fillStyle = this.color;
            ctx.fillRect(this.x, this.y, this.size, this.size);
            ctx.globalAlpha = 1;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.life -= 0.02;
        }
    }

    function initGame() {
        score = 0;
        gameActive = true;
        player = new Player();
        bullets = [];
        enemies = [];
        particles = [];
        stars = Array.from({length: 50}, () => new Star());
        
        scoreVal.innerText = score;
        menu.style.display = 'none';
        gameOverScreen.style.display = 'none';
        
        requestAnimationFrame(update);
    }

    // 输入控制
    const handleMove = (e) => {
        if (!gameActive) return;
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        player.x = clientX - rect.left;
    };
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('touchmove', (e) => {
        handleMove(e);
        e.preventDefault();
    }, {passive: false});

    // 自动射击
    setInterval(() => {
        if (gameActive) bullets.push(new Bullet(player.x, player.y - 20));
    }, 200);

    function update() {
        if (!gameActive) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. 背景
        stars.forEach(s => { s.update(); s.draw(); });

        // 2. 玩家
        player.draw();

        // 3. 子弹处理
        bullets.forEach((b, i) => {
            b.update();
            b.draw();
            if (b.y < 0) bullets.splice(i, 1);
        });

        // 4. 敌人生成
        if (Math.random() < 0.04) enemies.push(new Enemy());

        // 5. 敌人更新与碰撞检测
        enemies.forEach((en, i) => {
            en.update();
            en.draw();

            // 撞击玩家检测
            const distToPlayer = Math.hypot(en.x - player.x, en.y - player.y);
            if (distToPlayer < 30) {
                endGame();
            }

            // 越界
            if (en.y > canvas.height) {
                enemies.splice(i, 1);
                score = Math.max(0, score - 5); // 漏掉敌人扣分
            }

            // 被子弹击中
            bullets.forEach((b, bi) => {
                const dist = Math.hypot(en.x - b.x, en.y - b.y);
                if (dist < 25) {
                    // 产生粒子
                    for(let i=0; i<10; i++) particles.push(new Particle(en.x, en.y, en.color));
                    enemies.splice(i, 1);
                    bullets.splice(bi, 1);
                    score += 10;
                    scoreVal.innerText = score;
                }
            });
        });

        // 6. 粒子动画
        particles.forEach((p, i) => {
            p.update();
            p.draw();
            if (p.life <= 0) particles.splice(i, 1);
        });

        requestAnimationFrame(update);
    }

    function endGame() {
        gameActive = false;
        gameOverScreen.style.display = 'block';
        finalScore.innerText = score;
    }
</script>

</body>
</html>
